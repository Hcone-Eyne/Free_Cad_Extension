# ============================================================
# FILE: speech_processor/voice_handler.py
# PURPOSE: Listens to the microphone and converts speech to text.
#
# IMPORTANT: An instance of The_listener should ONLY be created
# inside a background thread — never on the main (UI) thread.
# Reason: PyAudio opens CoreAudio on macOS, which conflicts with
# the Tcl/Tk event notifier if used on the main thread.
# ============================================================

import speech_recognition as sr # type: ignore
import sys
from pathlib import Path

# --- Path Fix ---
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from voice_input.Keys.config import logs_location


class The_listener:
    """
    Phil's ear.
    Uses the SpeechRecognition library to capture audio and send it to
    Google's speech API to convert it into text.

    How it works:
      1. Opens the microphone
      2. Adjusts for background noise (calibration)
      3. Waits for the user to speak
      4. Sends the audio to Google for transcription
      5. Returns the text (or None if nothing was heard)
    """

    def __init__(self):
        # Recognizer: the engine that understands speech audio.
        self.recognizer = sr.Recognizer()

        # Microphone: the hardware input.
        # This opens a PyAudio stream — must be done on a background thread.
        self.microphone = sr.Microphone()

        # pause_threshold: how many seconds of silence = end of phrase.
        # 0.8s is a good balance — not too eager, not too slow.
        self.recognizer.pause_threshold = 0.8

        # energy_threshold: minimum audio energy to detect as speech.
        # Lower = more sensitive (picks up quiet speech but also noise).
        # adjust_for_ambient_noise() will auto-tune this below.
        self.recognizer.energy_threshold = 300

        # dynamic_energy_threshold: automatically adjusts energy threshold
        # to ambient noise levels. Helpful in variable environments.
        self.recognizer.dynamic_energy_threshold = True

        print("[Listener] Microphone initialised.")

    def listen(self):
        """
        Opens the mic, listens for one phrase, and returns it as text.
        Returns None if nothing was heard or an error occurred.

        timeout          = how long to wait for speech to START (seconds)
        phrase_time_limit = max length of a single spoken phrase (seconds)
        """
        try:
            with self.microphone as source:
                # Calibrate to ambient noise. 0.3s is fast but good enough.
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                print("[Listener] Listening...")

                # Actually listen. This blocks until speech ends or timeout.
                audio = self.recognizer.listen(
                    source,
                    timeout=6,            # Give up waiting after 6s of silence
                    phrase_time_limit=12  # Max 12s per phrase
                )

        except sr.WaitTimeoutError:
            # No speech detected within the timeout window. Not an error.
            return None
        except Exception as e:
            # Microphone access error (e.g., device unplugged).
            print(f"[Listener] Microphone error: {e}")
            self._log_error(e)
            return None

        # --- Send audio to Google Speech API for transcription ---
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"[Listener] You said: {text}")
            return text

        except sr.UnknownValueError:
            # Google couldn't understand the audio (too quiet, too noisy, etc.)
            print("[Listener] Could not understand audio. Please speak clearly.")
            return None

        except sr.RequestError as e:
            # Network error or Google API is down.
            print(f"[Listener] Google API error: {e}")
            self._log_error(e)
            return None

        except Exception as e:
            print(f"[Listener] Unexpected error: {e}")
            self._log_error(e)
            return None

    def _log_error(self, error):
        """
        Saves error details to a log file for debugging later.
        The underscore in _log_error means: "this is a private helper method,
        only used inside this class."
        """
        try:
            log_file = logs_location / "error.report.txt"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "a") as f:
                f.write(f"[VoiceHandler Error]: {error}\n")
        except Exception:
            pass  # Don't crash while trying to log a crash
