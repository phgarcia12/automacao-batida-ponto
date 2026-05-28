#!/usr/bin/env python3
"""Verifica o Cartao Ponto e salva screenshot"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from datetime import date
import time

USUARIO = "172"
SENHA = "172"
URL_LOGIN = "https://centraldofuncionario.com.br/54128/incluir-ponto"
URL_CARTAO = "https://centraldofuncionario.com.br/54128/cartao-ponto"
log_dir = Path.home() / "AppData" / "Local" / "batida_ponto_logs"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,800")

driver = webdriver.Chrome(options=options)

try:
    print("Fazendo login...")
    driver.get(URL_LOGIN)
    time.sleep(3)

    campo_usuario = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "login-numero-folha"))
    )
    campo_usuario.send_keys(USUARIO)
    time.sleep(0.5)

    driver.find_element(By.ID, "login-senha").send_keys(SENHA)
    time.sleep(0.5)

    driver.find_element(By.XPATH, "//*[@data-testid='login-entrar']").click()
    time.sleep(3)

    print("Acessando Cartao Ponto...")
    driver.get(URL_CARTAO)
    time.sleep(4)

    screenshot = log_dir / "cartao_ponto_verificacao.png"
    driver.save_screenshot(str(screenshot))
    print(f"Screenshot salvo: {screenshot}")

    # Pegar o texto da pagina para analise
    hoje_str = date.today().strftime("%d/%m")
    texto = driver.find_element(By.TAG_NAME, "body").text
    linhas_hoje = [l for l in texto.split('\n') if hoje_str in l]
    print(f"\n=== DADOS DE HOJE ({hoje_str}) ===")
    for linha in linhas_hoje:
        print(linha)

except Exception as e:
    print(f"ERRO: {e}")
    driver.save_screenshot(str(log_dir / "cartao_erro.png"))
finally:
    driver.quit()
