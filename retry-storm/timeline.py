"""Print one fan's merged client + server timeline. Usage: timeline.py results/pct-20.json [fan-id]
Without a fan id, picks the first fan whose first reservation call timed out and who later got a seat."""
import json
import re
import sys
from pathlib import Path

result = json.loads(Path(sys.argv[1]).read_text())
server_log = Path(sys.argv[1]).with_name("server-" + Path(sys.argv[1]).name.replace(".json", ".log"))


def pick():
    for f in result["fans"]:
        c = f["calls"]
        if c and c[0]["path"] == "/reservations" and c[0]["outcome"] == "timeout" and f["outcome"] == "confirmed":
            return f["id"]


fan = sys.argv[2] if len(sys.argv) > 2 else pick()
rows = [(e["at"], "client", e["text"], i) for i, e in enumerate( result["timeline"]) if e["fan"] == fan]
for line in server_log.read_text().splitlines():
    if f"fan={fan} " in line:
        at = line.split(" ", 1)[0]
        rows.append((at, "server", line.split(" ", 1)[1], -1))
print(f"# {fan}")
for at, src, text, _ in sorted(rows, key=lambda r: (r[0], r[3])):
    print(f"{at[11:]}  {src:6}  {text}")
