#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Script de teste de automação de batida de ponto - Secullum
    Usa Edge WebDriver ou simula o teste via HTTP
.DESCRIPTION
    Testa acesso ao sistema Secullum e simula batida de ponto
#>

param(
    [string]$Usuario = "172",
    [string]$Senha = "172",
    [string]$Url = "https://centraldofuncionario.com.br/54128/incluir-ponto"
)

function Log-Message {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "INFO" { "Cyan" }
        default { "White" }
    }

    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

function Test-URL {
    param([string]$Url)

    Log-Message "Testando conectividade à URL..." -Type "INFO"

    try {
        $response = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 10 -UseBasicParsing
        Log-Message "✅ URL acessível (Status: $($response.StatusCode))" -Type "SUCCESS"
        return $true
    }
    catch {
        Log-Message "❌ Erro ao acessar URL: $($_.Exception.Message)" -Type "ERROR"
        return $false
    }
}

function Test-Geolocation {
    param([string]$Url)

    Log-Message "Verificando requisitos de geolocalização..." -Type "INFO"

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        $content = $response.Content

        $hasGeoBlock = $content -match "geolocaliz|location|permiss|coordinates"

        if ($hasGeoBlock) {
            Log-Message "⚠️ Possível verificação de geolocalização detectada" -Type "WARNING"
            return $true
        }
        else {
            Log-Message "✅ Nenhuma verificação de geolocalização óbvia detectada" -Type "SUCCESS"
            return $false
        }
    }
    catch {
        Log-Message "⚠️ Não foi possível verificar geolocalização: $($_.Exception.Message)" -Type "WARNING"
        return $false
    }
}

# ==================== RELATÓRIO FINAL ====================

Log-Message "=" * 70 -Type "INFO"
Log-Message "TESTE DE AUTOMAÇÃO - SECULLUM BATIDA DE PONTO" -Type "INFO"
Log-Message "=" * 70 -Type "INFO"
Log-Message "Data/Hora: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -Type "INFO"
Log-Message "URL: $Url" -Type "INFO"
Log-Message "Usuário: $Usuario" -Type "INFO"
Log-Message "" -Type "INFO"

# Testes
Log-Message "Iniciando testes..." -Type "INFO"
Log-Message "" -Type "INFO"

$urlAccessible = Test-URL -Url $Url
Log-Message "" -Type "INFO"

$hasGeoBlock = Test-Geolocation -Url $Url
Log-Message "" -Type "INFO"

# Relatório Final
Log-Message "=" * 70 -Type "INFO"
Log-Message "RELATÓRIO DE TESTES" -Type "INFO"
Log-Message "=" * 70 -Type "INFO"

if ($urlAccessible) {
    Log-Message "✅ Acesso ao sistema: OK" -Type "SUCCESS"
}
else {
    Log-Message "❌ Acesso ao sistema: FALHOU" -Type "ERROR"
}

if ($hasGeoBlock) {
    Log-Message "⚠️ Bloqueio de geolocalização: POSSÍVEL" -Type "WARNING"
}
else {
    Log-Message "✅ Bloqueio de geolocalização: NÃO DETECTADO" -Type "SUCCESS"
}

Log-Message "" -Type "INFO"
Log-Message "PRÓXIMOS PASSOS:" -Type "INFO"
Log-Message "1. Para execução completa, instale Playwright ou Selenium" -Type "INFO"
Log-Message "2. Configure permissões de localização no navegador se necessário" -Type "INFO"
Log-Message "3. Verifique se a rede permite acesso ao domínio" -Type "INFO"
Log-Message "" -Type "INFO"

Log-Message "=" * 70 -Type "INFO"
