import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import pyjokes
import webbrowser
import requests
import psutil
import pyautogui
import os
import google.generativeai as genai
import time
import creds
import contact_directery as cd


os.makedirs("Screenshots", exist_ok=True)
gemini_api_key=creds.gemini_api_kay
genai.configure(api_key = gemini_api_key )
model = genai.GenerativeModel("gemini-2.5-flash")

def speak(text):
    """Reliable speech function that always re-initializes pyttsx3"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)  
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Speech error: {e}")



def listen_once():
    """Listen for a single short response (like city name)"""
    r = sr.Recognizer()
    r.pause_threshold = 2.0
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("🎧 Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=4)
            response = r.recognize_google(audio, language="en-in").lower()
            print(f"Heard: {response}")
            return response
        except sr.UnknownValueError:
            speak("Sorry, I didn’t catch that.")
            return None
        except sr.RequestError:
            speak("Speech service error.")
            return None



def take_command():
    """Continuously listen for the wake word 'Friday' and return the user's next command"""
    r = sr.Recognizer()
    r.pause_threshold = 2.0
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.8)
        print("🎧 Listening for wake word 'Friday'...")

        try:
            # Listen for short bursts
            audio = r.listen(source, timeout=None, phrase_time_limit=4)
            word = r.recognize_google(audio, language="en-in").lower()
            print(f"Heard: {word}")

            # Wake word detection (broader matching)
            if any(trigger in word for trigger in ["friday", "hey friday", "hi friday", "okay friday", "hello friday", "ok friday"]):
                speak("Yes")
                print("🎤 Wake word detected. Listening for command...")

                # Now listen for the actual command
                audio = r.listen(source, timeout=None, phrase_time_limit=10)
                query = r.recognize_google(audio, language="en-in").lower()
                print(f"Command: {query}")
                return query
            else:
                print("Wake word not detected.")
                return None

        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            speak("Speech recognition service error.")
            return None
        except Exception as e:
            return None

    
         

def open_website(url):
    """Open a website"""
    webbrowser.open(url)
    

def get_time():
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.strftime("%M")
    period = ""

    # Determine natural time period
    if 5 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    elif 17 <= hour < 20:
        period = "evening"
    else:
        period = "night"

    # Convert to 12-hour format
    formatted_time = now.strftime("%I:%M:%p")
    formatted_time = formatted_time.lstrip("0")  # Remove leading zero (e.g. 08 → 8)

    return f"It's {formatted_time} {period}"

def get_date():
    return datetime.datetime.now().strftime("%d-%m-%Y")

def get_weather(city):
    """Get weather info using OpenWeatherMap API"""
    api_key = creds.open_api_key # Replace with your key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("main"):
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            return f"{city} weather: {desc}, temperature: {temp}°C"
        else:
            return "City not found."
    except Exception as e:
        print(e)
        return "Could not retrieve weather."

def take_screenshot():
    """Take a screenshot and save in Screenshots folder"""
    screenshot = pyautogui.screenshot()
    filename = f"Screenshots/screenshot_{datetime.datetime.now().strftime('%H%M%S')}.png"
    screenshot.save(filename)
    speak(f"Screenshot saved as {filename}")

