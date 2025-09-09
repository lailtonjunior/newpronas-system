const { test, expect } = require('@playwright/test');

test.describe('Gerenciamento de Projetos', () => {
    test('deve permitir a criação de um novo projeto', async ({ page }) => {
        // Navega para a página de dashboard
        await page.goto('http://localhost:3000/dashboard');

        // Clica no botão para criar um novo projeto
        await page.click('text=+ Novo Projeto com IA');
        await expect(page).toHaveURL('http://localhost:3000/projects/new');

        // Anexa um arquivo (simulado)
        await page.setInputFiles('input[type="file"]', {
            name: 'projeto.pdf',
            mimeType: 'application/pdf',
            buffer: Buffer.from('simulação de um arquivo pdf'),
        });

        // Clica para analisar e gerar
        await page.click('button:has-text("Analisar e Gerar Rascunho")');

        // Verifica se o resultado da análise é exibido
        await expect(page.locator('text=Resultado da Análise')).toBeVisible();
        await expect(page.locator('text="projeto.pdf"')).toBeVisible();
    });
});