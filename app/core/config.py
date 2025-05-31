from app.shared.core.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]

# Re-export settings for backward compatibility
settings = get_settings() 