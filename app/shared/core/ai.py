import logging
from typing import Dict, Any, Optional
from openai import OpenAI, OpenAIError
from app.shared.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered functionality."""
    
    def __init__(self):
        """Initialize the AI service with OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"

    async def generate_outreach_message(
        self,
        lead_name: str,
        lead_source: str,
        channel: str,
        property_preferences: Optional[Dict[str, Any]] = None,
        budget_range: Optional[Dict[str, float]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a personalized outreach message using AI.
        
        Args:
            lead_name: Name of the lead (required)
            lead_source: Source of the lead (required)
            channel: Communication channel (required)
            property_preferences: Optional property preferences
            budget_range: Optional budget range
            additional_context: Optional additional context
            
        Returns:
            str: Generated outreach message
            
        Raises:
            ValueError: If required parameters are missing or invalid
            OpenAIError: For OpenAI API specific errors
            Exception: For other errors
        """
        # Validate required parameters
        if not lead_name or not isinstance(lead_name, str):
            raise ValueError("lead_name is required and must be a string")
        if not lead_source or not isinstance(lead_source, str):
            raise ValueError("lead_source is required and must be a string")
        if not channel or not isinstance(channel, str):
            raise ValueError("channel is required and must be a string")

        # Validate optional parameters
        if property_preferences is not None and not isinstance(property_preferences, dict):
            raise ValueError("property_preferences must be a dictionary")
        if budget_range is not None:
            if not isinstance(budget_range, dict):
                raise ValueError("budget_range must be a dictionary")
            if not all(isinstance(v, (int, float)) for v in budget_range.values()):
                raise ValueError("budget_range values must be numbers")

        try:
            # Build the prompt
            prompt = self._build_outreach_prompt(
                lead_name=lead_name,
                lead_source=lead_source,
                channel=channel,
                property_preferences=property_preferences,
                budget_range=budget_range,
                additional_context=additional_context
            )

            # Generate message using OpenAI API with latest best practices
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a real estate outreach specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                presence_penalty=0.6,  # Encourage diversity in responses
                frequency_penalty=0.3,  # Reduce repetition
                response_format={"type": "text"},  # Ensure text response
                stream=False  # Set to True for streaming responses
            )

            # Extract and return the generated message
            return response.choices[0].message.content.strip()

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIError(f"Failed to generate outreach message: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Failed to generate outreach message: {str(e)}")

    def _build_outreach_prompt(
        self,
        lead_name: str,
        lead_source: str,
        channel: str,
        property_preferences: Optional[Dict[str, Any]] = None,
        budget_range: Optional[Dict[str, float]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for message generation."""
        prompt = f"Generate a personalized outreach message for {lead_name} "
        prompt += f"who came from {lead_source} through {channel} channel. "
        
        if property_preferences:
            prompt += f"They are interested in: {property_preferences}. "
            
        if budget_range:
            prompt += f"Their budget range is: {budget_range}. "
            
        if additional_context:
            prompt += f"Additional context: {additional_context}. "
            
        prompt += "Make the message professional, personalized, and engaging."
        
        return prompt 