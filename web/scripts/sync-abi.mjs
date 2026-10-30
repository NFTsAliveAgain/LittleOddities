// Copies the compiled contract ABI from ../contracts into the website.
import fs from "node:fs";
const src = new URL("../../contracts/artifacts/contracts/LittleOddities.sol/LittleOddities.json", import.meta.url);
const out = new URL("../src/lib/abi.json", import.meta.url);
const { abi } = JSON.parse(fs.readFileSync(src, "utf8"));
fs.writeFileSync(out, JSON.stringify(abi, null, 2));
console.log(`ABI synced (${abi.length} entries)`);
