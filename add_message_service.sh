 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/app/outreach/services/message_service.py
index 0000000000000000000000000000000000000000..1fee2dd1fd221746fc079e8c7617470b3c115149 100644
--- a//dev/null
+++ b/app/outreach/services/message_service.py
@@ -0,0 +1,18 @@
+from app.shared.core.ai import AIService
+from app.outreach.schemas.outreach import OutreachChannel
+from app.lead.models.lead import Lead
+
+class MessageService:
+    """Generate outreach messages using the AI service."""
+    def __init__(self, ai_service: AIService | None = None) -> None:
+        self.ai_service = ai_service or AIService()
+
+    async def generate(self, lead: Lead, channel: OutreachChannel) -> str:
+        return await self.ai_service.generate_outreach_message(
+            lead_name=lead.name,
+            lead_source=lead.source,
+            channel=channel,
+            property_preferences=lead.property_preferences,
+            budget_range=lead.budget_range,
+            notes=lead.notes,
+        )
 
EOF
)