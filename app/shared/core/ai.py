from typing import Dict, Any, Optional
import openai
from app.shared.core.config import settings

class AIService:
    """Service for AI-powered functionality."""
    
    def __init__(self):
        self.openai = openai
        self.openai.api_key = settings.OPENAI_API_KEY

    async def generate_outreach_message(
        self,
        lead_name: str,
        lead_source: str,
        channel: str,
        property_preferences: Optional[Dict[str, Any]] = None,
        budget_range: Optional[Dict[str, float]] = None,
        notes: Optional[str] = None
    ) -> str:
        """Generate personalized outreach message using GPT."""
        prompt = self._build_outreach_prompt(
            lead_name=lead_name,
            lead_source=lead_source,
            channel=channel,
            property_preferences=property_preferences,
            budget_range=budget_range,
            notes=notes
        )

        response = await self.openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate agent assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    def _build_outreach_prompt(
        self,
        lead_name: str,
        lead_source: str,
        channel: str,
        property_preferences: Optional[Dict[str, Any]] = None,
        budget_range: Optional[Dict[str, float]] = None,
        notes: Optional[str] = None
    ) -> str:
        """Build prompt for outreach message generation."""
        prompt = f"Generate a personalized {channel} message for {lead_name} "
        prompt += f"who came from {lead_source}."

        if property_preferences:
            prompt += f"\nProperty preferences: {property_preferences}"
        if budget_range:
            prompt += f"\nBudget range: {budget_range}"
        if notes:
            prompt += f"\nAdditional notes: {notes}"

        prompt += "\nMake the message professional, engaging, and focused on their specific interests."
        return prompt 