# ============================================================
# FILE: voice_input/command_bridge.py
# PURPOSE: The bridge between user input and the AI + FreeCAD runner.
#          Both voice and text input funnel through here.
#
# Think of this as the "traffic controller" — it receives a text
# command, sends it to the AI (translator), and then runs the
# resulting Python script in FreeCAD (runner).
# ============================================================

from voice_input.cad_assist.ai_core import translator
from voice_input.cad_assist import runner


# Words that mean "stop" — we check for these before doing any work.
EXIT_COMMANDS = {"exit", "exits", "quit", "q"}


def process_command(user_input: str) -> bool:
    """
    Takes a text command (from voice or keyboard) and:
      1. Sends it to the AI to generate a FreeCAD Python script.
      2. Runs the generated script in FreeCAD.

    Returns True if successful, False if something went wrong.
    """
    # --- Guard: reject empty input ---
    if not user_input or not user_input.strip():
        print("[Bridge] Empty input received. Ignoring.")
        return False

    # --- Guard: check for quit commands ---
    # (Main loop handles actual quitting; we just skip processing here.)
    if user_input.strip().lower() in EXIT_COMMANDS:
        print("[Bridge] Exit command received.")
        return False

    print(f"[Bridge] Sending to AI: '{user_input}'")

    # --- Step 1: Translate the command into a FreeCAD Python script ---
    # translator() sends the text to the local AI (Qwen via Ollama)
    # and returns the filename of the generated script, or None on failure.
    generated_script = translator(user_input)

    if not generated_script:
        print("[Bridge] AI failed to generate a script.")
        return False

    # --- Step 2: Run the generated script in FreeCAD ---
    print(f"[Bridge] Executing script: {generated_script}")
    runner.execute_cad_scripts(generated_script)
    print("[Bridge] Script execution complete.")
    return True
