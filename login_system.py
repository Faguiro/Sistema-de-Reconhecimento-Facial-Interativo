# login_system.py (VERSÃO FINAL CORRIGIDA)

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import json
import os
import threading
import time
import subprocess
import sys 

# --- Constantes e Funções de Dados ---

ARQUIVO_DADOS = 'dados_registrados.json'
TOLERANCIA = 0.6
TEMPO_LIMITE_LOGIN = 5

def carregar_dados_salvos():
    if not os.path.exists(ARQUIVO_DADOS):
        return [], []
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        rostos_codificados = [np.array(item['codificacao']) for item in dados]
        nomes = [item['nome'] for item in dados]
        return rostos_codificados, nomes
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return [], []

# --- Tela Principal (Home) ---
class TelaHome:
    def __init__(self, user_name):
        self.root = tk.Tk()
        self.root.title("Tela Principal")
        self.root.geometry("600x400")
        
        # ... estilos e layout ...
        style = ttk.Style(self.root)
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 11, 'bold'))
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        welcome_label = ttk.Label(main_frame, text=f"Bem-vindo(a), {user_name}!", font=('Helvetica', 16, 'bold'))
        welcome_label.pack(pady=20)
        apps_frame = ttk.LabelFrame(main_frame, text="Meus Aplicativos", padding="15")
        apps_frame.pack(fill=tk.BOTH, expand=True)
        btn_face_app = ttk.Button(apps_frame, text="Reconhecimento Facial", command=lambda: self.launch_app("faces_detection.py"))
        btn_face_app.pack(pady=10, padx=20, fill=tk.X)
        btn_car_app = ttk.Button(apps_frame, text="Detector de Carros", command=lambda: self.launch_app("cars_detection.py"))
        btn_car_app.pack(pady=10, padx=20, fill=tk.X)

        self.root.mainloop()

    # --- FUNÇÃO PARA LANCAR OUTROS SCRIPTS ---
    def launch_app(self, script_name):
        """Lança um script Python como um novo processo USANDO O MESMO INTERPRETADOR."""
        try:
            print(f"Tentando iniciar o aplicativo: {script_name}")
            # Usamos sys.executable para garantir que o mesmo ambiente Python seja usado
            subprocess.Popen([sys.executable, script_name])
        except FileNotFoundError:
            messagebox.showerror("Erro", f"O arquivo '{script_name}' não foi encontrado. Certifique-se de que ele está na mesma pasta.")
        except Exception as e:
            messagebox.showerror("Erro ao Iniciar", f"Ocorreu um erro: {e}")


# --- Tela de Login ---
class TelaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Login com Reconhecimento Facial")
        self.login_successful = False
        self.user_name = None
        self.is_running = True
        self.is_logging_in = False
        self.login_start_time = 0
        self.known_face_encodings, self.known_face_names = carregar_dados_salvos()
        style = ttk.Style(self.root)
        style.configure('TButton', font=('Helvetica', 11))
        self.video_label = ttk.Label(self.root)
        self.video_label.pack(padx=10, pady=10)
        self.status_label = ttk.Label(self.root, text="Aponte o rosto para a câmera", font=('Helvetica', 10))
        self.status_label.pack(pady=5)
        self.login_button = ttk.Button(self.root, text="Login com Rosto", command=self.start_login_attempt)
        self.login_button.pack(pady=10)
        self.detection_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.detection_thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def login_success(self, user_name):
        self.is_running = False
        self.login_successful = True
        self.user_name = user_name
        messagebox.showinfo("Login Bem-Sucedido", f"Olá, {self.user_name}! Acesso permitido.")
        self.root.destroy()
        
    def start_login_attempt(self):
        if not self.known_face_names:
            messagebox.showerror("Erro", "Nenhum rosto cadastrado no sistema.")
            return
        self.is_logging_in = True
        self.login_start_time = time.time()
        self.login_button.config(state=tk.DISABLED)
        self.status_label.config(text="Analisando... Por favor, olhe para a câmera.")
        
    def video_loop(self):
        cap = cv2.VideoCapture(0)
        while self.is_running:
            ret, frame = cap.read()
            if not ret: continue
            if self.is_logging_in:
                if time.time() - self.login_start_time > TEMPO_LIMITE_LOGIN:
                    self.login_failure()
                self.process_login_frame(frame)
            self.update_video_label(frame)
        cap.release()

    def process_login_frame(self, frame):
        rgb_small_frame = cv2.cvtColor(cv2.resize(frame, (0, 0), fx=0.25, fy=0.25), cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=TOLERANCIA)
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
                self.login_success(name)
                return

    def update_video_label(self, frame):
        try:
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            pil_image.thumbnail((640, 480), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(image=pil_image)
            self.video_label.config(image=tk_image)
            self.video_label.image = tk_image
        except: pass

    def login_failure(self):
        self.is_logging_in = False
        messagebox.showerror("Acesso Negado", "Rosto não reconhecido ou tempo esgotado.")
        self.status_label.config(text="Tente novamente.")
        self.login_button.config(state=tk.NORMAL)

    def on_closing(self):
        self.is_running = False
        self.root.destroy()

# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    if not os.path.exists(ARQUIVO_DADOS) or not carregar_dados_salvos()[1]:
        root = tk.Tk()
        root.withdraw() 
        messagebox.showinfo("Primeiro Uso", "Nenhum usuário cadastrado.\nExecute 'faces_detection.py' para cadastrar um rosto antes de usar o login.")
    else:
        login_root = tk.Tk()
        app_login = TelaLogin(login_root)
        login_root.mainloop()
        if app_login.login_successful:
            print(f"Login bem-sucedido para o usuário: {app_login.user_name}. Iniciando a tela principal.")
            TelaHome(app_login.user_name)
        else:
            print("A aplicação foi fechada sem um login bem-sucedido.")