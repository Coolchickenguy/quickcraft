const puppeteer = require('puppeteer');
// Constants
const TEXT = 'Quickcraft';
const OUTPUT_PATH = 'logo_full.png';
const quality = 2048;

// Code
// Scales font size so there is basicly no difference between higher and lower resolutions
const size = [quality*2,quality]


const HTML_CONTENT = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Nabla&display=swap" rel="stylesheet">
  <style>
    html, body {
      margin: 0;
      padding: 0;
      background: transparent;
    }
    .container {
      width: ${size[0]}px;
      height: ${size[1]}px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Nabla', sans-serif;
      font-size: 15vw;
    }
  </style>
</head>
<body>
  <div class="container">${TEXT}</div>
  <script>
  // Expensive but WHATEVER, this only happens rarely
  function fitTextToContainer(container, textEl) {
      let fontSize = 10;
      textEl.style.fontSize = fontSize + 'px';

      while (textEl.offsetWidth < container.offsetWidth) {
        fontSize++;
        textEl.style.fontSize = fontSize + 'px';
      }

      // Go back because it gets too big by1px due to how the loop works
      textEl.style.fontSize = (fontSize - 1) + 'px';
    }

    const container = document.body;
    const text = document.getElementByClassName('container')[0];

    fitTextToContainer(container, text);
    
    </script>
</body>
</html>
`;

(async () => {
  const browser = await puppeteer.launch({headless:false});
  const page = await browser.newPage();

  // Set viewport to match container size
  await page.setViewport({ width: size[0], height: size[1] });

  // Load the HTML content directly
  await page.setContent(HTML_CONTENT, { waitUntil: 'networkidle0' });
  // Wait for font to load
  await page.evaluateHandle('document.fonts.ready');
  
  const container = await page.waitForSelector('div');
  // Take screenshot with transparent background
  await container.screenshot({ path: OUTPUT_PATH, omitBackground: true });

  await browser.close();
  console.log(`✅ Rendered and saved: ${OUTPUT_PATH}`);
})();
