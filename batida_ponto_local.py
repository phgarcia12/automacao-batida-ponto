#!/usr/bin/env python3
"""
Automação de Batida de Ponto - Secullum
Script local que roda via Windows Task Scheduler
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
log_dir = Path(os.path.expanduser("~")) / "AppData" / "Local" / "batida_ponto_logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"batida_ponto_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    import time
except ImportError:
    logger.error("Selenium não está instalado. Execute: pip install selenium")
    sys.exit(1)

# Configurações
USUARIO = "172"
SENHA = "172"
URL = "https://centraldofuncionario.com.br/54128/incluir-ponto"
TIMEOUT = 30

def bater_ponto():
    """Executa a batida de ponto"""

    logger.info("=" * 60)
    logger.info("INICIANDO BATIDA DE PONTO")
    logger.info("=" * 60)

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modo invisível
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Usar perfil de usuário para manter sessões
    chrome_options.add_argument(f"user-data-dir={os.path.expanduser('~')}/.chrome_batida_ponto")

    driver = None
    try:
        logger.info(f"Abrindo navegador Chrome...")
        driver = webdriver.Chrome(options=chrome_options)

        logger.info(f"Acessando URL: {URL}")
        driver.get(URL)

        time.sleep(2)

        # Tentar encontrar botão "Incluir Ponto" primeiro (já logado)
        try:
            logger.info("Procurando botão 'Incluir Ponto' (já pode estar logado)...")
            botao_incluir = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Incluir Ponto')]"))
            )
            logger.info("✅ Página já está logada!")
        except:
            # Se não encontrou, tentar fazer login
            logger.info("Não encontrou sessão ativa. Fazendo login...")

            try:
                # Encontrar campos de login por ID
                logger.info("Preenchendo credenciais...")
                campo_usuario = WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "login-numero-folha"))
                )
                campo_usuario.clear()
                campo_usuario.send_keys(USUARIO)
                time.sleep(0.5)

                campo_senha = driver.find_element(By.ID, "login-senha")
                campo_senha.clear()
                campo_senha.send_keys(SENHA)
                time.sleep(0.5)

                logger.info("Clicando botão 'Entrar'...")
                # O botão é uma div com data-testid
                botao_login = driver.find_element(By.XPATH, "//*[@data-testid='login-entrar']")
                botao_login.click()

                logger.info("Aguardando carregamento após login...")
                time.sleep(3)

                # Após login, pode ter sido redirecionado para outra página
                # Vamos navegar novamente para a URL de batida de ponto
                logger.info("Navegando para página de batida de ponto...")
                driver.get(URL)
                time.sleep(3)

                # Procurar botão de forma mais flexível
                logger.info("Procurando botão 'Incluir Ponto'...")
                botao_incluir = WebDriverWait(driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Incluir Ponto')]"))
                )
            except Exception as login_error:
                logger.error(f"Erro ao fazer login: {str(login_error)}")
                raise

        time.sleep(1)

        logger.info("Clicando no botão 'Incluir Ponto'...")
        botao_incluir.click()

        # Aguardar resposta/confirmação
        time.sleep(3)

        logger.info("SUCESSO: PONTO BATIDO COM SUCESSO!")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"ERRO NA BATIDA DE PONTO: {str(e)}")
        logger.error(f"Tipo de erro: {type(e).__name__}")

        # Tirar screenshot para debug
        try:
            screenshot_path = log_dir / f"erro_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            driver.save_screenshot(str(screenshot_path))
            logger.error(f"Screenshot salvo em: {screenshot_path}")
        except:
            pass

        logger.info("=" * 60)
        return False

    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Navegador fechado")
            except:
                pass

if __name__ == "__main__":
    try:
        sucesso = bater_ponto()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1)
