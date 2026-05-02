"""
FILE: ui/phil_overlay.py
CRASH ROOT CAUSE & FIX:
  On macOS with Python 3.14 / Tk 9.0, two things cause
  'Tcl_WaitForEvent: Notifier not initialized' + SIGTRAP:

  1. A background thread calling input() which holds the terminal
     file descriptor while Tcl's notifier also tries to select() on it.
  2. A background audio thread holding a CoreAudio stream while
     Tcl's kqueue notifier runs on the main thread.

  FIX applied here:
  - NO background input() thread. Terminal prompt removed entirely.
    All input goes through the GUI buttons (Voice / Text).
  - NO persistent audio thread. Mic opens only on button click,
    records one phrase, closes immediately.
  - is_ready flag kept for compatibility but keyboard engine is gone.
"""

import threading
import time
import sys
from pathlib import Path

import customtkinter as ctk

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ui.phil_widget import Visual_look_Phill


class Phil_Overlay(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.is_ready        = False
        self._voice_active   = False
        self.processing_lock = threading.Lock()

        # ── window ───────────────────────────────────────────────────
        self.withdraw()

        # NOTE: overrideredirect(True) is intentionally SKIPPED on
        # Tk 9.0 because it causes the Tcl notifier crash on macOS.
        # The window will have a slim title bar — acceptable tradeoff.
        # self.overrideredirect(True)  ← DO NOT enable

        self.title("Phil")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = 320, 130
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{sh - 200}")

        # ── widget ───────────────────────────────────────────────────
        self.phil = Visual_look_Phill(master=self, bg_color=ctk.ThemeManager.theme["CTk"]["fg_color"])
        self.phil.pack(expand=True, fill="both")

        # dragging via title bar is free — no extra binding needed

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(300, self._show)

    # ── startup ──────────────────────────────────────────────────────

    def _show(self):
        self.deiconify()
        self.lift()
        self.is_ready = True
        print("[Phil] Ready!")

    # ── button handlers ───────────────────────────────────────────────

    def on_voice_click(self):
        if self._voice_active:
            self._voice_active = False
            self.phil.set_voice_active(False)
            self.phil.set_status("Ready To Build", "normal")
            return

        self._voice_active = True
        self.phil.set_voice_active(True)
        self.phil.set_status("Listening…", "thinking")

        threading.Thread(
            target=self._voice_task, daemon=True, name="VoiceTask"
        ).start()

    def on_text_click(self):
        if self.phil.entry_frame.winfo_ismapped():
            self.phil.hide_text_entry()
            self.geometry(f"320x130+{self.winfo_x()}+{self.winfo_y()}")
        else:
            self.phil.show_text_entry()
            self.geometry(f"320x180+{self.winfo_x()}+{self.winfo_y()}")

    def on_text_submit(self, text: str):
        text = text.strip()
        if not text:
            return
        self.phil.entry.delete(0, "end")
        self.phil.hide_text_entry()
        self.geometry(f"320x130+{self.winfo_x()}+{self.winfo_y()}")
        self._spawn_command(text)

    # kept for any external callers
    def execute_command_flow(self, user_input: str):
        self._spawn_command(user_input)

    # ── voice task ────────────────────────────────────────────────────

    def _voice_task(self):
        """
        Opens mic, records ONE phrase, closes mic, then signals main thread.
        Mic is fully closed before we call self.after() so CoreAudio
        is done before Tcl's notifier processes the callback.
        """
        result = None
        try:
            import speech_recognition as sr
            rec = sr.Recognizer()
            rec.pause_threshold   = 0.8
            rec.dynamic_energy_threshold = True

            with sr.Microphone() as source:
                rec.adjust_for_ambient_noise(source, duration=0.3)
                print("[Voice] Listening...")
                audio = rec.listen(source, timeout=8, phrase_time_limit=15)
            # ← mic closed here, CoreAudio stream released

            result = rec.recognize_google(audio)
            print(f"[Voice] Heard: {result}")

        except Exception as e:
            print(f"[Voice] {e}")

        # schedule UI update on main thread
        self.after(0, lambda: self._finish_voice(result))

    def _finish_voice(self, text):
        self._voice_active = False
        self.phil.set_voice_active(False)
        if text:
            self._spawn_command(text)
        else:
            self.phil.set_status("Didn't catch that", "danger")
            self.after(2000, lambda: self.phil.set_status("Ready To Build", "normal"))

    # ── command processing ────────────────────────────────────────────

    def _spawn_command(self, user_input: str):
        self.phil.set_status("Thinking…", "thinking")
        threading.Thread(
            target=self._run_command, args=(user_input,),
            daemon=True, name="CmdThread"
        ).start()

    def _run_command(self, user_input: str):
        with self.processing_lock:
            try:
                from voice_input.command_bridge import process_command
                process_command(user_input)
                self.after(0, lambda: self.phil.set_status("Done!", "safe"))
            except Exception as e:
                print(f"[Phil] Error: {e}")
                self.after(0, lambda: self.phil.set_status("Error!", "danger"))

            time.sleep(2)
            self.after(0, lambda: self.phil.set_status("Ready To Build", "normal"))

    # ── shutdown ─────────────────────────────────────────────────────

    def on_close(self):
        self.quit()
        self.destroy()