@echo off
cd /d "%~dp0truthguard"
"..\venv\Scripts\python.exe" manage.py check
"..\venv\Scripts\python.exe" manage.py makemigrations accounts entities reports alerts analytics
"..\venv\Scripts\python.exe" manage.py migrate
"..\venv\Scripts\python.exe" manage.py seed_truthguard
echo DONE
