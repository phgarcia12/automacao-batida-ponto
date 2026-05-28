@echo off
echo Suspendendo automacao de batida de ponto...

:: Parar monitor
taskkill /IM pythonw.exe /F >nul 2>&1
echo Monitor encerrado.

:: Desabilitar tarefas
schtasks /change /tn "BatidaPonto_0825" /disable
schtasks /change /tn "BatidaPonto_1200" /disable
schtasks /change /tn "BatidaPonto_1325" /disable
schtasks /change /tn "BatidaPonto_1800" /disable
echo Tarefas desabilitadas.

:: Remover startup do Registro
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "MonitorBatidaPonto" /f >nul 2>&1
echo Startup do Registro removido.

echo.
echo Automacao SUSPENSA. Execute reativar.bat para retomar.
pause
