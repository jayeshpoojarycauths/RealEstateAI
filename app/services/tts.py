from typing import Optional, Dict, Any, List
import requests
import os
from pathlib import Path
import tempfile
from app.shared.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        """Initialize TTS service with ElevenLabs API."""
        self.api_key = settings.ELEVENLABS_API_KEY
        self.model_id = settings.ELEVENLABS_MODEL_ID
        self.output_format = settings.ELEVENLABS_OUTPUT_FORMAT
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.cache_dir = Path(settings.ELEVENLABS_AUDIO_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        customer_id: Optional[str] = None,
        model_id: Optional[str] = None,
        output_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate speech from text using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            customer_id: Optional customer ID for caching
            model_id: Optional model ID override
            output_format: Optional output format override
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            # Prepare request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            data = {
                "text": text,
                "model_id": model_id or self.model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            # Make API request
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            
            # Get audio data
            audio_data = response.content
            
            # Cache if customer_id provided
            if customer_id:
                cache_path = self.cache_dir / f"{customer_id}_{voice_id}_{hash(text)}.mp3"
                cache_path.write_bytes(audio_data)
            
            return {
                "status": "success",
                "audio_data": audio_data,
                "format": output_format or self.output_format,
                "voice_id": voice_id,
                "model_id": model_id or self.model_id
            }
            
        except Exception as e:
            logger.error(f"Failed to generate speech: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def list_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            List of voice details
        """
        try:
            url = f"{self.base_url}/voices"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            voices = response.json()["voices"]
            return [
                {
                    "voice_id": voice["voice_id"],
                    "name": voice["name"],
                    "category": voice.get("category", "unknown"),
                    "description": voice.get("description", ""),
                    "preview_url": voice.get("preview_url")
                }
                for voice in voices
            ]
            
        except Exception as e:
            logger.error(f"Failed to list voices: {str(e)}")
            return []

    async def get_voice_details(self, voice_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific voice.
        
        Args:
            voice_id: ElevenLabs voice ID
            
        Returns:
            Dict containing voice details
        """
        try:
            url = f"{self.base_url}/voices/{voice_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            voice = response.json()
            return {
                "voice_id": voice["voice_id"],
                "name": voice["name"],
                "category": voice.get("category", "unknown"),
                "description": voice.get("description", ""),
                "preview_url": voice.get("preview_url"),
                "settings": voice.get("settings", {}),
                "labels": voice.get("labels", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get voice details: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 