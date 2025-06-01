import aiohttp
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_captcha(token: str) -> bool:
    """
    Verify reCAPTCHA token with Google's API.
    """
    if not settings.RECAPTCHA_SECRET_KEY:
        if settings.ENVIRONMENT == "development":
            logger.warning("reCAPTCHA secret key not configured, skipping verification in development")
            return True
        else:
            logger.error("reCAPTCHA secret key not configured in production environment")
            return False

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.google.com/recaptcha/api/siteverify",
                timeout=aiohttp.ClientTimeout(total=10),
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token
                }
            ) as response:
                result = await response.json()

                if not result.get("success"):
                    logger.warning(f"reCAPTCHA verification failed: {result.get('error-codes', [])}")
                    return False

                # Check if score meets threshold (for v3)
                if "score" in result:
                    return result["score"] >= settings.RECAPTCHA_SCORE_THRESHOLD

                return True
    except Exception as e:
        logger.error(f"Error verifying reCAPTCHA: {str(e)}")
        return False 