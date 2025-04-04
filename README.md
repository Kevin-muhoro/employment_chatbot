# employment_chatbot
employment_chatbot

# Employment Management WhatsApp Chatbot

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Django](https://img.shields.io/badge/django-5.1-green)
![Twilio](https://img.shields.io/badge/twilio-whatsapp-yellow)

A Django-based WhatsApp chatbot for employee management with:
- Authentication via WhatsApp
- Leave request system
- Task management
- HR functions
- Role-based access control

## Features ✨

📌 **Employee Authentication**
- Secure login via WhatsApp
- Password protection
- Session management

📅 **Leave Management**
- Apply for leave via chat
- HR approval system
- Leave status tracking

📋 **Task System**
- Assign tasks via chat
- Task progress tracking
- Deadline reminders

👔 **HR Features**
- Employee database
- Role management
- Analytics dashboard

## Tech Stack 🛠️

- **Backend**: Django 5.1
- **Database**: SQLite (Production: PostgreSQL)
- **WhatsApp API**: Twilio
- **Authentication**: Django Auth
- **Hosting**: Ngrok (Dev), Heroku/AWS (Prod)

## Setup Guide 🚀

### Prerequisites
- Python 3.11+
- Twilio account
- WhatsApp Business API access

### Installation
```bash
# Clone repository
git clone https://github.com/Kevin-muhoro/employment_chatbot.git
cd employment_chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp employment_chatbot/local_settings.example.py employment_chatbot/local_settings.py
# Edit with your credentials
