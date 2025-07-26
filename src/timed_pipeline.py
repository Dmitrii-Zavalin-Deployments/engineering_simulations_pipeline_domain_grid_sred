# src/timed_pipeline.py

"""
⏱️ Fault-Tolerant Wrapper for STEP Domain Pipeline

Executes the core pipeline logic with runtime diagnostics,
timeout handling, and structured error reporting for
robust integration in headless environments and CI workflows.
"""

import sys
import time
import traceback
import subprocess
from pathlib import Path
from logger_utils import log_checkpoint, log_error, log_success

# Configuration
MAX_DURATION_SEC = 300  # 5 minutes
PIPELINE_SCRIPT = Path(__file__).parent / "run_pipeline.py"
FREECAD_BINARY = Path(__file__).parent.parent / "FreeCAD.AppImage"
RESOLUTION = 0.01  # Meters

def execute_pipeline():
    """
    Run FreeCAD pipeline via subprocess and monitor execution.
    """
    cmd = [
        str(FREECAD_BINARY),
        "--console",
        "--py",
        str(PIPELINE_SCRIPT),
        "--resolution",
        str(RESOLUTION)
    ]

    log_checkpoint(f"📦 Launching pipeline: {' '.join(cmd)}")
    start_time = time.time()

    try:
        proc = subprocess.Popen(cmd, env={"QT_QPA_PLATFORM": "offscreen"})
        while True:
            exit_code = proc.poll()
            elapsed = time.time() - start_time

            if exit_code is not None:
                if exit_code == 0:
                    log_success("🏁 FreeCAD pipeline completed successfully")
                else:
                    log_error(f"💥 Pipeline exited with code {exit_code}", fatal=True)
                break

            if elapsed > MAX_DURATION_SEC:
                proc.kill()
                log_error("⏳ Pipeline execution timed out", fatal=True)
                break

            time.sleep(1)

    except Exception as e:
        log_error("🔻 Exception during pipeline execution", fatal=True)
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    log_checkpoint("🧪 Timed pipeline wrapper initiated")
    if not FREECAD_BINARY.exists():
        log_error(f"FreeCAD binary missing: {FREECAD_BINARY}", fatal=True)
    if not PIPELINE_SCRIPT.exists():
        log_error(f"Pipeline script missing: {PIPELINE_SCRIPT}", fatal=True)
    execute_pipeline()



