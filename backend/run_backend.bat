@echo off
echo Creating virtual environment (if not exists)...
if not exist .venv (
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Starting FastAPI backend with Uvicorn...
uvicorn backend.main:app --reload --port 8000
<<<<<<< HEAD
pause
=======
pause
>>>>>>> a69096ac3a8e5d679cd246b1ebe8423a4c82c726
