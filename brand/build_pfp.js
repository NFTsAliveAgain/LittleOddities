// X/Twitter profile pictures (1000x1000, circle-safe). Run: node brand/build_pfp.js
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const H = __dirname;
const mark = fs.readFileSync(path.join(H, "logos/mark.svg"), "utf8").replace("<svg", '<svg style="width:100%;height:100%;display:block"');
const variants = {
  butter: { bg: "#ffd86b", ring: "#1e1a2e", dots: ["#f59ac5", "#7cc8ff", "#8ee3b0"], shadow: "rgba(30,26,46,.9)", halo: "" },
  night: { bg: "#141a2e", ring: "#ffd86b", dots: ["#f59ac5", "#8ee3b0", "#ffd86b"], shadow: "#ffd86b", halo: "#fbf5ea" },
  mint: { bg: "#8ee3b0", ring: "#1e1a2e", dots: ["#f59ac5", "#ffd86b", "#7cc8ff"], shadow: "rgba(30,26,46,.9)", halo: "" },
};
const page = ({ bg, ring, dots, shadow, halo }) => `<!doctype html><html><body style="margin:0">
<div style="position:relative;width:1000px;height:1000px;background:${bg};overflow:hidden">
  <div style="position:absolute;inset:0;background-image:radial-gradient(rgba(30,26,46,.07) 2px,transparent 2px);background-size:22px 22px"></div>
  <div style="position:absolute;left:140px;top:140px;width:720px;height:720px;border-radius:50%;border:10px dashed ${ring};opacity:.18"></div>
  ${halo ? `<div style="position:absolute;left:230px;top:300px;width:540px;height:540px;border-radius:50%;background:radial-gradient(circle, ${halo}33 0%, transparent 65%)"></div>` : ""}
  ${[[205, 560, 40], [800, 470, 30], [700, 830, 34]].map(([x, y, r], i) =>
    `<div style="position:absolute;left:${x - r}px;top:${y - r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;background:${dots[i]};border:7px solid #1e1a2e"></div>`).join("")}
  <div style="position:absolute;left:170px;top:150px;width:660px;height:660px;filter:drop-shadow(14px 14px 0 ${shadow})">${mark}</div>
</div></body></html>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
  fs.mkdirSync(path.join(H, "social"), { recursive: true });
  for (const [name, v] of Object.entries(variants)) {
    await p.setContent(page(v));
    await p.screenshot({ path: path.join(H, "social", `x-profile-${name}-1000.png`) });
  }
  // circle-crop preview sheet (how X will show them)
  const imgs = Object.keys(variants).map((n) => `data:image/png;base64,${fs.readFileSync(path.join(H, "social", `x-profile-${n}-1000.png`)).toString("base64")}`);
  await p.setViewportSize({ width: 1200, height: 460 });
  await p.setContent(`<body style="margin:0;background:#000;display:flex;gap:60px;justify-content:center;align-items:center;height:460px;font-family:sans-serif;color:#aaa">
    ${imgs.map((src, i) => `<div style="text-align:center"><img src="${src}" style="width:320px;height:320px;border-radius:50%;border:4px solid #000;box-shadow:0 0 0 2px #333"><p>${Object.keys(variants)[i]}</p></div>`).join("")}</body>`);
  await p.screenshot({ path: path.join(H, "social", "x-profile-preview.png") });
  await b.close();
  console.log("done");
})();
