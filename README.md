# Real Estate With ML — Django scaffold

This workspace contains the original static site and a minimal Django scaffold so you can run the UI with Django's development server.

Quick start (Windows PowerShell):

```
python -m venv .venv
; .\.venv\Scripts\Activate.ps1
; pip install -r requirements.txt
; python manage.py migrate
; python manage.py runserver
```

Notes:
- Templates are in `templates/`.
- Static CSS files are in `static/css/`. Original images remain in `photo/` and are exposed via Django static config.
- The app `listings` contains simple views that render the templates. No database models or authentication are configured yet.
