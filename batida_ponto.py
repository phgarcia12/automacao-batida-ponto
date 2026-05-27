#!/usr/bin/env python3
"""
Script de automação de batida de ponto - Secullum
Executa login e clica no botão "Incluir Ponto"
"""

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Credenciais (pode usar variáveis de ambiente para maior segurança)
USUARIO = os.getenv('BATIDA_USUARIO', '172')
SENHA = os.getenv('BATIDA_SENHA', '172')
URL = 'https://centraldofuncionario.com.br/54128/incluir-ponto'

def bater_ponto():
    """Acessa o sistema e bate o ponto"""

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando batida de ponto...")

    # Configurar opções do Chrome para rodar em background
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Roda sem interface gráfica
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = None
    try:
        # Inicializar o navegador
        driver = webdriver.Chrome(options=options)
        driver.get(URL)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Página carregada")

        # Aguardar e preencher campo de usuário
        campo_usuario = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'login'))
        )
        campo_usuario.send_keys(USUARIO)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Usuário preenchido")

        # Preencher senha
        campo_senha = driver.find_element(By.NAME, 'password')
        campo_senha.send_keys(SENHA)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Senha preenchida")

        # Clicar em login
        botao_login = driver.find_element(By.XPATH, "//button[contains(text(), 'Entrar')]")
        botao_login.click()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Botão de login clicado")

        # Aguardar carregamento da página principal
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Incluir Ponto')]"))
        )
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Página principal carregada")

        # Clicar no botão "Incluir Ponto"
        botao_incluir = driver.find_element(By.XPATH, "//button[contains(text(), 'Incluir Ponto')]")
        botao_incluir.click()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Ponto batido com sucesso!")

        return True

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro: {str(e)}")
        return False

    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    bater_ponto()
