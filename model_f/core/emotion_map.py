"""Lightweight emotional labeling layer for drive vectors.

Maps a 6-dimensional drive vector to human-readable emotion labels using
cosine similarity against prototype vectors.  Pure observation — does not
affect system dynamics.
"""

from dataclasses import dataclass

import numpy as np

# Drive dimensions (for reference):
#   [seek_novelty, withdraw, engage, rest, seek_comfort, express]

DEFAULT_PROTOTYPES: dict[str, np.ndarray] = {
    "restless":    np.array([0.8, 0.1, 0.7, 0.1, 0.2, 0.6]),
    "anxious":     np.array([0.2, 0.8, 0.2, 0.1, 0.7, 0.1]),
    "content":     np.array([0.2, 0.1, 0.3, 0.8, 0.5, 0.2]),
    "excited":     np.array([0.9, 0.0, 0.9, 0.0, 0.2, 0.8]),
    "melancholic": np.array([0.1, 0.6, 0.1, 0.5, 0.6, 0.1]),
    "energized":   np.array([0.5, 0.0, 0.9, 0.1, 0.1, 0.7]),
    "calm":        np.array([0.1, 0.0, 0.2, 0.7, 0.4, 0.1]),
    "fearful":     np.array([0.1, 0.9, 0.1, 0.0, 0.8, 0.0]),
    "curious":     np.array([0.9, 0.0, 0.6, 0.1, 0.1, 0.5]),
    "lethargic":   np.array([0.0, 0.3, 0.0, 0.9, 0.3, 0.0]),
}


@dataclass
class EmotionLabel:
    """A single emotion label with its cosine-similarity confidence score."""

    name: str           # e.g., "anxious", "content"
    confidence: float   # cosine similarity score, 0.0 to 1.0


class EmotionMap:
    """Maps drive vectors to human-readable emotion labels via cosine similarity."""

    def __init__(self, prototypes: dict[str, np.ndarray] | None = None) -> None:
        """
        Args:
            prototypes: mapping from emotion name to a prototype drive vector
                        (length 6).  If None, uses DEFAULT_PROTOTYPES.
        """
        self._prototypes: dict[str, np.ndarray] = (
            prototypes if prototypes is not None else DEFAULT_PROTOTYPES
        )

    def label(self, drive_vector: np.ndarray, top_k: int = 3) -> list[EmotionLabel]:
        """Return top-k closest emotion labels by cosine similarity.

        Args:
            drive_vector: 6-dimensional drive state vector.
            top_k: number of labels to return.

        Returns:
            List of EmotionLabel sorted by confidence descending.
        """
        results: list[EmotionLabel] = []
        for name, prototype in self._prototypes.items():
            sim = self._cosine_similarity(drive_vector, prototype)
            results.append(EmotionLabel(name=name, confidence=sim))

        results.sort(key=lambda el: el.confidence, reverse=True)
        return results[:top_k]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two vectors, safe for zero vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
