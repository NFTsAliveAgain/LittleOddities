export default function Section({ title, kicker, children, className = "" }: { title: string; kicker?: string; children: React.ReactNode; className?: string }) {
  return (
    <section className={`mx-auto max-w-7xl px-4 py-12 ${className}`}>
      {kicker && <p className="font-hand text-2xl text-tomato -mb-1">{kicker}</p>}
      <h2 className="font-display font-black text-3xl sm:text-4xl">{title}</h2>
      <div className="mt-6">{children}</div>
    </section>
  );
}
