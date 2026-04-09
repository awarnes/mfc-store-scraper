"""Module for managing image media lifecycle for shopify"""

import shutil
import os
import requests

from src.shopify.shopify import Shopify
from src.shopify.mutations import Mutations


class MediaDownloadFailedError(Exception):
    """Error thrown when a media download fails"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class StagedUploadFailedError(Exception):
    """Error thrown when a staged upload fails"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class MediaManager:
    """Manages uploading media to Shopify"""

    def download(self, file_name: str, url: str, path: str) -> str:
        """Download file at `url` to `dir` return file path"""
        resp = requests.get(url, stream=True, timeout=5)
        if resp.status_code == 200:
            file_path = os.path.join(path, f"{file_name}.png")

            with open(file_path, "wb") as file:
                resp.raw.decode_content = True
                shutil.copyfileobj(resp.raw, file)

            return file_path

        raise MediaDownloadFailedError()

    def upload_image_to_staged_target(self, staged_target: dict, image_path: str):
        """
        From Shopify bot to help upload a file to the staged target

        staged_target: one element from stagedUploadsCreate.stagedTargets
        {
            "url": "...",
            "resourceUrl": "...",
            "parameters": [
            {"name": "key", "value": "..."},
            {"name": "Content-Type", "value": "image/jpeg"},
            ...
            ]
        }
        image_path: local path to the image file, e.g. "./my-image.jpg"
        """
        url = staged_target["url"]
        params = staged_target["parameters"]

        # Build form fields from parameters
        data = {}
        for p in params:
            # All parameters must be sent as regular form fields
            data[p["name"]] = p["value"]

        # Open the image file as binary
        with open(image_path, "rb") as f:
            # `files` tells requests to send multipart/form-data
            # The field name is almost always "file" for these staged uploads
            files = {
                "file": (
                    image_path,
                    f,
                    data.get("Content-Type", "application/octet-stream"),
                )
            }

            response = requests.post(url, data=data, files=files, timeout=5)

        # Staged upload services usually return 201 or 204 on success
        if response.status_code not in (200, 201, 204):
            raise StagedUploadFailedError(
                f"Staged upload failed: {response.status_code} {response.text}"
            )

        return response

    def generate_staged_upload(self, file_name: str):
        """Generate handle for uploading files"""

        staged_upload_input = [
            {
                "filename": file_name,
                "mimeType": "image/png",
                "resource": "IMAGE",
                "httpMethod": "POST",
            }
        ]

        s = Shopify()
        return s.query_file(
            Mutations.generate_staged_uploads,
            {"input": staged_upload_input},
        )

    def create_file(self, original_source: str):
        """Create a file from staged upload"""

        s = Shopify()
        return s.query_file(
            Mutations.file_create,
            {"files": [{"originalSource": original_source}]},
        )
