export default function LegalDraft({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <p className="card p-4 bg-butter/50 text-sm font-bold">DRAFT — pending review by a qualified lawyer. Not yet in effect.</p>
      <h1 className="font-display font-black text-5xl mt-6">{title}</h1>
      <div className="mt-6 grid gap-4 leading-relaxed [&_h2]:font-display [&_h2]:font-black [&_h2]:text-2xl [&_h2]:mt-4 [&_ul]:list-disc [&_ul]:pl-6">{children}</div>
    </div>
  );
}
