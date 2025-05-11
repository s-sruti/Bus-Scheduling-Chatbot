from twilio.rest import Client
from flask import Flask, request, jsonify
import intent_detector 
import urllib.parse
app = Flask(__name__)

# Twilio credentials
account_sid = 'AC12ba045703c96a6c94e9dd42dfbd6819'
auth_token = 'c2e66c44f0d725d59b71b2f587289efd'
twilio_number = 'whatsapp:+14155238886'  # This is your Twilio Sandbox number

client = Client(account_sid, auth_token)

completed=True
intent_data={"intent":None,
             "idx":None
}

session_data_map={
    "source":None,
    "destination":None
}
location=None
intent_detector_obj=intent_detector.IntentDetector("examples.json")
# WhatsApp Message Handler
@app.route("/whatsapp", methods=['POST'])
def handle_whatsapp():
    global completed,session_data_map,location,intent_data,intent_detector_obj
    user_message = request.values.get('Body', '').lower()
    response_message = ""
    if completed:
        intent_data['idx'],intent_data['intent']=intent_detector_obj.detect_intent(user_message)

    if intent_data['intent']=="greeting":
        response_message=intent_detector_obj.reply[intent_data['idx']]
    elif intent_data['intent']=="wrapup":
        response_message=intent_detector_obj.reply[intent_data['idx']]
    elif intent_data['intent']=="book_ticket":
        response_message='''Hello!
We do not offer direct ticket booking services .
However, if you'd like to explore or book tickets yourself, you can also use the official sites below:

🔹 MSRTC Official Website: https://msrtc.maharashtra.gov.in/
🔹 RedBus Ticket Booking : https://www.redbus.in/

Thank you.'''
    elif intent_data['intent']=="view_schedule":
        completed=False
        if None in session_data_map.values():
            response_message,session_data_map=intent_detector.entities_detect_map(user_message,session_data_map)
        if not(None in session_data_map.values()):
            response_message="Today's schedule:\n"
            res=intent_detector.schedule(location=session_data_map)
            response_message+=res
            completed=True
            session_data_map={
            "source":None,
            "destination":None
            }
    elif intent_data['intent']=="location_query":
        completed=False
        if None in session_data_map.values():
            response_message,session_data_map=intent_detector.entities_detect_map(user_message,session_data_map)
        if not(None in session_data_map.values()):
            origin = urllib.parse.quote(session_data_map['source'])
            destination = urllib.parse.quote(session_data_map['destination'])
            map_link = f"\n https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
            response_message+=map_link
            completed=True
            session_data_map={
            "source":None,
            "destination":None
            }
    else:
        response_message="Sorry, I can only assist you with bus schedules and guide you for other resources currently! 🚌✨"

    client.messages.create(
        body=response_message,
        from_=twilio_number,
        to=request.values.get('From')
    )

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True)
