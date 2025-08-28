Bulk WhatsApp Message Generator (OpenAI preview)
-----------------------------------------------
How to run:
1. Install dependencies:
   pip install -r requirements.txt
2. Set environment variables:
   - Groq_API_KEY (required to use OpenAI online generation)
   - OPENAI_MODEL (optional, default openai/gpt-oss-20b)
3. Run:
   python app.py
4. Open http://127.0.0.1:5000 in your browser.

Notes:
- The Generate button will send the prompt to OpenAI and display a polished preview below the button.
- Generated messages are personalized by prefixing the recipient's name (Hi Name, ...).
- Default send mode is MOCK (prints sends to console). To actually send via Twilio, configure SEND_MODE=twilio and Twilio credentials.
- Excel must contain columns named 'Name' and a phone column like 'PhoneNumber' or 'Phone'.
