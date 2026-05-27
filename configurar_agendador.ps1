# Script para configurar Windows Task Scheduler
# Execute como Administrador!

$scriptPath = "C:\Users\paulo.garcia\Desktop\Repos\automao-batida-ponto\batida_ponto_local.py"
$pythonExe = "python"

# Verificar se Python está instalado
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado! Instale Python primeiro." -ForegroundColor Red
    exit 1
}

# Verificar se Selenium está instalado
Write-Host "`nVerificando dependências..."
$seleniumCheck = & python -c "import selenium" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Selenium não instalado. Instalando..." -ForegroundColor Yellow
    & pip install selenium -q
    Write-Host "✅ Selenium instalado" -ForegroundColor Green
}

# ChromeDriver - verificar se precisa
Write-Host "`nVerificando ChromeDriver..."
$chromedriverCheck = & python -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Instalando webdriver-manager..." -ForegroundColor Yellow
    & pip install webdriver-manager -q
    & python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()" 2>&1
    Write-Host "✅ ChromeDriver configurado" -ForegroundColor Green
}

Write-Host "`n"
Write-Host "🔧 Configurando tarefas agendadas..." -ForegroundColor Cyan
Write-Host "=" * 60

# Função para criar tarefa
function CreateTask($taskName, $horaMinuto, $descricao) {
    $hora, $minuto = $horaMinuto.Split(':')

    Write-Host "`n📅 Criando: $descricao ($horaMinuto)" -ForegroundColor Cyan

    # Remover tarefa anterior se existir
    $taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($taskExists) {
        Write-Host "⏸️  Removendo tarefa anterior..."
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false | Out-Null
    }

    # Criar ação
    $action = New-ScheduledTaskAction `
        -Execute $pythonExe `
        -Argument "`"$scriptPath`"" `
        -WorkingDirectory "C:\Users\paulo.garcia\Desktop\Repos\automao-batida-ponto"

    # Criar gatilho (segunda a sexta)
    $trigger = New-ScheduledTaskTrigger `
        -Weekly `
        -WeeksInterval 1 `
        -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday `
        -At "$horaMinuto"

    # Criar configurações
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable

    # Registrar tarefa
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description $descricao `
        -Force | Out-Null

    Write-Host "✅ Tarefa criada: $taskName" -ForegroundColor Green
}

# Criar as 4 tarefas
CreateTask "BatidaPonto_0825" "08:25" "Entrada - Batida às 08:25"
CreateTask "BatidaPonto_1200" "12:00" "Saída Manhã - Batida às 12:00"
CreateTask "BatidaPonto_1325" "13:25" "Entrada Tarde - Batida às 13:25"
CreateTask "BatidaPonto_1800" "18:00" "Saída - Batida às 18:00"

Write-Host "`n"
Write-Host "=" * 60
Write-Host "✅ CONFIGURAÇÃO COMPLETA!" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n📋 Tarefas Criadas:`n" -ForegroundColor Cyan
Get-ScheduledTask -TaskName "BatidaPonto_*" | Select-Object TaskName, @{N='Próx. Execução';E={$_.Triggers[0].StartBoundary}} | Format-Table

Write-Host "`n📝 Logs:`n" -ForegroundColor Cyan
Write-Host "   Localização: $env:LOCALAPPDATA\batida_ponto_logs\" -ForegroundColor Yellow
Write-Host "`n✨ A batida de ponto será executada automaticamente nos horários acima!" -ForegroundColor Green
Write-Host "💡 Dica: Seu PC não precisa estar ligado se estiver em Sleep/Hibernate" -ForegroundColor Yellow
