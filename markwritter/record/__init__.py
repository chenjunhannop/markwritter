"""Record module for note creation and AI assistance.

This module provides:
- WritingAssistant: AI-powered writing assistance (continue, rewrite, polish)
- AutoClassifier: Automatic note classification and tagging
- ClassifyResult: Result model for classification
"""

from markwritter.record.assistant import AutoClassifier, ClassifyResult, WritingAssistant

__all__ = ["WritingAssistant", "AutoClassifier", "ClassifyResult"]