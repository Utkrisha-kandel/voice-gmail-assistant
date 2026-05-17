Voice Gmail Assistant

I built this because I wanted to check and send emails without typing. Just talk to it and it handles the rest.

What it does

Listen to your voice and understand what you want
Read out your latest emails
Send emails on your behalf
Connects securely to your Gmail account
How it works

You speak → Groq transcribes it → LLaMA 3 figures out what you want → Gmail API reads or sends the email → browser speaks the reply back to you.

Stack

FastAPI for the backend
Groq for speech to text and AI
Gmail API for email access
Google OAuth2 for login
Browser's built-in TTS for speaking responses
Running it locally

Clone the repo and install dependencies pip install -r requirements.txt

Get a Groq API key from groq.com and add it to .env GROQ_API_KEY=your_key_here

Download credentials.json from Google Cloud Console and place it in the project root

Run it python main.py

Go to http://localhost:8000 and connect your Gmail

Notes

credentials.json is not pushed to GitHub for obvious reasons
If you see a Google warning screen, click Advanced and proceed
Works best in Chrome
Live Demo
[voice-gmail-assistant-production.up.railway.app](https://voice-gmail-assistant-production.up.railway.app)
