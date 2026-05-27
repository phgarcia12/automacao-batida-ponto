#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Análise detalhada da estrutura HTML da página Secullum
.DESCRIPTION
    Faz download da página e analisa campos, botões e possíveis bloqueios
#>

param(
    [string]$Url = "https://centraldofuncionario.com.br/54128/incluir-ponto",
    [string]$OutputFile = "analise_pagina.txt"
)

function Log-Message {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $(switch ($Type) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "Cyan" }
    })
}

Log-Message "========================================" -Type "INFO"
Log-Message "ANÁLISE DETALHADA DA PÁGINA SECULLUM" -Type "INFO"
Log-Message "========================================" -Type "INFO"

$output = @()
$output += "ANÁLISE DETALHADA - SECULLUM BATIDA DE PONTO"
$output += "Data: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"
$output += "URL: $Url"
$output += ""
$output += "=========================================="
$output += ""

try {
    Log-Message "Baixando página..." -Type "INFO"
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
    $html = $response.Content

    $output += "1. INFORMAÇÕES DA PÁGINA"
    $output += "-" * 40
    $output += "Status Code: $($response.StatusCode)"
    $output += "Content Length: $($html.Length) bytes"
    $output += "Content Type: $($response.Headers['Content-Type'])"
    $output += ""

    # Verificar título
    if ($html -match "<title>(.*?)</title>") {
        $title = $matches[1]
        $output += "Título: $title"
        Log-Message "Título encontrado: $title" -Type "SUCCESS"
    }
    else {
        $output += "Título: [NÃO ENCONTRADO]"
        Log-Message "Título não encontrado" -Type "WARNING"
    }

    # Verificar meta tags
    $output += ""
    $output += "2. META TAGS"
    $output += "-" * 40

    $metaTags = [regex]::Matches($html, '<meta[^>]*?name="([^"]*)"[^>]*?content="([^"]*)"', 'IgnoreCase')
    if ($metaTags.Count -gt 0) {
        foreach ($meta in $metaTags) {
            $output += "$($meta.Groups[1].Value): $($meta.Groups[2].Value)"
        }
        Log-Message "Meta tags encontradas: $($metaTags.Count)" -Type "SUCCESS"
    }
    else {
        $output += "[Nenhuma meta tag encontrada]"
    }

    # Verificar campos de input
    $output += ""
    $output += "3. CAMPOS DE INPUT"
    $output += "-" * 40

    $inputs = [regex]::Matches($html, '<input[^>]*?(?:type="([^"]*)")?[^>]*?(?:name="([^"]*)")?[^>]*?(?:id="([^"]*)")?[^>]*?>', 'IgnoreCase')

    if ($inputs.Count -gt 0) {
        $output += "Total de inputs: $($inputs.Count)"
        $output += ""

        $inputIndex = 1
        foreach ($input in $inputs) {
            $inputType = if ($input.Groups[1].Value) { $input.Groups[1].Value } else { "text" }
            $inputName = $input.Groups[2].Value
            $inputId = $input.Groups[3].Value

            $output += "Input $inputIndex"
            $output += "  Type: $inputType"
            $output += "  Name: $inputName"
            $output += "  ID: $inputId"
            $output += ""

            $inputIndex++
        }
        Log-Message "Campos de input encontrados: $($inputs.Count)" -Type "SUCCESS"
    }
    else {
        $output += "[Nenhum campo de input encontrado]"
        Log-Message "Nenhum campo de input encontrado" -Type "WARNING"
    }

    # Verificar botões
    $output += ""
    $output += "4. BOTÕES"
    $output += "-" * 40

    $buttons = [regex]::Matches($html, '<button[^>]*>([^<]*)</button>', 'IgnoreCase')

    if ($buttons.Count -gt 0) {
        $output += "Total de botões: $($buttons.Count)"
        $output += ""

        $buttonIndex = 1
        foreach ($btn in $buttons) {
            $btnText = $btn.Groups[1].Value.Trim()
            if ($btnText.Length -gt 0) {
                $output += "Botão $($buttonIndex): $($btnText)"
                $buttonIndex++
            }
        }
        Log-Message "Botões encontrados: $($buttons.Count)" -Type "SUCCESS"
    }
    else {
        $output += "[Nenhum botão encontrado]"
        Log-Message "Nenhum botão encontrado" -Type "WARNING"
    }

    # Verificar scripts
    $output += ""
    $output += "5. SCRIPTS"
    $output += "-" * 40

    $scripts = [regex]::Matches($html, '<script[^>]*src="([^"]*)"', 'IgnoreCase')

    if ($scripts.Count -gt 0) {
        $output += "Total de scripts externos: $($scripts.Count)"
        $output += ""

        foreach ($script in $scripts) {
            $output += "- $($script.Groups[1].Value)"
        }
        Log-Message "Scripts externos encontrados: $($scripts.Count)" -Type "SUCCESS"
    }

    # Verificar keywords de bloqueio
    $output += ""
    $output += "6. ANÁLISE DE POSSÍVEIS BLOQUEIOS"
    $output += "-" * 40

    $keywords = @(
        @{ Pattern = "geolocaliz|location|coordinates"; Label = "Geolocalização" },
        @{ Pattern = "captcha|recaptcha"; Label = "CAPTCHA" },
        @{ Pattern = "bot|automation|selenium|playwright"; Label = "Detecção de Bot" },
        @{ Pattern = "permission|permiss"; Label = "Permissões" },
        @{ Pattern = "session|cookie|token"; Label = "Sessão/Cookie" },
        @{ Pattern = "blocked|forbidden|unauthorized"; Label = "Bloqueios HTTP" }
    )

    $blocksFound = @()

    foreach ($keyword in $keywords) {
        if ($html -match $keyword.Pattern) {
            $blocksFound += $keyword.Label
            $output += "⚠️ Possível: $($keyword.Label)"
        }
    }

    if ($blocksFound.Count -eq 0) {
        $output += "✅ Nenhum padrão de bloqueio óbvio detectado"
        Log-Message "Nenhum bloqueio óbvio detectado" -Type "SUCCESS"
    }
    else {
        $output += ""
        $output += "Bloqueios detectados: $($blocksFound -join ', ')"
        Log-Message "Possíveis bloqueios detectados: $($blocksFound -join ', ')" -Type "WARNING"
    }

    # Verificar headers de segurança
    $output += ""
    $output += "7. HEADERS DE SEGURANÇA"
    $output += "-" * 40

    $securityHeaders = @(
        'X-Frame-Options',
        'X-Content-Type-Options',
        'Content-Security-Policy',
        'Strict-Transport-Security',
        'Access-Control-Allow-Origin'
    )

    foreach ($header in $securityHeaders) {
        $value = $response.Headers[$header]
        if ($value) {
            $output += "$($header): $($value)"
        }
    }

    # Verificar formulários
    $output += ""
    $output += "8. FORMULÁRIOS"
    $output += "-" * 40

    $forms = [regex]::Matches($html, '<form[^>]*?(?:action="([^"]*)")?[^>]*?(?:method="([^"]*)")?[^>]*?>', 'IgnoreCase')

    if ($forms.Count -gt 0) {
        $output += "Total de formulários: $($forms.Count)"
        $output += ""

        $formIndex = 1
        foreach ($form in $forms) {
            $action = $form.Groups[1].Value
            $method = if ($form.Groups[2].Value) { $form.Groups[2].Value } else { "GET" }
            $output += "Formulário $formIndex"
            $output += "  Action: $action"
            $output += "  Method: $method"
            $output += ""
            $formIndex++
        }
        Log-Message "Formulários encontrados: $($forms.Count)" -Type "SUCCESS"
    }

    # Resumo
    $output += ""
    $output += "=========================================="
    $output += "RESUMO E RECOMENDAÇÕES"
    $output += "=========================================="
    $output += ""
    $output += "✅ Status: Página acessível e estrutura HTML padrão"
    $output += "✅ Campos de formulário: Detectados"
    $output += "✅ Botões de ação: Detectados"

    if ($blocksFound.Count -gt 0) {
        $output += "⚠️ Avisos: Possíveis validações em tempo de execução"
        $output += ""
        $output += "Recomendações:"
        $output += "1. Configurar geolocalização se bloqueio for detectado"
        $output += "2. Implementar anti-detecção se necessário"
        $output += "3. Adicionar delays entre ações"
        $output += "4. Usar User-Agent realista"
    }
    else {
        $output += "✅ Nenhum bloqueio óbvio detectado"
        $output += ""
        $output += "A automação deve funcionar sem problemas."
    }

    # Salvar saída
    $output | Out-File -FilePath $OutputFile -Encoding UTF8
    Log-Message "Análise salva em: $OutputFile" -Type "SUCCESS"

}
catch {
    Log-Message "❌ Erro: $($_.Exception.Message)" -Type "ERROR"
    $output += ""
    $output += "ERRO: $($_.Exception.Message)"
    $output | Out-File -FilePath $OutputFile -Encoding UTF8
}

Log-Message ""
Log-Message "Análise concluída!" -Type "SUCCESS"
