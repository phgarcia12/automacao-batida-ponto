@echo off
echo Reativando automacao de batida de ponto...

:: Habilitar tarefas no Task Scheduler
schtasks /change /tn "BatidaPonto_0825" /enable
schtasks /change /tn "BatidaPonto_1200" /enable
schtasks /change /tn "BatidaPonto_1325" /enable
schtasks /change /tn "BatidaPonto_1800" /enable
echo Tarefas habilitadas.

:: Restaurar startup do Registro
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "MonitorBatidaPonto" /t REG_SZ /d "\"C:\Users\paulo.garcia\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe\" \"C:\Users\paulo.garcia\Desktop\Repos\automao-batida-ponto\monitor_batida.py\"" /f
echo Startup do Registro restaurado.

:: Iniciar monitor imediatamente
start "" /B "C:\Users\paulo.garcia\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe" "C:\Users\paulo.garcia\Desktop\Repos\automao-batida-ponto\monitor_batida.py"
echo Monitor iniciado em background.

echo.
echo Automacao ATIVA. Proximo ponto sera batido automaticamente.
pause
