#!/usr/bin/env node

/**
 * Script de automação de batida de ponto - Secullum
 * Usa Playwright para testar login e clique em "Incluir Ponto"
 * Execução: node batida_ponto.js
 */

const { chromium } = require('playwright');
const path = require('path');

// Credenciais
const USUARIO = process.env.BATIDA_USUARIO || '172';
const SENHA = process.env.BATIDA_SENHA || '172';
const URL = 'https://centraldofuncionario.com.br/54128/incluir-ponto';

function log(message) {
  const timestamp = new Date().toLocaleTimeString('pt-BR');
  console.log(`[${timestamp}] ${message}`);
}

async function testarBatidaPonto() {
  log('='.repeat(70));
  log('Iniciando teste de automação - Secullum Batida de Ponto');
  log(`URL: ${URL}`);
  log(`Usuário: ${USUARIO}`);
  log('='.repeat(70));

  let browser;
  let page;

  try {
    // Lançar navegador
    log('Iniciando navegador (Chromium headless)...');
    browser = await chromium.launch({
      headless: true,
      args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
      geolocation: undefined,
      permissions: [],
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });

    page = await context.newPage();

    // Acessar URL
    log('Acessando URL...');
    try {
      await page.goto(URL, { waitUntil: 'networkidle', timeout: 15000 });
      log('✅ Página carregada com sucesso');
    } catch (e) {
      log(`⚠️ Timeout ao carregar (${e.message}) - continuando mesmo assim...`);
    }

    // Log de título e informações
    const title = await page.title();
    log(`Título da página: "${title}"`);

    // Procurar e preencher campo de usuário
    log('Procurando campo de usuário...');
    let usuarioField = await page.$('input[name="login"]');
    if (!usuarioField) {
      usuarioField = await page.$('input[type="text"]');
    }

    if (usuarioField) {
      log('✅ Campo de usuário encontrado');
      await usuarioField.fill(USUARIO);
      log(`Usuário '${USUARIO}' preenchido`);
    } else {
      log('❌ Campo de usuário não encontrado');
      const allInputs = await page.$$('input');
      log(`Total de inputs encontrados: ${allInputs.length}`);
      for (let i = 0; i < allInputs.length; i++) {
        const type = await allInputs[i].getAttribute('type');
        const name = await allInputs[i].getAttribute('name');
        const id = await allInputs[i].getAttribute('id');
        log(`  Input ${i}: type="${type}", name="${name}", id="${id}"`);
      }
    }

    // Procurar e preencher campo de senha
    log('Procurando campo de senha...');
    let senhaField = await page.$('input[name="password"]');
    if (!senhaField) {
      senhaField = await page.$('input[type="password"]');
    }

    if (senhaField) {
      log('✅ Campo de senha encontrado');
      await senhaField.fill(SENHA);
      log('Senha preenchida');
    } else {
      log('❌ Campo de senha não encontrado');
    }

    // Procurar e clicar botão de login
    log('Procurando botão de login...');
    let loginButton = await page.$('button:has-text("Entrar")');
    if (!loginButton) {
      loginButton = await page.$('button:has-text("Login")');
    }
    if (!loginButton) {
      loginButton = await page.$('button[type="submit"]');
    }

    if (loginButton) {
      log('✅ Botão de login encontrado');
      await loginButton.click();
      log('Botão de login clicado');

      // Aguardar redirecionamento
      try {
        await page.waitForLoadState('networkidle', { timeout: 10000 });
        log('✅ Página carregada após login');
      } catch (e) {
        log(`⚠️ Timeout ao aguardar carregamento: ${e.message}`);
      }
    } else {
      log('❌ Botão de login não encontrado');
      const allButtons = await page.$$('button');
      log(`Total de botões encontrados: ${allButtons.length}`);
      for (let i = 0; i < allButtons.length; i++) {
        const text = await allButtons[i].textContent();
        log(`  Botão ${i}: "${text.trim()}"`);
      }
    }

    // Aguardar um pouco antes de procurar botão de incluir ponto
    await page.waitForTimeout(2000);

    // Procurar e clicar botão "Incluir Ponto"
    log('Procurando botão "Incluir Ponto"...');
    let incluirButton = await page.$('button:has-text("Incluir Ponto")');
    if (!incluirButton) {
      incluirButton = await page.$('button:has-text("incluir ponto")');
    }
    if (!incluirButton) {
      incluirButton = await page.$('[onclick*="ponto"]');
    }

    if (incluirButton) {
      log('✅ Botão "Incluir Ponto" encontrado');
      await incluirButton.click();
      log('✅✅✅ PONTO BATIDO COM SUCESSO! ✅✅✅');

      await page.waitForTimeout(2000);
      return true;
    } else {
      log('❌ Botão "Incluir Ponto" não encontrado');

      // Verificar se há bloqueio de geolocalização
      const pageText = await page.textContent('body');
      if (pageText.toLowerCase().includes('geolocaliz')) {
        log('⚠️ Possível validação de geolocalização detectada');
      }
      if (pageText.toLowerCase().includes('permiss')) {
        log('⚠️ Possível requisição de permissão detectada');
      }

      // Listar botões disponíveis
      const allButtons = await page.$$('button');
      log(`Total de botões na página: ${allButtons.length}`);
      for (let i = 0; i < Math.min(10, allButtons.length); i++) {
        const text = await allButtons[i].textContent();
        log(`  Botão ${i}: "${text.trim()}"`);
      }

      return false;
    }

  } catch (error) {
    log(`❌ Erro geral: ${error.message}`);
    console.error(error);
    return false;
  } finally {
    if (page) {
      try {
        await page.close();
      } catch (e) {
        // Ignorar erro ao fechar página
      }
    }
    if (browser) {
      try {
        await browser.close();
      } catch (e) {
        // Ignorar erro ao fechar browser
      }
    }
  }
}

// Executar
(async () => {
  try {
    const resultado = await testarBatidaPonto();

    log('='.repeat(70));
    if (resultado) {
      log('✅ TESTE FINALIZADO COM SUCESSO');
      process.exit(0);
    } else {
      log('❌ TESTE NÃO FOI CONCLUÍDO COM SUCESSO');
      process.exit(1);
    }
  } catch (error) {
    log(`❌ Erro fatal: ${error.message}`);
    console.error(error);
    process.exit(1);
  }
})();
