from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class VoiceSettings(BaseModel):
    """Schema for voice settings."""
    stability: float = Field(default=0.5, ge=0.0, le=1.0)
    similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0)

class TTSRequest(BaseModel):
    """Schema for TTS request."""
    text: str
    voice_id: str
    model_id: Optional[str] = None
    output_format: Optional[str] = None
    voice_settings: Optional[VoiceSettings] = None

class TTSResponse(BaseModel):
    """Schema for TTS response."""
    status: str
    audio_data: Optional[bytes] = None
    format: str
    voice_id: str
    model_id: str
    error: Optional[str] = None

class VoiceDetails(BaseModel):
    """Schema for voice details."""
    voice_id: str
    name: str
    category: str
    description: Optional[str] = None
    preview_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    labels: Optional[Dict[str, Any]] = None 