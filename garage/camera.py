"""Live webcam scanning: video window, background OCR and a box around the plate."""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from garage.plate_reader import PlateDetection, PlateReader
from garage.storage import JsonStorage, StorageError

try:  
    import cv2
except ImportError:  
    cv2 = None


# --------------------------------------------------------------------------- #
# Results and settings
# --------------------------------------------------------------------------- #
class ScanStatus(Enum):
    CAPTURED = "captured"    # a plate was read
    MANUAL = "manual"        # the user pressed M
    CANCELLED = "cancelled"  # Esc or window closed
    ERROR = "error"          # camera problem


@dataclass(frozen=True)
class ScanResult:
    status: ScanStatus
    plate: str | None = None
    message: str = ""


class CameraSettings:
    """Remembers which camera to use (saved in ``data/camera.json``)."""

    LABELS = {0: "Mac webcam", 1: "iPhone camera"}

    def __init__(self, path: str | Path) -> None:
        self._storage = JsonStorage(path)
        self.index = self._load()

    def _load(self) -> int:
        try:
            data = self._storage.read(default={})
        except StorageError:
            return 0
        index = data.get("camera_index", 0) if isinstance(data, dict) else 0
        return index if index in self.LABELS else 0

    @property
    def label(self) -> str:
        return self.label_of(self.index)

    @classmethod
    def label_of(cls, index: int) -> str:
        return cls.LABELS.get(index, f"Camera {index}")

    def other_index(self) -> int:
        return 1 - self.index if self.index in (0, 1) else 0

    def use(self, index: int) -> None:
        self.index = index
        try:
            self._storage.write({"camera_index": self.index})
        except StorageError:
            pass  # not being able to remember the camera is not a problem


