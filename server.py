import os
import subprocess
import webbrowser
import datetime
import time
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Advanced Automation Libraries
import pywhatkit
import wikipedia
import pyautogui
import psutil
import winshell

# AI Library
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("WARNING: google-generativeai library not found. Please run 'pip install google-generativeai'")

app = Flask(__name__)
CORS(app)

# --- Configuration ---
# Replace with your actual API Key
API_KEY = "AIzaSyAHpvZAvdvBEbveEfeOH7UuLP3LqzT1KeU" 

if AI_AVAILABLE:
    genai.configure(api_key=API_KEY)
    # Dynamic Model Selection
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        print(f"Available Models: {available_models}")
        
        if available_models:
            # Prefer gemini-1.5-flash or gemini-pro if available
            selected_model = next((m for m in available_models if 'flash' in m), None)
            if not selected_model:
                selected_model = next((m for m in available_models if 'pro' in m), available_models[0])
            
            print(f"Selected Model: {selected_model}")
            model = genai.GenerativeModel(selected_model)
        else:
            print("Error: No models found that support generateContent.")
            model = None
            AI_AVAILABLE = False

    except Exception as e:
        print(f"Error listing models: {e}")
        # Fallback to a safe default if listing fails
        model = genai.GenerativeModel('gemini-pro')

APP_PATHS = {
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "cmd": "start cmd",
    "explorer": "explorer.exe",
    "chrome": "start chrome",
    "settings": "start ms-settings:",
    "task manager": "taskmgr",
    "store": "start ms-windows-store:",
    "whatsapp": "start whatsapp:",
}

# --- Helper Functions ---

def get_system_status():
    battery = psutil.sensors_battery()
    percent = battery.percent if battery else "unknown"
    plugged = "plugged in" if battery and battery.power_plugged else "on battery"
    return f"Battery is at {percent} percent and {plugged}."

def find_and_open_file(filename):
    user_dir = os.path.expanduser("~")
    search_dirs = [
        os.path.join(user_dir, "Desktop"),
        os.path.join(user_dir, "Documents"),
        os.path.join(user_dir, "Downloads"),
        os.path.join(user_dir, "Pictures"),
        os.path.join(user_dir, "Videos"),
        os.path.join(user_dir, "Music")
    ]
    print(f"Searching for {filename}...")
    for directory in search_dirs:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['AppData', 'node_modules']]
                for file in files:
                    if filename.lower() in file.lower():
                        file_path = os.path.join(root, file)
                        try:
                            os.startfile(file_path)
                            return f"Opening {file}"
                        except:
                            return f"Found {file} but couldn't open it."
    return f"I couldn't find any file named {filename}."

def execute_ai_action(action_data):
    """Executes the JSON action(s) returned by Gemini."""
    
    # Handle list of actions
    if isinstance(action_data, list):
        results = []
        for action_item in action_data:
            result = execute_ai_action(action_item)
            results.append(result)
        return " | ".join(results)

    action = action_data.get("action")
    target = action_data.get("target", "")
    
    print(f"Executing AI Action: {action} -> {target}")

    if action == "delay":
        try:
            seconds = float(target)
            time.sleep(seconds)
            return f"Waited {seconds}s"
        except:
            time.sleep(1)
            return "Waited 1s"

    if action == "open_app":
        if target in APP_PATHS:
            os.system(APP_PATHS[target])
            return f"Opening {target}"
        else:
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write(target)
            time.sleep(0.5)
            pyautogui.press('enter')
            return f"Opening {target}"

    elif action == "open_web":
        if not target.startswith('http'): target = 'https://' + target
        webbrowser.open(target)
        return f"Opening {target}"

    elif action == "play_music":
        pywhatkit.playonyt(target)
        return f"Playing {target} on YouTube"

    elif action == "system":
        if "shutdown" in target: os.system("shutdown /s /t 10"); return "Shutting down in 10s"
        if "restart" in target: os.system("shutdown /r /t 10"); return "Restarting in 10s"
        if "sleep" in target: os.system("rundll32.dll powrprof.dll,SetSuspendState 0,1,0"); return "Going to sleep"
        if "battery" in target: return get_system_status()
        if "recycle" in target: 
            try: winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False); return "Recycle bin emptied"
            except: return "Recycle bin already empty"

    elif action == "mouse":
        sub = action_data.get("sub")
        if sub == "move":
            direction = target
            amount = 100
            if "up" in direction: pyautogui.moveRel(0, -amount)
            if "down" in direction: pyautogui.moveRel(0, amount)
            if "left" in direction: pyautogui.moveRel(-amount, 0)
            if "right" in direction: pyautogui.moveRel(amount, 0)
            return "Moved mouse"
        if sub == "click": pyautogui.click(); return "Clicked"
        if sub == "right_click": pyautogui.click(button='right'); return "Right clicked"
        if sub == "scroll": 
            if "up" in target: pyautogui.scroll(500)
            else: pyautogui.scroll(-500)
            return "Scrolled"

    elif action == "keyboard":
        sub = action_data.get("sub")
        if sub == "type": pyautogui.write(target, interval=0.1); return f"Typed {target}"
        if sub == "press": pyautogui.press(target); return f"Pressed {target}"
        if sub == "copy": pyautogui.hotkey('ctrl', 'c'); return "Copied"
        if sub == "paste": pyautogui.hotkey('ctrl', 'v'); return "Pasted"

    elif action == "file":
        return find_and_open_file(target)

    return "Action completed."

