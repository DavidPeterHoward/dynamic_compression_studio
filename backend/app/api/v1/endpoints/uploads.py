"""
Media Upload & Compression API Endpoints
Handles file uploads and compression/decompression operations
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.services.media_processor import MediaProcessor
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models

class CompressRequest(BaseModel):
    """Compress media request"""
    media_url: str
    media_type: str = Field(..., pattern='^(image|video|audio)$')
    algorithm: str = Field('default')
    parameters: Optional[Dict[str, Any]] = None


class DecompressRequest(BaseModel):
    """Decompress media request"""
    compressed_url: str
    media_type: str = Field(..., pattern='^(image|video|audio)$')


# Endpoints

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    generate_thumbnail: bool = Form(True)
):
    """
    Upload image file

    Accepts image upload, performs validation, analysis, and optional thumbnail generation.
    Returns file metadata and quality metrics.
    """
    try:
        processor = MediaProcessor()
        result = await processor.process_image_upload(file, generate_thumbnail)
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
):
    """
    Upload video file

    Accepts video upload and performs validation.
    Returns file metadata.
    """
    try:
        processor = MediaProcessor()
        result = await processor.process_video_upload(file)
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
):
    """
    Upload audio file

    Accepts audio upload and performs validation.
    Returns file metadata.
    """
    try:
        processor = MediaProcessor()
        result = await processor.process_audio_upload(file)
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload audio: {str(e)}"
        )


@router.post("/compress")
async def compress_media(
    request: CompressRequest,
):
    """
    Compress uploaded media

    Applies compression algorithm to uploaded media and returns compression metrics
    including compression ratio, quality scores (PSNR, SSIM), and processing time.
    """
    try:
        processor = MediaProcessor()
        result = await processor.compress_media(
            media_url=request.media_url,
            media_type=request.media_type,
            algorithm=request.algorithm,
            parameters=request.parameters
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error compressing media: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compress media: {str(e)}"
        )


@router.post("/decompress")
async def decompress_media(
    request: DecompressRequest,
):
    """
    Decompress media

    Decompresses previously compressed media file.
    """
    try:
        processor = MediaProcessor()
        result = await processor.decompress_media(
            compressed_url=request.compressed_url,
            media_type=request.media_type
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error decompressing media: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decompress media: {str(e)}"
        )
