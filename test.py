# -*- coding: utf-8 -*-
import subprocess
import sys
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
install("PyQt5")

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QHBoxLayout
from PyQt5.QtCore import QProcess

class TerminalGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Terminal GUI mit PyQt5')
        self.setGeometry(100, 100, 600, 400)
        
        # Layout
        layout = QVBoxLayout()
        
        # Textbereich für Ausgabe
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        
        # Eingabefeld und Button für Eingabe
        input_layout = QHBoxLayout()
        self.entry = QLineEdit(self)
        self.send_button = QPushButton('Senden', self)
        self.send_button.clicked.connect(self.send_input)
        input_layout.addWidget(self.entry)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # QProcess zum Ausführen des Skripts
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_error)
        try:
            self.process.start('python', ['main.py'])
        except Exception as e:
            self.text_area.append(f"Fehler beim Starten des Skripts: {e}")
        
    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode('latin-1')
        self.text_area.append(output)
        
    def read_error(self):
        error = self.process.readAllStandardError().data().decode('latin-1')
        self.text_area.append(error)
        
    def send_input(self):
        user_input = self.entry.text()
        self.process.write(user_input.encode() + b'\n')
        self.entry.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal_gui = TerminalGUI()
    terminal_gui.show()
    sys.exit(app.exec_())
