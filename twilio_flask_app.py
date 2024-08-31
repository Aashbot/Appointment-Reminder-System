from flask import Flask, request, redirect
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    gather = Gather(action="/gather", num_digits=1, timeout=5)
    gather.say("Press 1 to hear your appointment details. Press 2 to reschedule your appointment.")
    response.append(gather)
    return str(response)

@app.route("/gather", methods=['GET', 'POST'])
def gather():
    response = VoiceResponse()
    digit = request.values.get('Digits')
    custom_message = request.values.get('custom_message', "Default appointment details message.")
    
    if digit == '1':
        response.say(custom_message)
    elif digit == '2':
        response.say("Please contact the clinic to reschedule your appointment.")
    else:
        response.say("Sorry, I didn't understand that choice.")

    response.hangup()
    return str(response)

if __name__ == "__main__":
    app.run(port=5000)
