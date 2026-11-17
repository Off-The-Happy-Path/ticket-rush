"""Start ticket-rush with a given DROP_RESPONSE_AFTER_COMMIT_PCT, run the fans, stop it.

  python run_demo.py 0 20          # control, then 20%
  python run_demo.py 0 10 20 40    # the sweep
Writes results/pct-<N>.json and results/server-pct-<N>.log.
"""
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
API = Path(os.getenv("TICKET_RUSH_DIR", str(HERE.parent))) / "demo-api"
PY = API / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PORT = 8000
FANS = os.getenv("FANS", "100")
SEED = os.getenv("SEED", "42")


def run(pct: int) -> None:
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    env = {**os.environ, "ADMIN_ENABLED": "true", "DROP_RESPONSE_AFTER_COMMIT_PCT": str(pct),
           "DROP_SEED": SEED, "PYTHONUNBUFFERED": "1"}
    with open(out / f"server-pct-{pct}.log", "w") as log:
        server = subprocess.Popen([str(PY), "-m", "uvicorn", "app.main:app", "--port", str(PORT),
                                   "--log-level", "warning"], cwd=API, env=env, stderr=log, stdout=log)
        try:
            for _ in range(50):
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1)
                    break
                except Exception:
                    time.sleep(0.2)
            subprocess.run([str(PY), str(HERE / "fans.py"), "--fans", FANS, "--seed", SEED,
                            "--out", str(out / f"pct-{pct}.json")], check=True)
        finally:
            server.terminate()
            server.wait()


if __name__ == "__main__":
    for arg in sys.argv[1:] or ["0", "20"]:
        run(int(arg))
