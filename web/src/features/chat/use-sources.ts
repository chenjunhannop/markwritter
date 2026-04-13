import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  clearSelectedSources,
  getFileTree,
  getSelectedSources,
  selectSources,
} from "./chat-api";
import { useChatStore } from "./chat-store";

export function useFileTree() {
  return useQuery({
    queryKey: ["chat", "file-tree"],
    queryFn: getFileTree,
    staleTime: 60_000,
  });
}

export function useSelectedSources(sessionId: string | null) {
  return useQuery({
    queryKey: ["chat", "sources", sessionId],
    queryFn: () => {
      if (!sessionId) throw new Error("No session");
      return getSelectedSources(sessionId);
    },
    enabled: !!sessionId,
    staleTime: 30_000,
  });
}

export function useSelectSources() {
  const queryClient = useQueryClient();
  const setActiveSessionSources = useChatStore(
    (s) => s.setActiveSessionSources,
  );

  return useMutation({
    mutationFn: ({
      sessionId,
      paths,
    }: {
      sessionId: string;
      paths: string[];
    }) => selectSources(sessionId, paths),
    onSuccess: (_, variables) => {
      setActiveSessionSources(variables.paths);
      queryClient.invalidateQueries({
        queryKey: ["chat", "sources", variables.sessionId],
      });
    },
  });
}

export function useClearSources() {
  const queryClient = useQueryClient();
  const setActiveSessionSources = useChatStore(
    (s) => s.setActiveSessionSources,
  );

  return useMutation({
    mutationFn: (sessionId: string) => clearSelectedSources(sessionId),
    onSuccess: (_, sessionId) => {
      setActiveSessionSources([]);
      queryClient.invalidateQueries({
        queryKey: ["chat", "sources", sessionId],
      });
    },
  });
}
