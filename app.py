from flask import Flask, render_template, request, jsonify
import os
import pathlib
import tempfile
import requests
import time
import pyautogui
import webbrowser as web
import pandas as pd
import keyboard as k
from urllib.parse import quote
from pyngrok import ngrok

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
pathlib.Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Set your Groq API key here or via environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "Give_your_API_KEY") # Give your Groq API key here
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# In-memory store
last_generated = {
    "preview": "",
    "messages": []  # list of {"name","phone","message"}
}

# ------------------- GROQ API ------------------- #
def generate_message_with_groq(script: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-oss-20b",  # Better model for WhatsApp message generation
        "messages": [
            {"role": "system", "content": "You are a helpful assistant "},
            {"role": "user", "content": script}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=15)
    response.raise_for_status()
    result = response.json()
    return result['choices'][0]['message']['content']


@app.route('/generate_message', methods=['POST'])
def generate_message():
    global last_generated
    last_generated = {"preview": "", "messages": []}

    mode = request.form.get('mode')  # "manual" or "ai"

    # Manual mode: user enters a single message + Excel with numbers
    if mode == "manual":
        message_text = request.form.get('manual_message')
        file = request.files.get('file')

        if not message_text or not file:
            return jsonify({'error': 'Message and file are required for manual mode'}), 400

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            df = pd.read_excel(tmp.name)
        os.unlink(tmp.name)

        if "PhoneNumber" not in df.columns:
            return jsonify({'error': "Excel must have 'PhoneNumber' column"}), 400

        messages = []
        for _, row in df.iterrows():
            phone = str(row["PhoneNumber"]).strip()
            messages.append({"name": row.get("Name", ""), "phone": phone, "message": message_text})

        last_generated["preview"] = message_text
        last_generated["messages"] = messages

        return jsonify({"preview": message_text, "messages": messages})

    # AI mode: same as your existing flow
    elif mode == "ai":
        prompt = request.form.get('prompt')
        file = request.files.get('file')

        if not prompt or not file:
            return jsonify({'error': 'Prompt and file are required for AI mode'}), 400

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            df = pd.read_excel(tmp.name)
        os.unlink(tmp.name)

        if not {"Name", "PhoneNumber"}.issubset(df.columns):
            return jsonify({'error': "Excel must have 'Name' and 'PhoneNumber' columns"}), 400

        messages = []
        for _, row in df.iterrows():
            name = str(row["Name"])
            phone = str(row["PhoneNumber"]).strip()
            script = f"Create a personalized WhatsApp message for {name} based on: {prompt}"

            try:
                message_text = generate_message_with_groq(script)
            except Exception as e:
                return jsonify({"error": f"Groq API error: {e}"}), 500

            messages.append({"name": name, "phone": phone, "message": message_text})

        last_generated["preview"] = messages[0]["message"] if messages else ""
        last_generated["messages"] = messages

        return jsonify({"preview": last_generated["preview"], "messages": messages})

    else:
        return jsonify({'error': 'Invalid mode'}), 400


# ------------------- WHATSAPP SENDING ------------------- #
def send_whatsapp(phone: str, message: str, x_cord=787, y_cord=972): # Adjust x_cord and y_cord based on your screen resolution 
    """
    Send a WhatsApp message using web.whatsapp.com, pyautogui, and keyboard.
    """
    try:
        # Ensure phone format
        phone = str(phone).strip().replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            if phone.startswith("91"):
                phone = f"+{phone}"
            else:
                phone = f"+91{phone}"

        # Open WhatsApp Web with message
        web.open(f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}")
        time.sleep(15)  # Wait for WhatsApp Web to load

        # Click message box
        pyautogui.click(x_cord, y_cord)
        time.sleep(2)

        # Press Enter to send
        k.press_and_release('enter')
        time.sleep(2)

        # Close tab
        k.press_and_release('ctrl+w')
        time.sleep(1)

        return {'status': 'sent'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# ------------------- ROUTES ------------------- #

@app.route('/send_all', methods=['POST'])
def send_all():
    results = []
    for item in last_generated.get('messages', []):
        try:
            res = send_whatsapp(item['phone'], item['message'])
            results.append({'phone': item['phone'], 'status': res.get('status')})
        except Exception as e:
            results.append({'phone': item['phone'], 'status': 'error', 'error': str(e)})
    return jsonify({'results': results})

@app.route('/send_one', methods=['POST'])
def send_one():
    phone = request.form.get('phone')
    message = request.form.get('message')
    if not phone or not message:
        return jsonify({'error': 'phone and message required'}), 400
    try:
        res = send_whatsapp(phone, message)
        return jsonify({'status': res.get('status')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
# # Start Ngrok tunnel
#     port = 5000
#     public_url = ngrok.connect(port)
#     print(" * Ngrok tunnel URL:", public_url)
#     # Run Flask app
#     app.run(port=port, debug=True)
    app.run(debug=True)