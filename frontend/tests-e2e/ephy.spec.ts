import { test, expect } from '@playwright/test';

test('E-Phy search page loads', async ({ page }) => {
  await page.goto('/ephy');
  await expect(page.getByRole('heading', { name: 'Recherche Produits Phyto (E-Phy)' })).toBeVisible();
  await expect(page.getByPlaceholder('Rechercher un produit (AMM ou nom)')).toBeVisible();
});
