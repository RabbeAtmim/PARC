# 🤖 Parc & Milo: The Ultimate AI Desktop Assistant

Welcome to the **Parc & Milo** repository! This project combines a powerful, hands-free computer automation tool (Parc) with a witty, conversational AI companion (Milo). Together, they are designed to drastically reduce the human effort required to operate a PC while making the experience interactive and fun.

---

## ✨ Features

### 🛠️ Parc: The Operator
Parc is your system's command center. It handles the heavy lifting of PC navigation and system control, all wrapped in a sleek, modern GUI. 

* **🖐️ Hand Gesture Control:** Control your mouse cursor entirely hands-free using intuitive hand gestures.
* **🪟 Advanced Window Management:** Instantly maximize, minimize, or split screens and tabs.
* **⚙️ System Operations:** Open the File Manager, tweak system settings, and fetch real-time system status.
* **🌐 Web & Media:** Launch websites and play music on command.
* **🔊 Audio Control:** Increase/decrease volume or mute your system instantly.
* **📝 Productivity:** Save quick notes without breaking your workflow.
* **🔒 Security:** Lock down your PC remotely or via direct command.
* **📱 Mobile Integration:** Control Parc's core functions directly from your mobile phone.
* **🖥️ Cool GUI:** A highly interactive and visually appealing graphical user interface.

### 💬 Milo: The Companion
Milo is the personality of the system. Whenever you need a break from work, Milo is there to keep things light.

* **🗣️ Conversational AI:** Loves to chat and keep you company.
* **🎭 Sense of Humor:** Always ready with a joke to brighten up your workflow.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.x**
* **Ollama** (Running locally for Milo's AI processing)
* **PyQt6** (For the GUI components)
* **OpenCV & MediaPipe** (For hand-gesture tracking and computer vision)
* **RealtimeSTT & Edge-TTS** (For voice recognition and speech output)
* **PyAutoGUI & Psutil** (For system control and resource monitoring)
* **FastAPI & Uvicorn** (For mobile/local server integration)

Installation & Setup
Follow these step-by-step instructions to pull and run the project locally on your machine:

1. Clone the repository:
   git clone https://github.com/RabbeAtmim/PARC.git

2. Navigate into project directory:
   cd PARC

3. Set up a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate

4. Install the required dependencies:
   pip install -r requirements.txt

5. Run the application:   
   python jarvis.py   
