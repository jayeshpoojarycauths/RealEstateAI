import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from app.shared.db.session import SessionLocal
from app.lead.models.lead import Lead, LeadScore
from app.project.models.project import RealEstateProject
from app.outreach.models.outreach import OutreachLog
from app.shared.models.interaction import InteractionLog, CallInteraction, MessageInteraction
from datetime import datetime, timedelta
import numpy as np
from app.lead.services.lead_scoring import LeadScoringService

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def format_currency(value):
    """Format number as currency."""
    return f"₹{value:,.2f}"

def calculate_metrics(outreach_logs):
    """Calculate outreach metrics."""
    total = len(outreach_logs)
    if total == 0:
        return 0, 0, 0
        
    success_rate = len(outreach_logs[outreach_logs['success']]) / total * 100
    response_rate = len(outreach_logs[outreach_logs['response_received']]) / total * 100
    conversion_rate = len(outreach_logs[outreach_logs['converted']]) / total * 100
    
    return success_rate, response_rate, conversion_rate

def main():
    st.set_page_config(page_title="Real Estate CRM Dashboard", layout="wide")
    
    st.title("Real Estate CRM Dashboard")
    
    # Initialize database session
    db = get_db()

    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    # Location filter
    locations = [loc[0] for loc in db.query(Lead.city).distinct().all() if loc[0]]
    selected_locations = st.sidebar.multiselect("Locations", locations)
    
    # Property type filter
    property_types = ["Residential", "Commercial", "Land", "Industrial"]
    selected_property_types = st.sidebar.multiselect("Property Types", property_types)

    # Lead Scoring Section
    st.header("Lead Scoring Analysis")
    
    # Get lead scores
    lead_scores = db.query(LeadScore).all()
    if lead_scores:
        scores_df = pd.DataFrame([
            {
                "lead_id": score.lead_id,
                "score": score.score,
                "last_updated": score.last_updated,
                **score.scoring_factors
            }
            for score in lead_scores
        ])
        
        # Score distribution
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                scores_df,
                x="score",
                nbins=20,
                title="Lead Score Distribution",
                labels={"score": "Score", "count": "Number of Leads"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Scoring factors correlation
        with col2:
            factors = ["contact_completeness", "interaction_history", "response_time", "property_interest"]
            corr_matrix = scores_df[factors].corr()
            fig = px.imshow(
                corr_matrix,
                title="Scoring Factors Correlation",
                labels=dict(x="Factor", y="Factor", color="Correlation")
            )
            st.plotly_chart(fig, use_container_width=True)

    # Interaction Analysis Section
    st.header("Interaction Analysis")
    
    # Get interactions
    interactions = db.query(InteractionLog).all()
    if interactions:
        interactions_df = pd.DataFrame([
            {
                "id": i.id,
                "lead_id": i.lead_id,
                "type": i.interaction_type,
                "status": i.status,
                "start_time": i.start_time,
                "duration": i.duration
            }
            for i in interactions
        ])
        
        # Interaction types distribution
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                interactions_df,
                names="type",
                title="Interaction Types Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Interaction status over time
        with col2:
            interactions_df["date"] = pd.to_datetime(interactions_df["start_time"]).dt.date
            status_over_time = interactions_df.groupby(["date", "status"]).size().reset_index(name="count")
            fig = px.line(
                status_over_time,
                x="date",
                y="count",
                color="status",
                title="Interaction Status Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Call Analysis
        st.subheader("Call Analysis")
        call_interactions = db.query(CallInteraction).all()
        if call_interactions:
            calls_df = pd.DataFrame([
                {
                    "id": c.id,
                    "duration": c.interaction.duration,
                    "has_recording": bool(c.recording_url),
                    "has_transcript": bool(c.transcript),
                    "menu_selections": len(c.menu_selections) if c.menu_selections else 0
                }
                for c in call_interactions
            ])
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(
                    calls_df,
                    x="duration",
                    nbins=20,
                    title="Call Duration Distribution",
                    labels={"duration": "Duration (seconds)", "count": "Number of Calls"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(
                    calls_df,
                    x="duration",
                    y="menu_selections",
                    title="Call Duration vs Menu Selections",
                    labels={"duration": "Duration (seconds)", "menu_selections": "Number of Menu Selections"}
                )
                st.plotly_chart(fig, use_container_width=True)

        # Message Analysis
        st.subheader("Message Analysis")
        message_interactions = db.query(MessageInteraction).all()
        if message_interactions:
            messages_df = pd.DataFrame([
                {
                    "id": m.id,
                    "type": m.interaction.interaction_type,
                    "response_time": m.response_time,
                    "delivery_status": m.delivery_status
                }
                for m in message_interactions
            ])
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.box(
                    messages_df,
                    x="type",
                    y="response_time",
                    title="Response Time by Message Type",
                    labels={"type": "Message Type", "response_time": "Response Time (seconds)"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(
                    messages_df,
                    names="delivery_status",
                    title="Message Delivery Status"
                )
                st.plotly_chart(fig, use_container_width=True)

    # Top Leads Section
    st.header("Top Leads")
    if lead_scores:
        top_leads = scores_df.nlargest(5, "score")
        for _, lead in top_leads.iterrows():
            lead_data = db.query(Lead).filter(Lead.id == lead["lead_id"]).first()
            if lead_data:
                st.write(f"""
                ### {lead_data.name}
                - Score: {lead['score']:.1f}
                - Contact: {lead_data.email or 'N/A'} | {lead_data.phone or 'N/A'}
                - Location: {lead_data.city or 'N/A'}, {lead_data.state or 'N/A'}
                - Last Updated: {lead['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}
                """)

    # Leads Overview
    st.header("Leads Overview")
    leads = pd.read_sql(
        db.query(Lead).statement,
        db.bind
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Leads", len(leads))
    with col2:
        st.metric("Leads with Email", len(leads[leads['email'].notna()]))
    with col3:
        st.metric("Leads with Phone", len(leads[leads['phone'].notna()]))
    with col4:
        conversion_rate = len(leads[leads['status'] == 'converted']) / len(leads) * 100 if len(leads) > 0 else 0
        st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
    
    # Lead Sources and Status
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lead Sources")
        lead_sources = leads['source'].value_counts()
        fig = px.pie(
            values=lead_sources.values,
            names=lead_sources.index,
            title="Lead Sources Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Lead Status")
        lead_status = leads['status'].value_counts()
        fig = px.bar(
            x=lead_status.index,
            y=lead_status.values,
            title="Lead Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Properties Overview
    st.header("Properties Overview")
    properties = pd.read_sql(
        db.query(RealEstateProject).statement,
        db.bind
    )
    
    # Apply filters
    if selected_locations:
        properties = properties[properties['location'].isin(selected_locations)]
    if selected_property_types:
        properties = properties[properties['type'].isin(selected_property_types)]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Properties", len(properties))
    with col2:
        avg_price = properties['price'].astype(float).mean()
        st.metric("Average Price", format_currency(avg_price))
    with col3:
        st.metric("Unique Locations", properties['location'].nunique())
    with col4:
        st.metric("Active Projects", len(properties[properties['status'] == 'active']))
    
    # Property Analysis
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Property Types")
        property_types = properties['type'].value_counts()
        fig = px.bar(
            x=property_types.index,
            y=property_types.values,
            title="Property Types Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Price Distribution")
        fig = px.histogram(
            properties,
            x='price',
            nbins=20,
            title="Property Price Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Location Analysis
    st.subheader("Location Analysis")
    location_stats = properties.groupby('location').agg({
        'price': ['mean', 'count'],
        'type': lambda x: x.value_counts().index[0]
    }).reset_index()
    
    location_stats.columns = ['Location', 'Average Price', 'Property Count', 'Most Common Type']
    location_stats['Average Price'] = location_stats['Average Price'].apply(format_currency)
    
    st.dataframe(location_stats, use_container_width=True)
    
    # Outreach Performance
    st.header("Outreach Performance")
    outreach_logs = pd.read_sql(
        db.query(OutreachLog).statement,
        db.bind
    )
    
    # Filter by date range
    outreach_logs['created_at'] = pd.to_datetime(outreach_logs['created_at'])
    mask = (outreach_logs['created_at'].dt.date >= date_range[0]) & \
           (outreach_logs['created_at'].dt.date <= date_range[1])
    outreach_logs = outreach_logs[mask]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Outreach Attempts", len(outreach_logs))
    with col2:
        success_rate, response_rate, conversion_rate = calculate_metrics(outreach_logs)
        st.metric("Success Rate", f"{success_rate:.1f}%")
    with col3:
        st.metric("Response Rate", f"{response_rate:.1f}%")
    
    # Channel Performance
    st.subheader("Channel Performance")
    channel_stats = outreach_logs.groupby('channel').agg({
        'status': lambda x: (x == 'success').mean() * 100,
        'response_received': 'mean',
        'created_at': 'count'
    }).reset_index()
    
    channel_stats.columns = ['Channel', 'Success Rate', 'Response Rate', 'Total Attempts']
    channel_stats['Success Rate'] = channel_stats['Success Rate'].round(1)
    channel_stats['Response Rate'] = (channel_stats['Response Rate'] * 100).round(1)
    
    st.dataframe(channel_stats, use_container_width=True)
    
    # Outreach Timeline
    st.subheader("Outreach Timeline")
    timeline = outreach_logs.groupby(
        outreach_logs['created_at'].dt.date
    ).agg({
        'status': 'count',
        'response_received': 'sum'
    }).reset_index()
    
    timeline.columns = ['Date', 'Attempts', 'Responses']
    timeline['Response Rate'] = (timeline['Responses'] / timeline['Attempts'] * 100).round(1)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline['Date'],
        y=timeline['Attempts'],
        name='Outreach Attempts',
        mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=timeline['Date'],
        y=timeline['Responses'],
        name='Responses',
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title="Daily Outreach Volume and Responses",
        xaxis_title="Date",
        yaxis_title="Count"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity
    st.header("Recent Activity")
    recent_activity = outreach_logs.sort_values('created_at', ascending=False).head(10)
    st.dataframe(
        recent_activity[['created_at', 'channel', 'status', 'message', 'response_received']],
        use_container_width=True
    )

    db.close()

if __name__ == "__main__":
    main() 