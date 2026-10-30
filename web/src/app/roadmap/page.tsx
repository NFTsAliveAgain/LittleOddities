import RoadmapView from "@/components/RoadmapView";
import { getRoadmap } from "@/lib/content";

export const dynamic = "force-dynamic";
export const metadata = { title: "Roadmap" };

export default async function RoadmapPage() {
  const items = await getRoadmap();
  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <p className="font-hand text-2xl text-tomato">Where we&apos;re headed</p>
      <h1 className="font-display font-black text-5xl">Roadmap</h1>
      <p className="mt-4 max-w-2xl">
        Every item shows its real status: <strong>Planned</strong>, <strong>In progress</strong> or <strong>Completed</strong>.
        Nothing is marked completed until it&apos;s actually done. Later phases are intentions and plans, not guarantees —
        they&apos;ll grow and change with community feedback.
      </p>
      <div className="mt-8"><RoadmapView items={items} /></div>
    </div>
  );
}
