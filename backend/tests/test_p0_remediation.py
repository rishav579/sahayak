from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException, UploadFile
import httpx
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_413_REQUEST_ENTITY_TOO_LARGE, HTTP_415_UNSUPPORTED_MEDIA_TYPE

from app.api.health import readiness_check
from app.api.routes import get_media, upload_meeting
from app.db import mongo
from app.services.media_storage import LocalMediaStorage


class MediaStorageTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = LocalMediaStorage(self.temp_dir.name)

    async def asyncTearDown(self):
        self.temp_dir.cleanup()

    def make_upload(self, name: str, content_type: str, payload: bytes) -> UploadFile:
        return UploadFile(
            filename=name,
            file=io.BytesIO(payload),
            headers=Headers({"content-type": content_type}),
        )

    async def test_oversized_upload_is_rejected_without_excessive_buffering(self):
        upload = self.make_upload("meeting.mp3", "audio/mpeg", b"ID3" + b"x" * 11)
        with self.assertRaises(HTTPException) as raised:
            await self.storage.save_upload(upload, max_bytes=10)
        self.assertEqual(raised.exception.status_code, HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertEqual(list(Path(self.temp_dir.name).iterdir()), [])

    async def test_invalid_media_type_and_signature_are_rejected(self):
        wrong_type = self.make_upload("meeting.mp3", "text/plain", b"ID3" + b"x")
        with self.assertRaises(HTTPException) as raised_type:
            await self.storage.save_upload(wrong_type, max_bytes=100)
        self.assertEqual(raised_type.exception.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        wrong_signature = self.make_upload("meeting.mp3", "audio/mpeg", b"not an mp3")
        with self.assertRaises(HTTPException) as raised_signature:
            await self.storage.save_upload(wrong_signature, max_bytes=100)
        self.assertEqual(raised_signature.exception.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(list(Path(self.temp_dir.name).iterdir()), [])

    def test_path_traversal_identifier_is_rejected(self):
        self.assertIsNone(self.storage.resolve("../secret.mp3"))
        self.assertIsNone(self.storage.resolve("nested/secret.mp3"))


class MediaRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_unauthenticated_recording_access_is_rejected(self):
        from app.main import app

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/media/recording.mp3")
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    async def test_owner_can_access_and_cross_user_cannot(self):
        temp_dir = tempfile.TemporaryDirectory()
        storage = LocalMediaStorage(temp_dir.name)
        stored_path = Path(temp_dir.name) / "recording.mp3"
        stored_path.write_bytes(b"ID3owner")

        with patch("app.api.routes.storage", storage), patch(
            "app.api.routes.get_meeting_for_media",
            new=AsyncMock(side_effect=lambda filename, user_id: {"media_content_type": "audio/mpeg"} if user_id == "owner" else None),
        ):
            owner_response = await get_media("recording.mp3", {"sub": "owner"})
            self.assertEqual(Path(owner_response.path), stored_path)
            with self.assertRaises(HTTPException) as denied:
                await get_media("recording.mp3", {"sub": "other"})
            self.assertEqual(denied.exception.status_code, HTTP_404_NOT_FOUND)
        temp_dir.cleanup()

    async def test_processing_failure_cleans_up_uploaded_file(self):
        temp_dir = tempfile.TemporaryDirectory()
        storage = LocalMediaStorage(temp_dir.name)
        upload = UploadFile(
            filename="meeting.mp3",
            file=io.BytesIO(b"ID3valid"),
            headers=Headers({"content-type": "audio/mpeg"}),
        )
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/upload",
            "headers": [(b"host", b"localhost")],
            "scheme": "http",
            "server": ("localhost", 8000),
            "client": ("127.0.0.1", 1234),
            "query_string": b"",
            "root_path": "",
        }
        request = Request(scope)
        with patch("app.api.routes.storage", storage), patch(
            "app.api.routes.create_meeting_from_upload", new=AsyncMock(side_effect=RuntimeError("processing failed"))
        ):
            with self.assertRaises(HTTPException) as raised:
                await upload_meeting(request, upload, "Meeting", {"sub": "owner"})
        self.assertEqual(raised.exception.status_code, 500)
        self.assertEqual(list(Path(temp_dir.name).iterdir()), [])
        temp_dir.cleanup()


class ReadinessTests(unittest.IsolatedAsyncioTestCase):
    async def test_mongodb_unavailable_is_not_ready(self):
        old_client, old_ready = mongo.client, mongo.mongo_ready
        mongo.client = None
        mongo.mongo_ready = False
        try:
            with self.assertRaises(HTTPException) as raised:
                await readiness_check()
            self.assertEqual(raised.exception.status_code, 503)
        finally:
            mongo.client, mongo.mongo_ready = old_client, old_ready


if __name__ == "__main__":
    unittest.main()
