Bulk WhatsApp Message Generator (Flask App)
-----------------------------------------------
How to run:
1. Install dependencies:
   pip install -r requirements.txt
2. Set environment variables:
   - Groq_API_KEY (required to use OpenAI online generation)
   - OPENAI_MODEL (optional, default openai/gpt-oss-20b)
3. Adjust x and y Coordinates:
   - run test.py to know the x_cord and y_cord Coordinates and paste it on send_whatsapp(phone: str, message: str, x_cord=787, y_cord=972) function(by default x_cord=787 and y_cord=972).  
4. Run:
   Double-check on the start_flask_and_tunnel.bat file, it will automatically runs the project and only provide the public URL, using that URL project can be anywhere.
   (or)
   On terminal: python app.py and Open http://127.0.0.1:5000 in your browser.

Notes:
- The Generate button will send the prompt to OpenAI and display a generated prompt preview below the button.
- Generated messages are personalized by prefixing the recipient's name (Hi Name, ...).
- Manually user-entered messages can also be sent without generating a message using the Groq api.
- Generated message can also be edited by clicking on the Edit message button.    
- Excel must contain columns named 'Name' and a phone column like 'PhoneNumber' or 'Phone'.
