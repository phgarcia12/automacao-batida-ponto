#!/usr/bin/env python3
"""
Automacao de Batida de Ponto - Secullum
Executado pelo Task Scheduler ou pelo monitor de backup.
Grava arquivo .marker ao concluir para evitar dupla execucao.
"""

import os
import sys
import logging
from datetime import datetime, date
from pathlib import Path

# Configurar logging
log_dir = Path(os.path.expanduser("~")) / "AppData" / "Local" / "batida_ponto_logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"batida_ponto_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
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
    from selenium.common.exceptions import (
        TimeoutException,
        ElementClickInterceptedException,
    )
    import time
except ImportError:
    logger.error("Selenium nao instalado. Execute: pip install selenium")
    sys.exit(1)

USUARIO = "172"
SENHA = "172"
URL = "https://centraldofuncionario.com.br/54128/incluir-ponto"
TIMEOUT = 30
HORARIOS = ["08:25", "12:00", "13:25", "18:00"]


# ---------------------------------------------------------------------------
# Deduplicacao: arquivo .marker impede dupla execucao (Task Scheduler + Monitor)
# ---------------------------------------------------------------------------

def _slot_mais_proximo():
    """Retorna o horario agendado mais proximo do momento atual (tolerancia 15 min)."""
    agora = datetime.now()
    minutos_agora = agora.hour * 60 + agora.minute
    for h in HORARIOS:
        hh, mm = map(int, h.split(":"))
        if abs(minutos_agora - (hh * 60 + mm)) <= 15:
            return h
    return None


def marker_path(horario):
    hoje = date.today().isoformat()
    return log_dir / f"executado_{hoje}_{horario.replace(':', '')}.marker"


def ja_foi_executado():
    """Retorna True se este slot ja foi executado hoje (por qualquer processo)."""
    slot = _slot_mais_proximo()
    if slot and marker_path(slot).exists():
        logger.info(f"Slot {slot} ja foi executado hoje (marker encontrado). Abortando.")
        return True
    return False


def marcar_como_executado():
    """Cria o arquivo .marker para o slot atual."""
    slot = _slot_mais_proximo()
    if slot:
        p = marker_path(slot)
        p.touch()
        logger.info(f"Marker criado: {p.name}")


# ---------------------------------------------------------------------------
# Selenium helpers
# ---------------------------------------------------------------------------

def salvar_screenshot(driver, prefixo="debug"):
    try:
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        path = log_dir / f"{prefixo}_{ts}.png"
        driver.save_screenshot(str(path))
        logger.info(f"Screenshot: {path.name}")
    except Exception:
        pass


def aguardar_sem_progressbar(driver, timeout=20):
    """Aguarda o progressbar desaparecer (pagina carregada)."""
    try:
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[role='progressbar']"))
        )
        logger.info("Pagina pronta (sem progressbar)")
    except TimeoutException:
        logger.warning("Progressbar persistiu — continuando mesmo assim")
    time.sleep(0.5)


def fazer_login(driver):
    """Login na pagina. Retorna True se ok."""
    logger.info(f"Acessando {URL}")
    driver.get(URL)
    time.sleep(2)

    # Se ja estiver na pagina com o botao, nao precisa logar
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(), 'Incluir Ponto') and not(@data-testid='menu-incluir-ponto')]"
            ))
        )
        logger.info("Sessao ativa — sem necessidade de login")
        return True
    except TimeoutException:
        pass

    logger.info("Fazendo login...")
    try:
        campo_usuario = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "login-numero-folha"))
        )
        campo_usuario.clear()
        campo_usuario.send_keys(USUARIO)
        time.sleep(0.3)

        campo_senha = driver.find_element(By.ID, "login-senha")
        campo_senha.clear()
        campo_senha.send_keys(SENHA)
        time.sleep(0.3)

        botao_login = driver.find_element(By.XPATH, "//*[@data-testid='login-entrar']")
        botao_login.click()
        logger.info("Login enviado, aguardando redirecionamento...")
        time.sleep(4)

        # Apos login o site redireciona — voltar para a pagina de ponto
        logger.info("Voltando para pagina de incluir ponto...")
        driver.get(URL)
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return False


