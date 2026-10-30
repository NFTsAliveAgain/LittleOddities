import { NextResponse } from "next/server";
import { search } from "@/lib/collection";

export async function GET(req: Request) {
  const u = new URL(req.url).searchParams;
  return NextResponse.json(search({ q: u.get("q") || "", tier: u.get("tier") || "", trait: u.get("trait") || "",
    sort: u.get("sort") || "id", page: Number(u.get("page") || 1) }));
}
