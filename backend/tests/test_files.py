"""
Unit tests for file management endpoints.

This module tests the file management functionality including upload,
download, listing, metadata, and file operations.
"""

import pytest
import io
from fastapi.testclient import TestClient


class TestFileEndpoints:
    """Test cases for file management endpoints."""

    def test_upload_file_text(self, client: TestClient):
        """Test file upload with text content."""
        file_content = "This is a test file content for upload"
        files = {
            "file": ("test_file.txt", io.StringIO(file_content), "text/plain")
        }
        data = {
            "description": "Test file for compression",
            "tags": "test,compression"
        }
        
        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 200
        
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "size" in data
        assert "content_type" in data
        assert data["filename"] == "test_file.txt"
        assert data["size"] == len(file_content)

    def test_upload_file_binary(self, client: TestClient):
        """Test file upload with binary content."""
        file_content = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09" * 100
        files = {
            "file": ("test_binary.bin", io.BytesIO(file_content), "application/octet-stream")
        }
        data = {
            "description": "Test binary file"
        }
        
        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 200
        
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test_binary.bin"
        assert data["size"] == len(file_content)

    def test_upload_file_large(self, client: TestClient):
        """Test file upload with large content."""
        large_content = "A" * 100000  # 100KB
        files = {
            "file": ("large_file.txt", io.StringIO(large_content), "text/plain")
        }
        
        response = client.post("/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert data["size"] == 100000

    def test_upload_file_with_metadata(self, client: TestClient):
        """Test file upload with detailed metadata."""
        file_content = "Test file with metadata"
        files = {
            "file": ("metadata_test.txt", io.StringIO(file_content), "text/plain")
        }
        data = {
            "description": "Test file with comprehensive metadata",
            "tags": "test,metadata,compression",
            "category": "test",
            "priority": "high"
        }
        
        response = client.post("/upload", files=files, data=data)
        assert response.status_code == 200
        
        data = response.json()
        assert "metadata" in data
        assert data["metadata"]["description"] == "Test file with comprehensive metadata"
        assert "test" in data["metadata"]["tags"]

    def test_list_files(self, client: TestClient):
        """Test file listing endpoint."""
        response = client.get("/list")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["files"], list)

    def test_list_files_with_pagination(self, client: TestClient):
        """Test file listing with pagination."""
        response = client.get("/list?page=1&page_size=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_files_with_filters(self, client: TestClient):
        """Test file listing with filters."""
        response = client.get("/list?content_type=text&size_min=100&size_max=10000")
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data

    def test_get_file_info(self, client: TestClient):
        """Test getting file information."""
        # First upload a file
        file_content = "Test file for info retrieval"
        files = {
            "file": ("info_test.txt", io.StringIO(file_content), "text/plain")
        }
        
        upload_response = client.post("/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # Get file info
        response = client.get(f"/{file_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "size" in data
        assert "content_type" in data
        assert "uploaded_at" in data

    def test_get_file_metadata(self, client: TestClient):
        """Test getting file metadata."""
        # First upload a file
        file_content = "Test file for metadata"
        files = {
            "file": ("metadata_test.txt", io.StringIO(file_content), "text/plain")
        }
        upload_data = {
            "description": "Test file for metadata retrieval",
            "tags": "test,metadata"
        }
        
        upload_response = client.post("/upload", files=files, data=upload_data)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # Get file metadata
        response = client.get(f"/{file_id}/metadata")
        assert response.status_code == 200
        
        data = response.json()
        assert "file_id" in data
        assert "metadata" in data
        assert "analysis" in data
        assert data["metadata"]["description"] == "Test file for metadata retrieval"

    def test_download_file(self, client: TestClient):
        """Test file download."""
        # First upload a file
        file_content = "Test file for download"
        files = {
            "file": ("download_test.txt", io.StringIO(file_content), "text/plain")
        }
        
        upload_response = client.post("/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # Download file
        response = client.get(f"/{file_id}/download")
        assert response.status_code == 200
        assert response.content.decode() == file_content

    def test_download_file_binary(self, client: TestClient):
        """Test binary file download."""
        # First upload a binary file
        file_content = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09" * 50
        files = {
            "file": ("binary_test.bin", io.BytesIO(file_content), "application/octet-stream")
        }
        
        upload_response = client.post("/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # Download file
        response = client.get(f"/{file_id}/download")
        assert response.status_code == 200
        assert response.content == file_content

    def test_delete_file(self, client: TestClient):
        """Test file deletion."""
        # First upload a file
        file_content = "Test file for deletion"
        files = {
            "file": ("delete_test.txt", io.StringIO(file_content), "text/plain")
        }
        
        upload_response = client.post("/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # Delete file
        response = client.delete(f"/{file_id}")
        assert response.status_code == 200
        
        # Verify file is deleted
        get_response = client.get(f"/{file_id}")
        assert get_response.status_code == 404

    def test_update_file(self, client: TestClient):
        """Test file update."""
        # First upload a file
        file_content = "Test file for update"
        files = {
            "file": ("update_test.txt", io.StringIO(file_content), "text/plain")
        }
        
        upload_response = client.post("/upload", files=files)
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # Update file metadata
        update_data = {
            "description": "Updated description",
            "tags": "updated,test"
        }
        
        response = client.put(f"/{file_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metadata"]["description"] == "Updated description"

    def test_search_files(self, client: TestClient):
        """Test file search functionality."""
        # First upload some files
        files_to_upload = [
            ("search_test1.txt", "First search test file"),
            ("search_test2.txt", "Second search test file"),
            ("other_file.txt", "File not matching search")
        ]
        
        for filename, content in files_to_upload:
            files = {
                "file": (filename, io.StringIO(content), "text/plain")
            }
            client.post("/upload", files=files)
        
        # Search for files
        search_data = {
            "query": "search_test",
            "content_type": "text",
            "size_min": 0,
            "size_max": 1000
        }
        
        response = client.post("/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        assert "total" in data
        assert data["total"] >= 2  # Should find at least 2 files

    def test_search_files_advanced(self, client: TestClient):
        """Test advanced file search with multiple criteria."""
        # First upload files with different characteristics
        files_to_upload = [
            ("large_file.txt", "A" * 1000, "text/plain"),
            ("small_file.txt", "Small content", "text/plain"),
            ("code_file.py", "def test(): pass", "text/x-python")
        ]
        
        for filename, content, content_type in files_to_upload:
            files = {
                "file": (filename, io.StringIO(content), content_type)
            }
            client.post("/upload", files=files)
        
        # Advanced search
        search_data = {
            "query": "file",
            "content_type": "text/plain",
            "size_min": 100,
            "size_max": 2000,
            "date_from": "2024-01-01T00:00:00Z",
            "date_to": "2024-12-31T23:59:59Z"
        }
        
        response = client.post("/search", json=search_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data

    def test_upload_invalid_file(self, client: TestClient):
        """Test upload with invalid file data."""
        # No file provided
        response = client.post("/upload")
        assert response.status_code == 422
        
        # Invalid file type
        files = {
            "file": ("test.exe", io.StringIO("test"), "application/x-executable")
        }
        response = client.post("/upload", files=files)
        assert response.status_code in [400, 422]  # Should reject executable files

    def test_file_not_found(self, client: TestClient):
        """Test operations on non-existent file."""
        non_existent_id = "99999999-9999-9999-9999-999999999999"
        
        # Get file info
        response = client.get(f"/{non_existent_id}")
        assert response.status_code == 404
        
        # Download file
        response = client.get(f"/{non_existent_id}/download")
        assert response.status_code == 404
        
        # Delete file
        response = client.delete(f"/{non_existent_id}")
        assert response.status_code == 404

    def test_upload_multiple_files(self, client: TestClient):
        """Test uploading multiple files in sequence."""
        files_content = [
            ("file1.txt", "Content of file 1"),
            ("file2.txt", "Content of file 2"),
            ("file3.txt", "Content of file 3")
        ]
        
        uploaded_files = []
        for filename, content in files_content:
            files = {
                "file": (filename, io.StringIO(content), "text/plain")
            }
            
            response = client.post("/upload", files=files)
            assert response.status_code == 200
            
            data = response.json()
            uploaded_files.append(data["file_id"])
        
        # Verify all files are listed
        response = client.get("/list")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 3

    def test_file_size_limits(self, client: TestClient):
        """Test file size limits."""
        # Test with very large file (should be rejected or handled appropriately)
        large_content = "A" * 10000000  # 10MB
        
        files = {
            "file": ("large_file.txt", io.StringIO(large_content), "text/plain")
        }
        
        response = client.post("/upload", files=files)
        # Should either succeed or return appropriate error
        assert response.status_code in [200, 413, 422]

    def test_file_content_analysis(self, client: TestClient):
        """Test file content analysis during upload."""
        # Upload a file with specific content for analysis
        code_content = """
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        print(fibonacci(10))
        """
        
        files = {
            "file": ("test_code.py", io.StringIO(code_content), "text/x-python")
        }
        
        response = client.post("/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis" in data
        assert "content_type" in data["analysis"]
        assert "entropy" in data["analysis"]
        assert "complexity" in data["analysis"]
