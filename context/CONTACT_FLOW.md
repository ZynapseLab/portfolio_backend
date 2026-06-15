# Contact Flow Context

- Contact intent is detected by the classifier; required fields are `name`, `email`, `subject`, and `message` in `app/agent/nodes/classifier.py`.
- `app/services/email_service.py` also reads `country` from `contact_data`; keep classifier prompts and contact handling aligned so `country` is present before sending email.
- Complete contact requests go to `contact_handler`, which enforces `EMAIL_DAILY_LIMIT` by counting `contact_leads` for the requester IP and current UTC date.
- Contact emails are sent to configured `JONATHAN_EMAIL` and `PABLO_EMAIL`, then a confirmation is sent to the submitted email when present.
- HTML templates are `app/templates/contact_notification.html` and `app/templates/contact_confirmation.html`; they use simple string replacement placeholders, not a template engine.
- Non-English contact responses and rejection messages stream through `app/services/translator.py` using `OPENROUTER_TRANSLATOR_MODEL`.
