# TODO

## WhatsApp via Twilio
- [ ] Remove any code that accesses `prefs.whatsapp_settings` or expects a WhatsApp API key in communication preferences.
- [ ] Update WhatsApp sending logic to use the Twilio client:
  - Use `from_="whatsapp:+14155238886"` (Twilio sandbox number) and `to="whatsapp:+91XXXXXXXXXX"` (recipient, must have joined sandbox).
  - Reference: https://www.twilio.com/docs/whatsapp/sandbox
- [ ] Note: With a Twilio free trial, you can only send WhatsApp messages to numbers that have joined your sandbox. Recipients must opt in by sending the join code to the sandbox number.
- [ ] For production, upgrade your Twilio account and apply for WhatsApp Business API access.

## Lead Sourcing Integrations (previous TODOs)
- [ ] Integrate lead sourcing from Facebook Marketplace
- [ ] Integrate lead sourcing from local forums/WhatsApp groups
- [ ] Integrate lead sourcing from B2B CRM datasets
- [ ] Integrate lead sourcing from Google Maps Places API
- [ ] Implement ProjectListResponse schema in app/shared/schemas/project.py 
- [ ] Implement RealEstateProjectList schema in app/project/schemas/project.py 