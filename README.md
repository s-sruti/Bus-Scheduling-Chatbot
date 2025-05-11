# Twilio SMS Bus Scheduling Chatbot

An AI-powered chatbot that allows users to schedule bus journeys via SMS using [Twilio](https://www.twilio.com/) and ChatGPT. The application runs a lightweight Python Flask server that receives and responds to SMS messages using Twilio's webhook system.

---

##  Features

- SMS-based interaction through Twilio Sandbox
-  Supports real-time bus scheduling queries
-  Local development with public exposure via Cloudflare or Ngrok

---

##  Tech Stack

- **Backend:** Python, Flask
- **Messaging:** Twilio Programmable SMS
- **AI/NLP:** sentence embeddings
- **Tunnel:** Cloudflare (`cloudflare.exe`) or Ngrok (optional)

---

##  Getting Started

### 1. Clone the Repository


git clone https://github.com/s-sruti/Bus-Scheduling-Chatbot.git
cd bus-scheduler-bot

###2. Create and Activate a Virtual Environment

python -m venv venv
source venv/bin/activate         
On Windows: venv\Scripts\activate

###3. Install Dependencies


pip install -r requirements.txt

twilio_account_sid: "your_account_sid"
twilio_auth_token: "your_auth_token"
twilio_phone_number: "+1234567890"


###4.Expose Localhost to the Internet
Use Cloudflare Tunnel or Ngrok to expose your local server:

if cloudflare-
./cloudflare.exe tunnel

Or if using Ngrok-
ngrok http 5000
Copy the public URL (e.g., https://abc123.ngrok.io) for Twilio setup.

