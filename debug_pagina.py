#!/usr/bin/env python3
"""Debug da página de login"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

URL = "https://centraldofuncionario.com.br/54128/incluir-ponto"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

try:
    print("Acessando página...")
    driver.get(URL)
    time.sleep(3)

    # Procurar todos os botões
    print("\n=== BOTÕES ENCONTRADOS ===")
    botoes = driver.find_elements(By.TAG_NAME, "button")
    print(f"Total de botões: {len(botoes)}")
    for i, botao in enumerate(botoes):
        print(f"  {i}: {botao.text}")
        print(f"     tag: {botao.tag_name}")
        print(f"     class: {botao.get_attribute('class')}")
        print()

    # Procurar inputs
    print("\n=== INPUTS ENCONTRADOS ===")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"Total de inputs: {len(inputs)}")
    for i, inp in enumerate(inputs):
        print(f"  {i}: placeholder='{inp.get_attribute('placeholder')}' type='{inp.get_attribute('type')}'")
        print()

    # Salvar HTML para análise
    print("\n=== SALVANDO HTML ===")
    html = driver.page_source
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML salvo em: debug_page.html")

finally:
    driver.quit()
