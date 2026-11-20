# tests/light_smoke.py — smoke test RINGAN tanpa API key (hemat kuota).
# Jalankan: uv run python tests/light_smoke.py        (default: 3 call live kecil, limit=1)
#           uv run python tests/light_smoke.py --offline   (zero network)
# Cakupan:
#   0. import registry + hitungan (zero network)
#   1. auth-gate tanpa request (core_search → auth-required sebelum HTTP)
#   2. handshake MCP stdio — stdin DIJAGA TERBUKA (lihat e2e_all_tools.py: closing stdin
#      berakhir race response-vs-shutdown)
#   3. opsional: 3 call live limit=1 (openalex/europepmc/zenodo) ≈ beberapa KB

from __future__ import annotations

import asyncio
import json
import subprocess
import sys

from scholarmesh.registry import SOURCES, all_tools, call_tool

FAILS: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<24} {detail}")
    if not ok:
        FAILS.append(label)


async def main() -> None:
    offline = "--offline" in sys.argv

    # 0. import & struktur (zero network)
    check("import+counts", len(SOURCES) == 40 and len(all_tools()) == 44,
          f"{len(SOURCES)} sources, {len(all_tools())} connector tools")

    # 1. auth-gate tanpa HTTP (registry menolak sebelum request)
    r = await call_tool("core_search", {"query": "x", "limit": 1})
    check("auth-gate[core]", r["status"] == "auth-required" and r["meta"]["env"] == "CORE_API_KEY",
          "zero network")

    # 2. handshake stdio (zero upstream; stdin terbuka sampai tools/list terbaca)
    proc = subprocess.Popen(
        ["uv", "run", "scholarmesh"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    reqs = "\n".join([
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "smoke", "version": "0"}}}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]) + "\n"
    try:
        proc.stdin.write(reqs.encode())
        proc.stdin.flush()
        parsed: list[dict] = []
        while not any(p.get("id") == 2 for p in parsed):
            raw = proc.stdout.readline()
            if not raw:
                break
            try:
                parsed.append(json.loads(raw.decode()))
            except json.JSONDecodeError:
                pass
        init = next((p for p in parsed if p.get("id") == 1), None)
        tl = next((p for p in parsed if p.get("id") == 2), None)
        n = len(tl["result"]["tools"]) if tl else 0
        name = init["result"]["serverInfo"]["name"] if init else "?"
        check("stdio handshake", name == "scholarmesh" and n == 46, f"{name}, {n} tools")
    finally:
        try:
            proc.kill()
        except OSError:
            pass

    # 3. call live mini (default on, limit=1; --offline untuk skip)
    if not offline:
        for name, args in [("openalex_search", {"query": "crispr", "limit": 1}),
                           ("europepmc_search", {"query": "crispr", "limit": 1}),
                           ("zenodo_search", {"query": "crispr", "limit": 1})]:
            r = await call_tool(name, args)
            it = (r["items"] or [{}])[0]
            ok = r["status"] in ("ok", "empty")
            check(f"live[{name}]", ok, f"status={r['status']} — {str(it.get('title'))[:55]}")

    print(f"\ntotal FAIL: {len(FAILS)}" + (f" -> {FAILS}" if FAILS else ""))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    asyncio.run(main())
