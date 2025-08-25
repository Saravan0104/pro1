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
pause