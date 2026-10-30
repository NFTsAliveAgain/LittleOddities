import LegalDraft from "@/components/LegalDraft";
export const metadata = { title: "Terms of Service" };
export default function Terms() {
  return (
    <LegalDraft title="Terms of Service">
      <p>These draft terms cover your use of this website and the Little Oddities smart contract.</p>
      <h2>Not an investment</h2><p>Little Oddities are digital collectibles. We make no promises about value, price, liquidity or future features. Roadmap items are plans, not obligations.</p>
      <h2>Blockchain risks</h2><p>Transactions on Ethereum are final and can&apos;t be reversed by us. You are responsible for your wallet, keys and gas fees. Smart contracts can contain bugs despite testing and review.</p>
      <h2>Eligibility</h2><p>You must be of legal age and allowed by your local laws to buy digital collectibles.</p>
      <h2>Community conduct</h2><p>We may remove suggestions or content that is abusive, illegal or spam.</p>
      <h2>Intellectual property</h2><p>Artwork use is governed by the NFT Holder License.</p>
      <h2>Liability</h2><p>To the extent the law allows, the service is provided &ldquo;as is&rdquo; without warranties. [Limitation of liability and governing law to be completed by counsel.]</p>
    </LegalDraft>
  );
}
