@echo off
echo ======================================
echo    Chatbot-Demo Startup Script
echo ======================================

:: Check and install dependencies
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt -q
    echo Dependencies installed.
) else (
    echo requirements.txt not found, skipping.
)

:: Check and copy env file
if not exist ".env" (
    if exist ".env.example" (
        echo .env not found, copying from .env.example...
        copy .env.example .env
        echo Please edit .env and configure your API Key, then run this script again!
        pause
        exit /b 1
    )
) else (
    echo .env file is ready.
)

:: Start backend and frontend
echo Starting project...
start "Chatbot-Backend" cmd /k python backend.py
start "Chatbot-Frontend" cmd /k streamlit run frontend.py

echo ======================================
echo    Project started! Open your browser.
echo ======================================
pause
