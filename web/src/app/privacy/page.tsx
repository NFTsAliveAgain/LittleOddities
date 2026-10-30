import LegalDraft from "@/components/LegalDraft";
export const metadata = { title: "Privacy Policy" };
export default function Privacy() {
  return (
    <LegalDraft title="Privacy Policy">
      <h2>What we collect</h2>
      <ul>
        <li>Public wallet addresses you connect or use to sign (for votes, suggestions and admin access).</li>
        <li>Text you submit as a suggestion.</li>
        <li>Standard technical logs from our hosting provider (such as IP address and browser type).</li>
      </ul>
      <h2>What we never collect</h2><p>Private keys, seed phrases or passwords. We will never ask for them.</p>
      <h2>Public by nature</h2><p>Blockchain transactions, including mints and giveaway transfers, are permanently public on Ethereum.</p>
      <h2>Third parties</h2><p>Wallet connections use RainbowKit/WalletConnect; blockchain data is read through an RPC provider; the site is hosted by [hosting provider]. Each has its own privacy policy.</p>
      <h2>Contact</h2><p>[Contact email to be added.]</p>
    </LegalDraft>
  );
}
