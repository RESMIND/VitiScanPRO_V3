import { test, expect, request } from '@playwright/test';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

test('user can complete onboarding wizard', async ({ page, context }) => {
  // Create a test user via API
  const username = `e2e+${Date.now()}@vitiscan.test`;
  const password = 'Test123!@#';
  await request.post(`${API_BASE}/register`, { data: { username, password, language: 'ro', role: 'user', accept_terms: true, accept_privacy: true } });

  // Login to get token
  const loginResp = await request.post(`${API_BASE}/login`, { data: { username, password } });
  const loginJson = await loginResp.json();
  const token = loginJson.access_token;
  expect(token).toBeTruthy();

  // Set token in localStorage and open onboarding page
  await page.goto('/');
  await page.evaluate((t) => localStorage.setItem('jwt_token', t), token);
  await page.goto('/onboarding');

  // Start wizard
  await page.click('text=Start');

  // Phone verification step: send and auto-retrieve code
  await page.fill('input[placeholder="Phone (+40...)"]', '+40700123456');
  await page.click('text=Send code');

  // Dev-only: fetch code from server
  const devResp = await request.get(`${API_BASE}/dev/verification-code?phone=+40700123456`);
  const devJson = await devResp.json();
  const code = devJson.code;

  await page.fill('input[placeholder="Enter code"]', code);
  await page.click('text=Verify');
  await page.click('text=Next');

  // Establishment details
  await page.fill('input[placeholder="Farm name"]', 'E2E Farm');
  await page.fill('input[placeholder="Address"]', 'Test St 1');
  await page.click('text=Next');

  // Upload logo
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.click('input[type="file"]')
  ]);
  await fileChooser.setFiles({ name: 'logo.png', mimeType: 'image/png', buffer: Buffer.from('PNGDATA') });

  // Finish onboarding (submits and uploads)
  await page.click('text=Finish onboarding');

  // Expect success message or final step
  await expect(page.locator('text=All set!')).toBeVisible();
});