def clicar_botao_incluir(driver):
    """Clica no botao azul Incluir Ponto. Retorna True se clicou."""
    logger.info("Aguardando botao 'Incluir Ponto'...")
    aguardar_sem_progressbar(driver)

    try:
        botao = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//*[contains(text(), 'Incluir Ponto') and not(@data-testid='menu-incluir-ponto')]"
            ))
        )
        logger.info(f"Botao: tag={botao.tag_name}, pos=({botao.location['x']},{botao.location['y']})")
    except TimeoutException:
        logger.error("Botao 'Incluir Ponto' nao encontrado")
        salvar_screenshot(driver, "erro_botao_nao_encontrado")
        return False

    # Tentativa 1: clique normal
    try:
        botao.click()
        logger.info("Clique normal OK")
        return True
    except ElementClickInterceptedException:
        logger.warning("Clique interceptado — aguardando e tentando novamente")

    # Aguardar progressbar desaparecer e tentar de novo
    time.sleep(2)
    aguardar_sem_progressbar(driver, timeout=15)

    try:
        botao = driver.find_element(By.XPATH,
            "//*[contains(text(), 'Incluir Ponto') and not(@data-testid='menu-incluir-ponto')]"
        )
        botao.click()
        logger.info("Segundo clique OK")
        return True
    except ElementClickInterceptedException:
        pass
    except Exception:
        pass

    # Tentativa final: JavaScript click
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", botao)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", botao)
        logger.info("Clique via JavaScript OK")
        return True
    except Exception as e:
        logger.error(f"JavaScript click falhou: {e}")
        return False


def verificar_confirmacao(driver, timeout=15):
    """
    Aguarda o modal de confirmacao. Retorna True SOMENTE se o sistema
    confirmou 'Inclusao de ponto efetuada com exito'.
    """
    logger.info("Aguardando confirmacao do sistema...")

    textos_sucesso = ["efetuada com", "xito", "instantes"]

    try:
        WebDriverWait(driver, timeout).until(
            lambda d: any(
                t.lower() in d.find_element(By.TAG_NAME, "body").text.lower()
                for t in textos_sucesso + ["Nova Inclus"]
            )
        )
    except TimeoutException:
        logger.warning("Timeout aguardando confirmacao")

    try:
        texto = driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        logger.error("Nao foi possivel ler a pagina apos clique")
        salvar_screenshot(driver, "erro_leitura")
        return False

    texto_l = texto.lower()

    if any(t.lower() in texto_l for t in textos_sucesso):
        logger.info("CONFIRMACAO DO SISTEMA: ponto efetuado com exito!")
        salvar_screenshot(driver, "sucesso_confirmado")
        return True

    # Detectar erros conhecidos
    erros = ["fora do per", "nao permitido", "horario nao", "erro ao"]
    for e in erros:
        if e in texto_l:
            logger.error(f"Sistema retornou erro: '{e}' detectado")
            salvar_screenshot(driver, "erro_sistema")
            return False

    logger.error(f"Estado indefinido. Texto (300c): {texto[:300]}")
    salvar_screenshot(driver, "estado_indefinido")
    return False


# ---------------------------------------------------------------------------
# Fluxo principal
# ---------------------------------------------------------------------------

def bater_ponto():
    logger.info("=" * 60)
    logger.info("INICIANDO BATIDA DE PONTO")
    logger.info("=" * 60)

    # Verificar deduplicacao antes de abrir o browser
    if ja_foi_executado():
        return True  # Ja foi feito por outro processo — nao e erro

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1280,900")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    # SEM user-data-dir: sempre sessao limpa

    driver = None
    try:
        logger.info("Abrindo Chrome headless...")
        driver = webdriver.Chrome(options=chrome_options)

        if not fazer_login(driver):
            raise Exception("Falha no login")

        if not clicar_botao_incluir(driver):
            raise Exception("Falha ao clicar no botao")

        confirmado = verificar_confirmacao(driver)

        if confirmado:
            marcar_como_executado()  # Gravar marker para deduplicacao
            logger.info("SUCESSO: PONTO BATIDO E CONFIRMADO PELO SISTEMA!")
            logger.info("=" * 60)
            return True
        else:
            logger.error("FALHA: sistema NAO confirmou o registro do ponto")
            logger.info("=" * 60)
            return False

    except Exception as e:
        logger.error(f"ERRO: {type(e).__name__}: {str(e)[:200]}")
        if driver:
            salvar_screenshot(driver, "erro_excecao")
        logger.info("=" * 60)
        return False

    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Chrome encerrado")
            except Exception:
                pass


if __name__ == "__main__":
    sucesso = bater_ponto()
    sys.exit(0 if sucesso else 1)
