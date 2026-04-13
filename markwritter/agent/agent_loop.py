# Agent loop for Markwritter.
# Orchestrates the LLM tool-use loop:
#   1. Send messages + tools to LLM
#   2. If LLM responds with tool_use blocks, execute them
#   3. Feed tool results back to LLM
#   4. Repeat until LLM returns text-only response (or max iterations)

import json
import logging
from typing import Any, AsyncGenerator

import aiohttp

from markwritter.agent.tool_executor import ToolExecutor
from markwritter.agent.tools import get_vault_tools
from markwritter.llm_client import LLMClient

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 10


class AgentLoop:

    def __init__(self, tool_executor: ToolExecutor) -> None:
        self._tool_executor = tool_executor
        self._tools = get_vault_tools()

    async def run(
        self,
        messages: list[dict[str, Any]],
        llm_client: LLMClient,
        model: str,
        api_base: str,
        api_key: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        # Run the agent loop, yielding SSE events.
        #
        # Yields dicts with keys:
        #   type: "thinking" | "text_delta" | "tool_start" | "tool_result" | "tool_end" | "done" | "error"
        #   content: str (for text_delta, error)
        #   tool_name: str (for tool_start, tool_result, tool_end)
        #   tool_input: dict (for tool_start)
        #   tool_output: str (for tool_result)
        #   is_error: bool (for tool_result)

        tool_definitions = self._tools
        current_messages = list(messages)

        for iteration in range(MAX_TOOL_ITERATIONS):
            logger.info("Agent loop iteration %d", iteration + 1)

            # Stream LLM response and collect tool_use blocks
            text_parts: list[str] = []
            tool_use_blocks: list[dict[str, Any]] = []
            stop_reason = "end_turn"

            async for event in self._stream_llm(
                llm_client=llm_client,
                messages=current_messages,
                model=model,
                api_base=api_base,
                api_key=api_key,
                tools=tool_definitions,
            ):
                if event["type"] == "text_delta":
                    text_parts.append(event["content"])
                    yield event
                elif event["type"] == "tool_use_block":
                    tool_use_blocks.append(event["block"])
                elif event["type"] == "stop_reason":
                    stop_reason = event["reason"]
                elif event["type"] == "error":
                    yield event
                    return

            # If no tool_use blocks or stop_reason is end_turn, we're done
            if not tool_use_blocks or stop_reason != "tool_use":
                # Stream completed, yield done
                full_text = "".join(text_parts)

                # Add assistant message to conversation
                assistant_content: list[dict[str, Any]] = []
                if full_text:
                    assistant_content.append({"type": "text", "text": full_text})
                for tb in tool_use_blocks:
                    assistant_content.append(tb)
                if assistant_content:
                    current_messages.append({"role": "assistant", "content": assistant_content})

                yield {"type": "done", "content": full_text}
                return

            # Build assistant message with tool_use blocks
            assistant_content = []
            if text_parts:
                assistant_content.append({"type": "text", "text": "".join(text_parts)})
            for tb in tool_use_blocks:
                assistant_content.append(tb)
            current_messages.append({"role": "assistant", "content": assistant_content})

            # Execute each tool and collect results
            tool_results: list[dict[str, Any]] = []
            for tool_block in tool_use_blocks:
                tool_id = tool_block.get("id", "")
                tool_name = tool_block.get("name", "")
                tool_input = tool_block.get("input", {})

                # Yield tool_start event
                yield {
                    "type": "tool_start",
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                }

                # Execute the tool
                result_str = self._tool_executor.execute(tool_name, tool_input)
                is_error = False
                try:
                    parsed = json.loads(result_str)
                    is_error = "error" in parsed
                except json.JSONDecodeError:
                    is_error = True

                # Yield tool_result event
                yield {
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "tool_output": result_str,
                    "is_error": is_error,
                }

                # Build Anthropic tool_result content block
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result_str,
                    "is_error": is_error,
                })

            # Add tool results as user message (Anthropic convention)
            current_messages.append({"role": "user", "content": tool_results})

            # Yield tool_end to signal all tools in this iteration completed
            yield {
                "type": "tool_end",
                "tool_count": len(tool_use_blocks),
            }

            # Loop continues - LLM will see tool results and decide what to do next

        # Max iterations reached
        yield {"type": "error", "content": "Agent loop reached maximum iterations"}

    async def _stream_llm(
        self,
        llm_client: LLMClient,
        messages: list[dict[str, Any]],
        model: str,
        api_base: str,
        api_key: str,
        tools: list[dict[str, Any]],
    ) -> AsyncGenerator[dict[str, Any], None]:
        # Stream from the Anthropic-compatible Messages API with tools.
        # Parses SSE events to extract text deltas, tool_use blocks, and stop_reason.

        payload = llm_client.build_anthropic_payload(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=None,
        )
        payload["tools"] = tools

        headers = llm_client.build_anthropic_bearer_headers(api_key)
        url = llm_client.build_anthropic_request_url(api_base)

        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status >= 400:
                    error_body = await response.text()
                    yield {"type": "error", "content": f"API error ({response.status}): {error_body[:500]}"}
                    return

                event_name = None
                data_lines: list[str] = []

                # Track current content block
                current_tool_block: dict[str, Any] | None = None
                current_input_json_parts: list[str] = []

                async for raw_line in response.content:
                    line = raw_line.decode("utf-8").strip()

                    if not line:
                        if not data_lines:
                            event_name = None
                            continue

                        data = "\n".join(data_lines)
                        if data == "[DONE]":
                            event_name = None
                            data_lines = []
                            continue

                        try:
                            payload_event = json.loads(data)
                        except json.JSONDecodeError:
                            event_name = None
                            data_lines = []
                            continue

                        evt_type = event_name or payload_event.get("type")

                        if evt_type == "content_block_start":
                            block = payload_event.get("content_block", {})
                            if block.get("type") == "tool_use":
                                current_tool_block = {
                                    "type": "tool_use",
                                    "id": block.get("id", ""),
                                    "name": block.get("name", ""),
                                    "input": {},
                                }
                                current_input_json_parts = []

                        elif evt_type == "content_block_delta":
                            delta = payload_event.get("delta", {})
                            if delta.get("type") == "text_delta":
                                text = delta.get("text", "")
                                if text:
                                    yield {"type": "text_delta", "content": text}
                            elif delta.get("type") == "input_json_delta":
                                partial = delta.get("partial_json", "")
                                if partial:
                                    current_input_json_parts.append(partial)

                        elif evt_type == "content_block_stop":
                            if current_tool_block is not None:
                                # Parse accumulated input JSON
                                raw_json = "".join(current_input_json_parts)
                                try:
                                    parsed_input = json.loads(raw_json) if raw_json else {}
                                except json.JSONDecodeError:
                                    parsed_input = {}
                                current_tool_block["input"] = parsed_input
                                yield {"type": "tool_use_block", "block": current_tool_block}
                                current_tool_block = None
                                current_input_json_parts = []

                        elif evt_type == "message_delta":
                            delta = payload_event.get("delta", {})
                            stop = delta.get("stop_reason")
                            if stop:
                                yield {"type": "stop_reason", "reason": stop}

                        elif evt_type == "error":
                            error = payload_event.get("error", {})
                            msg = error.get("message") or payload_event.get("message", "Unknown error")
                            yield {"type": "error", "content": msg}

                        event_name = None
                        data_lines = []
                        continue

                    if line.startswith("event:"):
                        event_name = line[6:].strip()
                    elif line.startswith("data:"):
                        data_lines.append(line[5:].strip())
