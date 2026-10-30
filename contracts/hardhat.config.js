require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();
const { subtask } = require("hardhat/config");
const { TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD } = require("hardhat/builtin-tasks/task-names");

// Use the official Solidity compiler shipped in the "solc" npm package (pinned in
// package.json) instead of downloading it, so builds work offline and are reproducible.
subtask(TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD, async (args, hre, runSuper) => {
  const solc = require("solc");
  if (args.solcVersion === "0.8.28") {
    return { compilerPath: require.resolve("solc/soljson.js"), isSolcJs: true, version: args.solcVersion, longVersion: solc.version() };
  }
  return runSuper();
});

// Secrets come ONLY from a local .env file that is never committed (see .env.example).
const { SEPOLIA_RPC_URL, MAINNET_RPC_URL, DEPLOYER_PRIVATE_KEY, ETHERSCAN_API_KEY } = process.env;
const accounts = DEPLOYER_PRIVATE_KEY ? [DEPLOYER_PRIVATE_KEY] : [];

module.exports = {
  solidity: { version: "0.8.28", settings: { optimizer: { enabled: true, runs: 200 }, evmVersion: "cancun" } },
  networks: {
    hardhat: {},
    sepolia: { url: SEPOLIA_RPC_URL || "", accounts, chainId: 11155111 },
    mainnet: { url: MAINNET_RPC_URL || "", accounts, chainId: 1 },
  },
  etherscan: { apiKey: ETHERSCAN_API_KEY || "" },
  gasReporter: { enabled: !!process.env.REPORT_GAS, currency: "USD" },
};
