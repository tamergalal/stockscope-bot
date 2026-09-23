@echo off
REM Auto-start helper for Windows Task Scheduler (local free hosting).
cd /d "C:\Users\Dr.Tamer Galal\AppData\Local\Cline\stock_bot_project"
python main.py >> bot_run.log 2>&1
