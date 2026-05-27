#!/usr/bin/env python3
"""Investiga qual elemento 'Incluir Ponto' está sendo clicado"""

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
options.add_argument("--window-size=1280,900")

driver = webdriver.Chrome(options=options)

try:
    # Login
    driver.get(URL)
    time.sleep(3)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login-numero-folha"))).send_keys(USUARIO)
    driver.find_element(By.ID, "login-senha").send_keys(SENHA)
    driver.find_element(By.XPATH, "//*[@data-testid='login-entrar']").click()
    time.sleep(3)
    driver.get(URL)
    time.sleep(4)

    # Listar TODOS os elementos que contêm "Incluir Ponto"
    print("=== TODOS OS ELEMENTOS COM 'Incluir Ponto' ===")
    elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'Incluir Ponto')]")
    for i, el in enumerate(elementos):
        print(f"\n[{i}] Tag: {el.tag_name}")
        print(f"    Texto: '{el.text}'")
        print(f"    data-testid: '{el.get_attribute('data-testid')}'")
        print(f"    class: '{el.get_attribute('class')[:80]}'")
        print(f"    Localização: x={el.location['x']}, y={el.location['y']}")
        print(f"    Tamanho: {el.size}")

    # Salvar HTML da página logada
    with open("debug_page_logada.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("\nHTML salvo em debug_page_logada.html")

except Exception as e:
    print(f"ERRO: {type(e).__name__}: {str(e)[:200]}")
finally:
    driver.quit()
