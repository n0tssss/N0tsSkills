#!/usr/bin/env node
/**
 * 牛马报告截图工具
 * 使用 Playwright 将 HTML 报告截图为手机尺寸 PNG
 * 
 * 用法: node screenshot.js <html_path> <output_path>
 */

const { chromium } = require('/Users/wkea/.hermes/hermes-agent/node_modules/playwright');

async function screenshot(htmlPath, outputPath) {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true
  });
  
  const page = await context.newPage();
  await page.goto(`file://${htmlPath}`);
  await page.waitForTimeout(1500); // 等待字体加载
  
  await page.screenshot({ 
    path: outputPath,
    fullPage: true
  });
  
  await browser.close();
  console.log(JSON.stringify({ success: true, path: outputPath }));
}

// 命令行入口
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node screenshot.js <html_path> <output_path>');
  process.exit(1);
}

screenshot(args[0], args[1]).catch(err => {
  console.error(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
