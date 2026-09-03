#!/usr/bin/env python3
import os
import sys
import platform
import time
import asyncio
import edge_tts
import subprocess
import psutil
from RealtimeSTT import AudioToTextRecorder
import logging
import threading
import traceback
import cv2
import numpy as np
import datetime
import json
import webbrowser
import re
import ollama
import math
import urllib.request
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QGraphicsDropShadowEffect, QScrollArea, QFrame
from PyQt6.QtCore import QTimer, Qt, QRectF, QPointF, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QColor, QPolygonF, QImage, QPixmap, QFont, QBrush
import pyautogui

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    HAS_MEDIAPIPE = True
except ImportError:
    HAS_MEDIAPIPE = False
    print("[System Notice] mediapipe not available — hand-tracking gestures disabled, camera preview still works.")

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# =====================================================================
# CRASH LOGGING — writes every uncaught exception to disk with a full
# traceback, including ones raised inside Qt callbacks (paintEvent,
# timers, threads) that PyQt6 can otherwise swallow silently.
# =====================================================================
CRASH_LOG_PATH = "/tmp/parc_crash.log"

def _log_crash(exc_type, exc_value, exc_tb):
    with open(CRASH_LOG_PATH, "a") as f:
        f.write(f"\n\n===== CRASH at {datetime.datetime.now()} =====\n")
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    traceback.print_exception(exc_type, exc_value, exc_tb, file=sys.stderr)
    print(f"\n[CRASH LOGGED] Full traceback written to {CRASH_LOG_PATH}\n", file=sys.stderr)

sys.excepthook = _log_crash

def _log_thread_crash(args):
    _log_crash(args.exc_type, args.exc_value, args.exc_traceback)

threading.excepthook = _log_thread_crash

print(f"DEBUG: Running with: {sys.executable}")
print(f"DEBUG: sys.path: {sys.path}")
# Suppress standard subsystem clutter logs without hiding Python crashes
logging.getLogger("RealtimeSTT").setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

MODEL_NAME = "hermes3:3b"

# Global System State Variables
LAST_EXECUTION_TIME = 0.0
COOLDOWN_PERIOD = 3.0
IS_SPEAKING = False

# ==========================================
# 1. THE ADVANCED ENGINE ARRAYS (TOOLS)
# ==========================================

