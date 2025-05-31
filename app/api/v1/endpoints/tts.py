from fastapi import APIRouter, HTTPException, Response, Depends, Request
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from app.services.text_to_speech import tts_service
from app.core.deps import get_current_active_user
from app.api.deps import get_db, get_current_customer
from app.models.models import Customer
from app.services.tts import TTSService
from app.schemas.tts import TTSRequest, TTSResponse
import io
import tempfile
from pathlib import Path
import logging
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice_id: str
    model_id: str = None
    output_format: str = None
    use_cache: bool = True

class TTSVoice(BaseModel):
    voice_id: str
    name: str
    category: str
    description: str
    preview_url: str = None

@router.post("/", response_model=TTSResponse)
async def generate_speech(
    request: TTSRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """Generate speech from text using TTS service."""
    tts_service = TTSService()
    return await tts_service.generate_speech(
        text=request.text,
        voice_id=request.voice_id,
        customer_id=current_customer.id
    )

@router.post("/generate")
async def generate_tts(
    request: TTSRequest,
    req: Request,
    current_tenant = Depends(get_current_customer)
):
    """
    Generate text-to-speech audio using ElevenLabs API.
    """
    try:
        client_ip = req.client.host
        audio_data = tts_service.generate_audio(
            text=request.text,
            voice_id=request.voice_id,
            model_id=request.model_id,
            output_format=request.output_format,
            use_cache=request.use_cache,
            client_ip=client_ip
        )
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=tts_audio.mp3"
            }
        )
    except Exception as e:
        logger.error(f"Error generating TTS audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preview")
async def preview_tts(
    request: TTSRequest,
    req: Request,
    current_tenant = Depends(get_current_customer)
):
    """
    Generate a preview of text-to-speech audio and return a temporary URL.
    """
    try:
        client_ip = req.client.host
        # Generate temporary audio file
        temp_path = tts_service.generate_temp_audio(
            text=request.text,
            voice_id=request.voice_id,
            use_cache=request.use_cache,
            client_ip=client_ip
        )
        
        # Return the temporary file
        return FileResponse(
            temp_path,
            media_type="audio/mpeg",
            filename="preview.mp3"
        )
    except Exception as e:
        logger.error(f"Error generating TTS preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices", response_model=list[TTSVoice])
async def get_voices(current_tenant = Depends(get_current_customer)):
    """
    Get list of available voices from ElevenLabs.
    """
    try:
        voices = tts_service.get_available_voices()
        return [
            TTSVoice(
                voice_id=voice["voice_id"],
                name=voice["name"],
                category=voice.get("category", "unknown"),
                description=voice.get("description", ""),
                preview_url=voice.get("preview_url")
            )
            for voice in voices
        ]
    except Exception as e:
        logger.error(f"Error fetching available voices: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices/{voice_id}")
async def get_voice_details(
    voice_id: str,
    current_tenant = Depends(get_current_customer)
):
    """
    Get detailed information about a specific voice.
    """
    try:
        voice_details = tts_service.get_voice_details(voice_id)
        return voice_details
    except Exception as e:
        logger.error(f"Error fetching voice details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def list_voices(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
    current_customer: Customer = Depends(get_current_customer)
):
    """List available TTS voices."""
    tts_service = TTSService()
    return await tts_service.list_voices() 