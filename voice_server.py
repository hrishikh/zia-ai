from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=['POST'])
def incoming_call():
    """Zia answers the phone via Twilio Webhook"""
    response = VoiceResponse()
    # This is what people will hear when they call your Twilio number
    response.say("Hello! You've reached Zia, Hrishik's neural agent. How can I help you today?", voice='alice')
    return str(response)

if __name__ == "__main__":
    print("🚀 Zia's Voice Server is active on port 5000...")
    # This must match the port you used in your ngrok command
    app.run(port=5000)