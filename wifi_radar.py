import os
import sys
import time
from collections import deque
import numpy as np
from collections import deque
from rich.console import Console
from rich.panel import Panel
from scapy.all import Dot11, RadioTap, sniff

# Try importing M.I.L.O presence handler
try:
    from milo import on_user_entered_room

    MILO_AVAILABLE = True
except ImportError:
    MILO_AVAILABLE = False

INTERFACE = "wlan0"
TARGET_BSSID = "E0:D3:62:12:2C:3C"
WINDOW_SIZE = 50
ALPHA = 0.05

console = Console()


class WiFiPresenceRadar:

    def __init__(self, window_size=60, alpha=0.03):
        self.history = deque(maxlen=window_size)
        self.ewma_mean = None
        self.ewma_var = None
        self.alpha = alpha

        # State Machine Hysteresis Tracking
        self.is_occupied = False
        self.still_frames = 0
        self.active_frames = 0
        self.last_trigger_time = 0

    def process_rssi(self, rssi: float):
        self.history.append(rssi)

        if len(self.history) < 20:
            return "CALIBRATING", 0.0, float(rssi)

        samples = np.array(self.history)
        sample_mean = np.mean(samples)
        sample_var = np.var(samples) + 1e-6

        if self.ewma_mean is None:
            self.ewma_mean = sample_mean
            self.ewma_var = sample_var
        else:
            self.ewma_mean = (self.alpha * sample_mean) + ((1 - self.alpha) * self.ewma_mean)
            self.ewma_var = (self.alpha * sample_var) + ((1 - self.alpha) * self.ewma_var)

        std_dev = np.sqrt(self.ewma_var)
        z_score = abs(rssi - self.ewma_mean) / std_dev
        now = time.time()
        status = ""

        # --- SCHMITT TRIGGER LOGIC (Hyper-Sensitive Mode) ---

        if not self.is_occupied:
            # 1. VACANT STATE: Looking for an Entry
            # Dropped threshold to 1.6 to catch fast movement in a small room
            if z_score > 0.9:
                self.active_frames += 1
                # Trigger on the VERY FIRST disrupted frame, no waiting.
                if self.active_frames >= 1 and (now - self.last_trigger_time) > 15:
                    self.is_occupied = True
                    self.last_trigger_time = now
                    self.active_frames = 0
                    self.still_frames = 0
                    status = "ENTRY DETECTED (Greeting User)"

                    if MILO_AVAILABLE:
                        import threading
                        print("\n[SYSTEM] Triggering M.I.L.O. Audio Thread...")
                        threading.Thread(target=on_user_entered_room, daemon=True).start()
            else:
                self.active_frames = 0
                status = "VACANT (Room Empty)"

        else:
            # 2. OCCUPIED STATE: Looking for an Exit
            if z_score < 1.3:
                self.still_frames += 1
                # Still requires 25 quiet frames to confirm you actually left
                if self.still_frames > 25:
                    self.is_occupied = False
                    self.still_frames = 0
                    status = "VACANT (Room Empty)"
                else:
                    status = f"OCCUPIED (Settling... {self.still_frames}/25)"
            else:
                self.still_frames = 0
                status = "OCCUPIED (Active Movement)"

        return status, z_score, float(rssi)
radar = WiFiPresenceRadar(window_size=WINDOW_SIZE, alpha=ALPHA)

def packet_handler(pkt):
    if pkt.haslayer(Dot11) and pkt.haslayer(RadioTap):
        target = TARGET_BSSID.lower()
        addrs = [str(getattr(pkt, f"addr{i}", "")).lower() for i in (1, 2, 3)]

        if target in addrs:
            radiotap = pkt.getlayer(RadioTap)
            if hasattr(radiotap, "dBm_AntSignal"):
                rssi = radiotap.dBm_AntSignal
                status, z_score, current_rssi = radar.process_rssi(rssi)

                color = (
                    "red"
                    if "ENTRY" in status
                    else ("green" if "VACANT" in status else "yellow")
                )

                panel_content = (
                    f"[bold]Target Router:[/bold] {TARGET_BSSID}\n"
                    f"[bold]Room State:[/bold] [{color}]{status}[/{color}]\n"
                    f"[bold]Presence Status:[/bold] {'Occupied' if radar.is_occupied else 'Vacant'}\n"
                    f"[bold]Signal Deviation (Z-Score):[/bold] {z_score:.2f} σ\n"
                    f"[bold]Current RSSI:[/bold] {current_rssi} dBm"
                )

                console.clear()
                console.print(
                    Panel(
                        panel_content,
                        title="[bold cyan]M.I.L.O. Spatial Presence System[/bold cyan]",
                        expand=False,
                    )
                )


if __name__ == "__main__":
    if os.geteuid() != 0:
        sys.exit("[!] Error: Root privileges required. Run with 'sudo'.")

    sniff(iface=INTERFACE, prn=packet_handler, store=0)