def ask_gemini_brain(user_command):
    """Sends command to Gemini and gets a JSON action or text response."""
    if not AI_AVAILABLE:
        return None, "AI Library not installed."

    system_prompt = """
    You are Tuuna, an advanced PC automation assistant.
    Analyze the user's command and decide if it requires a PC action or just a chat response.

    If it is a PC ACTION, output ONLY a JSON LIST of objects with this format:
    [
        {"action": "open_app", "target": "notepad"},
        {"action": "delay", "target": "2"},
        {"action": "keyboard", "sub": "type", "target": "Hello World"}
    ]

    Available Actions:
    - Open App: {"action": "open_app", "target": "app_name"} (e.g. calculator, notepad, vscode)
    - Open Website: {"action": "open_web", "target": "url_or_name"}
    - Play Media: {"action": "play_music", "target": "song_name"}
    - System Control: {"action": "system", "target": "shutdown/restart/sleep/battery/recycle_bin"}
    - Mouse: {"action": "mouse", "sub": "move/click/right_click/scroll", "target": "up/down/left/right"}
    - Keyboard: {"action": "keyboard", "sub": "type/press/copy/paste", "target": "text_to_type_or_key_name"}
    - Files: {"action": "file", "sub": "open", "target": "filename_approximate"}
    - Delay: {"action": "delay", "target": "seconds_to_wait"} (IMPORTANT: Use this between opening an app and typing in it!)

    If it is a CHAT/QUESTION (e.g. "Who is...", "Tell me a joke", "Help me write"), output a normal plain text response. Do NOT output JSON for chat.
    
    User Command: 
    """
    
    try:
        response = model.generate_content(system_prompt + user_command)
        text = response.text.strip()
        
        # Try to find JSON in the response
        if "[" in text and "]" in text:
            try:
                # Extract JSON part if there's extra text
                start = text.find("[")
                end = text.rfind("]") + 1
                json_str = text[start:end]
                action_data = json.loads(json_str)
                return action_data, None # Action found
            except:
                pass # Failed to parse, treat as text
        
        # Fallback for single object legacy support (just in case)
        if "{" in text and "}" in text:
             try:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
                action_data = json.loads(json_str)
                return [action_data], None # Wrap in list
             except:
                 pass

        return None, text # Treat as chat response
        
    except Exception as e:
        print(f"AI Error: {e}")
        return None, f"I had trouble thinking. Error: {e}"


@app.route('/')
def home():
    return send_file('gui.html')

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command', '').lower()
    print(f"Received command: {command}")
    
    response_text = ""

    # 1. Try AI Processing First
    if AI_AVAILABLE:
        action_data, chat_response = ask_gemini_brain(command)
        
        if action_data:
            # AI decided it's an action
            response_text = execute_ai_action(action_data)
        elif chat_response:
            # AI decided it's a chat
            response_text = chat_response
        else:
            response_text = "I'm not sure what to do."
    else:
        # Fallback to old logic if AI is missing
        response_text = "AI Brain not installed. Please install google-generativeai."
        # (You can keep the old if/elif block here as a backup if you want, 
        # but for 'Ultimate' mode we rely on the AI)

    return jsonify({"response": response_text})

if __name__ == '__main__':
    print("Tuuna Ultimate AI Server Running...")
    app.run(debug=True, port=5000)
