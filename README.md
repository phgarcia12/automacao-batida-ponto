# Automação de Batida de Ponto - Secullum

Automação para teste do sistema Secullum de batida de ponto, com suporte a múltiplas tecnologias.

## Testes Realizados (26/05/2026)

### Resultados:
- ✅ **Acessibilidade da URL**: Sistema respondendo normalmente (Status 200)
- ✅ **Conectividade de Rede**: Conexão estabelecida com sucesso
- ⚠️ **Geolocalização**: Nenhum bloqueio óbvio detectado, mas pode haver validação em runtime
- ✅ **Estrutura HTML**: DOM padrão com campos de formulário detectáveis

### Conclusão Geral
O sistema está **acessível e a automação é tecnicamente viável**. Possível validação de geolocalização em tempo de execução.

---

## Estrutura do Projeto

```
├── batida_ponto.js                 # Playwright (Node.js)
├── batida_ponto.py                 # Selenium (Python)
├── batida_ponto_playwright.py       # Playwright (Python)
├── teste_automation.ps1             # PowerShell
├── package.json                     # Dependências Node.js
├── requirements.txt                 # Dependências Python
├── relatorio_teste.html             # Relatório em HTML
└── README.md                        # Este arquivo
```

---

## Instalação

### Opção 1: Node.js + Playwright

```bash
npm install
```

### Opção 2: Python + Selenium

```bash
pip install -r requirements.txt
python -m pip install selenium
python -m pip install playwright
playwright install chromium
```

### Opção 3: PowerShell (sem dependências adicionais)

Apenas verifique conectividade:

```powershell
.\teste_automation.ps1
```

---

## Execução

### Usando Node.js/Playwright

```bash
node batida_ponto.js
```

**Saída esperada:**
```
[17:38:31] Iniciando teste de automação - Secullum Batida de Ponto
[17:38:31] Página carregada com sucesso
[17:38:31] Campo de usuário encontrado
[17:38:31] Botão de login encontrado
[17:38:31] ✅ PONTO BATIDO COM SUCESSO!
```

### Usando Python/Selenium

```bash
python batida_ponto.py
```

### Usando Python/Playwright

```bash
python batida_ponto_playwright.py
```

### Usando PowerShell

```powershell
.\teste_automation.ps1 -Usuario "172" -Senha "172"
```

---

## Configuração de Credenciais

### Via Variáveis de Ambiente

**Windows (PowerShell):**
```powershell
$env:BATIDA_USUARIO = "172"
$env:BATIDA_SENHA = "172"
```

**Windows (CMD):**
```cmd
set BATIDA_USUARIO=172
set BATIDA_SENHA=172
```

**Linux/Mac:**
```bash
export BATIDA_USUARIO=172
export BATIDA_SENHA=172
```

### Via Arquivo .env

Crie um arquivo `.env` na raiz do projeto:
```
BATIDA_USUARIO=172
BATIDA_SENHA=172
```

---

## Possíveis Bloqueios

### 🌍 Geolocalização
O sistema pode validar a localização do cliente.

**Solução:**
- Conceder permissão de geolocalização no navegador
- Usar Playwright com geolocalização configurada
- Usar VPN para simular localização

**Exemplo com Playwright:**
```javascript
const context = await browser.newContext({
  geolocation: { latitude: -23.5505, longitude: -46.6333 }, // São Paulo
  permissions: ['geolocation']
});
```

### 🔒 CAPTCHA
Sistema pode exigir verificação CAPTCHA.

**Solução:**
- Usar serviço de CAPTCHA solving (2Captcha, Anti-Captcha)
- Implementar retry com delay entre tentativas
- Adicionar headers realistas ao navegador

### 🔐 Cookies/Sessão
Sistema pode rejeitar sessões automatizadas.

**Solução:**
- Usar contexto de navegador com cookies persistentes
- Implementar anti-detecção (stealth plugins)
- Usar User-Agent realista

---

## Logs e Diagnóstico

### Ver Logs de Execução

**PowerShell:**
```powershell
.\teste_automation.ps1 -Verbose
```

**Node.js:**
```bash
DEBUG=* node batida_ponto.js
```

**Python:**
```bash
python -u batida_ponto.py  # -u para unbuffered output
```

---

## Agendamento Automático

### Windows - Agendador de Tarefas

```powershell
# Criar tarefa que executa diariamente às 8:00
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
$action = New-ScheduledTaskAction -Execute "node" -Argument "batida_ponto.js" -WorkingDirectory "C:\Repos\automao-batida-ponto"
Register-ScheduledTask -TaskName "Batida Ponto Secullum" -Trigger $trigger -Action $action
```

### Linux/Mac - Cron

```bash
# Adicionar ao crontab para executar diariamente às 8:00
0 8 * * * cd /home/user/automao-batida-ponto && node batida_ponto.js
```

---

## Estrutura de Resposta

### Sucesso (Exit Code 0)
```
[HH:MM:SS] ✅✅✅ PONTO BATIDO COM SUCESSO! ✅✅✅
```

### Erro (Exit Code 1)
```
[HH:MM:SS] ❌ Erro: [Descrição do erro]
```

### Aviso (Exit Code 2)
```
[HH:MM:SS] ⚠️ [Descrição do aviso]
```

---

## Troubleshooting

### "Chrome/Chromium não encontrado"
```bash
# Instalar navegadores Playwright
npx playwright install
```

### "Timeout ao carregar página"
- Aumentar timeout nos scripts (padrão: 15s)
- Verificar conexão de internet
- Tentar com VPN se houver restrição geográfica

### "Campo de login não encontrado"
- Verificar nome do campo (`name="login"`)
- Inspecionar página com DevTools
- Verificar se página carregou completamente

### "Botão Incluir Ponto não encontrado"
- Pode não estar logado corretamente
- Credenciais inválidas
- Página bloqueada por geolocalização

---

## Requisitos Mínimos

| Tecnologia | Versão |
|-----------|--------|
| Node.js | 14+ |
| npm | 6+ |
| Python | 3.7+ |
| PowerShell | 5.1+ |

---

## Dependências

### Node.js
- `playwright@^1.40.0`

### Python
- `selenium>=4.0.0`
- `playwright>=1.40.0`

---

## Documentação

- [Playwright Docs](https://playwright.dev)
- [Selenium Docs](https://www.selenium.dev)
- [Relatório de Testes](relatorio_teste.html)

---

## Contato e Suporte

Para problemas ou dúvidas, verifique:
1. Este README
2. [Relatório HTML](relatorio_teste.html)
3. Logs de execução do script

---

**Última atualização:** 26/05/2026
**Status:** ✅ Sistema operacional e acessível
