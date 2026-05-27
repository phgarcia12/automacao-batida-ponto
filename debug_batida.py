#!/usr/bin/env python3
"""Debug completo da batida - captura resposta do sistema"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time

USUARIO = "172"
SENHA = "172"
URL = "https://centraldofuncionario.com.br/54128/incluir-ponto"
log_dir = Path.home() / "AppData" / "Local" / "batida_ponto_logs"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,800")

driver = webdriver.Chrome(options=options)

try:
    print("1. Acessando pagina...")
    driver.get(URL)
    time.sleep(3)
    driver.save_screenshot(str(log_dir / "debug_1_login.png"))

    print("2. Fazendo login...")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login-numero-folha"))).send_keys(USUARIO)
    driver.find_element(By.ID, "login-senha").send_keys(SENHA)
    driver.find_element(By.XPATH, "//*[@data-testid='login-entrar']").click()
    time.sleep(3)

    print("3. Navegando para incluir-ponto...")
    driver.get(URL)
    time.sleep(4)
    driver.save_screenshot(str(log_dir / "debug_2_antes_clique.png"))
    print(f"   URL atual: {driver.current_url}")

    print("4. Clicando em Incluir Ponto...")
    botao = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Incluir Ponto')]"))
    )
    botao.click()
    print("   Botao clicado!")

    # Aguardar resposta do sistema
    time.sleep(5)
    driver.save_screenshot(str(log_dir / "debug_3_apos_clique.png"))
    print(f"   URL apos clique: {driver.current_url}")

    # Pegar texto da pagina para ver resposta
    texto = driver.find_element(By.TAG_NAME, "body").text
    print("\n=== TEXTO DA PAGINA APOS CLIQUE ===")
    for linha in texto.split('\n')[:30]:
        if linha.strip():
            print(f"  {linha}")

    # Aguardar mais e tirar screenshot final
    time.sleep(3)
    driver.save_screenshot(str(log_dir / "debug_4_final.png"))

except Exception as e:
    print(f"ERRO: {type(e).__name__}: {e}")
    driver.save_screenshot(str(log_dir / "debug_erro.png"))
finally:
    driver.quit()
    print("\nScreenshots salvas em:", log_dir)
