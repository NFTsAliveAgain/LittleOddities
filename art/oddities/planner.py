"""Plans the whole collection before any image is drawn.

* Exact tier quantities (5,000 / 3,000 / 1,500 / 400 / 100).
* Every non-Common token carries exactly one 'signature' trait of its own
  tier; signature traits are allocated in exact, reproducible quotas.
* No trait may be rarer than the token's tier, so a token's Rarity always
  equals its rarest trait.
* Compatibility rules from traits.json are enforced.
* Every token has a unique trait combination (DNA) and a unique name.
"""
from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from .names import NameMaker

CONFIG = Path(__file__).resolve().parent.parent / "config" / "traits.json"


def load_config(path=CONFIG) -> dict:
    cfg = json.loads(Path(path).read_text())
    cfg["tier_names"] = [t["name"] for t in cfg["tiers"]]
    cfg["rank"] = {n: i for i, n in enumerate(cfg["tier_names"])}
    cfg["order"] = [c["key"] for c in cfg["categories"]]
    cfg["by_key"] = {c["key"]: c for c in cfg["categories"]}
    cfg["value"] = {(c["key"], v["name"]): v for c in cfg["categories"] for v in c["values"]}
    total = sum(t["count"] for t in cfg["tiers"])
    if total != cfg["collection"]["supply"]:
        raise ValueError(f"tier counts add to {total}, supply is {cfg['collection']['supply']}")
    for c in cfg["categories"]:
        if not any(v["tier"] == "Common" for v in c["values"]):
            raise ValueError(f"category {c['key']} needs at least one Common value")
    return cfg


def violations(traits: dict, cfg: dict) -> list:
    out = []
    for rule in cfg["rules"]:
        if rule["type"] == "no_shared_family":
            fa = set(cfg["value"][(rule["a"], traits[rule["a"]])].get("families", []))
            fb = set(cfg["value"][(rule["b"], traits[rule["b"]])].get("families", []))
            if fa & fb:
                out.append(rule["_why"])
        elif rule["type"] == "exclude":
            (ka, va), = rule["a"].items()
            (kb, vb), = rule["b"].items()
            if traits[ka] in va and traits[kb] in vb:
                out.append(rule["_why"])
    return out


def _largest_remainder(items, total):
    """items = [(key, weight)] -> {key: exact integer count} summing to total."""
    wsum = sum(w for _, w in items)
    raw = [(k, total * w / wsum) for k, w in items]
    counts = {k: int(r) for k, r in raw}
    left = total - sum(counts.values())
    for k, r in sorted(raw, key=lambda kr: -(kr[1] - int(kr[1])))[:left]:
        counts[k] += 1
    return counts


def signature_quotas(cfg: dict) -> dict:
    quotas = {}
    for t in cfg["tiers"][1:]:
        items = [((c["key"], v["name"]), v["weight"]) for c in cfg["categories"] for v in c["values"] if v["tier"] == t["name"]]
        quotas[t["name"]] = _largest_remainder(items, t["count"])
    return quotas


def plan_collection(cfg: dict, seed: int | None = None, max_tries: int = 2000) -> list:
    seed = cfg["collection"]["seed"] if seed is None else seed
    rng = random.Random(seed)
    supply = cfg["collection"]["supply"]
    rank = cfg["rank"]
    up = cfg["upgrade_factor"]["value"]

    tiers = [t["name"] for t in cfg["tiers"] for _ in range(t["count"])]
    rng.shuffle(tiers)

    sig_pool = {}
    for tier, q in signature_quotas(cfg).items():
        lst = [k for k, n in q.items() for _ in range(n)]
        rng.shuffle(lst)
        sig_pool[tier] = lst

    names = NameMaker(random.Random(seed + 1))
    seen = set()
    tokens = []
    for token_id in range(1, supply + 1):
        tier = tiers[token_id - 1]
        tr = rank[tier]
        sig = sig_pool[tier].pop() if tr > 0 else None
        for attempt in range(max_tries):
            traits = {}
            for c in cfg["categories"]:
                if sig and sig[0] == c["key"]:
                    traits[c["key"]] = sig[1]
                    continue
                pool = [v for v in c["values"] if rank[v["tier"]] <= tr]
                # extra traits may be rarer than Common (but never rarer than the token)
                weights = [v["weight"] * (1.0 if rank[v["tier"]] == 0 else up) for v in pool]
                traits[c["key"]] = rng.choices(pool, weights)[0]["name"]
            if violations(traits, cfg):
                continue
            dna = "|".join(traits[k] for k in cfg["order"])
            if dna in seen:
                continue
            seen.add(dna)
            break
        else:
            raise RuntimeError(f"could not find a valid unique combination for token {token_id} ({tier}, {sig})")
        tokens.append({
            "id": token_id, "tier": tier, "name": names.next(),
            "signature": f"{cfg['by_key'][sig[0]]['label']}: {sig[1]}" if sig else None,
            "traits": traits, "dna": dna,
        })
    return tokens


def statistics(tokens: list, cfg: dict) -> dict:
    tiers = Counter(t["tier"] for t in tokens)
    per = {}
    for c in cfg["categories"]:
        cnt = Counter(t["traits"][c["key"]] for t in tokens)
        per[c["label"]] = {v["name"]: {"count": cnt.get(v["name"], 0), "tier": v["tier"],
                                       "percent": round(100 * cnt.get(v["name"], 0) / len(tokens), 2)} for v in c["values"]}
    return {"supply": len(tokens), "tiers": {n: tiers.get(n, 0) for n in cfg["tier_names"]}, "traits": per}


def verify_plan(tokens: list, cfg: dict) -> list:
    """Independent re-check of every planning guarantee. Returns problems."""
    problems = []
    rank = cfg["rank"]
    expected = {t["name"]: t["count"] for t in cfg["tiers"]}
    got = Counter(t["tier"] for t in tokens)
    if dict(got) != {k: v for k, v in expected.items() if v}:
        problems.append(f"tier counts {dict(got)} != {expected}")
    ids = [t["id"] for t in tokens]
    if ids != list(range(1, cfg["collection"]["supply"] + 1)):
        problems.append("token ids are not exactly 1..supply in order")
    if len({t["dna"] for t in tokens}) != len(tokens):
        problems.append("duplicate trait combinations found")
    if len({t["name"] for t in tokens}) != len(tokens):
        problems.append("duplicate character names found")
    for t in tokens:
        rarest = max(rank[cfg["value"][(k, v)]["tier"]] for k, v in t["traits"].items())
        if rarest != rank[t["tier"]]:
            problems.append(f"token {t['id']}: rarest trait tier {cfg['tier_names'][rarest]} != token tier {t['tier']}")
        v = violations(t["traits"], cfg)
        if v:
            problems.append(f"token {t['id']}: rule violations {v}")
    return problems
