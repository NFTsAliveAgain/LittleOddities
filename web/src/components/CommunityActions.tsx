"use client";
import { useState } from "react";
import { useAccount } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useWalletSignature } from "./useWalletSignature";

type Poll = { id: number; question: string; kind: string; holders_only: number; open: number; closes_at: string | null; options: { id: number; label: string; votes: number }[] };

export function PollCard({ poll }: { poll: Poll }) {
  const { isConnected } = useAccount();
  const sign = useWalletSignature();
  const [msg, setMsg] = useState("");
  const total = poll.options.reduce((s, o) => s + o.votes, 0);
  async function vote(optionId: number) {
    setMsg("");
    try {
      const { address, signature } = await sign("vote");
      const r = await fetch("/api/community", { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ action: "vote", address, signature, pollId: poll.id, optionId }) }).then((x) => x.json());
      setMsg(r.ok ? "Vote recorded — thank you! Refresh to see updated results." : r.error);
    } catch (e) { setMsg((e as Error).message); }
  }
  return (
    <div className="card p-5">
      <div className="flex justify-between gap-2"><span className="text-xs font-bold uppercase opacity-60">{poll.kind === "character" ? "Character vote" : "Poll"}{poll.holders_only ? " · holders only" : ""}</span>
        <span className="text-xs font-bold">{poll.open ? "Open" : "Closed"}</span></div>
      <h3 className="font-display font-black text-xl mt-1">{poll.question}</h3>
      <ul className="mt-3 grid gap-2">
        {poll.options.map((o) => (
          <li key={o.id}>
            <button disabled={!poll.open || !isConnected} onClick={() => vote(o.id)} className="w-full text-left rounded-xl border-2 border-ink overflow-hidden relative bg-white disabled:cursor-default">
              <span className="absolute inset-y-0 left-0 bg-mint" style={{ width: `${total ? (100 * o.votes) / total : 0}%` }} />
              <span className="relative flex justify-between p-2"><span className="font-bold">{o.label}</span><span className="tabular-nums">{o.votes}</span></span>
            </button>
          </li>
        ))}
      </ul>
      <p className="text-xs mt-2 opacity-60">{total} vote{total === 1 ? "" : "s"} from real wallets · one vote per wallet · voting is a free signature</p>
      {poll.open && !isConnected && <div className="mt-3"><ConnectButton label="Connect to vote" /></div>}
      {msg && <p className="text-sm mt-2" role="status">{msg}</p>}
    </div>
  );
}

export function SuggestionForm() {
  const { isConnected } = useAccount();
  const sign = useWalletSignature();
  const [text, setText] = useState("");
  const [msg, setMsg] = useState("");
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    try {
      const { address, signature } = await sign("suggestion");
      const r = await fetch("/api/community", { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ action: "suggest", address, signature, body: text }) }).then((x) => x.json());
      if (r.ok) setText("");
      setMsg(r.ok ? r.note : r.error);
    } catch (e) { setMsg((e as Error).message); }
  }
  return (
    <form onSubmit={submit} className="card p-5">
      <h3 className="font-display font-black text-xl">Suggest an idea</h3>
      <p className="text-sm opacity-70">Character ideas, events, improvements — anything. Suggestions are reviewed before appearing publicly.</p>
      <textarea className="input mt-3 min-h-28" value={text} onChange={(e) => setText(e.target.value)} maxLength={1000} placeholder="I think the Oddities should…" />
      {isConnected ? <button className="btn bg-butter mt-3" disabled={text.trim().length < 10}>Sign & submit</button> : <div className="mt-3"><ConnectButton label="Connect to suggest" /></div>}
      {msg && <p className="text-sm mt-2" role="status">{msg}</p>}
    </form>
  );
}
