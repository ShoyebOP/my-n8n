const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// --- Main function to render HTML with MathJax to PDF ---
async function renderHtmlWithMathJax(inputHtmlPath, outputPdfPath) {
    let browser;

    try {
        // --- MODIFICATION START ---
        // This is the only part you need to change.
        // We must tell Puppeteer where to find the Alpine-native Chromium
        // and add arguments required for running in a Docker container.
        browser = await puppeteer.launch({
            headless: "new", // "new" is the modern headless mode
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH, // Use the ENV var we set in the Dockerfile
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });
        // --- MODIFICATION END ---

        const page = await browser.newPage();

        const absoluteInputHtmlPath = path.resolve(inputHtmlPath);
        if (!fs.existsSync(absoluteInputHtmlPath)) {
            throw new Error(`Input HTML file not found: ${absoluteInputHtmlPath}`);
        }

        console.log(`Loading HTML from: file://${absoluteInputHtmlPath}`);
        await page.goto(`file://${absoluteInputHtmlPath}`, { waitUntil: 'networkidle0' });

        console.log('Waiting for MathJax to render...');
        await page.evaluate(() => {
            return new Promise(resolve => {
                if (window.MathJax && window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise().then(() => {
                        console.log("MathJax v3 typeset complete.");
                        resolve();
                    }).catch(error => {
                        console.error("MathJax v3 typeset error:", error);
                        resolve();
                    });
                }
                else if (window.MathJax && window.MathJax.Hub && window.MathJax.Hub.Queue) {
                    window.MathJax.Hub.Queue(() => {
                        console.log("MathJax v2 typeset complete.");
                        resolve();
                    });
                } else {
                    console.warn("MathJax not detected. Proceeding without MathJax wait.");
                    resolve();
                }
            });
        });

        console.log('MathJax rendering complete. Generating PDF...');
        await page.pdf({
            path: outputPdfPath,
            format: 'A4',
            printBackground: true,
            margin: {
                top: '20mm',
                right: '20mm',
                bottom: '20mm',
                left: '20mm'
            }
        });

        console.log(`PDF successfully generated at: ${outputPdfPath}`);

    } catch (error) {
        console.error('An error occurred during PDF generation:', error);
        process.exit(1);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// --- Command-line argument parsing ---
const args = process.argv.slice(2);

if (args.length !== 2) {
    console.log('Usage: node render_math_and_pdf.js <inputHtmlPath> <outputPdfPath>');
    process.exit(1);
}

const inputHtml = args[0];
const outputPdf = args[1];

renderHtmlWithMathJax(inputHtml, outputPdf);
