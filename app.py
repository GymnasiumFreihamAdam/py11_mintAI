import subprocess
import sys
import os
import libdictionary as dict
from flask import Flask, request, jsonify, render_template
from groq import Groq

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
    import groq
except ImportError:
    install("groq")
    import groq


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
    user_input = request.json.get("message")
    response = chatbot.respond(user_input)
    if response == "Entschuldigung, das verstehe ich nicht. Können Sie das bitte anders formulieren?":
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192"
        )
        response = chat_completion.choices[0].message.content
    elif response == "systemmath":
        return jsonify({"response": "Bitte geben Sie Ihren mathematischen Ausdruck ein."})
    return jsonify({"response": response})

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
    allowed_commands = ["ls", "pwd", "echo", "whoami","cd"]  # Sicherstellen, dass nur erlaubte Befehle ausgeführt werden
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
