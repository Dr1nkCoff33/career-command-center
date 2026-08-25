"""Global configuration for the Career Command Center workspace."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_OUTPUT_DIR = OUTPUT_DIR / "analysis"
REPORTS_OUTPUT_DIR = OUTPUT_DIR / "reports"
EXPORTS_OUTPUT_DIR = OUTPUT_DIR / "exports"
TEMP_OUTPUT_DIR = OUTPUT_DIR / "temp"

for dir_path in [ANALYSIS_OUTPUT_DIR, REPORTS_OUTPUT_DIR, EXPORTS_OUTPUT_DIR, TEMP_OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
