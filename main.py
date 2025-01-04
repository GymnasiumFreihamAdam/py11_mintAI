import subprocess
import sys
import json
import nltk
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

# Installiere notwendige Bibliotheken
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("nltk")
install("scikit-learn")

# Lade NLTK-Daten
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('maxent_ne_chunker_tab')

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, ne_chunk

# Setze Seed für Reproduzierbarkeit
def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)

set_seed(42)  # Beispiel-Seed

# Lade das Trainingsdatenset aus der JSON-Datei
def load_training_data(file_path='training_data.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

training_data = load_training_data()

# Überprüfen, ob `training_data` nicht leer ist
if not training_data:
    raise ValueError("Das Trainingsdatenset ist leer. Bitte überprüfen Sie die Quelle der Daten.")

# Daten vorverarbeiten
vectorizer = TfidfVectorizer()
questions = [data['question'] for data in training_data]
X = vectorizer.fit_transform(questions)

answers = [data['answer'] for data in training_data]
model = SVC(kernel='linear')
model.fit(X, answers)

# Zusatzfunktionen für NLP
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    tokens = word_tokenize(text)
    stemmed = [stemmer.stem(token) for token in tokens]
    lemmatized = [lemmatizer.lemmatize(token) for token in tokens]
    pos_tags = pos_tag(tokens)
    named_entities = ne_chunk(pos_tags)
    return {
        "tokens": tokens,
        "stemmed": stemmed,
        "lemmatized": lemmatized,
        "pos_tags": pos_tags,
        "named_entities": named_entities
    }

# Funktion zur Beantwortung von Fragen
def chatbot_response(question):
    question_tfidf = vectorizer.transform([question])
    try:
        response = model.predict(question_tfidf)[0]
        nlp_info = preprocess_text(question)
        return response, nlp_info
    except:
        return None, None

# Funktion zum Hinzufügen von neuen Fragen und Antworten
def add_to_training_data(question, answer, file_path='training_data.json'):
    global training_data
    new_entry = {"question": question, "answer": answer}
    training_data.append(new_entry)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(training_data, file, ensure_ascii=False, indent=4)
    
    # Modelle neu trainieren
    questions = [data['question'] for data in training_data]
    X = vectorizer.fit_transform(questions)
    answers = [data['answer'] for data in training_data]
    model.fit(X, answers)

# Automatisches Lernen aus Interaktionen
def learn_from_interaction(user_input, expected_response):
    add_to_training_data(user_input, expected_response)

# Funktion zur Überprüfung und Verbesserung der Antwort
def validate_response(user_input, response):
    print(f"Chatbot: {response}")
    feedback = input("War die Antwort korrekt? (ja/nein): ").strip().lower()
    if feedback == "nein":
        correct_answer = input("Wie hätte ich antworten sollen? ")
        learn_from_interaction(user_input, correct_answer)
        return correct_answer
    return response

# Chatbot testen
if __name__ == "__main__":
    while True:
        user_input = input("Du: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        response, nlp_info = chatbot_response(user_input)
        
        if response is None:
            print("Ich habe deine Frage nicht verstanden. Wie sollte ich darauf antworten?")
            new_answer = input("Neue Antwort: ")
            learn_from_interaction(user_input, new_answer)
            response = new_answer
        else:
            response = validate_response(user_input, response)
        
        print("Chatbot:", response)
        print("NLP Info:", nlp_info)
