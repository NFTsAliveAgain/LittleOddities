import LegalDraft from "@/components/LegalDraft";
export const metadata = { title: "NFT Holder License" };
export default function License() {
  return (
    <LegalDraft title="NFT Holder License">
      <p>This license explains what you may do with the artwork of a Little Oddity you own. Owning the NFT does <strong>not</strong> transfer copyright;
        the artwork&apos;s copyright stays with the project owner. While you own the NFT, you receive the rights below.</p>
      <h2>You may</h2>
      <ul>
        <li>Display your Oddity anywhere for personal, non-commercial use — profile pictures, wallpapers, prints for your home.</li>
        <li>Sell, trade or give away the NFT; these rights pass to the new owner and end for you.</li>
        <li>Use your Oddity in commercial merchandise or projects with gross revenue up to a limit to be set by the owner (draft: US$10,000 per year), with credit to &ldquo;Little Oddities&rdquo;.</li>
      </ul>
      <h2>You may not</h2>
      <ul>
        <li>Use the artwork of Oddities you don&apos;t own.</li>
        <li>Use the NFTs Alive Again or Little Oddities names or logos as your own brand, or imply endorsement.</li>
        <li>Use the artwork in hateful, illegal, deceptive or infringing content, or to create other NFTs or tokens.</li>
        <li>Register trademarks or claim copyright in the artwork.</li>
      </ul>
      <h2>Ending</h2>
      <p>These rights end automatically when you no longer own the NFT, or if you breach this license.</p>
    </LegalDraft>
  );
}