def execute_system_bash(bash_command: str) -> str:
    """
    Executes a raw bash command directly in the Arch Linux shell environment and returns the output.
    Use this to fix system flags, inspect logs, manage files, or check active network connections.
    """
    print(f"\n[MAINFRAME ACTUATION] Running Shell Command: {bash_command}")
    try:
        # 10-Second structural safety timeout to prevent hanging commands
        result = subprocess.run(bash_command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip() if result.stdout else ""
        errors = result.stderr.strip() if result.stderr else ""

        return f"[Exit Code: {result.returncode}]\nSTDOUT:\n{output}\nSTDERR:\n{errors}"
    except subprocess.TimeoutExpired:
        return "[System Warning] Operational sequence timed out."
    except Exception as e:
        return f"[System Error] Shell execution critical failure: {e}"


def manipulate_x11_windows(action_type: str, application_query: str = "") -> str:
    """Controls and reshapes active windows on the X11 Display Server environment."""
    action = str(action_type).lower().strip()
    query = str(application_query).lower().strip()
    try:
        if "minimize_all" in action or "clear" in action:
            subprocess.run(["xdotool", "key", "super+d"])
            return "[System Success] All workspace modules minimized."

        # Grab the target Window ID
        active_window = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()

        # ==========================================
        # THE DESKTOP SHIELD (PREVENTS SYSTEM ZOOM/CRASH)
        # ==========================================
        try:
            window_name = subprocess.check_output(["xdotool", "getwindowname", active_window]).decode().strip().lower()
            if "plasma" in window_name or "desktop" in window_name or window_name == "":
                print("[System Shield] Blocked attempt to manipulate root desktop shell.")
                return "[System Warning] Cannot reshape the root desktop environment."
        except Exception:
            pass # Failsafe if getwindowname throws an error

        # ==========================================
        # STANDARD WINDOW MANIPULATION
        # ==========================================
        if "maximize" in action:
            subprocess.run(["xdotool", "windowsize", active_window, "100%", "100%"])
            return "[System Success] Target window geometry maximized."

        elif "split" in action:
            subprocess.run(["xdotool", "windowsize", active_window, "50%", "100%"])
            subprocess.run(["xdotool", "windowmove", active_window, "0", "0"])

            subprocess.Popen(["setsid", "konsole"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            time.sleep(0.4)

            new_terminal = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            subprocess.run(["xdotool", "windowsize", new_terminal, "50%", "100%"])
            subprocess.run(["xdotool", "windowmove", new_terminal, "960", "0"])
            return "[System Success] Asymmetric terminal window split applied."

        return "[System Error] Invalid window operation requested."
    except Exception as e:
        return f"[System Error] X11 interface rejected interaction: {e}"

def control_hardware_peripherals(component_target: str, adjustment_value: str) -> str:
    """
    Modifies physical hardware environment states such as system volume or monitor layouts.
    Targets:
    - 'volume' (values: 'mute', 'unmute', 'up', 'down', or explicit percentages like '80%')
    - 'display' (values: 'off', 'on' via xset engine)
    """
    target = str(component_target).lower().strip()
    val = str(adjustment_value).lower().strip()
    try:
        if "volume" in target:
            if "mute" in val:
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", "mute"], check=True)
                return "[System Success] Core audio arrays muted."
            elif "unmute" in val:
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", "unmute"], check=True)
                return "[System Success] Core audio arrays unmuted."
            elif "up" in val:
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", "5%+"], check=True)
            elif "down" in val:
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", "5%-"], check=True)
            else:
                clean_pct = ''.join(c for c in val if c.isdigit()) + "%"
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", clean_pct], check=True)
            return f"[System Success] System output audio modified to: {val}"

        elif "display" in target:
            if "off" in val:
                subprocess.run(["xset", "dpms", "force", "off"])
                return "[System Success] Display panel interface deactivated."
            elif "on" in val:
                subprocess.run(["xset", "dpms", "force", "on"])
                return "[System Success] Display panel interface energized."

        return "[System Error] Unknown component target asset."
    except Exception as e:
        return f"[System Error] Peripheral modification failure: {e}"

def capture_desktop_vision() -> str:
    """Captures an instantaneous raw screenshot of the current X11 display server output layout."""
    output_path = "/tmp/parc_vision_matrix.png"
    try:
        subprocess.run(["import", "-window", "root", output_path], check=True) # Uses ImageMagick core tool
        return f"[System Success] Display frame captured successfully at: {output_path}"
    except Exception as e:
        return f"[System Error] Vision frame capture rejected: {e}"

def launch_system_application(app_name: str, cinematic_mode: bool = True) -> str:
    """Deploys any native application binary installed locally on the Linux machine."""
    app = str(app_name).lower().strip()
    try:
        if cinematic_mode:
            cmd = f'xdotool key Alt+space && sleep 0.3 && xdotool type --delay 40 "{app}" && sleep 0.1 && xdotool key Return'
            subprocess.Popen(cmd, shell=True)
            return f"[System Success] Initiating cinematic launch routine for: {app}"
        else:
            cmd = f'setsid {app} >/dev/null 2>&1 &'
            subprocess.Popen(cmd, shell=True)
            return f"[System Success] Background session detached for application: {app}"
    except Exception as e:
        return f"[System Error] Application initialization fault: {e}"

def open_web_destination(destination_name: str = "browser") -> str:
    """Launches high-frequency web addresses via your primary system web browser."""
    dest = str(destination_name).lower().strip()
    try:
        url = "https://www.google.com" # Default fallback
        if "youtube" in dest:
            url = "https://www.youtube.com"
        elif "chess" in dest:
            url = "https://www.chess.com"
        elif "browser" in dest or "google" in dest or "chrome" in dest:
            url = "https://www.google.com"

        subprocess.Popen(["google-chrome-stable", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"[System Success] Opened web dashboard for {dest}."
    except Exception as e:
        return f"[System Error] Web routing fault: {e}"

def play_music_on_youtube(search_query: str = "music") -> str:
    """Searches for a specific media track stream using yt-dlp and plays it automatically."""
    if not search_query: search_query = "music"
    try:
        cmd = ["yt-dlp", "--get-id", f"ytsearch1:{search_query}"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        video_id = result.stdout.strip()
        if video_id:
            url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
            subprocess.Popen([
                "google-chrome-stable",
                "--user-data-dir=/tmp/parc_media_profile",
                "--autoplay-policy=no-user-gesture-required",
                url
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"[System Success] Found match. Playing '{search_query}' inside media sandbox profile."
        return "[System Error] Extraction engine failed to isolate a matching video ID."
    except Exception as e:
        return f"[System Error] Media streaming pipeline disrupted: {e}"

def get_system_telemetry() -> str:
    """Extracts a complete operational vector detailing CPU temperature, memory usage, disk constraints, and active processes."""
    try:
        temps = psutil.sensors_temperatures()
        cpu_temp = "Restricted"
        if temps:
            for name, entries in temps.items():
                if entries:
                    cpu_temp = f"{entries[0].current}°C"
                    break
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        proc_count = len(psutil.pids())
        return f"Core Temp: {cpu_temp} | Memory Load: {mem}% | Main Partition Space Used: {disk}% | Active PIDs: {proc_count} processes."
    except Exception as e:
        return f"Telemetry extraction fault: {e}"

def lock_system_workstation() -> str:
    """Locks the Linux terminal and display environment instantly."""
    subprocess.run(["xdg-screensaver", "lock"])
    return "[System Success] Operational terminal locked."

def terminate_assistant_core() -> str:
    """Powers down the system agent runtime loop."""
    return "[System Action] AI Core shutdown sequence executed."


TOOL_REGISTRY = {
    'execute_system_bash': execute_system_bash,
    'manipulate_x11_windows': manipulate_x11_windows,
    'control_hardware_peripherals': control_hardware_peripherals,
    'capture_desktop_vision': capture_desktop_vision,
    'launch_system_application': launch_system_application,
    'open_web_destination': open_web_destination,
    'play_music_on_youtube': play_music_on_youtube,
    'get_system_telemetry': get_system_telemetry,
    'lock_system_workstation': lock_system_workstation,
    'terminate_assistant_core': terminate_assistant_core
}

# ==========================================
# 2. AUDIO FEEDBACK NETWORK (TTS)
# ==========================================

def speak(text, recorder_instance=None):
    global IS_SPEAKING
    if not text: return

    IS_SPEAKING = True
    if recorder_instance:
        try: recorder_instance.stop()
        except: pass

    print(f"P.A.R.C: {text}")
    output_file = "/tmp/parc_voice_buffer.mp3"

    try:
        asyncio.run(edge_tts.Communicate(text, "en-US-AriaNeural").save(output_file))
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", output_file],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        if recorder_instance:
            time.sleep(0.2)
            try: recorder_instance.start()
            except: pass
        IS_SPEAKING = False

# ==========================================
# 3. KINETIC INITIALIZATION
# ==========================================

def run_startup_sequence(recorder=None):
    now = datetime.datetime.now()
    greeting = "Good morning, Atmim Sir." if now.hour < 12 else "Good afternoon, Atmim Sir." if now.hour < 18 else "Good evening, Atmim Sir."
    telemetry = get_system_telemetry()
    speak(f"{greeting} System diagnostic complete. {telemetry} All channels online.", recorder)

# ==========================================
# 4. INTELLECT ROUTING PIPELINE
# ==========================================


def execute_command(command_text, recorder_instance):
    global LAST_EXECUTION_TIME

    # Cooldown and basic filter
    if time.time() - LAST_EXECUTION_TIME < COOLDOWN_PERIOD or IS_SPEAKING:
        return

    # 1. AGGRESSIVE PUNCTUATION & WAKE-WORD STRIPPING
    clean_input = command_text.lower().strip()
    while clean_input.startswith((".", ",", "-", " ")):
        clean_input = clean_input[1:]
    clean_input = clean_input.replace(".", "")

    # WAKE-WORD CLEANING & ENFORCEMENT MATRIX
    wake_variants = ["park ", "parc ", "park, ", "parc, "]
    wake_word_detected = False

    # Edge Case: If you only say the name and nothing else
    if clean_input in ["parc", "park"]:
        wake_word_detected = True
        clean_input = ""
    else:
        # Standard Case: Check if the phrase starts with a wake variant
        for variant in wake_variants:
            if clean_input.startswith(variant):
                clean_input = clean_input[len(variant):].strip()
                wake_word_detected = True
                break

    # THE ENFORCEMENT GATE: If no wake word was spoken, kill execution immediately
    if not wake_word_detected:
        return  # Drops out silently. Ollama and your custom tools will never trigger.

    # Validate remaining command length (only if a command was actually given)
    if clean_input != "" and len(clean_input) < 3:
        return

    print(f"\n-> Captured System Trigger Input: '{clean_input}'")


    # =====================================================================
    # # SYSTEM DEFENSE MATRIX: EMERGENCY PROTOCOLS
    # =====================================================================
    if "code red" in clean_input:
        print("[CRITICAL]: CODE RED DETECTED. Executing immediate lockdown.")

        # 1. Audible deployment warning
        speak("EXECUTING CODE RED", recorder_instance)

        # 2. Kinetic Lockdown Engine (Resilient multi-tool attack to lock X11/Arch)
        import subprocess
        lock_commands = [
            ["loginctl", "lock-session"],          # Standard systemd lock
            ["xdg-screensaver", "lock"],           # Universal X11 desktop lock
            ["i3lock", "-c", "000000"],            # Fallback if using vanilla i3wm
            ["gnome-screensaver-command", "-l"]    # Fallback if using GNOME environment
        ]

        for cmd in lock_commands:
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                continue

        # 3. Secure variables and exit instantly
        LAST_EXECUTION_TIME = time.time()
        return

    # =====================================================================
    # # DIRECT HARDWARE STATS INTERCEPTOR (BYPASS LLM & CIRCUITS)
    # =====================================================================
    if any(x in clean_input for x in ["temperature", "cpu", "core temp", "ram", "memory", "pc stats", "disk", "partition"]):
        print("[System Interceptor]: Isolating targeted hardware query.")
        try:
            # 1. Fetch the complete telemetry string from your registry
            full_stats = str(TOOL_REGISTRY["get_system_telemetry"]())
            parts = [p.strip() for p in full_stats.split("|")]

            # 2. Extract sections safely using simple searches
            cpu_stat = next((p for p in parts if "temp" in p.lower() or "core" in p.lower()), "CPU metrics missing")
            ram_stat = next((p for p in parts if "memory" in p.lower() or "ram" in p.lower()), "RAM metrics missing")
            disk_stat = next((p for p in parts if "partition" in p.lower() or "space" in p.lower()), "Disk metrics missing")

            # 3. Check what the user actually said and pick the matching piece
            if "ram" in clean_input or "memory" in clean_input:
                clean_speech = f"{ram_stat}, Sir."
            elif "cpu" in clean_input or "temp" in clean_input or "temperature" in clean_input:
                clean_speech = f"{cpu_stat}, Sir."
            elif "disk" in clean_input or "space" in clean_input or "partition" in clean_input:
                clean_speech = f"{disk_stat}, Sir."
            else:
                clean_speech = f"Full diagnostic details: {full_stats}"

            # 4. Speak only the isolated answer
            speak(clean_speech, recorder_instance)

        except Exception as e:
            print(f"[Interceptor Error]: Hardware mapping failed: {e}")
            speak("Sensor array communication error, Sir.", recorder_instance)

        LAST_EXECUTION_TIME = time.time()
        return


    # 2. ELITE ABSOLUTE CIRCUIT BREAKER
    if clean_input.startswith(("open ", "launch ", "go to ", "play ", "minimize", "maximize", "split")):

        # --- ROUTE A: WINDOW MANAGEMENT ---
        if clean_input.startswith(("minimize", "maximize", "split")):
            speak("Adjusting visual matrix, Sir.", recorder_instance)
            if "minimize" in clean_input:
                manipulate_x11_windows("minimize_all")
            elif "maximize" in clean_input:
                manipulate_x11_windows("maximize")
            elif "split" in clean_input:
                manipulate_x11_windows("split")
            LAST_EXECUTION_TIME = time.time()
            return

        # --- ROUTE B: MUSIC PLAYBACK ---
        if clean_input.startswith("play "):
            song_query = clean_input.replace("play ", "", 1).strip()
            speak(f"Initializing audio stream for {song_query}, Sir.", recorder_instance)
            play_music_on_youtube(song_query)
            LAST_EXECUTION_TIME = time.time()
            return

        # --- ROUTE C: SYSTEM APPLICATIONS & WEB ---
        # 1. Clean wake words ("park", "parc") and punctuation (commas, periods)
        clean_text = clean_input.lower().replace(",", "").replace(".", "")
        clean_text = clean_text.replace("park", "").replace("parc", "").strip()
        target = clean_text.replace("open ", "").replace("launch ", "").replace("go to ", "").strip()

        # Web Destinations Mapping
        url_map = {
            "youtube": "https://youtube.com",
            "browser": "https://google.com",
            "chrome": "https://google.com",
            "chess": "https://chess.com",
            "google": "https://google.com",
            "underrun": "https://underrun.com"
        }

        if target in url_map:
            # Delegate entirely to your unified web function to avoid duplicate triggers
            open_web_destination(target)
            try:
                speak(f"Accessing web interface for {target}, Sir.", recorder_instance)
            except Exception as e:
                print(f"[Audio Error Handled]: {e}")
            LAST_EXECUTION_TIME = time.time()
            return

        # Semantic Translation Dictionary for Linux
        app_dictionary = {
            "file manager": ["dolphin", "nautilus", "thunar", "pcmanfm"],
            "files": ["dolphin", "nautilus", "thunar", "pcmanfm"],
            "settings": ["systemsettings", "gnome-control-center", "xfce4-settings-manager"],
            "system settings": ["systemsettings", "gnome-control-center"],
            "calculator": ["kcalc", "gnome-calculator", "galculator"],
            "terminal": ["konsole", "gnome-terminal", "alacritty", "kitty"],
            "system monitor": ["ksysguard", "gnome-system-monitor", "btop", "htop"]
        }

        # Determine which binaries to attempt launching
        binaries_to_try = [target]
        for human_phrase, linux_binaries in app_dictionary.items():
            if human_phrase in target:
                binaries_to_try = linux_binaries
                break

        # Kinetic Launch Sequence
        launched = False
        for binary in binaries_to_try:
            try:
                import subprocess
                subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[System] SUCCESS: Fired Linux binary '{binary}'")
                launched = True
                break
            except Exception:
                continue

        if launched:
            try:
                speak(f"Initializing {target}, Sir.", recorder_instance)
            except Exception as e:
                print(f"[Audio Error Handled]: {e}")
        else:
            print(f"[System] FAILURE: Could not locate a valid binary for '{target}'")
            try:
                speak("I could not locate that application in the system path, Sir.", recorder_instance)
            except Exception as e:
                print(f"[Audio Error Handled]: {e}")

        LAST_EXECUTION_TIME = time.time()
        return

    # 3. LLM EXECUTION AND TOOL ROUTING
    messages = [
        {
            "role": "system",
            "content": (
                "You are P.A.R.C., an ultra-elite built by Atmim(Full name Sheikh Rabbe Atmim), omnipotent system intelligence running on Arch Linux with an X11 engine. "
                "You address your creator as 'Sir'. "
                "CRITICAL DIRECTIVE: If you need to perform an action, use the designated tool_call function. "
                "NEVER write out tool schemas, JSON blocks, or function names in your text response. "
                "If the user is asking a conversational question, answer naturally in plain, concise English without formatting artifacts."
            )
        },
        {"role": "user", "content": command_text}
    ]

    try:
        response = ollama.chat(
            model="hermes3:3b",
            messages=messages,
            tools=list(TOOL_REGISTRY.values())
        )

        # =====================================================================
        # # HANDLE NATIVE TOOL ACTIONS
       # =====================================================================
        if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
            primary_call = response.message.tool_calls[0]
            func_name = primary_call.function.name
            func_args = primary_call.function.arguments

            print(f"[Core Routing] Orchestrating Action Matrix: {func_name}")

            if func_name in TOOL_REGISTRY:
                if func_name == 'execute_system_bash':
                    speak("Interfacing with terminal environment, Sir.", recorder_instance)
                elif func_name == 'manipulate_x11_windows':
                    speak("Reconfiguring active window arrays, Sir.", recorder_instance)
                elif func_name == 'control_hardware_peripherals':
                    speak("Adjusting component signals, Sir.", recorder_instance)
                elif func_name == 'capture_desktop_vision':
                    speak("Caching visual display coordinates, Sir.", recorder_instance)
                elif func_name == 'launch_system_application':
                    app_name = func_args.get('app_name', 'application')
                    speak(f"Initializing process run-vector for {app_name}, Sir.", recorder_instance)

                # Execute the actual tool function from your registry
                TOOL_REGISTRY[func_name](**func_args)
                LAST_EXECUTION_TIME = time.time()
                return

        # =====================================================================
        # # HANDLE CASUAL CHAT RESPONSES SAFELY
        # =====================================================================
        else:
            raw_content = response.message.content if response.message.content else ""
            raw_lower = raw_content.lower()

            # --- 1. HARDWARE INTERCEPTOR (THE KILL-SHOT) ---
            if 'control_hardware_peripherals' in raw_lower and 'volume' in raw_lower:
                import subprocess
                if 'unmute' in raw_lower:
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "unmute"])
                    clean_speech = "Audio arrays unmuted, Sir."
                elif 'mute' in raw_lower:
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "mute"])
                    clean_speech = "Audio arrays muted, Sir."
                elif 'down' in raw_lower or 'decrease' in raw_lower or '5%-' in raw_lower:
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "5%-"])
                    clean_speech = "Decreasing system volume, Sir."
                else:
                    subprocess.run(["amixer", "-D", "pulse", "set", "Master", "5%+"])
                    clean_speech = "Increasing system volume, Sir."

            # --- 2. RESILIENT PARSER FOR MIXED TEXT, CODE, & JSON ---
            else:
                import re
                import json

                tool_executed = False
                clean_speech = ""


                json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
                if json_match:
                    try:
                        potential_json = json_match.group(0).replace("'", '"')
                        tool_data = json.loads(potential_json)

                        if "name" in tool_data and tool_data["name"] in TOOL_REGISTRY:
                            f_name = tool_data["name"]
                            f_args = tool_data.get("arguments", {})

                            # SAFE ARGUMENT EXECUTION LAYER
                            try:
                                # Try to execute with the model's arguments first
                                tool_result = TOOL_REGISTRY[f_name](**f_args)
                            except TypeError:
                                # Fallback: If LLM sent hallucinated arguments, strip them and run clean
                                print(f"[System Notice]: Stripping unexpected arguments from {f_name}")
                                tool_result = TOOL_REGISTRY[f_name]()

                            if tool_result:
                                clean_speech = str(tool_result)
                                tool_executed = True

                    except Exception as e:
                        print(f"[Tool Execution Leak Error]: {e}")

                # If no tool was triggered, process normal conversational text
                if not tool_executed:
                    clean_text = re.sub(r'\{.*?\}', '', raw_content, flags=re.DOTALL)        # Wipe JSON blocks
                    clean_text = re.sub(r'.*?', '', clean_text, flags=re.DOTALL)      # Wipe markdown code blocks
                    clean_text = re.sub(r'<.?>|\]\)\)\s\{', '', clean_text)                # Wipe brackets and tag leaks

                    clean_speech = clean_text.strip()

                    # Resilient Fallback if regex stripping leaves nothing but whitespace
                    if not clean_speech or len(clean_speech) < 3:
                        clean_speech = "System metrics synchronized, Sir."

            # --- 3. AUDIBLE FEEDBACK INTERFACE ---
            speak(clean_speech, recorder_instance)
            LAST_EXECUTION_TIME = time.time()

    except Exception as err:
        print(f"[System Execution Error]: {err}")




## =====================================================================
# 5. VISION ENGINE (MediaPipe Hand Tracking & Window Control)
# =====================================================================

class VisionEngine(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    move_window_signal = pyqtSignal(int, int)
    status_signal = pyqtSignal(str)
    opacity_signal = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self.prev_x = None
        self.prev_y = None

        # Mouse States
        self.is_left_pinching = False
        self.is_right_pinching = False

        # Grab (Window Move) States
        self.is_grabbing = False
        self.prev_grab_x = None
        self.prev_grab_y = None

        self._last_timestamp_ms = 0

    def run(self):

        try:
            import pyautogui
            pyautogui.FAILSAFE = False
            mouse_active = True
        except ImportError:
            print("[SYSTEM WARNING] pyautogui not found")
            mouse_active = False

        cap = None
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            for idx in [0, 1, 2]:
                c = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                if c.isOpened():
                    for _ in range(3):
                        ret, test_frame = c.read()
                        if ret and test_frame is not None:
                            cap = c
                            break
                        time.sleep(0.05)
                    if cap is not None:
                        break
                    c.release()

        if cap is None or not cap.isOpened():
            self.status_signal.emit("CAMERA ERROR ")
            return

        detector = None
        if 'HAS_MEDIAPIPE' in globals() and HAS_MEDIAPIPE:
            try:
                model_path = "/tmp/hand_landmarker.task"
                if not os.path.exists(model_path):
                    urllib.request.urlretrieve(
                        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
                        model_path
                    )

                base_options = python.BaseOptions(model_asset_path=model_path)
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    running_mode=vision.RunningMode.VIDEO,
                    num_hands=1,
                    min_hand_detection_confidence=0.5,
                    min_hand_presence_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                detector = vision.HandLandmarker.create_from_options(options)
                self.status_signal.emit(" MOTION TRACKING ACTIVED")
            except Exception as e:
                self.status_signal.emit(f"MEDIAPIPE ERROR // {e}")
                print(f"[MEDIAPIPE INIT ERROR] {e}")

        while not self.isInterruptionRequested():
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.03)
                continue

            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            rgb_frame = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if detector:
                try:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                    timestamp_ms = int(time.time() * 1000)
                    if timestamp_ms <= self._last_timestamp_ms:
                        timestamp_ms = self._last_timestamp_ms + 1
                    self._last_timestamp_ms = timestamp_ms

                    detection_result = detector.detect_for_video(mp_image, timestamp_ms)

                    if detection_result and detection_result.hand_landmarks:
                        for hand_landmarks in detection_result.hand_landmarks:
                            # Base and joints
                            wrist = hand_landmarks[0]
                            index_mcp = hand_landmarks[5]
                            middle_mcp = hand_landmarks[9]
                            ring_mcp = hand_landmarks[13]
                            pinky_mcp = hand_landmarks[17]

                            # Tips
                            thumb_tip = hand_landmarks[4]
                            index_tip = hand_landmarks[8]
                            middle_tip = hand_landmarks[12]
                            ring_tip = hand_landmarks[16]
                            pinky_tip = hand_landmarks[20]

                            def get_dist(lm1, lm2):
                                return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

                            # -------------------------------------------------------------
                            # 1. DETECT CLOSED FIST (GRAB)
                            # If tips are closer to the wrist than the knuckles are to the wrist, fingers are folded
                            # -------------------------------------------------------------
                            is_fist = (
                                get_dist(index_tip, wrist) < get_dist(index_mcp, wrist) and
                                get_dist(middle_tip, wrist) < get_dist(middle_mcp, wrist) and
                                get_dist(ring_tip, wrist) < get_dist(ring_mcp, wrist) and
                                get_dist(pinky_tip, wrist) < get_dist(pinky_mcp, wrist)
                            )

                            if is_fist:
                                # Anchor tracking to the middle knuckle (highly stable during a fist)
                                knuckle_px = (int(middle_mcp.x * w), int(middle_mcp.y * h))

                                # Draw a massive red indicator showing GRAB is locked
                                cv2.circle(rgb_frame, knuckle_px, 12, (0, 0, 255), -1)
                                cv2.putText(rgb_frame, "GRAB", (knuckle_px[0]-40, knuckle_px[1]-20),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                                if not self.is_grabbing:
                                    self.is_grabbing = True
                                    self.prev_grab_x, self.prev_grab_y = knuckle_px[0], knuckle_px[1]
                                else:
                                    # Calculate drag delta
                                    dx = int((knuckle_px[0] - self.prev_grab_x) * 1.5)
                                    dy = int((knuckle_px[1] - self.prev_grab_y) * 1.5)

                                    # Emit to main GUI to move window
                                    if abs(dx) > 1 or abs(dy) > 1:
                                        self.move_window_signal.emit(dx, dy)
                                        self.prev_grab_x, self.prev_grab_y = knuckle_px[0], knuckle_px[1]

                                # Kill all mouse interactions while grabbing
                                self.is_left_pinching = False
                                self.is_right_pinching = False
                                self.prev_y = None

                            else:
                                # -------------------------------------------------------------
                                # 2. MOUSE TRACKING & GESTURES (Only runs if hand is open)
                                # -------------------------------------------------------------
                                self.is_grabbing = False
                                self.prev_grab_x = None
                                self.prev_grab_y = None

                                thm_px = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                                idx_px = (int(index_tip.x * w), int(index_tip.y * h))
                                mid_px = (int(middle_tip.x * w), int(middle_tip.y * h))

                                cv2.circle(rgb_frame, thm_px, 6, (0, 240, 255), -1)
                                cv2.circle(rgb_frame, idx_px, 6, (0, 255, 136), -1)
                                cv2.circle(rgb_frame, mid_px, 6, (255, 0, 136), -1)

                                if mouse_active:
                                    try:
                                        screen_w, screen_h = pyautogui.size()
                                        target_x = int(index_tip.x * screen_w)
                                        target_y = int(index_tip.y * screen_h)
                                        pyautogui.moveTo(target_x, target_y, _pause=False)

                                        dist_thumb_index = get_dist(index_tip, thumb_tip)
                                        dist_index_middle = get_dist(index_tip, middle_tip)
                                        dist_thumb_middle = get_dist(middle_tip, thumb_tip)

                                        if dist_thumb_index < 0.055:
                                            cv2.line(rgb_frame, idx_px, thm_px, (0, 255, 136), 2)
                                            if not self.is_left_pinching:
                                                self.is_left_pinching = True
                                                pyautogui.click(button='left')
                                        else:
                                            self.is_left_pinching = False

                                        if dist_index_middle < 0.055:
                                            cv2.line(rgb_frame, idx_px, mid_px, (255, 0, 136), 2)
                                            if not self.is_right_pinching:
                                                self.is_right_pinching = True
                                                pyautogui.click(button='right')
                                        else:
                                            self.is_right_pinching = False

                                        if dist_thumb_middle < 0.055:
                                            cv2.line(rgb_frame, mid_px, thm_px, (0, 240, 255), 2)
                                            if self.prev_y is not None:
                                                dy_scroll = mid_px[1] - self.prev_y
                                                if dy_scroll > 5:
                                                    pyautogui.scroll(-5)
                                                elif dy_scroll < -5:
                                                    pyautogui.scroll(5)
                                            self.prev_y = mid_px[1]
                                        else:
                                            self.prev_y = None

                                    except Exception as mouse_err:
                                        pass
                    else:
                        self.is_grabbing = False
                        self.is_left_pinching = False
                        self.is_right_pinching = False
                        self.prev_y = None
                except Exception as vision_err:
                    print(f"[VISION PROCESS ERROR] {vision_err}")

            q_img = QImage(rgb_frame.data, w, h, c * w, QImage.Format.Format_RGB888)
            self.change_pixmap_signal.emit(q_img.copy())
            time.sleep(0.016)

        if detector:
            try:
                detector.close()
            except Exception:
                pass
        if cap:
            cap.release()

    def stop(self):
        self.requestInterruption()
        self.quit()
        self.wait(1000)

# =====================================================================
# 6. PARC V1 3D HOLOGRAPHIC HUD (ROUND SINGULARITY CORE)
# =====================================================================
class ParcHUD(QMainWindow):
    command_signal = pyqtSignal(str)

    def __init__(self, recorder_instance=None):
        super().__init__()
        self.recorder = recorder_instance

        # --- 1. Dense 3D Neural Cloud Setup (Fibonacci Sphere) ---
        self.num_nodes = 180
        self.nodes_3d = []
        phi = math.pi * (math.sqrt(5.0) - 1.0)  # Golden angle
        for i in range(self.num_nodes):
            y = 1 - (i / float(self.num_nodes - 1)) * 2
            radius = math.sqrt(1 - y * y)
            theta = phi * i
            x = math.cos(theta) * radius
            z = math.sin(theta) * radius
            r_var = random.uniform(0.85, 1.15)
            self.nodes_3d.append([x * r_var, y * r_var, z * r_var])

        # --- 2. Roaming Ambient Dust Particles ---
        self.num_particles = 140
        self.particles_3d = []
        for _ in range(self.num_particles):
            r = random.uniform(70, 340)
            p_theta = random.uniform(0, 2 * math.pi)
            p_phi = random.uniform(-math.pi / 2, math.pi / 2)
            speed = random.uniform(0.4, 1.2)
            size = random.uniform(1.2, 3.2)
            self.particles_3d.append({
                'r': r,
                'theta': p_theta,
                'phi': p_phi,
                'speed': speed,
                'size': size,
                'x': r * math.cos(p_phi) * math.cos(p_theta),
                'y': r * math.cos(p_phi) * math.sin(p_theta),
                'z': r * math.sin(p_phi)
            })

        # --- 3. Centered Voice Equalizer Engine (48 Radial Bars) ---
        self.num_voice_bars = 48
        self.voice_frequencies = [random.uniform(0.1, 0.4) for _ in range(self.num_voice_bars)]
        self.mic_volume = 0.0

        # --- 4. 3D Rotation Controllers ---
        self.rot_x = 15.0
        self.rot_y = 0.0
        self.rot_z = 0.0

        self.init_ui()

        # Signal connection
        self.command_signal.connect(self.update_command_display)

        # Voice Listening Thread
        self.audio_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.audio_thread.start()

        self.anim_angle = 0

        # ~60 FPS Timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate_hud)
        self.anim_timer.start(16)

    def project_3d(self, x, y, z, cx, cy, rx, ry, rz):
        """Projects 3D world coordinates onto 2D viewport with perspective depth."""
        rad_x, rad_y, rad_z = math.radians(rx), math.radians(ry), math.radians(rz)

        # Rotation X
        y1 = y * math.cos(rad_x) - z * math.sin(rad_x)
        z1 = y * math.sin(rad_x) + z * math.cos(rad_x)

        # Rotation Y
        x2 = x * math.cos(rad_y) + z1 * math.sin(rad_y)
        z2 = -x * math.sin(rad_y) + z1 * math.cos(rad_y)

        # Rotation Z
        x3 = x2 * math.cos(rad_z) - y1 * math.sin(rad_z)
        y3 = x2 * math.sin(rad_z) + y1 * math.cos(rad_z)

        fov = 520
        dist = 480
        denom = dist + z2
        if denom == 0:
            denom = 0.0001
        scale = fov / denom

        px = cx + x3 * scale
        py = cy + y3 * scale
        return px, py, scale, z2

    def update_command_display(self, text: str):
        self.cmd_lbl.setText(f"PARC V1.0 > {text.upper()}")

    def listen_loop(self):
        while True:
            try:
                if self.recorder is not None:
                    text = self.recorder.text()
                    if text:
                        self.mic_volume = 1.0
                        self.command_signal.emit(text)
                        if "execute_command" in globals():
                            execute_command(text, self.recorder)
                time.sleep(0.1)
            except Exception:
                time.sleep(1.0)

    def set_hud_opacity(self, opacity: float):
        self.setWindowOpacity(1.0)

    def update_frame(self, q_img):
        """Receives QImage from VisionEngine thread and renders it on self.cam_label."""
        try:
            if hasattr(self, 'cam_label') and self.cam_label:
                # Ensure the label actually has valid dimensions before scaling
                target_size = self.cam_label.size()
                if target_size.width() <= 1 or target_size.height() <= 1:
                    # Fallback default frame size if widget size is not yet rendered
                    target_size = QSize(320, 240)

                pixmap = QPixmap.fromImage(q_img)
                scaled_pixmap = pixmap.scaled(
                    target_size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.cam_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"[GUI ERROR] Failed to update camera frame: {e}")

    def update_status(self, text):
        self.status_lbl.setText(text)

    def move_gui(self, dx, dy):
        pos = self.pos()
        self.move(pos.x() + dx, pos.y() + dy)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if hasattr(self, 'vision_thread') and hasattr(self.vision_thread, 'stop'):
                self.vision_thread.stop()
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        if hasattr(self, 'vision_thread') and self.vision_thread.isRunning():
            self.vision_thread.stop()
            self.vision_thread.wait()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'cam_label'):
            cam_w, cam_h = 220, 220
            margin = 35
            self.cam_label.setGeometry(margin, self.height() - cam_h - margin, cam_w, cam_h)

    def animate_hud(self):
        # 3D Gyroscope Rotations
        self.rot_y = (self.rot_y + 0.8) % 360
        self.rot_x = (self.rot_x + 0.3) % 360
        self.rot_z = (self.rot_z + 0.2) % 360

        self.anim_angle = (self.anim_angle + 2) % 360

        # Decaying mic volume pulse
        if self.mic_volume > 0.05:
            self.mic_volume *= 0.92
        else:
            self.mic_volume = 0.0

        # Dynamic Voice Bar Frequency Waves
        for i in range(self.num_voice_bars):
            base_wave = (math.sin(math.radians(self.anim_angle * 4 + i * 15)) + 1) * 0.25
            speech_boost = random.uniform(0.5, 1.0) * self.mic_volume
            self.voice_frequencies[i] = max(0.1, min(1.0, base_wave + speech_boost))

        # Ambient Dust Particles Swirl
        for p in self.particles_3d:
            p['theta'] += 0.004 * p['speed']
            p['phi'] += 0.002 * p['speed']
            p['x'] = p['r'] * math.cos(p['phi']) * math.cos(p['theta'])
            p['y'] = p['r'] * math.cos(p['phi']) * math.sin(p['theta'])
            p['z'] = p['r'] * math.sin(p['phi'])

        self.update()

    def draw_3d_arc_ring(self, painter, cx, cy, radius, rx, ry, rz, color, width=2, arc_count=4):
        """Renders segmented 3D orbital rings."""
        segments_per_arc = 15
        total_segments = arc_count * 2
        deg_step = 360 / total_segments

        for arc_idx in range(0, total_segments, 2):
            start_deg = arc_idx * deg_step + self.anim_angle
            points = []
            for i in range(segments_per_arc + 1):
                ang = math.radians(start_deg + (deg_step / segments_per_arc) * i)
                x = math.cos(ang) * radius
                y = math.sin(ang) * radius
                px, py, scale, z_depth = self.project_3d(x, y, 0, cx, cy, rx, ry, rz)
                points.append((px, py, z_depth, scale))

            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i + 1]
                avg_z = (p1[2] + p2[2]) / 2.0
                alpha = int(max(20, min(255, 170 + avg_z * 0.9)))
                pen = QPen(QColor(color.red(), color.green(), color.blue(), alpha), width * ((p1[3] + p2[3]) / 2.0))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawLine(QPointF(p1[0], p1[1]), QPointF(p2[0], p2[1]))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        # --- PARC V1 Signature Amber Palette ---
        amber_main = QColor(255, 115, 0)     # Glowing orange
        amber_bright = QColor(255, 185, 40)  # Core highlight
        amber_deep = QColor(200, 45, 0)      # Deep shadow red
        white_core = QColor(255, 245, 220)   # Center singularity

        # Deep Void Background
        painter.fillRect(self.rect(), QColor(4, 3, 2, 255))

        # =========================================================
        # 1. OUTER & INNER CONCENTRIC CIRCLES
        # =========================================================
        circle_pen = QPen(QColor(255, 115, 0, 45), 1.5)
        painter.setPen(circle_pen)
        painter.drawEllipse(QPointF(cx, cy), 280, 280)
        painter.drawEllipse(QPointF(cx, cy), 300, 300)

        # Subtle Circular Radar Ticks
        tick_pen = QPen(QColor(255, 185, 40, 90), 1)
        tick_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(tick_pen)
        for deg in range(0, 360, 15):
            rad = math.radians(deg)
            x1 = cx + math.cos(rad) * 280
            y1 = cy + math.sin(rad) * 280
            x2 = cx + math.cos(rad) * 290
            y2 = cy + math.sin(rad) * 290
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # =========================================================
        # 2. FIXED CENTER VOICE EQUALIZER BARS
        # =========================================================
        base_eq_r = 95
        max_bar_height = 55

        for i in range(self.num_voice_bars):
            angle_deg = (360 / self.num_voice_bars) * i
            angle_rad = math.radians(angle_deg)

            bar_val = self.voice_frequencies[i]
            bar_len = bar_val * max_bar_height

            x_in = cx + math.cos(angle_rad) * base_eq_r
            y_in = cy + math.sin(angle_rad) * base_eq_r
            x_out = cx + math.cos(angle_rad) * (base_eq_r + bar_len)
            y_out = cy + math.sin(angle_rad) * (base_eq_r + bar_len)

            alpha = int(120 + bar_val * 135)

            if bar_val > 0.4:
                bar_pen = QPen(QColor(amber_bright.red(), amber_bright.green(), amber_bright.blue(), alpha), 3)
            else:
                bar_pen = QPen(QColor(amber_main.red(), amber_main.green(), amber_main.blue(), alpha), 2)

            bar_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(bar_pen)
            painter.drawLine(QPointF(x_in, y_in), QPointF(x_out, y_out))

            # Voice Bar Outer Nodes
            if bar_val > 0.5:
                painter.setBrush(QBrush(white_core))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(x_out, y_out), 2, 2)

        # Inner Reticle Ring for Voice Equalizer Base
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 115, 0, 80), 1, Qt.PenStyle.DashLine))
        painter.drawEllipse(QPointF(cx, cy), base_eq_r, base_eq_r)

        # =========================================================
        # 3. 3D ORBITAL RINGS
        # =========================================================
        self.draw_3d_arc_ring(painter, cx, cy, 220, self.rot_x, self.rot_y, self.rot_z, amber_bright, width=2, arc_count=6)
        self.draw_3d_arc_ring(painter, cx, cy, 175, -self.rot_y, self.rot_x, self.rot_z * 1.4, amber_deep, width=2, arc_count=4)
        self.draw_3d_arc_ring(painter, cx, cy, 140, self.rot_x * 1.5, -self.rot_z, self.rot_y, amber_main, width=3, arc_count=3)

        # =========================================================
        # 4. AMBIENT DUST PARTICLES (Roaming Around Core)
        # =========================================================
        projected_particles = []
        for p in self.particles_3d:
            px, py, scale, z_depth = self.project_3d(p['x'], p['y'], p['z'], cx, cy, self.rot_x, self.rot_y, self.rot_z)
            projected_particles.append((px, py, z_depth, scale, p['size']))

        # =========================================================
        # 5. DENSE 3D NEURAL CORE MATRIX
        # =========================================================
        core_r = 120
        projected_nodes = []

        for nx, ny, nz in self.nodes_3d:
            sx, sy, sz = nx * core_r, ny * core_r, nz * core_r
            px, py, scale, z_depth = self.project_3d(sx, sy, sz, cx, cy, self.rot_x, self.rot_y, self.rot_z)
            projected_nodes.append((px, py, z_depth, scale))

        # Depth Sorting (Back to Front)
        all_renderables = []
        for pt in projected_nodes:
            all_renderables.append(('node', pt[0], pt[1], pt[2], pt[3], 0))
        for p in projected_particles:
            all_renderables.append(('particle', p[0], p[1], p[2], p[3], p[4]))

        all_renderables.sort(key=lambda item: item[3])

        painter.setPen(Qt.PenStyle.NoPen)
        for item_type, px, py, z_depth, scale, size in all_renderables:
            alpha = int(max(25, min(255, 160 + z_depth * 1.2)))

            if item_type == 'particle':
                p_color = QColor(amber_bright.red(), amber_bright.green(), amber_bright.blue(), int(alpha * 0.6))
                painter.setBrush(QBrush(p_color))
                rad = max(1.0, (size * scale) / 2.0)
                painter.drawEllipse(QPointF(px, py), rad, rad)
            else:
                if z_depth > 0:
                    pt_color = QColor(amber_bright.red(), amber_bright.green(), amber_bright.blue(), alpha)
                    rad = max(1.5, (4.5 * scale) / 2.0)
                else:
                    pt_color = QColor(amber_deep.red(), amber_deep.green(), amber_deep.blue(), alpha)
                    rad = max(1.0, (2.5 * scale) / 2.0)

                painter.setBrush(QBrush(pt_color))
                painter.drawEllipse(QPointF(px, py), rad, rad)

        # Web Filament Lines
        for i in range(0, len(projected_nodes) - 1, 2):
            p1 = projected_nodes[i]
            p2 = projected_nodes[i + 1]
            dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
            if dist < 65:
                line_pen = QPen(QColor(amber_main.red(), amber_main.green(), amber_main.blue(), 65), 1)
                line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(line_pen)
                painter.drawLine(QPointF(p1[0], p1[1]), QPointF(p2[0], p2[1]))

        # =========================================================
        # 6. PERFECT CIRCULAR SINGULARITY CORE GLOW (NO SQUARES)
        # =========================================================
        painter.setPen(Qt.PenStyle.NoPen)

        # Outer Soft Amber Core Circle
        painter.setBrush(QBrush(QColor(amber_bright.red(), amber_bright.green(), amber_bright.blue(), 180)))
        painter.drawEllipse(QPointF(cx, cy), 8, 8)

        # Inner Hot White Singularity Circle
        painter.setBrush(QBrush(white_core))
        painter.drawEllipse(QPointF(cx, cy), 3.5, 3.5)

    def init_ui(self):
        self.setWindowTitle("PARC V1 NEURAL SYSTEM")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setWindowOpacity(1.0)
        self.showFullScreen()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(35, 35, 35, 35)

        # Header Bar
        header = QHBoxLayout()
        title = QLabel("P.A.R.C // VERSION 1.0")
        title.setFont(QFont("Monospace", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff7300; border: none;")
        header.addWidget(title)
        header.addStretch()

        self.status_lbl = QLabel("PARC V1 ONLINE // CORE ACTIVED")
        self.status_lbl.setFont(QFont("Monospace", 11))
        self.status_lbl.setStyleSheet("color: #ffb928; border: none;")
        header.addWidget(self.status_lbl)
        main_layout.addLayout(header)

        main_layout.addStretch()

        # Bottom Dock
        bottom_dock = QHBoxLayout()

        # Bottom-Left Camera Viewport
        self.cam_label = QLabel(self)
        self.cam_label.setFixedSize(260, 260)
        self.cam_label.setStyleSheet("border: 2px solid #ff7300; background-color: #000000; border-radius: 8px;")
        bottom_dock.addWidget(self.cam_label)

        bottom_dock.addStretch()

        # Bottom-Right Telemetry Feed
        side_panel = QVBoxLayout()
        info_label = QLabel(
            "PARC V1 SYSTEM STATUS:\n"
            "• Center Equalizer Matrix: 48 Bars\n"
            "• Ambient Dust Matrix: 140 Particles\n"
            "• Vocal Processing Loop: ACTIVE\n\n"
            "Press [ESC] to Terminate System."
        )
        info_label.setFont(QFont("Monospace", 10))
        info_label.setStyleSheet("color: #a87d54; border: none;")
        side_panel.addWidget(info_label)

        side_panel.addSpacing(15)

        self.cmd_lbl = QLabel("PARC V1 > LISTENING...")
        self.cmd_lbl.setFont(QFont("Monospace", 9, QFont.Weight.Bold))
        self.cmd_lbl.setStyleSheet("color: #ff7300; border: 1px solid #ff7300; padding: 6px; background-color: rgba(255, 115, 0, 15);")
        self.cmd_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        side_panel.addWidget(self.cmd_lbl)

        bottom_dock.addLayout(side_panel)
        main_layout.addLayout(bottom_dock)

        # Vision Thread Handler
        if "VisionEngine" in globals():
            self.vision_thread = VisionEngine()

            # Connect the change_pixmap_signal to update_frame
            self.vision_thread.change_pixmap_signal.connect(self.update_frame)
            self.vision_thread.move_window_signal.connect(self.move_gui)
            self.vision_thread.status_signal.connect(self.update_status)
            self.vision_thread.opacity_signal.connect(self.set_hud_opacity)

            self.vision_thread.start()

# =====================================================================
# 7. UNIFIED DAEMON EXECUTION RUNWAY
# =====================================================================
if __name__ == "__main__":
    print("\n=== PARC ===")

    try:
        # 1. Initialize Audio Recorder
        recorder = AudioToTextRecorder(
            spinner=True,
            model="base.en",
            device="cuda",
            use_microphone=True,
            compute_type="float16",
            input_device_index=11
        )
    except Exception:
        print("\n[FATAL] AudioToTextRecorder failed to initialize — this usually means CUDA/GPU\n"
              "isn't reachable the way RealtimeSTT expects (driver mismatch, wrong compute_type\n"
              "for your card, or PyTorch not built with CUDA support), or input_device_index=11\n"
              "doesn't match a real microphone on this machine. Full traceback below and in\n"
              f"{CRASH_LOG_PATH}.\n")
        with open(CRASH_LOG_PATH, "a") as f:
            f.write(f"\n\n===== RECORDER INIT CRASH at {datetime.datetime.now()} =====\n")
            traceback.print_exc(file=f)
        traceback.print_exc()
        sys.exit(1)

    wake_words = ["parc", "park"]

    # 2. Run Startup Sequence
    try:
        run_startup_sequence(recorder)
    except Exception:
        print("[Non-fatal] Startup greeting failed, continuing without it:")
        traceback.print_exc()

    print("\n[Telemetry Status] Signal tracking arrays configured. Awaiting voice triggers, Sir...\n")

    # 3. Launch Unified PyQt6 App & Kinetic HUD
    app = QApplication(sys.argv)
    hud = ParcHUD(recorder)
    hud.show()

    sys.exit(app.exec())
