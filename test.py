import streamlit as st
from twilio.rest import Client
from translate import Translator
from datetime import datetime
import threading
import queue
import pandas as pd
import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# AWS credentials and configuration
AWS_ACCESS_KEY = 'AWS_ACCESS_KEY'#AWS_ACCESS_KEY
AWS_SECRET_KEY = 'AWS_SECRET_KEY'#AWS_SECRET_KEY
AWS_REGION = 'AWS_REGION'#AWS_REGION
S3_BUCKET_NAME = 'S3_BUCKET_NAME'#S3_BUCKET_NAME

# Twilio credentials and configuration
TWILIO_ACCOUNT_SID = 'TWILIO_ACCOUNT_SID'#TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = 'TWILIO_AUTH_TOKEN'#TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = 'TWILIO_PHONE_NUMBER'#TWILIO_PHONE_NUMBER
TWILIO_WHATSAPP_NUMBER = 'TWILIO_WHATSAPP_NUMBER'#TWILIO_WHATSAPP_NUMBER
TWILIO_VOICE_NUMBER = 'TWILIO_VOICE_NUMBER'#TWILIO_VOICE_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Load patient data from CSV
csv_file_path = 'PatientData1.csv'  # Path to your CSV file
patient_data = pd.read_csv(csv_file_path)

# Language options
languages = {
    'English': 'en-US',
    'Kannada': 'kn-IN',
    'Tamil': 'ta-IN',
    'Telugu': 'te-IN',
    'Hindi': 'hi-IN',
    'Malayalam': 'ml-IN',
    'Arabic': 'arb'
}

# Predefined list of doctors
doctors_list = [
    'Dr. Rajesh Reddy',
    'Dr. Anil Kumar',
    'Dr. Priya Sharma',
    'Dr. Sanjay Rao',
    'Dr. Neha Singh',
    'Dr. Lakshmi Nair',
    'Dr. Arvind Krishna',
    'Dr. Deepa M',
    'Dr. Suresh Kumar',
    'Dr. Manjunath C.N.'
]

# To keep track of all jobs
scheduled_jobs = []

# Queue for communication between threads
message_queue = queue.Queue()

# AWS Polly client
polly_client = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
).client('polly')

# S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def synthesize_speech(text, language_code, voice_id='Aditi', output_format='mp3'):
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat=output_format,
            VoiceId=voice_id,
            LanguageCode=language_code
        )
        audio_file_path = 'reminder.mp3'
        with open(audio_file_path, 'wb') as file:
            file.write(response['AudioStream'].read())
        return audio_file_path
    except (NoCredentialsError, PartialCredentialsError) as e:
        message_queue.put(("error", f"Failed to authenticate with AWS: {e}"))
    except Exception as e:
        message_queue.put(("error", f"Failed to synthesize speech: {e}"))
        return None

def upload_to_s3(file_path, bucket_name, object_name):
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return s3_url
    except (NoCredentialsError, PartialCredentialsError) as e:
        message_queue.put(("error", f"Failed to authenticate with AWS S3: {e}"))
    except Exception as e:
        message_queue.put(("error", f"Failed to upload to S3: {e}"))
        return None

def send_sms(to_phone_numbers, message):
    try:
        for number in to_phone_numbers:
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=number
            )
        message_queue.put(("success", "SMS sent successfully."))
    except Exception as e:
        message_queue.put(("error", f"Failed to send SMS: {e}"))

def send_whatsapp_message(to_phone_numbers, message, audio_url=None):
    try:
        for number in to_phone_numbers:
            if audio_url:
                message += f"\nListen to your reminder: {audio_url}"
            client.messages.create(
                body=message,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=f'whatsapp:{number}'
            )
        message_queue.put(("success", "WhatsApp message sent successfully."))
    except Exception as e:
        message_queue.put(("error", f"Failed to send WhatsApp message: {e}"))

def send_voice(to_phone_number, message):
    try:
        client.calls.create(
            twiml=f'<Response><Say voice="Polly.Raveena" language="en-IN">{message}</Say></Response>',
            from_=TWILIO_VOICE_NUMBER,
            to=to_phone_number
        )
        message_queue.put(("success", "Voice call sent successfully."))
    except Exception as e:
        message_queue.put(("error", f"Failed to send voice message: {e}"))

def schedule_job(job_time, func, *args):
    def job():
        func(*args)
    delay = (job_time - datetime.now()).total_seconds()
    threading.Timer(delay, job).start()

