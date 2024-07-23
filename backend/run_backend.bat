@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Running python Scripts
python src\main.py
pause