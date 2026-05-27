#!/usr/bin/env python3
"""
Script de automação de batida de ponto - Secullum
Versão Playwright (headless)
Acessa o sistema, faz login e clica em "Incluir Ponto"
"""

import os
import sys
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Credenciais
USUARIO = os.getenv('BATIDA_USUARIO', '172')
SENHA = os.getenv('BATIDA_SENHA', '172')
URL = 'https://centraldofuncionario.com.br/54128/incluir-ponto'

def log(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

async def testar_batida_ponto():
    """Testa automação de batida de ponto com Playwright"""

    log("=" * 70)
    log("Iniciando teste de automação - Secullum Batida de Ponto")
    log(f"URL: {URL}")
    log("=" * 70)

    async with async_playwright() as p:
        # Usar Chrome/Chromium em modo headless
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

        page = None
        try:
            # Criar contexto sem geolocalização para evitar bloqueios iniciais
            context = await browser.new_context(
                geolocation=None,
                permissions=[]
            )
            page = await context.new_page()

            # Tentar acessar a URL
            log("Acessando URL...")
            try:
                await page.goto(URL, wait_until='networkidle', timeout=15000)
                log("✅ Página carregada com sucesso")
            except PlaywrightTimeoutError:
                log("⚠️ Timeout ao carregar página (15s) - continuando...")

            # Capturar título da página
            title = await page.title()
            log(f"Título da página: {title}")

            # Verificar conteúdo da página
            content = await page.content()

            # Procurar por campos de login
            try:
                log("Procurando campo de usuário...")
                usuario_field = await page.query_selector('input[name="login"]')

                if not usuario_field:
                    usuario_field = await page.query_selector('input[type="text"]')

                if usuario_field:
                    log("✅ Campo de usuário encontrado")
                    await usuario_field.fill(USUARIO)
                    log(f"Usuário '{USUARIO}' preenchido")
                else:
                    log("❌ Campo de usuário não encontrado")
                    log("Campos de input disponíveis:")
                    inputs = await page.query_selector_all('input')
                    for i, inp in enumerate(inputs):
                        input_type = await inp.get_attribute('type')
                        input_name = await inp.get_attribute('name')
                        input_id = await inp.get_attribute('id')
                        log(f"  Input {i}: type={input_type}, name={input_name}, id={input_id}")

            except Exception as e:
                log(f"❌ Erro ao preencher usuário: {e}")

            # Procurar campo de senha
            try:
                log("Procurando campo de senha...")
                senha_field = await page.query_selector('input[name="password"]')

                if not senha_field:
                    senha_field = await page.query_selector('input[type="password"]')

                if senha_field:
                    log("✅ Campo de senha encontrado")
                    await senha_field.fill(SENHA)
                    log("Senha preenchida")
                else:
                    log("❌ Campo de senha não encontrado")

            except Exception as e:
                log(f"❌ Erro ao preencher senha: {e}")

            # Procurar botão de login/entrar
            try:
                log("Procurando botão de login...")
                login_button = await page.query_selector('button:has-text("Entrar")')

                if not login_button:
                    login_button = await page.query_selector('button:has-text("Login")')

                if not login_button:
                    login_button = await page.query_selector('button[type="submit"]')

                if login_button:
                    log("✅ Botão de login encontrado")
                    await login_button.click()
                    log("Botão de login clicado")

                    # Aguardar redirecionamento
                    try:
                        await page.wait_for_load_state('networkidle', timeout=10000)
                        log("✅ Página carregada após login")
                    except:
                        log("⚠️ Timeout ao aguardar carregamento")
                else:
                    log("❌ Botão de login não encontrado")
                    log("Botões disponíveis:")
                    buttons = await page.query_selector_all('button')
                    for i, btn in enumerate(buttons):
                        text = await btn.text_content()
                        log(f"  Botão {i}: {text.strip()}")

            except Exception as e:
                log(f"❌ Erro ao clicar em login: {e}")

            # Procurar botão "Incluir Ponto"
            try:
                log("Procurando botão 'Incluir Ponto'...")
                await page.wait_for_timeout(2000)  # Pequena pausa

                incluir_button = await page.query_selector('button:has-text("Incluir Ponto")')

                if not incluir_button:
                    # Tenta alternativas
                    incluir_button = await page.query_selector('button:has-text("incluir ponto")')

                if not incluir_button:
                    incluir_button = await page.query_selector('[onclick*="ponto"]')

                if incluir_button:
                    log("✅ Botão 'Incluir Ponto' encontrado")
                    await incluir_button.click()
                    log("✅✅✅ PONTO BATIDO COM SUCESSO! ✅✅✅")

                    # Aguardar confirmação
                    try:
                        await page.wait_for_timeout(2000)
                    except:
                        pass

                    return True
                else:
                    log("❌ Botão 'Incluir Ponto' não encontrado")
                    log("Examinando página após login...")
                    page_text = await page.text_content()
                    if "geolocaliz" in page_text.lower():
                        log("⚠️ Possível validação de geolocalização detectada no HTML")
                    if "permiss" in page_text.lower():
                        log("⚠️ Possível requisição de permissão detectada")
                    return False

            except PlaywrightTimeoutError:
                log("⚠️ Timeout ao procurar botão 'Incluir Ponto'")
                return False
            except Exception as e:
                log(f"❌ Erro ao clicar em 'Incluir Ponto': {e}")
                return False

        except Exception as e:
            log(f"❌ Erro geral: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if page:
                await page.close()
            await context.close()
            await browser.close()

async def main():
    """Executar teste"""
    resultado = await testar_batida_ponto()

    log("=" * 70)
    if resultado:
        log("✅ TESTE FINALIZADO COM SUCESSO")
        sys.exit(0)
    else:
        log("❌ TESTE NÃO FOI CONCLUÍDO")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
