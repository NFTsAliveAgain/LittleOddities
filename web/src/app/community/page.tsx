import Section from "@/components/Section";
import SocialLinks from "@/components/SocialLinks";
import { PollCard, SuggestionForm } from "@/components/CommunityActions";
import { getAnnouncements, getApprovedSuggestions, getEvents, getGiveaways, getPolls, getSettings, getWinners, giveawayTotals } from "@/lib/content";
import { explorer } from "@/lib/site";

export const dynamic = "force-dynamic";
export const metadata = { title: "Community" };

const Empty = ({ children }: { children: React.ReactNode }) => <p className="card p-5 text-sm opacity-70">{children}</p>;
const short = (a: string) => `${a.slice(0, 6)}…${a.slice(-4)}`;

export default async function CommunityPage() {
  const [settings, ann, events, polls, gws, winners, sugg, totals] = await Promise.all([
    getSettings(), getAnnouncements(), getEvents(), getPolls(), getGiveaways(), getWinners(), getApprovedSuggestions(), giveawayTotals()]);
  return (
    <>
      <section className="bg-night text-cream border-b-4 border-ink">
        <div className="mx-auto max-w-6xl px-4 py-12">
          <p className="font-hand text-3xl text-butter">More than a collection — a movement</p>
          <h1 className="font-display font-black text-5xl">Community</h1>
          <p className="mt-4 max-w-2xl text-cream/80">{settings.welcome_message}</p>
          <div className="mt-4 text-cream"><SocialLinks /></div>
        </div>
      </section>

      <Section title="Announcements">
        {ann.length ? <div className="grid gap-3">{ann.map((a) => (
          <article key={a.id} className="card p-5"><p className="text-xs opacity-60">{a.created_at?.slice(0, 10)}{a.holders_only ? " · for holders" : ""}</p>
            <h3 className="font-display font-black text-xl">{a.title}</h3><p className="mt-2 whitespace-pre-line">{a.body}</p></article>))}</div>
          : <Empty>No announcements yet. The first ones will appear here.</Empty>}
      </Section>

      <Section title="Events & contests">
        {events.length ? <div className="grid md:grid-cols-2 gap-3">{events.map((e) => (
          <article key={e.id} className="card p-5"><p className="text-xs font-bold uppercase opacity-60">{e.kind}{e.starts_at ? ` · ${e.starts_at}` : ""}</p>
            <h3 className="font-display font-black text-xl">{e.title}</h3><p className="mt-2 text-sm">{e.body}</p>
            {e.link && <a className="underline text-sm" href={e.link} target="_blank" rel="noopener noreferrer">Details</a>}</article>))}</div>
          : <Empty>No events scheduled yet. Contests and creative events will be announced here.</Empty>}
      </Section>

      <Section title="Polls & character voting">
        {polls.length ? <div className="grid md:grid-cols-2 gap-4">{polls.map((p) => <PollCard key={p.id} poll={p} />)}</div>
          : <Empty>No polls are open yet. When they are, connected wallets can vote with a free signature — one vote per wallet.</Empty>}
      </Section>

      <Section title="Giveaways" className="scroll-mt-20" >
        <div id="giveaways" className="card p-5 mb-4">
          <p><strong>500</strong> Little Oddities are reserved for the community. <strong>{totals.distributed}</strong> distributed so far.
            Every winner below is linked to its real on-chain transfer.</p>
        </div>
        {gws.length ? <div className="grid gap-3">{gws.map((g) => {
          const w = winners.filter((x) => x.giveaway_id === g.id);
          return (
            <article key={g.id} className="card p-5">
              <div className="flex justify-between"><h3 className="font-display font-black text-xl">{g.title}</h3><span className="text-sm font-bold">{g.status} · {g.quantity} NFT{g.quantity > 1 ? "s" : ""}</span></div>
              <p className="text-sm mt-1">{g.description}</p>
              {w.length > 0 && <ul className="mt-3 text-sm grid gap-1">{w.map((x, i) => (
                <li key={i}>{short(x.wallet)}{x.token_id ? ` · #${x.token_id}` : ""}{x.tx_hash ? <> · <a className="underline" href={`${explorer}/tx/${x.tx_hash}`} target="_blank" rel="noopener noreferrer">transaction</a></> : " · pending transfer"}</li>))}</ul>}
            </article>);
        })}</div> : <Empty>No giveaways have started yet.</Empty>}
      </Section>

      <Section title="Community suggestions">
        <div className="grid md:grid-cols-2 gap-4">
          <SuggestionForm />
          <div className="grid gap-3 content-start">
            {sugg.length ? sugg.map((s) => (
              <article key={s.id} className="card p-4"><p className="text-xs opacity-60">{short(s.author)} · {s.status === "done" ? "Done ✓" : "Approved"}</p><p className="mt-1">{s.body}</p></article>
            )) : <Empty>No published suggestions yet — yours could be the first.</Empty>}
          </div>
        </div>
      </Section>
    </>
  );
}
