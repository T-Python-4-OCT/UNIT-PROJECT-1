"""Plate reading: text cleaning, finding the plate in OCR output, Apple Vision OCR."""

from __future__ import annotations

import importlib.util
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# A box is (x, y, width, height), all normalized 0..1, origin at the TOP-LEFT.
Box = tuple[float, float, float, float]


# --------------------------------------------------------------------------- #
# Plate text helpers
# --------------------------------------------------------------------------- #
class PlateCleaner:
    """Normalizes plate text and compares plates that OCR may have misread."""

    MIN_LENGTH = 4
    MAX_LENGTH = 10

    # Arabic-Indic (U+0660..) and Persian (U+06F0..) digits -> 0-9
    _DIGIT_MAP = {
        **{0x0660 + i: str(i) for i in range(10)},
        **{0x06F0 + i: str(i) for i in range(10)},
    }
    # Characters OCR often mixes up; used only to compare plates.
    _CONFUSABLE_MAP = str.maketrans(
        {"O": "0", "Q": "0", "D": "0", "I": "1", "L": "1",
         "Z": "2", "S": "5", "G": "6", "B": "8"}
    )

    @classmethod
    def to_latin_digits(cls, text: str) -> str:
        return text.translate(cls._DIGIT_MAP)

    @classmethod
    def clean(cls, text: str) -> str:
        """Uppercase, Latin digits, letters/digits only (no spaces or dashes)."""
        text = cls.to_latin_digits(text).upper()
        return "".join(ch for ch in text if ch.isalnum())
    
    @staticmethod
    def display(plate: str) -> str:
        """For showing only: 'ABC1234' -> 'A B C - 1 2 3 4'."""
        groups = [match.group() for match in re.finditer(r"\d+|\D+", plate)]
        return " | ".join(" ".join(group) for group in groups)

    @classmethod
    def is_plausible(cls, plate: str) -> bool:
        return cls.MIN_LENGTH <= len(plate) <= cls.MAX_LENGTH and any(
            ch.isdigit() for ch in plate
        )

    @classmethod
    def canonical(cls, plate: str) -> str:
        return plate.translate(cls._CONFUSABLE_MAP)

    @staticmethod
    def distance(a: str, b: str) -> int:
        """Levenshtein edit distance."""
        if a == b:
            return 0
        previous = list(range(len(b) + 1))
        for i, char_a in enumerate(a, start=1):
            current = [i]
            for j, char_b in enumerate(b, start=1):
                current.append(
                    min(
                        previous[j] + 1,                       # deletion
                        current[j - 1] + 1,                    # insertion
                        previous[j - 1] + (char_a != char_b),  # substitution
                    )
                )
            previous = current
        return previous[-1]

    @classmethod
    def is_similar(cls, a: str, b: str) -> bool:
        """True if two different plates could be the same car misread by OCR."""
        if a == b:
            return False
        return cls.canonical(a) == cls.canonical(b) or cls.distance(a, b) <= 1


# --------------------------------------------------------------------------- #
# Data objects
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class TextObservation:
    """One piece of text found by the OCR engine."""

    text: str
    confidence: float
    box: Box


@dataclass(frozen=True)
class PlateDetection:
    """The plate chosen among all the text found in an image."""

    plate: str
    confidence: float
    box: Box


# --------------------------------------------------------------------------- #
# Finding the plate among OCR text (pure logic, easy to test)
# --------------------------------------------------------------------------- #
class PlateFinder:
    """Chooses the most plate-like text among OCR observations.

    Plates are often split in several text pieces (letters and digits), so
    single observations and pairs of nearby observations are both considered.
    """

    MIN_CONFIDENCE = 0.3
    _LETTERS_DIGITS = re.compile(r"^[^\W\d_]{1,4}\d{2,4}$|^\d{2,4}[^\W\d_]{1,4}$")

    def find(self, observations: list[TextObservation]) -> PlateDetection | None:
        items = []
        for obs in observations:
            if obs.confidence < self.MIN_CONFIDENCE:
                continue
            cleaned = PlateCleaner.clean(obs.text)
            if cleaned:
                items.append((obs, cleaned))

        candidates: list[tuple[float, PlateDetection]] = []

        for obs, cleaned in items:
            if PlateCleaner.is_plausible(cleaned):
                candidates.append(self._candidate(cleaned, obs.confidence, obs.box))

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                first, second = self._reading_order(items[i], items[j])
                if not self._near(first[0].box, second[0].box):
                    continue
                combined = first[1] + second[1]
                if PlateCleaner.is_plausible(combined):
                    confidence = min(first[0].confidence, second[0].confidence)
                    box = self._union(first[0].box, second[0].box)
                    candidates.append(self._candidate(combined, confidence, box))

        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]

    # -- helpers ----------------------------------------------------------- #
    def _candidate(
        self, plate: str, confidence: float, box: Box
    ) -> tuple[float, PlateDetection]:
        score = confidence
        if any(ch.isalpha() for ch in plate) and any(ch.isdigit() for ch in plate):
            score += 0.3
        if self._LETTERS_DIGITS.match(plate):
            score += 0.2
        score += min(len(plate), 8) * 0.02
        return score, PlateDetection(plate, max(0.0, min(confidence, 1.0)), box)

    @staticmethod
    def _reading_order(a: tuple, b: tuple) -> tuple[tuple, tuple]:
        """Top line first; on the same line, left to right."""
        (ax, ay, aw, ah), (bx, by, bw, bh) = a[0].box, b[0].box
        if abs((ay + ah / 2) - (by + bh / 2)) > 0.5 * max(ah, bh):
            return (a, b) if ay <= by else (b, a)
        return (a, b) if ax <= bx else (b, a)

    @staticmethod
    def _near(a: Box, b: Box) -> bool:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        gap_x = max(0.0, max(ax, bx) - min(ax + aw, bx + bw))
        gap_y = max(0.0, max(ay, by) - min(ay + ah, by + bh))
        return gap_x <= max(aw, bw) and gap_y <= max(ah, bh)

    @staticmethod
    def _union(a: Box, b: Box) -> Box:
        x1, y1 = min(a[0], b[0]), min(a[1], b[1])
        x2 = max(a[0] + a[2], b[0] + b[2])
        y2 = max(a[1] + a[3], b[1] + b[3])
        return (x1, y1, x2 - x1, y2 - y1)


