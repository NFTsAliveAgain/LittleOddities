// Renders brand graphics (banners, profile images, OG image, favicons, palette) to PNG with Chromium.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const H = __dirname;
const read = (p) => fs.readFileSync(path.join(H, p), "utf8");
const font = (f) => `url(data:font/ttf;base64,${fs.readFileSync(path.join(H, "fonts", f)).toString("base64")})`;
const css = `@font-face{font-family:F;src:${font("Fraunces_900Black.ttf")}}@font-face{font-family:D;src:${font("DMSans_700Bold.ttf")}}
@font-face{font-family:C;src:${font("Caveat_700Bold.ttf")}} *{margin:0;box-sizing:border-box} body{font-family:D;color:#1e1a2e}
.night{background:#141a2e;color:#fbf5ea} .grain{background-image:radial-gradient(rgba(255,255,255,.06) 1.5px,transparent 1.5px);background-size:14px 14px}
.hand{font-family:C} .disp{font-family:F} .blob{position:absolute;border:5px solid #1e1a2e;border-radius:50%}`;
const mark = read("logos/mark.svg"), lo = read("logos/little-oddities.svg"), naa = read("logos/nfts-alive-again-dark.svg");
const blobs = (seed) => [["#f59ac5", 8, 30, 120], ["#8ee3b0", 82, 18, 90], ["#c9b8f2", 70, 70, 140], ["#ffd86b", 18, 78, 70], ["#7cc8ff", 92, 82, 60]]
  .map(([c, x, y, s], i) => `<div class="blob" style="background:${c};left:${(x + seed * 7 * i) % 100}%;top:${y}%;width:${s}px;height:${s}px;transform:translate(-50%,-50%)"></div>`).join("");
const sticker = (svg, w) => `<div style="background:#fbf5ea;border:6px solid #1e1a2e;border-radius:28px;box-shadow:8px 8px 0 #1e1a2e;padding:18px 26px;display:inline-block">${svg.replace("<svg", `<svg style="width:${w}px;height:auto;display:block"`)}</div>`;

const pages = {
  "banners/x-banner-1500x500.png": [1500, 500, `<div class="night grain" style="position:relative;width:1500px;height:500px;overflow:hidden">${blobs(1)}
     <div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(-2deg);text-align:center">${sticker(lo, 560)}
     <p class="hand" style="font-size:44px;margin-top:22px;color:#ffd86b">Bringing NFTs Alive Again.</p></div></div>`],
  "banners/opensea-banner-1400x350.png": [1400, 350, `<div class="night grain" style="position:relative;width:1400px;height:350px;overflow:hidden">${blobs(2)}
     <div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(-1.5deg)">${sticker(lo, 420)}</div></div>`],
  "banners/discord-banner-960x540.png": [960, 540, `<div class="night grain" style="position:relative;width:960px;height:540px;overflow:hidden">${blobs(3)}
     <div style="position:absolute;left:50%;top:46%;transform:translate(-50%,-50%);text-align:center">${sticker(lo, 420)}
     <p class="disp" style="font-size:40px;margin-top:24px">Welcome to the weird.</p></div></div>`],
  "social/og-1200x630.png": [1200, 630, `<div class="night grain" style="position:relative;width:1200px;height:630px;overflow:hidden">${blobs(4)}
     <div style="position:absolute;left:80px;top:90px">${naa.replace("<svg", '<svg style="width:520px;height:auto"')}</div>
     <div style="position:absolute;left:80px;top:185px;transform:rotate(-2deg)">${sticker(lo, 470)}</div>
     <p class="disp" style="position:absolute;left:80px;bottom:44px;font-size:30px">10,000 characters · 0.005 ETH · Nov 1, 2027</p></div>`],
  "social/profile-400x400.png": [400, 400, `<div style="width:400px;height:400px;background:#ffd86b;display:grid;place-items:center">${mark.replace("<svg", '<svg style="width:300px;height:300px"')}</div>`],
  "social/profile-night-400x400.png": [400, 400, `<div class="night" style="width:400px;height:400px;display:grid;place-items:center">${mark.replace("<svg", '<svg style="width:300px;height:300px"')}</div>`],
  "favicon/icon-512.png": [512, 512, `<div style="width:512px;height:512px">${read("favicon/favicon.svg").replace("<svg", '<svg style="width:512px;height:512px"')}</div>`],
  "favicon/apple-touch-icon-180.png": [180, 180, `<div style="width:180px;height:180px">${read("favicon/favicon.svg").replace("<svg", '<svg style="width:180px;height:180px"')}</div>`],
  "favicon/icon-32.png": [32, 32, `<div style="width:32px;height:32px">${read("favicon/favicon.svg").replace("<svg", '<svg style="width:32px;height:32px"')}</div>`],
  "palette/palette.png": [1200, 420, `<div style="width:1200px;height:420px;background:#fbf5ea;padding:40px"><p class="disp" style="font-size:40px">NFTs Alive Again — palette</p>
     <div style="display:flex;gap:16px;margin-top:30px">${[["Ink", "#1e1a2e"], ["Night", "#141a2e"], ["Cream", "#fbf5ea"], ["Pink", "#f59ac5"], ["Mint", "#8ee3b0"],
       ["Lilac", "#c9b8f2"], ["Sky", "#7cc8ff"], ["Butter", "#ffd86b"], ["Tomato", "#ff6b4a"], ["Moss", "#5dbb4a"]].map(([n, c]) =>
       `<div style="text-align:center"><div style="width:96px;height:96px;border-radius:20px;border:4px solid #1e1a2e;background:${c}"></div><p style="margin-top:8px">${n}</p><p style="font-size:13px;opacity:.6">${c}</p></div>`).join("")}</div></div>`],
};

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [file, [w, h, html]] of Object.entries(pages)) {
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<html><head><style>${css}</style></head><body>${html}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    fs.mkdirSync(path.join(H, path.dirname(file)), { recursive: true });
    await page.screenshot({ path: path.join(H, file), clip: { x: 0, y: 0, width: w, height: h } });
    console.log("wrote", file);
  }
  await browser.close();
})();
