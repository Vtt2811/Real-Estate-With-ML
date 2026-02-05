@echo off
REM scripts to run the django server with the virtual environment activated
call .venv\Scripts\activate.bat
python manage.py runserver
pause
