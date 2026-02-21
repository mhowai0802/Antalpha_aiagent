#!/usr/bin/env node
/**
 * Captures the "Proposed Enhancement: AI Translation + MCP I/O" section
 * from the Architecture page and saves it as JPG in the project root.
 */
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Script lives in frontend/; output goes to project root
const rootDir = path.resolve(__dirname, '..');
const outputPath = path.join(rootDir, 'Proposed_Enhancement_MCP_IO.jpg');

// Increase timeout for Mermaid diagram rendering
const RENDER_WAIT_MS = 3500;

async function capture() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1200, height: 1400 } });

  try {
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle', timeout: 15000 });
    // Click "How It Works" to navigate to Architecture page
    await page.click('button:has-text("How It Works")');
    await page.waitForSelector('.arch-section--proposed', { timeout: 10000 });
    // Wait for Mermaid diagrams to render
    await page.waitForTimeout(RENDER_WAIT_MS);
    const section = await page.locator('.arch-section--proposed');
    await section.screenshot({ path: outputPath, type: 'jpeg', quality: 90 });
    console.log('Saved:', outputPath);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

capture();
