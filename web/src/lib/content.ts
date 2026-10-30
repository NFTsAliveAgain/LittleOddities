import "server-only";
import { q } from "./db";

export type RoadmapItem = { id: number; phase: number; title: string; detail: string; status: "planned" | "in_progress" | "completed"; updated_at: string };

export const getRoadmap = () => q<RoadmapItem>("SELECT * FROM roadmap_items ORDER BY phase, sort, id");
export const getSettings = async () =>
  Object.fromEntries((await q<{ key: string; value: string }>("SELECT key, value FROM settings")).map((r) => [r.key, r.value]));
export const getAnnouncements = () =>
  q<{ id: number; title: string; body: string; holders_only: number; created_at: string }>(
    "SELECT * FROM announcements WHERE published = 1 ORDER BY id DESC LIMIT 20");
export const getEvents = () =>
  q<{ id: number; title: string; kind: string; body: string; starts_at: string; ends_at: string; link: string }>(
    "SELECT * FROM events WHERE published = 1 ORDER BY starts_at DESC LIMIT 20");
export const getGiveaways = () =>
  q<{ id: number; title: string; description: string; quantity: number; status: string; starts_at: string; ends_at: string }>(
    "SELECT * FROM giveaways WHERE published = 1 ORDER BY id DESC");
export const getWinners = () =>
  q<{ giveaway_id: number; wallet: string; token_id: number | null; tx_hash: string; distributed_at: string | null }>(
    "SELECT giveaway_id, wallet, token_id, tx_hash, distributed_at FROM giveaway_winners ORDER BY id DESC");
export const getApprovedSuggestions = () =>
  q<{ id: number; author: string; body: string; status: string; created_at: string }>(
    "SELECT * FROM suggestions WHERE status IN ('approved','done') ORDER BY id DESC LIMIT 30");

export async function getPolls() {
  const polls = await q<{ id: number; question: string; kind: string; holders_only: number; open: number; closes_at: string | null }>(
    "SELECT * FROM polls WHERE open = 1 OR id IN (SELECT DISTINCT poll_id FROM poll_votes) ORDER BY id DESC LIMIT 10");
  const out = [];
  for (const p of polls) {
    const options = await q<{ id: number; label: string; votes: number }>(
      `SELECT o.id, o.label, (SELECT COUNT(*) FROM poll_votes v WHERE v.option_id = o.id) AS votes
       FROM poll_options o WHERE o.poll_id = ? ORDER BY o.id`, [p.id]);
    out.push({ ...p, options: options.map((o) => ({ ...o, votes: Number(o.votes) })) });
  }
  return out;
}

/** Real numbers only: counts that come from actual records. */
export async function giveawayTotals() {
  const [r] = await q<{ n: number }>("SELECT COUNT(*) AS n FROM giveaway_winners WHERE tx_hash != ''");
  return { reserved: 500, distributed: Number(r.n) };
}
