/*
 Deploys LittleOddities. Sepolia first. Mainnet is blocked unless you explicitly
 set CONFIRM_MAINNET_DEPLOY=I_APPROVE_MAINNET in your shell for that one command.
*/
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const { ethers, network } = hre;
  const env = process.env;
  const chainId = Number((await ethers.provider.getNetwork()).chainId);
  if (chainId === 1 && env.CONFIRM_MAINNET_DEPLOY !== "I_APPROVE_MAINNET") {
    throw new Error("Mainnet deploy blocked. This spends real ETH and needs the founder's explicit approval (see docs/DEPLOYMENT_GUIDE.md).");
  }
  if (!ethers.isAddress(env.OWNER_ADDRESS) || /^0x0+$/.test(env.OWNER_ADDRESS)) throw new Error("Set OWNER_ADDRESS in .env to your PUBLIC owner wallet address");
  if (chainId === 1 && /__.*_CID__/.test(env.BASE_URI || "")) throw new Error("BASE_URI still has a placeholder CID. Upload + verify metadata on IPFS first.");

  const [deployer] = await ethers.getSigners();
  const bal = await ethers.provider.getBalance(deployer.address);
  console.log(`Network: ${network.name} (chain ${chainId})`);
  console.log(`Deployer: ${deployer.address}  balance: ${ethers.formatEther(bal)} ETH`);
  console.log(`Owner:    ${env.OWNER_ADDRESS}`);

  const args = [env.OWNER_ADDRESS, env.BASE_URI, env.CONTRACT_URI, Number(env.WALLET_LIMIT || 10), Number(env.ROYALTY_BPS || 500)];
  const F = await ethers.getContractFactory("LittleOddities");
  const est = await ethers.provider.estimateGas(await F.getDeployTransaction(...args));
  const fee = await ethers.provider.getFeeData();
  console.log(`Estimated deploy gas: ${est}  (~${ethers.formatEther(est * (fee.maxFeePerGas || fee.gasPrice))} ETH at current max fee)`);

  const c = await F.deploy(...args);
  await c.waitForDeployment();
  const address = await c.getAddress();
  const tx = c.deploymentTransaction();
  console.log(`Deployed LittleOddities at ${address}\nTx: ${tx.hash}`);

  const record = { network: network.name, chainId, address, txHash: tx.hash, args, deployedAt: new Date().toISOString() };
  const dir = path.join(__dirname, "..", "deployments");
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, `${network.name}.json`), JSON.stringify(record, null, 2));
  console.log(`Saved deployments/${network.name}.json`);
  console.log(`Verify with:\n  npx hardhat verify --network ${network.name} ${address} ${args.map((a) => JSON.stringify(String(a))).join(" ")}`);
}

main().catch((e) => { console.error(e.message || e); process.exitCode = 1; });