# --------------------------------------------------------------------------- #
# Background OCR and stability
# --------------------------------------------------------------------------- #
class OcrWorker:
    """Runs OCR in a background thread so the video never freezes."""

    def __init__(self, reader: PlateReader) -> None:
        self._reader = reader
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self._stop_event = threading.Event()
        self._frame: Any = None
        self._seq = 0
        self._detection: PlateDetection | None = None
        self._stamp = 0.0
        self._thread = threading.Thread(target=self._run, name="plate-ocr", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._wake.set()
        self._thread.join(timeout=2.0)

    def submit(self, frame: Any) -> None:
        """Give the newest frame; frames not yet processed are dropped."""
        with self._lock:
            self._frame = frame
        self._wake.set()

    def latest(self) -> tuple[int, PlateDetection | None, float]:
        """(result number, detection or None, time of the result)."""
        with self._lock:
            return self._seq, self._detection, self._stamp

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._wake.wait(timeout=0.2)
            self._wake.clear()
            with self._lock:
                frame, self._frame = self._frame, None
            if frame is None:
                continue
            try:
                detection = self._reader.detect(frame)
            except Exception:  # OCR problems must never crash the camera window
                detection = None
            with self._lock:
                self._seq += 1
                self._detection = detection
                self._stamp = time.monotonic()


class StabilityTracker:
    """Counts how many OCR results in a row gave the same plate."""

    def __init__(self, required: int = 3) -> None:
        self.required = required
        self._plate: str | None = None
        self._count = 0
        self._last_seq = -1

    def update(self, seq: int, plate: str | None) -> None:
        if seq == self._last_seq:  # same OCR result seen again: do not count twice
            return
        self._last_seq = seq
        if plate is None:
            self._plate, self._count = None, 0
        elif plate == self._plate:
            self._count += 1
        else:
            self._plate, self._count = plate, 1

    @property
    def stable_plate(self) -> str | None:
        return self._plate if self._count >= self.required else None

    def reset(self) -> None:
        self._plate, self._count = None, 0


# --------------------------------------------------------------------------- #
# The scanner
# --------------------------------------------------------------------------- #
class CameraScanner:
    """Opens the camera, shows live video and returns the plate that was read."""

    WINDOW = "Garage - plate scan"
    STABLE_READS = 3        # same number this many times in a row = captured
    RESULT_TTL = 55        # seconds a box stays on screen after the last read
    NO_FRAME_TIMEOUT = 8.0  # seconds without any image before giving up
    KEY_ESC = 27
    KEYS_ACCEPT = (13, 10, 32)  # Enter, Enter, Space

    GREEN = (60, 200, 60)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    PLATE_GREEN = (0, 150, 0)      # digits on the plate card (BGR)
    PLATE_BORDER = (40, 40, 40)


    def __init__(self, reader: PlateReader, settings: CameraSettings) -> None:
        self.reader = reader
        self.settings = settings

    @staticmethod
    def is_available() -> bool:
        return cv2 is not None

    # -- main loop --------------------------------------------------------- #
    def scan(self) -> ScanResult:
        if cv2 is None:
            return ScanResult(ScanStatus.ERROR, message="OpenCV is not installed.")

        capture = self._open_with_fallback()
        if capture is None:
            return ScanResult(
                ScanStatus.ERROR,
                message=(
                    "Cannot open the camera. Allow your Terminal in System Settings -> "
                    "Privacy & Security -> Camera, then restart the Terminal."
                ),
            )

        worker = OcrWorker(self.reader)
        tracker = StabilityTracker(self.STABLE_READS)
        worker.start()

        notice, notice_until = "", 0.0
        last_frame_time = time.monotonic()
        window_was_visible = False

        try:
            while True:
                ok, frame = capture.read()
                now = time.monotonic()
                if not ok or frame is None:
                    if now - last_frame_time > self.NO_FRAME_TIMEOUT:
                        return ScanResult(
                            ScanStatus.ERROR, message="The camera does not give any image."
                        )
                    cv2.waitKey(30)
                    continue
                last_frame_time = now

                worker.submit(frame)
                seq, detection, stamp = worker.latest()
                if detection is not None and now - stamp > self.RESULT_TTL:
                    detection = None
                tracker.update(seq, detection.plate if detection else None)

                stable = tracker.stable_plate
                if stable:
                    return ScanResult(ScanStatus.CAPTURED, plate=stable)

                view = frame.copy()
                self._draw(view, detection, notice if now < notice_until else "")
                cv2.imshow(self.WINDOW, view)
                key = cv2.waitKey(1) & 0xFF

                if key == self.KEY_ESC:
                    return ScanResult(ScanStatus.CANCELLED)
                if key in (ord("m"), ord("M")):
                    return ScanResult(ScanStatus.MANUAL)
                if key in self.KEYS_ACCEPT:
                    if detection is not None:
                        return ScanResult(ScanStatus.CAPTURED, plate=detection.plate)
                    notice, notice_until = "No plate detected yet", now + 2.0
                if key in (ord("c"), ord("C")):
                    capture, notice = self._switch_camera(capture)
                    notice_until = now + 3.0
                    tracker.reset()

                if self._window_closed(window_was_visible):
                    return ScanResult(ScanStatus.CANCELLED)
                window_was_visible = window_was_visible or self._window_visible()
        finally:
            worker.stop()
            capture.release()
            self._close_window()

    # -- camera handling --------------------------------------------------- #
    @staticmethod
    def _open(index: int) -> Any:
        backend = getattr(cv2, "CAP_AVFOUNDATION", 0) if sys.platform == "darwin" else 0
        capture = cv2.VideoCapture(index, backend) if backend else cv2.VideoCapture(index)
        if not capture.isOpened():
            capture.release()
            return None
        return capture

    def _open_with_fallback(self) -> Any:
        """Open the saved camera; if it fails, try the other one."""
        for index in (self.settings.index, self.settings.other_index()):
            capture = self._open(index)
            if capture is not None:
                if index != self.settings.index:
                    self.settings.use(index)
                return capture
        return None

    def _switch_camera(self, current: Any) -> tuple[Any, str]:
        new_index = self.settings.other_index()
        new_capture = self._open(new_index)
        if new_capture is None:
            return current, f"{self.settings.label_of(new_index)} is not available"
        current.release()
        self.settings.use(new_index)
        return new_capture, f"Using: {self.settings.label}"

    # -- window handling --------------------------------------------------- #
    def _window_visible(self) -> bool:
        try:
            return cv2.getWindowProperty(self.WINDOW, cv2.WND_PROP_VISIBLE) >= 1
        except cv2.error:
            return False

    def _window_closed(self, was_visible: bool) -> bool:
        """True only if the window was seen open before and is now gone."""
        return was_visible and not self._window_visible()

    @staticmethod
    def _close_window() -> None:
        try:
            cv2.destroyAllWindows()
            for _ in range(5):  # macOS needs a few event-loop turns to close it
                cv2.waitKey(1)
        except cv2.error:
            pass

    # -- drawing ----------------------------------------------------------- #
    def _draw(self, image: Any, detection: PlateDetection | None, notice: str) -> None:
        height, width = image.shape[:2]

        if detection is not None:
            x, y, w, h = detection.box
            x1, y1 = max(int(x * width), 0), max(int(y * height), 0)
            x2, y2 = min(int((x + w) * width), width - 1), min(int((y + h) * height), height - 1)
            cv2.rectangle(image, (x1, y1), (x2, y2), self.GREEN, 3)
            self._draw_plate_card(image, detection.plate, (x1, y1, x2, y2))

        help_line = f"Space: accept | M: manual | C: camera ({self.settings.label}) | Esc: cancel"
        self._text(image, help_line, (10, height - 12), 0.55, self.WHITE)
        if notice:
            self._text(image, notice, (10, 30), 0.8, (0, 215, 255))



    def _draw_plate_card(
        self, image: Any, plate: str, box: tuple[int, int, int, int]) -> None:
        """Draw the plate number as a white plate-like rectangle with green digits."""
        height, width = image.shape[:2]
        x1, y1, x2, y2 = box
        # OpenCV fonts cannot draw Arabic letters, so only Latin letters/digits are drawn.
        text = "".join(ch for ch in plate if ch.isascii()) or "-"
        font, scale, thickness = cv2.FONT_HERSHEY_DUPLEX, 1.2, 3
        (text_w, text_h), baseline = cv2.getTextSize(text, font, scale, thickness)

        card_w, card_h = text_w + 40, text_h + baseline + 28
        left = max(min((x1 + x2) // 2 - card_w // 2, width - card_w), 0)
        top = y1 - card_h - 10                      # above the green box...
        if top < 0:
            top = min(y2 + 10, height - card_h)     # ...or below it if there is no room
        right, bottom = left + card_w, top + card_h

        cv2.rectangle(image, (left, top), (right, bottom), (255, 255, 255), -1)
        cv2.rectangle(image, (left, top), (right, bottom), self.PLATE_BORDER, 3)
        cv2.rectangle(image, (left + 5, top + 5), (right - 5, bottom - 5), self.PLATE_BORDER, 1)
        cv2.putText(
            image, text, (left + (card_w - text_w) // 2, top + 14 + text_h),
            font, scale, self.PLATE_GREEN, thickness, cv2.LINE_AA,
        )


    def _text(self, image: Any, text: str, origin: tuple[int, int], scale: float,
              color: tuple[int, int, int]) -> None:
        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_w, text_h), baseline = cv2.getTextSize(text, font, scale, 2)
        x, y = origin
        cv2.rectangle(
            image, (x - 4, y - text_h - 6), (x + text_w + 4, y + baseline + 2), self.BLACK, -1
        )
        cv2.putText(image, text, (x, y), font, scale, color, 2, cv2.LINE_AA)
