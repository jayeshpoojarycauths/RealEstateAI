import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import os
from app.services.text_to_speech import TextToSpeechService
from fastapi import HTTPException

@pytest.fixture
def mock_requests():
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        yield {
            'post': mock_post,
            'get': mock_get
        }

@pytest.fixture
def tts_service():
    with patch('app.shared.core.config.settings') as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test_key"
        mock_settings.ELEVENLABS_MODEL_ID = "test_model"
        mock_settings.ELEVENLABS_OUTPUT_FORMAT = "test_format"
        mock_settings.ELEVENLABS_AUDIO_CACHE_DIR = tempfile.mkdtemp()
        service = TextToSpeechService()
        yield service
        # Cleanup
        import shutil
        shutil.rmtree(mock_settings.ELEVENLABS_AUDIO_CACHE_DIR)

def test_generate_audio_success(tts_service, mock_requests):
    # Mock successful API response
    mock_response = Mock()
    mock_response.content = b"test_audio_data"
    mock_response.raise_for_status = Mock()
    mock_requests['post'].return_value = mock_response
    
    # Test audio generation
    result = tts_service.generate_audio(
        text="Hello, world!",
        voice_id="test_voice",
        client_ip="127.0.0.1"
    )
    
    assert result == b"test_audio_data"
    mock_requests['post'].assert_called_once()
    
    # Verify cache file was created
    cache_dir = Path(tts_service.cache_dir)
    cache_files = list(cache_dir.glob("*.mp3"))
    assert len(cache_files) == 1

def test_generate_audio_cache_hit(tts_service, mock_requests):
    # First call to generate and cache
    mock_response = Mock()
    mock_response.content = b"test_audio_data"
    mock_response.raise_for_status = Mock()
    mock_requests['post'].return_value = mock_response
    
    tts_service.generate_audio(
        text="Hello, world!",
        voice_id="test_voice",
        client_ip="127.0.0.1"
    )
    
    # Reset mock to verify it's not called again
    mock_requests['post'].reset_mock()
    
    # Second call should use cache
    result = tts_service.generate_audio(
        text="Hello, world!",
        voice_id="test_voice",
        client_ip="127.0.0.1"
    )
    
    assert result == b"test_audio_data"
    mock_requests['post'].assert_not_called()

def test_generate_audio_rate_limit(tts_service):
    # Test rate limiting
    client_ip = "127.0.0.1"
    
    # Make max_requests + 1 calls
    for _ in range(tts_service.RATE_LIMIT + 1):
        try:
            tts_service.generate_audio(
                text="Hello, world!",
                voice_id="test_voice",
                client_ip=client_ip
            )
        except HTTPException as e:
            if e.status_code == 429:
                break
    else:
        pytest.fail("Rate limit not enforced")

def test_generate_audio_api_error(tts_service, mock_requests):
    # Mock API error
    mock_requests['post'].side_effect = Exception("API Error")
    
    with pytest.raises(Exception) as exc_info:
        tts_service.generate_audio(
            text="Hello, world!",
            voice_id="test_voice",
            client_ip="127.0.0.1"
        )
    
    assert "API Error" in str(exc_info.value)

def test_get_available_voices(tts_service, mock_requests):
    # Mock voices API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "voices": [
            {
                "voice_id": "voice1",
                "name": "Test Voice 1",
                "category": "test",
                "description": "Test voice"
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_requests['get'].return_value = mock_response
    
    voices = tts_service.get_available_voices()
    
    assert len(voices) == 1
    assert voices[0]["voice_id"] == "voice1"
    assert voices[0]["name"] == "Test Voice 1"

def test_get_voice_details(tts_service, mock_requests):
    # Mock voice details API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "voice_id": "voice1",
        "name": "Test Voice 1",
        "category": "test",
        "description": "Test voice"
    }
    mock_response.raise_for_status = Mock()
    mock_requests['get'].return_value = mock_response
    
    voice_details = tts_service.get_voice_details("voice1")
    
    assert voice_details["voice_id"] == "voice1"
    assert voice_details["name"] == "Test Voice 1"

def test_generate_temp_audio(tts_service, mock_requests):
    # Mock successful API response
    mock_response = Mock()
    mock_response.content = b"test_audio_data"
    mock_response.raise_for_status = Mock()
    mock_requests['post'].return_value = mock_response
    
    # Test temp audio generation
    temp_path = tts_service.generate_temp_audio(
        text="Hello, world!",
        voice_id="test_voice",
        client_ip="127.0.0.1"
    )
    
    assert os.path.exists(temp_path)
    assert Path(temp_path).suffix == ".mp3"
    
    # Clean up
    os.remove(temp_path) 