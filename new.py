import streamlit as st
from twilio.rest import Client
import pywhatkit as kit
from translate import Translator
import schedule
import time
from datetime import datetime
import threading

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
    'Konkani': 'kok',
    'Hindi': 'hi'
}

# A flag to indicate if the message has been sent
message_sent = False

def send_sms(to_phone_number, message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        global message_sent
        message_sent = True
    except Exception as e:
        st.error(f"Failed to send SMS: {e}")

def send_whatsapp(to_phone_number, message):
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=f'whatsapp:{to_phone_number}'
        )
        global message_sent
        message_sent = True
    except Exception as e:
        st.error(f"Failed to send WhatsApp message: {e}")

def schedule_message(date_time, func, *args):
    def job():
        func(*args)
        schedule.clear()
    schedule.every().day.at(date_time.strftime('%H:%M')).do(job)

def run_schedule():
    while not message_sent:
        schedule.run_pending()
        time.sleep(1)

def main():
    st.title("Appointment Reminder System")
    
    st.write("Send reminders via SMS and WhatsApp.")

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
            st.write(f"Scheduled SMS for {schedule_datetime}")

            threading.Thread(target=schedule_message, args=(schedule_datetime, send_sms, phone_number, translated_message)).start()
            threading.Thread(target=run_schedule).start()
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
            st.write(f"Scheduled WhatsApp message for {schedule_datetime}")

            threading.Thread(target=schedule_message, args=(schedule_datetime, send_whatsapp, phone_number, translated_message)).start()
            threading.Thread(target=run_schedule).start()
        else:
            st.error("Please enter all the details including the patient's name, phone number, select a language, and set a date and time.")

if __name__ == "__main__":
    main()