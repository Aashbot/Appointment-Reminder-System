# Appointment Reminder System

## Overview

This project is a **Streamlit** application designed to schedule and send appointment reminders via **SMS** and **WhatsApp** using **Twilio**. The application supports multiple languages and allows for customized messages, making it ideal for healthcare providers or any service requiring appointment reminders.

## Features

- **Send SMS/WhatsApp Reminders**: Easily send reminders to patients or clients.
- **Custom Messages**: Create personalized reminder messages with placeholders for patient names.
- **Language Support**: Translate messages into several languages.
- **Scheduling**: Schedule reminders to be sent at a specific date and time.
- **Multithreading**: Scheduling operations are handled in separate threads to ensure the app remains responsive.

## Requirements

- Python 3.7+
- A Twilio account with active SID, Auth Token, and phone numbers for SMS and WhatsApp.
- The following Python packages:
  - `streamlit`
  - `twilio`
  - `translate`
  - `schedule`

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/appointment-reminder-system.git
    cd appointment-reminder-system
    ```

2. **Create a virtual environment** (optional but recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:

    Create a `.env` file in the root of your project with the following content:

    ```bash
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    TWILIO_PHONE_NUMBER=your_twilio_phone_number
    TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number
    ```

5. **Run the Streamlit app**:

    ```bash
    streamlit run app.py
    ```

## Usage

1. Open the app in your browser. It should be running on `http://localhost:8501`.
2. Enter the patient's name, phone number, and select the language for the reminder.
3. Create a custom message or use the default template.
4. Select the date and time for the reminder.
5. Click on "Schedule SMS" or "Schedule WhatsApp Message" to schedule the reminder.
6. The app will send the message at the scheduled time.

## Customization

- **Message Templates**: Modify the default message template directly in the app or in the code by editing the `custom_message` variable.
- **Languages**: The app currently supports English, Kannada, Tamil, Telugu, Konkani, and Hindi. You can add more languages by expanding the `languages` dictionary.
- **Scheduler**: The app uses the `schedule` module to handle timing. For more complex scheduling (e.g., recurring reminders), consider expanding the scheduler logic.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss improvements or new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Twilio](https://www.twilio.com/)
- [Translator](https://pypi.org/project/translate/)
- [Schedule](https://pypi.org/project/schedule/)
