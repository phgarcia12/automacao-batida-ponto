@echo off
REM Script batch para executar a batida de ponto
REM Usado pelo Windows Task Scheduler

cd /d "C:\Users\paulo.garcia\Desktop\Repos\automao-batida-ponto"
python batida_ponto_local.py

exit /b %errorlevel%
