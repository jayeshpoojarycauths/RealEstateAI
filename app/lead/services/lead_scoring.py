from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Lead, LeadScore, InteractionLog, CallInteraction, MessageInteraction, RealEstateProject
from app.lead.schemas.interaction import LeadScoreCreate, InteractionLogCreate, CallInteractionCreate, MessageInteractionCreate
from uuid import UUID

class LeadScoringService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_lead_score(self, lead: Lead) -> float:
        """Calculate lead score based on various factors."""
        score = 0.0
        factors = {}

        # Factor 1: Contact Information Completeness (0-15 points)
        contact_score = 0
        if lead.email:
            contact_score += 3
            if '@' in lead.email and '.' in lead.email.split('@')[1]:
                contact_score += 2  # Valid email format
        if lead.phone:
            contact_score += 3
            if len(lead.phone) >= 10:
                contact_score += 2  # Valid phone format
        if lead.address:
            contact_score += 2
        if lead.city and lead.state:
            contact_score += 3
        score += contact_score
        factors["contact_completeness"] = contact_score

        # Factor 2: Interaction History (0-25 points)
        interaction_score = 0
        interactions = self.db.query(InteractionLog).filter(InteractionLog.lead_id == lead.id).all()
        if interactions:
            successful_interactions = sum(1 for i in interactions if i.status == "success")
            interaction_score = min(successful_interactions * 5, 25)
            
            # Bonus for recent interactions
            recent_interactions = sum(1 for i in interactions 
                                   if i.start_time > datetime.utcnow() - timedelta(days=7))
            interaction_score += min(recent_interactions * 2, 5)
        score += interaction_score
        factors["interaction_history"] = interaction_score

        # Factor 3: Response Time (0-15 points)
        response_score = 0
        message_interactions = self.db.query(MessageInteraction).join(
            InteractionLog
        ).filter(InteractionLog.lead_id == lead.id).all()
        if message_interactions:
            avg_response_time = sum(i.response_time or 0 for i in message_interactions) / len(message_interactions)
            if avg_response_time < 3600:  # Less than 1 hour
                response_score = 15
            elif avg_response_time < 86400:  # Less than 24 hours
                response_score = 12
            elif avg_response_time < 172800:  # Less than 48 hours
                response_score = 8
            else:
                response_score = 5
        score += response_score
        factors["response_time"] = response_score

        # Factor 4: Property Interest (0-20 points)
        interest_score = 0
        if lead.interested_properties:
            interest_score = min(len(lead.interested_properties) * 5, 20)
            
            # Bonus for specific property types
            property_types = set(p.type for p in lead.interested_properties)
            interest_score += min(len(property_types) * 2, 5)
        score += interest_score
        factors["property_interest"] = interest_score

        # Factor 5: Budget Alignment (0-10 points)
        budget_score = 0
        if lead.budget:
            try:
                budget = float(lead.budget.replace('₹', '').replace(',', ''))
                avg_property_price = self.db.query(func.avg(RealEstateProject.price)).scalar() or 0
                if avg_property_price > 0:
                    price_ratio = budget / avg_property_price
                    if 0.8 <= price_ratio <= 1.2:
                        budget_score = 10  # Budget within 20% of average
                    elif 0.6 <= price_ratio <= 1.4:
                        budget_score = 7   # Budget within 40% of average
                    else:
                        budget_score = 4   # Budget outside range
            except:
                pass
        score += budget_score
        factors["budget_alignment"] = budget_score

        # Factor 6: Location Match (0-15 points)
        location_score = 0
        if lead.location:
            # Check if lead's location matches any property locations
            matching_locations = self.db.query(RealEstateProject).filter(
                RealEstateProject.location.ilike(f"%{lead.location}%")
            ).count()
            location_score = min(matching_locations * 3, 15)
        score += location_score
        factors["location_match"] = location_score

        # Normalize score to 0-100 range
        score = min(score, 100)
        
        return score, factors

    def update_lead_score(self, lead_id: UUID) -> LeadScore:
        """Update lead score and store scoring factors."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise ValueError(f"Lead with ID {lead_id} not found")

        score, factors = self.calculate_lead_score(lead)
        
        # Update or create lead score
        lead_score = self.db.query(LeadScore).filter(LeadScore.lead_id == lead_id).first()
        if lead_score:
            lead_score.score = score
            lead_score.scoring_factors = factors
            lead_score.last_updated = datetime.utcnow()
        else:
            lead_score = LeadScore(
                lead_id=lead_id,
                score=score,
                scoring_factors=factors,
                last_updated=datetime.utcnow()
            )
            self.db.add(lead_score)

        self.db.commit()
        self.db.refresh(lead_score)
        return lead_score

    def log_interaction(
        self,
        lead_id: UUID,
        customer_id: UUID,
        interaction_type: str,
        status: str,
        user_input: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> InteractionLog:
        """Log a new interaction."""
        interaction = InteractionLog(
            lead_id=lead_id,
            customer_id=customer_id,
            interaction_type=interaction_type,
            status=status,
            start_time=datetime.utcnow(),
            user_input=user_input,
            error_message=error_message
        )
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def log_call_interaction(
        self,
        interaction_id: UUID,
        call_sid: str,
        recording_url: Optional[str] = None,
        transcript: Optional[str] = None,
        keypad_inputs: Optional[Dict[str, Any]] = None,
        menu_selections: Optional[Dict[str, Any]] = None,
        call_quality_metrics: Optional[Dict[str, Any]] = None
    ) -> CallInteraction:
        """Log call-specific interaction details."""
        call_interaction = CallInteraction(
            interaction_id=interaction_id,
            call_sid=call_sid,
            recording_url=recording_url,
            transcript=transcript,
            keypad_inputs=keypad_inputs,
            menu_selections=menu_selections,
            call_quality_metrics=call_quality_metrics
        )
        self.db.add(call_interaction)
        self.db.commit()
        self.db.refresh(call_interaction)
        return call_interaction

    def log_message_interaction(
        self,
        interaction_id: UUID,
        message_id: str,
        content: str,
        response_content: Optional[str] = None,
        response_time: Optional[int] = None,
        delivery_status: Optional[str] = None
    ) -> MessageInteraction:
        """Log message-specific interaction details."""
        message_interaction = MessageInteraction(
            interaction_id=interaction_id,
            message_id=message_id,
            content=content,
            response_content=response_content,
            response_time=response_time,
            delivery_status=delivery_status
        )
        self.db.add(message_interaction)
        self.db.commit()
        self.db.refresh(message_interaction)
        return message_interaction

    def get_lead_interaction_history(self, lead_id: UUID) -> List[Dict[str, Any]]:
        """Get complete interaction history for a lead."""
        interactions = self.db.query(InteractionLog).filter(
            InteractionLog.lead_id == lead_id
        ).order_by(InteractionLog.start_time.desc()).all()

        history = []
        for interaction in interactions:
            interaction_data = {
                "id": interaction.id,
                "type": interaction.interaction_type,
                "status": interaction.status,
                "start_time": interaction.start_time,
                "end_time": interaction.end_time,
                "duration": interaction.duration,
                "user_input": interaction.user_input,
                "error_message": interaction.error_message
            }

            # Add type-specific details
            if interaction.interaction_type == "call":
                call_details = self.db.query(CallInteraction).filter(
                    CallInteraction.interaction_id == interaction.id
                ).first()
                if call_details:
                    interaction_data["call_details"] = {
                        "recording_url": call_details.recording_url,
                        "transcript": call_details.transcript,
                        "keypad_inputs": call_details.keypad_inputs,
                        "menu_selections": call_details.menu_selections,
                        "call_quality_metrics": call_details.call_quality_metrics
                    }
            elif interaction.interaction_type in ["sms", "email", "whatsapp", "telegram"]:
                message_details = self.db.query(MessageInteraction).filter(
                    MessageInteraction.interaction_id == interaction.id
                ).first()
                if message_details:
                    interaction_data["message_details"] = {
                        "content": message_details.content,
                        "response_content": message_details.response_content,
                        "response_time": message_details.response_time,
                        "delivery_status": message_details.delivery_status
                    }

            history.append(interaction_data)

        return history 