# --------------------------------------------------------------------------- #
# OCR readers
# --------------------------------------------------------------------------- #
class PlateReader(ABC):
    """Base class: subclasses read text from an image, this class finds the plate."""

    def __init__(self, finder: PlateFinder | None = None) -> None:
        self.finder = finder or PlateFinder()

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """True if this reader can work on the current machine."""

    @abstractmethod
    def read_text(self, frame: Any) -> list[TextObservation]:
        """Run OCR on a BGR image (numpy array) and return all text found."""

    def detect(self, frame: Any) -> PlateDetection | None:
        return self.finder.find(self.read_text(frame))


class AppleVisionReader(PlateReader):
    """OCR using Apple Vision (built into macOS). Arabic + English."""

    MAX_WIDTH = 1280  # larger frames are shrunk before OCR to keep it fast
    _WANTED_LANGUAGES = ("ar", "en")

    def __init__(self, finder: PlateFinder | None = None) -> None:
        super().__init__(finder)
        self._languages: list[str] | None = None
        self._languages_ready = False

    @classmethod
    def is_available(cls) -> bool:
        if sys.platform != "darwin":
            return False
        return all(
            importlib.util.find_spec(name) is not None
            for name in ("cv2", "Vision", "Foundation", "objc")
        )

    def read_text(self, frame: Any) -> list[TextObservation]:
        import cv2
        import objc
        import Vision
        from Foundation import NSData

        height, width = frame.shape[:2]
        if width > self.MAX_WIDTH:
            scale = self.MAX_WIDTH / width
            frame = cv2.resize(frame, (self.MAX_WIDTH, int(height * scale)))

        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not ok:
            return []
        raw = buffer.tobytes()

        # This code runs in a background thread, so it needs its own memory pool.
        with objc.autorelease_pool():
            data = NSData.dataWithBytes_length_(raw, len(raw))
            if not self._languages_ready:
                self._languages = self._pick_languages(Vision)
                self._languages_ready = True

            results = self._perform(Vision, data, self._languages)
            if results is None and self._languages:
                # The language list was rejected: retry with the OS defaults.
                self._languages = None
                results = self._perform(Vision, data, None)
            return self._to_observations(results or [])

    # -- Vision helpers ---------------------------------------------------- #
    def _new_request(self, vision: Any, languages: list[str] | None) -> Any:
        request = vision.VNRecognizeTextRequest.alloc().init()
        request.setRecognitionLevel_(vision.VNRequestTextRecognitionLevelAccurate)
        request.setUsesLanguageCorrection_(False)  # plates are not dictionary words
        if languages:
            request.setRecognitionLanguages_(languages)
        return request

    def _pick_languages(self, vision: Any) -> list[str] | None:
        """Choose Arabic/English variants this macOS version really supports."""
        try:
            probe = self._new_request(vision, None)
            supported, _error = probe.supportedRecognitionLanguagesAndReturnError_(None)
            supported = [str(lang) for lang in (supported or [])]
        except Exception:
            return None
        chosen = []
        for prefix in self._WANTED_LANGUAGES:
            match = next((lang for lang in supported if lang.lower().startswith(prefix)), None)
            if match:
                chosen.append(match)
        return chosen or None

    def _perform(self, vision: Any, data: Any, languages: list[str] | None) -> list | None:
        try:
            handler = vision.VNImageRequestHandler.alloc().initWithData_options_(data, {})
            request = self._new_request(vision, languages)
            success, _error = handler.performRequests_error_([request], None)
        except Exception:
            return None
        if not success:
            return None
        return list(request.results() or [])

    @staticmethod
    def _to_observations(results: list) -> list[TextObservation]:
        observations = []
        for item in results:
            candidates = item.topCandidates_(1)
            if not candidates:
                continue
            best = candidates[0]
            rect = item.boundingBox()  # normalized, origin at the BOTTOM-left
            x, w = float(rect.origin.x), float(rect.size.width)
            h = float(rect.size.height)
            y = 1.0 - (float(rect.origin.y) + h)  # flip to top-left origin
            observations.append(
                TextObservation(str(best.string()), float(best.confidence()), (x, y, w, h))
            )
        return observations


def create_reader() -> PlateReader | None:
    """Return the best OCR reader for this machine, or None (manual entry only)."""
    if AppleVisionReader.is_available():
        return AppleVisionReader()
    return None
