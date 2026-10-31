/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The gallery reads data/collection.json at runtime; make sure hosting bundles it.
  outputFileTracingIncludes: { "/**": ["./data/collection.json"] },
  webpack: (config) => {
    // optional deps pulled in by wallet libraries that are not needed in the browser
    config.externals.push("pino-pretty", "lokijs", "encoding");
    // Optional payment add-ons of the Coinbase/Base connector that this site never uses.
    config.resolve.alias = { ...config.resolve.alias, "@x402/evm": false, "@x402/svm": false, "@x402/svm/exact/client": false,
      "@x402/evm/exact/client": false, "@x402/core": false, "@x402/fetch": false,
      "@react-native-async-storage/async-storage": false };
    return config;
  },
};
export default nextConfig;
