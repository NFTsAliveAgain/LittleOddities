// What the admin dashboard may edit. Anything not listed here cannot be changed through the API.
export const ADMIN_TABLES: Record<string, { columns: string[]; order: string; label: string }> = {
  roadmap_items: { label: "Roadmap", columns: ["phase", "title", "detail", "status", "sort"], order: "phase, sort, id" },
  announcements: { label: "Announcements", columns: ["title", "body", "holders_only", "published"], order: "id DESC" },
  events: { label: "Events & contests", columns: ["title", "kind", "body", "starts_at", "ends_at", "link", "published"], order: "id DESC" },
  polls: { label: "Polls & voting", columns: ["question", "kind", "holders_only", "open", "closes_at"], order: "id DESC" },
  poll_options: { label: "Poll options", columns: ["poll_id", "label"], order: "poll_id, id" },
  suggestions: { label: "Suggestions", columns: ["status"], order: "id DESC" },
  giveaways: { label: "Giveaways", columns: ["title", "description", "quantity", "status", "starts_at", "ends_at", "published"], order: "id DESC" },
  giveaway_winners: { label: "Giveaway winners", columns: ["giveaway_id", "wallet", "token_id", "tx_hash", "distributed_at", "note"], order: "id DESC" },
  settings: { label: "Site settings & links", columns: ["key", "value"], order: "key" },
  audit_log: { label: "Audit log (read-only)", columns: [], order: "id DESC" },
};
