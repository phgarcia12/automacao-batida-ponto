# 🕐 Automação de Batida de Ponto - Secullum

Sistema automatizado para bater ponto no Secullum da Gsurf, rodando localmente via Windows Task Scheduler.

## 📋 O que é?

Script Python que acessa automaticamente o sistema Secullum e bate o ponto nos horários:
- **08:25** - Entrada (manhã)
- **12:00** - Saída (manhã)
- **13:25** - Entrada (tarde)
- **18:00** - Saída (tarde)

Executa **de segunda a sexta**, exceto feriados.

## 🚀 Instalação Rápida

### Pré-requisitos
- Windows 10/11
- Python 3.7+
- Google Chrome
- Internet

### Instalação (2 passos)

**1. Abra PowerShell como Administrador**
```powershell
# Windows + X → Terminal do Windows (Admin)
# Ou clique direito no PowerShell
```

**2. Execute o configurador**
```powershell
cd C:\Users\paulo.garcia\Desktop\Repos\automao-batida-ponto
.\configurar_agendador.ps1
```

**Pronto! ✅**

Seu PC agora executa a batida automaticamente nos horários especificados.

## 📁 Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `batida_ponto_local.py` | Script principal de automação |
| `configurar_agendador.ps1` | Configura Windows Task Scheduler |
| `INSTALACAO.txt` | Instruções passo-a-passo |
| `README_INSTALACAO.md` | Este arquivo |

## 🧪 Testar Manualmente

```powershell
cd C:\Users\paulo.garcia\Desktop\Repos\automao-batida-ponto
python batida_ponto_local.py
```

Você verá:
- Navegador abrindo
- Login sendo realizado
- Ponto sendo batido
- Log de execução

## 📊 Monitorar Execuções

Logs salvos em:
```
C:\Users\paulo.garcia\AppData\Local\batida_ponto_logs\
```

## ⚙️ Verificar Tarefas Agendadas

Abra **Task Scheduler**:
1. Windows + R
2. Digite: `taskschd.msc`
3. Procure por `BatidaPonto_*`

## 💡 Dicas

- Seu PC **não precisa estar ligado** (Sleep é ok)
- Logs são criados automaticamente
- Tarefas rodam mesmo em modo Sleep

---

**Status:** ✅ Pronto para instalação
