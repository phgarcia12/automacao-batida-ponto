#!/usr/bin/env python3
"""Verifica se há modal de confirmação após clicar em Incluir Ponto"""

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

    print("Antes do clique:")
    driver.save_screenshot(str(log_dir / "confirm_1_antes.png"))

    # Clicar no botão azul correto
    botao = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH,
            "//*[contains(text(), 'Incluir Ponto') and not(@data-testid='menu-incluir-ponto')]"
        ))
    )
    print(f"Botão encontrado: tag={botao.tag_name}, x={botao.location['x']}, y={botao.location['y']}")
    botao.click()
    print("Clicado!")

    # Screenshots a cada segundo por 8 segundos
    for i in range(8):
        time.sleep(1)
        driver.save_screenshot(str(log_dir / f"confirm_{i+2}_pos{i+1}s.png"))
        # Checar se há alertas/modais
        try:
            alert = driver.switch_to.alert
            texto_alert = alert.text
            print(f"[{i+1}s] ALERT detectado: {texto_alert}")
            alert.accept()
        except:
            pass
        # Texto da página
        try:
            body_text = driver.execute_script("return document.body.innerText;")
            linhas = [l.strip() for l in body_text.split('\n') if l.strip()][:5]
            print(f"[{i+1}s] Primeiras linhas: {linhas[:3]}")
        except:
            pass

    print("\nScreenshots salvas!")

except Exception as e:
    print(f"ERRO: {type(e).__name__}: {str(e)[:300]}")
    driver.save_screenshot(str(log_dir / "confirm_erro.png"))
finally:
    driver.quit()
