#!/usr/bin/env python3
"""
Monitor de Batida de Ponto - Executa nos horários corretos
Mantém-se rodando em background checando a hora
"""

import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
log_dir = Path.home() / "AppData" / "Local" / "batida_ponto_logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "monitor_batida.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Horários de batida (hora:minuto)
HORARIOS = ["08:25", "12:00", "13:25", "18:00"]

# Script a executar
SCRIPT_PATH = Path(__file__).parent / "batida_ponto_local.py"

# Controlar se já foi executado hoje
executados_hoje = {}

def reset_executados():
    """Reseta o dicionário de execução quando muda o dia"""
    global executados_hoje
    executados_hoje = {h: False for h in HORARIOS}

def deveria_executar(horario_alvo):
    """Verifica se deveria executar em um horário específico"""
    agora = datetime.now()
    hora_atual = agora.strftime("%H:%M")

    # Executa se passou do horário e ainda não foi executado hoje
    if hora_atual >= horario_alvo and not executados_hoje[horario_alvo]:
        # Só executa uma vez por dia para cada horário
        return True

    return False

def executar_batida():
    """Executa o script de batida de ponto"""
    try:
        logger.info(f"Executando batida de ponto...")
        resultado = subprocess.run(
            ["python", str(SCRIPT_PATH)],
            cwd=str(SCRIPT_PATH.parent),
            capture_output=True,
            timeout=120
        )

        if resultado.returncode == 0:
            logger.info("✅ Batida executada com sucesso")
        else:
            logger.error(f"❌ Erro na batida: {resultado.stderr.decode()}")

        return resultado.returncode == 0
    except Exception as e:
        logger.error(f"❌ Erro ao executar batida: {str(e)}")
        return False

def main():
    """Loop principal do monitor"""
    logger.info("╔════════════════════════════════════════════════════════╗")
    logger.info("║  MONITOR DE BATIDA DE PONTO INICIADO                   ║")
    logger.info("╚════════════════════════════════════════════════════════╝")
    logger.info(f"Horários configurados: {HORARIOS}")
    logger.info(f"Script: {SCRIPT_PATH}")
    logger.info("Monitor rodando... (pressione Ctrl+C para parar)")

    reset_executados()
    dia_anterior = datetime.now().date()

    try:
        while True:
            agora = datetime.now()
            dia_atual = agora.date()

            # Resetar execução quando muda o dia
            if dia_atual != dia_anterior:
                logger.info(f"📅 Novo dia detectado ({dia_atual})")
                reset_executados()
                dia_anterior = dia_atual

            # Verificar cada horário
            for horario in HORARIOS:
                if deveria_executar(horario):
                    logger.info(f"⏰ Horário {horario} atingido - Executando...")
                    if executar_batida():
                        executados_hoje[horario] = True
                        logger.info(f"✅ Marcado como executado: {horario}")

            # Checar a cada 30 segundos
            time.sleep(30)

    except KeyboardInterrupt:
        logger.info("\n⏹️  Monitor parado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
    finally:
        logger.info("Monitor finalizado")

if __name__ == "__main__":
    main()
