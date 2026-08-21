from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".mpeg", ".webm"}
ALLOWED_CONTENT_TYPES = {
    ".mp3": {"audio/mpeg", "audio/mp3", "audio/mpeg3"},
    ".wav": {"audio/wav", "audio/x-wav", "audio/wave"},
    ".m4a": {"audio/mp4", "audio/x-m4a"},
    ".mp4": {"audio/mp4", "video/mp4"},
    ".mov": {"video/quicktime"},
    ".mpeg": {"video/mpeg", "audio/mpeg"},
    ".webm": {"audio/webm", "video/webm"},
}


@dataclass(frozen=True)
class StoredMedia:
    filename: str
    path: Path
    content_type: str
    size: int


class LocalMediaStorage:
    """Filesystem implementation behind a replaceable media-storage boundary."""

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, filename: str) -> Path | None:
        root = self.root.resolve()
        candidate = (root / Path(filename).name).resolve()
        if candidate.parent != root:
            return None
        return candidate

    async def save_upload(self, upload: UploadFile, max_bytes: int) -> StoredMedia:
        original_name = upload.filename or "audio"
        extension = Path(original_name).suffix.lower()
        content_type = (upload.content_type or "").lower().split(";", 1)[0].strip()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file extension")
        if content_type not in ALLOWED_CONTENT_TYPES[extension]:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported media content type")

        filename = f"{uuid4()}{extension}"
        path = self._safe_path(filename)
        if path is None:
            raise HTTPException(status_code=400, detail="Invalid media filename")

        total = 0
        header = bytearray()
        try:
            with path.open("wb") as destination:
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds the configured size limit")
                    if len(header) < 64:
                        header.extend(chunk[: 64 - len(header)])
                    destination.write(chunk)
        except Exception:
            path.unlink(missing_ok=True)
            raise

        if not has_expected_signature(extension, bytes(header)):
            path.unlink(missing_ok=True)
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="File content does not match its media type")

        return StoredMedia(filename=filename, path=path, content_type=content_type, size=total)

    def resolve(self, filename: str) -> Path | None:
        if not filename or Path(filename).name != filename:
            return None
        path = self._safe_path(filename)
        if path is None or not path.is_file():
            return None
        return path

    def delete(self, filename: str) -> None:
        path = self._safe_path(filename) if filename else None
        if path is not None:
            path.unlink(missing_ok=True)


def has_expected_signature(extension: str, header: bytes) -> bool:
    if extension == ".mp3":
        return header.startswith(b"ID3") or (len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0)
    if extension == ".wav":
        return len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WAVE"
    if extension in {".m4a", ".mp4", ".mov"}:
        return len(header) >= 12 and header[4:8] == b"ftyp"
    if extension == ".mpeg":
        return header.startswith(b"\x00\x00\x01\xba") or (len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0)
    if extension == ".webm":
        return header.startswith(b"\x1a\x45\xdf\xa3")
    return False


def media_content_type(path: Path, stored_content_type: str | None = None) -> str:
    return stored_content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
