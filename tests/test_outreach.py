import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.outreach.models.outreach import Outreach, OutreachTemplate, OutreachCampaign
from app.lead.models.lead import Lead
from app.outreach.schemas import (
    OutreachCreate, OutreachChannel, OutreachStatus,
    OutreachFilter
)
from app.outreach.services import OutreachService
from app.shared.core.pagination import PaginationParams
from fastapi import BackgroundTasks
from typing import List, Optional
from fastapi.testclient import TestClient
from app.main import app
from app.shared.core.exceptions import NotFoundException
from app.shared.models.customer import Customer

@pytest.fixture
def outreach_service(db_session: Session, test_customer: Customer):
    return OutreachService(db_session, test_customer)

@pytest.fixture
def test_lead(db_session: Session, test_customer):
    lead = Lead(
        name="Test Lead",
        email="test@example.com",
        phone="1234567890",
        source="website",
        status="active",
        customer_id=test_customer.id
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead

@pytest.fixture
def test_template(db_session: Session, test_customer):
    template = OutreachTemplate(
        name="Test Template",
        description="Test Description",
        channel=OutreachChannel.EMAIL,
        subject="Test Subject",
        body="Hello {{name}}, this is a test message.",
        variables=["name"],
        customer_id=test_customer.id
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template

class TestOutreachService:
    async def test_create_outreach(self, outreach_service: OutreachService, test_lead, test_customer):
        outreach_data = OutreachCreate(
            channel=OutreachChannel.EMAIL,
            message="Test message",
            subject="Test subject"
        )
        
        background_tasks = BackgroundTasks()
        result = await outreach_service.create_outreach(
            test_lead.id, outreach_data, test_customer.id, background_tasks
        )
        
        assert result is not None
        assert result.lead_id == test_lead.id
        assert result.channel == outreach_data.channel
        assert result.status == OutreachStatus.SCHEDULED

    async def test_list_outreach(self, outreach_service: OutreachService, test_lead, test_customer):
        # Create some outreach attempts
        for i in range(3):
            outreach_data = OutreachCreate(
                channel=OutreachChannel.EMAIL,
                message=f"Test message {i}",
                subject=f"Test subject {i}"
            )
            background_tasks = BackgroundTasks()
            await outreach_service.create_outreach(
                test_lead.id, outreach_data, test_customer.id, background_tasks
            )
        
        pagination = PaginationParams(page=1, limit=10)
        filters = OutreachFilter(channel=OutreachChannel.EMAIL)
        
        outreach_list = await outreach_service.list_outreach(
            test_customer.id, pagination, filters
        )
        
        assert len(outreach_list) == 3
        assert all(o.channel == OutreachChannel.EMAIL for o in outreach_list)

    async def test_get_lead_outreach(self, outreach_service: OutreachService, test_lead, test_customer):
        # Create outreach attempts
        for i in range(2):
            outreach_data = OutreachCreate(
                channel=OutreachChannel.EMAIL,
                message=f"Test message {i}",
                subject=f"Test subject {i}"
            )
            background_tasks = BackgroundTasks()
            await outreach_service.create_outreach(
                test_lead.id, outreach_data, test_customer.id, background_tasks
            )
        
        outreach_list = await outreach_service.get_lead_outreach(
            test_lead.id, test_customer.id
        )
        
        assert len(outreach_list) == 2
        assert all(o.lead_id == test_lead.id for o in outreach_list)

    async def test_get_outreach_stats(self, outreach_service: OutreachService, test_lead, test_customer):
        # Create outreach attempts with different statuses
        statuses = [
            OutreachStatus.SENT,
            OutreachStatus.DELIVERED,
            OutreachStatus.FAILED
        ]
        
        for status in statuses:
            outreach_data = OutreachCreate(
                channel=OutreachChannel.EMAIL,
                message="Test message",
                subject="Test subject"
            )
            background_tasks = BackgroundTasks()
            outreach = await outreach_service.create_outreach(
                test_lead.id, outreach_data, test_customer.id, background_tasks
            )
            outreach.status = status
            outreach_service.db.commit()
        
        stats = await outreach_service.get_outreach_stats(
            test_customer.id,
            start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        assert stats.total_outreach == 3
        assert stats.successful_outreach == 2
        assert stats.failed_outreach == 1

    async def test_get_outreach_analytics(self, outreach_service: OutreachService, test_lead, test_customer):
        # Create outreach attempts with different channels
        channels = [
            OutreachChannel.EMAIL,
            OutreachChannel.SMS,
            OutreachChannel.WHATSAPP
        ]
        
        for channel in channels:
            outreach_data = OutreachCreate(
                channel=channel,
                message="Test message",
                subject="Test subject" if channel == OutreachChannel.EMAIL else None
            )
            background_tasks = BackgroundTasks()
            await outreach_service.create_outreach(
                test_lead.id, outreach_data, test_customer.id, background_tasks
            )
        
        analytics = await outreach_service.get_outreach_analytics(
            test_customer.id,
            start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        assert len(analytics.channel_stats) == 3
        assert len(analytics.trends) > 0
        assert len(analytics.status_distribution) > 0

    async def test_schedule_outreach(self, outreach_service: OutreachService, test_lead, test_customer):
        outreach_data = OutreachCreate(
            channel=OutreachChannel.EMAIL,
            message="Test message",
            subject="Test subject"
        )
        
        schedule_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        result = await outreach_service.schedule_outreach(
            test_lead.id, outreach_data, schedule_time, test_customer.id
        )
        
        assert result is not None
        assert result.status == OutreachStatus.SCHEDULED
        assert result.scheduled_at is not None

    async def test_cancel_scheduled_outreach(self, outreach_service: OutreachService, test_lead, test_customer):
        # First schedule an outreach
        outreach_data = OutreachCreate(
            channel=OutreachChannel.EMAIL,
            message="Test message",
            subject="Test subject"
        )
        
        schedule_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        outreach = await outreach_service.schedule_outreach(
            test_lead.id, outreach_data, schedule_time, test_customer.id
        )
        
        # Then cancel it
        success = await outreach_service.cancel_scheduled_outreach(
            test_lead.id, outreach.id, test_customer.id
        )
        
        assert success is True
        
        # Verify cancellation
        cancelled_outreach = outreach_service.db.query(Outreach).filter(
            Outreach.id == outreach.id
        ).first()
        
        assert cancelled_outreach.status == OutreachStatus.CANCELLED 