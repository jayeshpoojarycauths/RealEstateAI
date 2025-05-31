from typing import Dict, Any, Optional, List
import openai
from app.shared.core.config import settings
from app.models.models import Lead, OutreachChannel
from app.lead.schemas.lead import LeadUpdate

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def enrich_lead(self, lead: Lead) -> Optional[LeadUpdate]:
        """
        Enrich lead data using GPT.
        """
        try:
            # Prepare prompt
            prompt = f"""
            Analyze this real estate lead and provide additional insights:
            Name: {lead.name}
            Email: {lead.email}
            Phone: {lead.phone}
            Source: {lead.source}
            Notes: {lead.notes}

            Please provide:
            1. Lead quality score (0-100)
            2. Recommended follow-up approach
            3. Additional contact information if available
            4. Property preferences if mentioned
            5. Budget range if mentioned
            """

            # Call GPT
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a real estate lead analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Parse response
            analysis = response.choices[0].message.content

            # Extract insights
            insights = self._parse_insights(analysis)

            # Create update
            return LeadUpdate(
                lead_score=insights.get('lead_score'),
                follow_up_notes=insights.get('follow_up_approach'),
                additional_info=insights.get('additional_info'),
                property_preferences=insights.get('property_preferences'),
                budget_range=insights.get('budget_range')
            )

        except Exception as e:
            print(f"Error enriching lead: {str(e)}")
            return None

    async def generate_outreach_message(
        self,
        lead_name: str,
        lead_source: str,
        channel: OutreachChannel,
        property_preferences: Optional[str] = None,
        budget_range: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Generate a personalized outreach message using GPT.
        """
        try:
            # Prepare context
            context = f"""
            Lead Information:
            - Name: {lead_name}
            - Source: {lead_source}
            - Property Preferences: {property_preferences or 'Not specified'}
            - Budget Range: {budget_range or 'Not specified'}
            - Additional Notes: {notes or 'None'}

            Channel: {channel.value}
            """

            # Prepare prompt based on channel
            if channel == OutreachChannel.EMAIL:
                prompt = f"""
                {context}

                Generate a professional real estate outreach email that:
                1. Is personalized to the lead's preferences and needs
                2. Has a compelling subject line
                3. Includes a clear value proposition
                4. Has a specific call to action
                5. Is concise (max 3-4 sentences)
                6. Maintains a professional yet friendly tone

                Format the response as:
                Subject: [subject line]
                Body: [email body]
                """
            else:  # SMS
                prompt = f"""
                {context}

                Generate a concise real estate outreach SMS that:
                1. Is personalized to the lead's preferences
                2. Fits within 160 characters
                3. Has a clear call to action
                4. Maintains a friendly, conversational tone
                5. Includes a way to opt out

                Format the response as just the message text.
                """

            # Call GPT
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a real estate communication expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating outreach message: {str(e)}")
            return ""

    def _parse_insights(self, analysis: str) -> dict:
        """
        Parse GPT response into structured insights.
        """
        insights = {}
        
        # Extract lead score
        if "Lead quality score:" in analysis:
            score_text = analysis.split("Lead quality score:")[1].split("\n")[0].strip()
            try:
                insights['lead_score'] = int(score_text)
            except ValueError:
                pass

        # Extract follow-up approach
        if "Recommended follow-up approach:" in analysis:
            insights['follow_up_approach'] = analysis.split("Recommended follow-up approach:")[1].split("\n")[0].strip()

        # Extract additional info
        if "Additional contact information:" in analysis:
            insights['additional_info'] = analysis.split("Additional contact information:")[1].split("\n")[0].strip()

        # Extract property preferences
        if "Property preferences:" in analysis:
            insights['property_preferences'] = analysis.split("Property preferences:")[1].split("\n")[0].strip()

        # Extract budget range
        if "Budget range:" in analysis:
            insights['budget_range'] = analysis.split("Budget range:")[1].split("\n")[0].strip()

        return insights 