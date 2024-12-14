import subprocess
import sys
import os
import libdictionary as dict

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])

# Bibliotheken installieren
try:
    import nltk
except ImportError:
    install("nltk")
    import nltk

try:
    from flask import Flask, request, jsonify, render_template
except ImportError:
    install("flask")
    from flask import Flask, request, jsonify, render_template

try:
    from groq import Groq
except ImportError:
    install("groq")
    from groq import Groq

try:
    import requests
except ImportError:
    install("requests")
    import requests

try:
    from bs4 import BeautifulSoup
except:
    install("beautifulsoup4 requests")
    from bs4 import BeautifulSoup





# API-Schlüssel direkt im Skript setzen
os.environ["GROQ_API_KEY"] = "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"
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("API-Schlüssel ist nicht gesetzt.")

client = Groq(api_key=api_key)

# Chatbot-Instanz erstellen
from nltk.chat.util import Chat, reflections
chatbot = Chat(dict.pairs, reflections)

app = Flask(__name__)

# Route für die Hauptseite
@app.route('/')
def index():
    return render_template('index.html')

# Route für den Chatbot
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message", "")
    
    response = chatbot.respond(user_input)
    if response == "Entschuldigung, das verstehe ich nicht. Können Sie das bitte anders formulieren?":
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_input},
                {"role": "system", "content": "You love math."}
            ],
            model="gemma2-9b-it",
            temperature=1,
            max_tokens=230,
            top_p=1,
            stop=None,
        )
        response = chat_completion.choices[0].message.content
    
    return jsonify({"response": response})

# Route für die Text-Umkehrung
@app.route('/reverse', methods=['POST'])
def reverse():
    text = request.json.get("text")
    if text is not None:
        reversed_text = text[::-1]
        return jsonify({"result": reversed_text})
    else:
        return jsonify({"error": "Kein Text zum Umkehren angegeben."})


# Route zur Überprüfung auf Palindrome
@app.route('/palindrome', methods=['POST'])
def palindrome():
    text = request.json.get("text")
    if text is not None:
        cleaned_text = ''.join(e for e in text if e.isalnum()).lower()
        is_palindrome = cleaned_text == cleaned_text[::-1]
        return jsonify({"result": is_palindrome})
    else:
        return jsonify({"error": "Kein Text zur Überprüfung angegeben."})

# Route für die Einheiten-Konvertierung
@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    value = data.get("value")
    from_unit = data.get("from_unit")
    to_unit = data.get("to_unit")
    if value is not None and from_unit is not None and to_unit is not None:
        conversions = {
            ("kilometer", "meile"): 0.621371,
            ("meile", "kilometer"): 1.60934,
            ("kilogramm", "pfund"): 2.20462,
            ("pfund", "kilogramm"): 0.453592
        }
        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            result = value * conversions[key]
            return jsonify({"result": result})
        else:
            return jsonify({"error": "Konvertierung nicht unterstützt."})
    else:
        return jsonify({"error": "Ungültige Eingaben für die Einheitenkonvertierung."})

# Route für den Rechner
@app.route('/calculate', methods=['POST'])
def calculate():
    expression = request.json.get("expression")
    try:
        result = eval(expression)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

# Route für die beschränkten Shell-Befehle
@app.route('/execute', methods=['POST'])
def execute():
    command = request.json.get("command")
    allowed_commands = ["ls", "pwd", "echo", "whoami", "cd"]  # Sicherstellen, dass nur erlaubte Befehle ausgeführt werden
    cmd = command.split()[0]
    if cmd in allowed_commands:
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            return jsonify({"output": result})
        except subprocess.CalledProcessError as e:
            return jsonify({"error": e.output})
    else:
        return jsonify({"error": f"Befehl '{cmd}' ist nicht erlaubt. Erlaubte Befehle sind: {', '.join(allowed_commands)}"})

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