def is_camera_open():
    """Check if Windows Camera app is already running."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'WindowsCamera' in proc.info['name']:
            return True
    return False

def take_picture_camera_app():
    """Simulate pressing Enter to take a picture."""
    time.sleep(1)
    pyautogui.press('enter')

def open_or_take_picture():
    """Open camera if not running, else just take picture."""
    if is_camera_open():
        print("📸 Camera is already open, taking picture...")
        take_picture_camera_app()
    else:
        print("🎥 Opening camera...")
        os.system("start microsoft.windows.camera:")
        time.sleep(5)  # wait for camera to load
        take_picture_camera_app()
        print("✅ Picture captured.")

def check_battery():
    battery = psutil.sensors_battery()
    if battery is None:
        return  # No battery detected (PC on power adapter only)

    percent = battery.percent
    plugged = battery.power_plugged

    if percent <= 20 and not plugged:
        speak(f"Warning! Battery is low, only {percent} percent remaining. Please plug in the charger.")
        print(f"Warning! Battery is low, only {percent} percent remaining. Please plug in the charger.")


def get_system_info():
    """Return battery, CPU, RAM, and Disk usage"""
    battery = psutil.sensors_battery()
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return f"Battery: {battery.percent}%, CPU: {cpu}%, RAM: {memory}%, Disk: {disk}%"


def chat_with_ai(prompt):
    try:
        short_prompt = f"Answer briefly and clearly in 2-3 sentences:\n{prompt}"
        response = model.generate_content(short_prompt)
        reply = response.text
        return reply
    except Exception as e:
        return f"Error using Gemini: {e}"

def send_whatsapp_message(query):
    contact=cd.contact
    try:
        query = query.lower().replace("send ", "")
        if " to " in query:
            msg, name = query.split(" to ", 1)
            name = name.strip()
            msg = msg.strip()
            
            # find contact number
            if name in contact:
                number = contact[name]
                speak(f"Sending message to {name}")
                pywhatkit.sendwhatmsg_instantly(number, msg)
                speak("Message sent successfully.")
            else:
                speak(f"I don’t have a contact named {name}.")
        else:
            speak("Please say the message and the contact name, like 'send hello to Aman'.")
    except Exception as e:
        print(e)
        speak("Sorry, I could not send the message.")
    
def pause_youtube():
    try:
        time.sleep(1)  # small delay to ensure browser is in focus
        pyautogui.press('space')
        print("⏸️ Toggled YouTube video (Play/Pause).")
    except Exception as e:
        print(f"Error pausing YouTube: {e}")

   

# ===================== COMMAND HANDLER =========================
def handle_command(query):
    if "time" in query:
        speak(f" {get_time()} ")
        print (f"time is {get_time()}")

    elif "date" in query:
        speak(f"Today's date is {get_date()}")
        print (f"date is {get_date()}")

    elif "open youtube" in query:
        speak("opening youtube")
        open_website("https://www.youtube.com")

    elif "open google" in query:
        open_website("https://www.google.com")

    elif "open chat gpt"  in query or "open chat gtp" in query:
        open_website("https://chatgpt.com/")

    elif "open notepad" in query or "note" in query:
        os.system("notepad.exe")

    elif "open calculator" in query:
        os.system("calc.exe")

    elif any(word in query for word in ["open camera", "start camera", "launch camera"]):
        os.system("start microsoft.windows.camera:")
    
    elif any(word in query for word in ["take picture","click","take a picture","click a picture"]):
        open_or_take_picture()

    elif "play" in query:
        song = query.replace("play", "").strip()
        speak(f"Playing {song}")
        pywhatkit.playonyt(song)

    elif any (command in query for command in ["pause","stop","hold","resume","play youtube","pause the video"]):
        pause_youtube()

    elif "joke" in query:
        speak(pyjokes.get_joke())
        print(pyjokes.get_joke())

    elif "weather" in query:
        speak("Which city?")
        print("which city")
        time.sleep(1)
        city = listen_once()
        if city:
            weather_info = get_weather(city)
            speak(weather_info)
            print(weather_info)

    elif "screenshot" in query:
        take_screenshot()

    elif "system info" in query or "system status" in query:
        info = get_system_info()
        speak(info)
        print (info)

    elif "quit" in query or "exit" in query or "terminate" in query:
        speak("Goodbye! Have a nice day!")
        return False
    
    elif "send" in query and "to" in query:
        send_whatsapp_message(query)
    
    else:
         ai_response = chat_with_ai(query)
         print(ai_response)
         speak(ai_response)
    return True

# ===================== MAIN FUNCTION =========================
def run_assistant():
    speak("Hello! I am  friday . How can I help you?")
    try:
        while True:
            check_battery()
            query = take_command()
            if query:
                if not handle_command(query):
                    break
    except Exception as e:
        print("Unexpected error:", e)
        speak("Sorry, something went wrong.")

# ===================== RUN ASSISTANT =========================
if __name__ == "__main__":
    run_assistant()
