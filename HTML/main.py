import subprocess
import sys
import os
import libdictionary as dict
import json
from groq import Groq

# Funktion zum Installieren von Bibliotheken
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])

# Bibliotheken installieren
try:
    import nltk
except ImportError:
    install("nltk")
    import nltk

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

def handle_chat(message):
    """Verarbeitet Chat-Nachrichten."""
    response = chatbot.respond(message)
    if response == "Entschuldigung, das verstehe ich nicht. Können Sie das bitte anders formulieren?":
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": message}
            ],
            model="llama3-8b-8192"
        )
        response = chat_completion.choices[0].message.content
    elif response == "systemmath":
        return {"response": "Bitte geben Sie Ihren mathematischen Ausdruck ein."}
    return {"response": response}

def handle_calculate(expression):
    """Berechnet mathematische Ausdrücke."""
    try:
        result = eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

def handle_execute(command):
    """Führt erlaubte Shell-Befehle aus."""
    allowed_commands = ["ls", "pwd", "echo", "whoami", "cd"]
    cmd = command.split()[0]
    if cmd in allowed_commands:
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            return {"output": result}
        except subprocess.CalledProcessError as e:
            return {"error": e.output}
    else:
        return {"error": f"Befehl '{cmd}' ist nicht erlaubt. Erlaubte Befehle sind: {', '.join(allowed_commands)}"}

def handle_text_reverse(text):
    """Gibt den umgekehrten Text zurück."""
    return {"result": text[::-1]}

def handle_palindrome_check(text):
    """Überprüft, ob der Text ein Palindrom ist."""
    cleaned_text = ''.join(e for e in text if e.isalnum()).lower()
    return {"result": cleaned_text == cleaned_text[::-1]}

def handle_unit_conversion(value, from_unit, to_unit):
    """Konvertiert Einheiten."""
    conversions = {
        ("kilometer", "meile"): 0.621371,
        ("meile", "kilometer"): 1.60934,
        ("kilogramm", "pfund"): 2.20462,
        ("pfund", "kilogramm"): 0.453592
    }
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        return {"result": value * conversions[key]}
    else:
        return {"error": "Konvertierung nicht unterstützt."}

def main():
    """Hauptmenü der Anwendung."""
    while True:
        print("\nWählen Sie eine Option:")
        print("1. Chat")
        print("2. Rechner")
        print("3. Befehl ausführen")
        print("4. Text umkehren")
        print("5. Palindrom überprüfen")
        print("6. Einheiten konvertieren")
        print("7. Beenden")
        choice = input("Ihre Wahl: ")

        if choice == '1':
            while True:
                message = input("Geben Sie Ihre Nachricht ein: ")
                response = handle_chat(message)
                print(f"Bot: {response['response']}")
                if message == "exit":
                    break
                

        elif choice == '2':
            expression = input("Geben Sie den mathematischen Ausdruck ein: ")
            result = handle_calculate(expression)
            if "result" in result:
                print(f"Ergebnis: {result['result']}")
            else:
                print(f"Fehler: {result['error']}")

        elif choice == '3':
            command = input("Geben Sie den Befehl ein: ")
            result = handle_execute(command)
            if "output" in result:
                print(result["output"])
            else:
                print(f"Fehler: {result['error']}")

        elif choice == '4':
            text = input("Geben Sie den Text ein, den Sie umkehren möchten: ")
            result = handle_text_reverse(text)
            print(f"Umgekehrter Text: {result['result']}")

        elif choice == '5':
            text = input("Geben Sie den Text ein, den Sie auf Palindrom überprüfen möchten: ")
            result = handle_palindrome_check(text)
            print(f"Palindrom: {result['result']}")

        elif choice == '6':
            value = float(input("Geben Sie den Wert ein: "))
            from_unit = input("Geben Sie die Ausgangseinheit ein: ")
            to_unit = input("Geben Sie die Ziel-Einheit ein: ")
            result = handle_unit_conversion(value, from_unit, to_unit)
            if "result" in result:
                print(f"Ergebnis: {result['result']} {to_unit}")
            else:
                print(f"Fehler: {result['error']}")

        elif choice == '7':
            print("Beenden...")
            break

        else:
            print("Ungültige Wahl. Bitte versuchen Sie es erneut.")

# Test des Handlers
if __name__ == '__main__':
    main()
