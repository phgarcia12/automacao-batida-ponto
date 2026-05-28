#!/usr/bin/env python3
"""
Monitor de Batida de Ponto - Gsurf
Fica rodando em background e executa a batida nos horarios corretos.
Inicia automaticamente com o Windows.
"""

import subprocess
import logging
import time
from datetime import datetime, date
from pathlib import Path

# Configurar logging
log_dir = Path.home() / "AppData" / "Local" / "batida_ponto_logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "monitor_batida.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

# Horarios de batida
HORARIOS = ["08:25", "12:00", "13:25", "18:00"]

# Janela de tolerancia: so executa se estiver dentro de X minutos do horario
TOLERANCIA_MINUTOS = 10

SCRIPT_PATH = Path(__file__).parent / "batida_ponto_local.py"

def ja_executou_hoje(horario, historico):
    """Verifica se ja executou este horario hoje"""
    hoje = date.today().isoformat()
    return historico.get(f"{hoje}_{horario}", False)

def marcar_executado(horario, historico):
    """Marca horario como executado hoje"""
    hoje = date.today().isoformat()
    historico[f"{hoje}_{horario}"] = True
    # Limpar entradas antigas (manter so ultimos 2 dias)
    chaves = list(historico.keys())
    for chave in chaves:
        data_chave = chave.split("_")[0]
        if data_chave < hoje:
            del historico[chave]

def deve_executar_agora(horario):
    """
    Retorna True se o horario atual esta dentro da janela de tolerancia
    Ex: horario=08:25, tolerancia=10min => executa entre 08:25 e 08:35
    """
    agora = datetime.now()
    h, m = map(int, horario.split(":"))

    # Minutos desde meia-noite
    minutos_alvo = h * 60 + m
    minutos_agora = agora.hour * 60 + agora.minute

    diferenca = minutos_agora - minutos_alvo
    return 0 <= diferenca <= TOLERANCIA_MINUTOS

def executar_batida():
    """Executa o script de batida de ponto"""
    try:
        resultado = subprocess.run(
            ["python", str(SCRIPT_PATH)],
            cwd=str(SCRIPT_PATH.parent),
            capture_output=True,
            timeout=120
        )
        if resultado.returncode == 0:
            logger.info("SUCESSO: batida executada com sucesso")
            return True
        else:
            logger.error(f"ERRO: {resultado.stderr.decode(errors='replace')[:200]}")
            return False
    except Exception as e:
        logger.error(f"ERRO ao executar: {str(e)}")
        return False

def main():
    logger.info("=" * 60)
    logger.info("MONITOR DE BATIDA INICIADO")
    logger.info(f"Horarios: {HORARIOS}")
    logger.info(f"Tolerancia: {TOLERANCIA_MINUTOS} minutos")
    logger.info("=" * 60)

    historico = {}

    while True:
        try:
            agora = datetime.now()

            # Pular fins de semana
            if agora.weekday() >= 5:  # 5=sabado, 6=domingo
                time.sleep(60)
                continue

            for horario in HORARIOS:
                if deve_executar_agora(horario) and not ja_executou_hoje(horario, historico):
                    logger.info(f"Horario {horario} atingido — iniciando batida...")
                    sucesso = executar_batida()
                    if sucesso:
                        marcar_executado(horario, historico)
                        logger.info(f"Horario {horario} marcado como executado")
                    else:
                        logger.warning(f"Falha no horario {horario} — tentara novamente em 2min")
                        time.sleep(120)

            time.sleep(30)

        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
