@echo off
echo 🚀 Starting SPY Iron Condor Pro...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install requirements
echo 📦 Installing required packages...
pip install -q -r requirements.txt

if errorlevel 1 (
    echo ⚠️ Some packages failed to install. Trying again...
    pip install --upgrade pip
    pip install -r requirements.txt
)

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Opening app at http://localhost:8501
echo 📊 Press Ctrl+C to stop the app
echo.
timeout /t 2 >nul

REM Run Streamlit app
streamlit run app.py