def main():
    st.title("Appointment Reminder System")
    
    st.write("Send reminders via SMS, WhatsApp, and Voice.")
    
    # Dropdown for patient ID
    patient_id = st.selectbox("Select the patient ID:", options=list(patient_data['Patient ID'].unique()), index=None)
    
    if patient_id:
        patient_row = patient_data[patient_data['Patient ID'] == patient_id]
        if not patient_row.empty:
            patient_name = patient_row['Patient Name'].values[0]
            phone_number = patient_row['Phone Number'].values[0]
            language = patient_row['Language'].values[0]
            ngo_name = patient_row['NGO'].values[0]
            area = patient_row['Area'].values[0]
            nphone_number = patient_row['Nphone Number'].values[0]
        else:
            st.error("Patient ID not found.")
            return
    else:
        patient_name = ""
        phone_number = ""
        language = ""
        ngo_name = ""
        area = ""
        nphone_number = ""
        
    patient_name = st.text_input("Enter the patient's name:", value=patient_name)
    phone_number = st.text_input("Enter the phone number (in international format):", value=f'+{phone_number}')
    language = st.selectbox("Select the language:", list(languages.keys()), index=list(languages.keys()).index(language) if language in languages else 0)
    area = st.text_input("Area:", value=area)
    ngo_name = st.text_input("NGO Name:", value=ngo_name)
    nphone_number = st.text_input("Nphone Number:", value=f'+{nphone_number}')

    # Doctor's name selection
    doctor_name = st.selectbox("Select the doctor's name:", options=doctors_list, index=None)

    custom_message = st.text_area("Enter your custom message (use {name} to insert the patient's name and {doctor} for doctor's name):", value="Hi {name}, reminder: Your appointment with {doctor} is scheduled for tomorrow at 10 AM. Please visit Jayadeva Hospital.")
    schedule_date = st.date_input("Select the date:", value=None)
    schedule_time = st.time_input("Select the time:", value=None)

    if st.button("Schedule SMS"):
        if patient_id and patient_name and phone_number and language and custom_message and schedule_date and schedule_time and doctor_name:
            reminder_message = custom_message.format(name=patient_name, doctor=doctor_name)
            if language != 'English':
                translator = Translator(to_lang=languages[language])
                translated_message = translator.translate(reminder_message)
            else:
                translated_message = reminder_message
            
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            st.write(f"Scheduled SMS for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}")
            
            schedule_job(schedule_datetime, send_sms, [phone_number, nphone_number], translated_message)
        else:
            st.error("Please enter all the details including the patient's ID, name, phone number, select a language, set a date and time, and enter the doctor's name.")

    if st.button("Schedule WhatsApp Message"):
        if patient_id and patient_name and phone_number and language and custom_message and schedule_date and schedule_time and doctor_name:
            reminder_message = custom_message.format(name=patient_name, doctor=doctor_name)
            if language != 'English':
                translator = Translator(to_lang=languages[language])
                translated_message = translator.translate(reminder_message)
            else:
                translated_message = reminder_message
            
            audio_file_path = synthesize_speech(translated_message, languages[language])
            if audio_file_path:
                audio_url = upload_to_s3(audio_file_path, S3_BUCKET_NAME, f"{patient_name}_reminder.mp3")
                if audio_url:
                    schedule_datetime = datetime.combine(schedule_date, schedule_time)
                    st.write(f"Scheduled WhatsApp message for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}")

                    schedule_job(schedule_datetime, send_whatsapp_message, [phone_number, nphone_number], translated_message, audio_url)
                else:
                    st.error("Failed to upload audio to S3.")
            else:
                st.error("Failed to generate audio file.")
        else:
            st.error("Please enter all the details including the patient's ID, name, phone number, select a language, set a date and time, and enter the doctor's name.")
            
    if st.button("Schedule Voice Call"):
        if patient_id and patient_name and phone_number and language and custom_message and schedule_date and schedule_time and doctor_name:
            reminder_message = custom_message.format(name=patient_name, doctor=doctor_name)
            if language != 'English':
                translator = Translator(to_lang=languages[language])
                translated_message = translator.translate(reminder_message)
            else:
                translated_message = reminder_message
            
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            st.write(f"Scheduled voice call for {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}")

            schedule_job(schedule_datetime, send_voice, phone_number, translated_message)
        else:
            st.error("Please enter all the details including the patient's ID, name, phone number, select a language, set a date and time, and enter the doctor's name.")
    
    # Process messages from the queue
    while not message_queue.empty():
        message_type, message_content = message_queue.get()
        if message_type == "success":
            st.success(message_content)
        elif message_type == "error":
            st.error(message_content)

if __name__ == "__main__":
    main()
