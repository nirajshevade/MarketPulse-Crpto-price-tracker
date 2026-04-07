from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from marketpulse.pipeline import run_pipeline


if __name__ == "__main__":
    raise SystemExit(run_pipeline(base_dir=ROOT_DIR))
