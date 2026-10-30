import { getSettings } from "@/lib/content";

// Links come from the admin dashboard. Empty links show as "coming soon" — never fake URLs.
export default async function SocialLinks() {
  const s = await getSettings().catch(() => ({} as Record<string, string>));
  const links = [["Discord", s.discord_url], ["X / Twitter", s.x_url], ["Instagram", s.instagram_url], ["YouTube", s.youtube_url]];
  return (
    <ul className="flex flex-wrap gap-2 text-xs">
      {links.map(([label, url]) => (
        <li key={label}>
          {url ? <a href={url} target="_blank" rel="noopener noreferrer" className="underline">{label}</a>
               : <span className="opacity-50" title="Not launched yet">{label} (soon)</span>}
        </li>
      ))}
    </ul>
  );
}
