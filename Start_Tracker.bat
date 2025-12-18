@echo off
:: This command ensures the script runs from the current folder
cd /d "%~dp0"

echo ==========================================
echo      LEAF STUDIOS - TRACKER SETUP
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found! 
    echo Please install Python from python.org and check "Add to PATH".
    pause
    exit
)

echo [Step 1/3] Checking & Installing Libraries...
:: This installs streamlit, pandas, playwright from your requirements file
pip install -r requirements.txt

echo.
echo [Step 2/3] Verifying Browser Engine...
:: This ensures the special browser for the bot is ready
playwright install

echo.
echo [Step 3/3] Launching Dashboard...
echo.
:: This actually starts your app
streamlit run app.py

:: This keeps the window open if the app crashes so you can see the error
pause