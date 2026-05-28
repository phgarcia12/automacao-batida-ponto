#!/usr/bin/env python3
"""
Monitor de Batida de Ponto - Gsurf
Processo de backup que roda em background.
As tarefas primarias estao no Task Scheduler (BatidaPonto_HHMM).
Este monitor garante execucao caso o Task Scheduler nao dispare.
Verifica arquivo .marker para nao duplicar com o Task Scheduler.
"""

import subprocess
import logging
import time
from datetime import datetime, date
from pathlib import Path

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

HORARIOS = ["08:25", "12:00", "13:25", "18:00"]
TOLERANCIA_MINUTOS = 10
SCRIPT_PATH = Path(__file__).parent / "batida_ponto_local.py"
PYTHON_PATH = Path(__file__).parent.parent.parent / "AppData" / "Local" / "Python" / "pythoncore-3.14-64" / "python.exe"

# Fallback para python no PATH caso o path absoluto nao exista
if not PYTHON_PATH.exists():
    PYTHON_PATH = "python"


def marker_path(horario):
    hoje = date.today().isoformat()
    return log_dir / f"executado_{hoje}_{horario.replace(':', '')}.marker"


def ja_executou_hoje(horario, historico):
    """Verifica historico em memoria E arquivo marker (gravado pelo Task Scheduler)."""
    hoje = date.today().isoformat()
    chave = f"{hoje}_{horario}"
    if historico.get(chave, False):
        return True
    # Verificar se o Task Scheduler ja executou
    if marker_path(horario).exists():
        historico[chave] = True  # Sincronizar historico
        logger.info(f"Marker encontrado para {horario} — ja executado pelo Task Scheduler")
        return True
    return False


def marcar_executado(horario, historico):
    """Marca horario como executado (historico em memoria)."""
    hoje = date.today().isoformat()
    historico[f"{hoje}_{horario}"] = True
    # Limpar entradas de dias anteriores
    for chave in list(historico.keys()):
        if chave.split("_")[0] < hoje:
            del historico[chave]


def deve_executar_agora(horario):
    """
    Retorna True se estiver dentro da janela de tolerancia.
    Ex: 08:25, tolerancia=10 -> executa entre 08:25 e 08:35.
    """
    agora = datetime.now()
    h, m = map(int, horario.split(":"))
    minutos_alvo = h * 60 + m
    minutos_agora = agora.hour * 60 + agora.minute
    diferenca = minutos_agora - minutos_alvo
    return 0 <= diferenca <= TOLERANCIA_MINUTOS


def executar_batida():
    """Executa o script de batida de ponto e retorna True se CONFIRMADO."""
    try:
        python = str(PYTHON_PATH)
        resultado = subprocess.run(
            [python, str(SCRIPT_PATH)],
            cwd=str(SCRIPT_PATH.parent),
            capture_output=True,
            timeout=120
        )
        # O script retorna 0 apenas se CONFIRMADO pelo sistema
        if resultado.returncode == 0:
            logger.info("SUCESSO: batida confirmada pelo sistema")
            return True
        else:
            stderr = resultado.stderr.decode(errors='replace')[:300]
            logger.error(f"Script retornou erro (code {resultado.returncode}): {stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("TIMEOUT: script demorou mais de 120s")
        return False
    except Exception as e:
        logger.error(f"Erro ao executar script: {e}")
        return False


def main():
    logger.info("=" * 60)
    logger.info("MONITOR DE BATIDA INICIADO (backup do Task Scheduler)")
    logger.info(f"Horarios: {HORARIOS}")
    logger.info(f"Tolerancia: {TOLERANCIA_MINUTOS} minutos")
    logger.info("=" * 60)

    historico = {}

    while True:
        try:
            agora = datetime.now()

            # Pular fins de semana
            if agora.weekday() >= 5:
                time.sleep(60)
                continue

            for horario in HORARIOS:
                if deve_executar_agora(horario) and not ja_executou_hoje(horario, historico):
                    logger.info(f"Horario {horario} atingido — executando batida...")
                    sucesso = executar_batida()
                    if sucesso:
                        marcar_executado(horario, historico)
                        logger.info(f"Horario {horario} concluido com sucesso")
                    else:
                        logger.warning(f"Horario {horario} falhou — nova tentativa em 2 min")
                        time.sleep(120)

            time.sleep(30)

        except Exception as e:
            logger.error(f"Erro no loop: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
