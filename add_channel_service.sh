 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/app/outreach/services/channel_service.py
index 0000000000000000000000000000000000000000..4640492b3c729aa2fc94f9c128ffa80f8d4dc1f3 100644
--- a//dev/null
+++ b/app/outreach/services/channel_service.py
@@ -0,0 +1,30 @@
+from sendgrid import SendGridAPIClient
+from sendgrid.helpers.mail import Mail
+from twilio.rest import Client
+from app.shared.core.config import settings
+
+class EmailClient:
+    """Thin wrapper around SendGrid client."""
+    def __init__(self) -> None:
+        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
+
+    async def send(self, to_email: str, subject: str, body: str) -> None:
+        email = Mail(
+            from_email=settings.FROM_EMAIL,
+            to_emails=to_email,
+            subject=subject,
+            plain_text_content=body,
+        )
+        self.client.send(email)
+
+class SMSClient:
+    """Thin wrapper around the Twilio client."""
+    def __init__(self) -> None:
+        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
+
+    async def send(self, to_phone: str, message: str) -> None:
+        self.client.messages.create(
+            body=message,
+            from_=settings.TWILIO_PHONE_NUMBER,
+            to=to_phone,
+        )
 
EOF
)