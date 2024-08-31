import streamlit as st
from twilio.rest import Client
from translate import Translator
import schedule
import time
from datetime import datetime
import threading
import base64
from gtts import gTTS
import io

# Set your Twilio credentials here
TWILIO_ACCOUNT_SID = 'TWILIO_ACCOUNT_SID'#TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = 'TWILIO_AUTH_TOKEN'#TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = 'TWILIO_PHONE_NUMBER'#TWILIO_PHONE_NUMBER
TWILIO_WHATSAPP_NUMBER = 'TWILIO_WHATSAPP_NUMBER'#TWILIO_WHATSAPP_NUMBER
TWILIO_VOICE_NUMBER = 'TWILIO_VOICE_NUMBER'#TWILIO_VOICE_NUMBER
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Language options
languages = {
    'English': 'en',
    'Kannada': 'kn',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Hindi': 'hi'
}

# To keep track of all jobs
jobs = []

def send_sms(to_phone_number, message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
    except Exception as e:
        st.error(f"Failed to send SMS: {e}")

def send_whatsapp(to_phone_number, message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:{to_phone_number}'
        )
    except Exception as e:
        st.error(f"Failed to send WhatsApp message: {e}")

def send_voice(to_phone_number, message, audio_content):
    try:
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        client.calls.create(
            twiml=f'<Response><Say>{message}</Say><Play>{audio_base64}</Play></Response>',
            from_=TWILIO_VOICE_NUMBER,
            to=to_phone_number
        )
    except Exception as e:
        st.error(f"Failed to send voice message: {e}")

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    audio_io = io.BytesIO()
    tts.write_to_fp(audio_io)
    audio_io.seek(0)
    audio_content = audio_io.read()
    return audio_content

def schedule_message(date_time, func, *args):
    def job():
        func(*args)
        jobs.remove(job)  # Remove job from the list after execution

    # Schedule the job
    job = schedule.every().day.at(date_time.strftime('%H:%M')).do(job)
    jobs.append(job)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    st.title("Appointment Reminder System")
    
    st.write("Send reminders via SMS, WhatsApp, and Voice.")

    patient_name = st.text_input("Enter the patient's name:")
    phone_number = st.text_input("Enter the phone number (in international format):")
    language = st.selectbox("Select the language:", list(languages.keys()))
    custom_message = st.text_area("Enter your custom message (use {name} to insert the patient's name):", value="Hi {name}, reminder: Your appointment is scheduled for tomorrow at 10 AM. Please visit Jayadeva Hospital.")
    schedule_date = st.date_input("Select the date:")
    schedule_time = st.time_input("Select the time:")

    if st.button("Schedule SMS"):
        if patient_name and phone_number and language and custom_message and schedule_date and schedule_time:
            reminder_message = custom_message.format(name=patient_name)
            if language != 'English':
                translator = Translator(to_lang=languages[language])
                translated_message = translator.translate(reminder_message)
            else:
                translated_message = reminder_message
            
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            st.write(f"Scheduled SMS for {schedule_datetime.strftime('%d/%m/%Y at %H:%M')}")

            threading.Thread(target=schedule_message, args=(schedule_datetime, send_sms, phone_number, translated_message)).start()
        else:
            st.error("Please enter all the details including the patient's name, phone number, select a language, and set a date and time.")

    if st.button("Schedule WhatsApp Message"):
        if patient_name and phone_number and language and custom_message and schedule_date and schedule_time:
            reminder_message = custom_message.format(name=patient_name)
            if language != 'English':
                translator = Translator(to_lang=languages[language])
                translated_message = translator.translate(reminder_message)
            else:
                translated_message = reminder_message
            
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            st.write(f"Scheduled WhatsApp message for {schedule_datetime.strftime('%d/%m/%Y at %H:%M')}")

            threading.Thread(target=schedule_message, args=(schedule_datetime, send_whatsapp, phone_number, translated_message)).start()
        else:
            st.error("Please enter all the details including the patient's name, phone number, select a language, and set a date and time.")

    if st.button("Schedule Voice Call"):
        if patient_name and phone_number and language and custom_message and schedule_date and schedule_time:
            reminder_message = custom_message.format(name=patient_name)
            if language != 'English':
                translator = Translator(to_lang=languages[language])
                translated_message = translator.translate(reminder_message)
            else:
                translated_message = reminder_message
            
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            st.write(f"Scheduled voice call for {schedule_datetime.strftime('%d/%m/%Y at %H:%M')}")

            audio_content = text_to_speech(translated_message, languages[language])

            threading.Thread(target=schedule_message, args=(schedule_datetime, send_voice, phone_number, translated_message, audio_content)).start()
        else:
            st.error("Please enter all the details including the patient's name, phone number, select a language, and set a date and time.")

    # Display success or error messages if any
    if "sent" in st.session_state and st.session_state["sent"]:
        st.success("Message sent successfully.")
        st.session_state["sent"] = False
    elif "error" in st.session_state and st.session_state["error"]:
        st.error(st.session_state["error"])
        st.session_state["error"] = ""

# Start the scheduling thread
if "scheduler_thread" not in st.session_state:
    scheduler_thread = threading.Thread(target=run_schedule)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    st.session_state["scheduler_thread"] = scheduler_thread

if __name__ == "__main__":
    main()
