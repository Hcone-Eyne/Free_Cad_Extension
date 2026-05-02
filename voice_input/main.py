"""
FILE: voice_input/main.py

No keyboard input() loop — all input is via GUI buttons.
Removing the input() thread eliminates stdin fd competition with
Tcl's notifier (the second cause of the trace trap crash).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ui.phil_overlay import Phil_Overlay


if __name__ == "__main__":
    print("[Main] Starting Phil...")
    app = Phil_Overlay()
    # mainloop() on main thread — mandatory on macOS
    app.mainloop()
    print("[Main] Exited cleanly.")