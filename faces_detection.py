import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import json
import os
import threading

# --- Constantes ---
ARQUIVO_DADOS = 'dados_registrados.json'
PASTA_FOTOS = 'fotos_registro'
TOLERANCIA = 0.6

# --- Funções Auxiliares (sem alteração) ---

def carregar_dados_salvos():
    if not os.path.exists(ARQUIVO_DADOS): return [], [], []
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        rostos_codificados = [np.array(item['codificacao']) for item in dados]
        codigos = [item['codigo'] for item in dados]
        nomes = [item['nome'] for item in dados]
        return rostos_codificados, codigos, nomes
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return [], [], []

def carregar_dados_para_edicao():
    if not os.path.exists(ARQUIVO_DADOS): return []
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def salvar_dados(codigo, nome, codificacao_rosto):
    dados_atuais = carregar_dados_para_edicao()
    item_encontrado = False
    for item in dados_atuais:
        if item['codigo'] == codigo:
            item.update({'nome': nome, 'codificacao': codificacao_rosto.tolist()})
            item_encontrado = True
            break
    if not item_encontrado:
        dados_atuais.append({
            'codigo': codigo, 'nome': nome, 'codificacao': codificacao_rosto.tolist()
        })
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados_atuais, f, indent=4, ensure_ascii=False)


# --- Classe Principal da Aplicação ---
class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconhecimento Facial")
        self.root.geometry("900x700")

        self.video_source = None
        self.is_running = False
        self.detection_thread = None
        self.current_frame = None
        self.save_photo = tk.BooleanVar(value=True)

        self.carregar_dados_conhecidos()

        style = ttk.Style(self.root)
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TFrame', background='#f0f0f0')

        # --- Layout da Interface ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = ttk.Label(main_frame, text="Selecione uma fonte de vídeo para começar", anchor=tk.CENTER, background="black")
        self.video_label.pack(fill=tk.BOTH, expand=True, pady=5)

        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # --- Controles ---
        self.btn_select_video = ttk.Button(control_frame, text="Selecionar Vídeo", command=self.select_video_file)
        self.btn_select_video.pack(side=tk.LEFT, padx=5, pady=5)
        
        #Label para o Combobox de câmeras
        ttk.Label(control_frame, text="Câmera:").pack(side=tk.LEFT, padx=(10, 0), pady=5)

        #Combobox para listar as câmeras
        self.camera_options = self.listar_cameras_disponiveis()
        self.camera_combobox = ttk.Combobox(control_frame, values=self.camera_options, width=15)

        if not self.camera_options:
            self.camera_combobox['values'] = ["Nenhuma câmera encontrada"]
            self.camera_combobox.set("Nenhuma câmera encontrada")
            self.camera_combobox.config(state=tk.DISABLED)
        else:
             self.camera_combobox.set("Selecione a câmera")
        self.camera_combobox.pack(side=tk.LEFT, padx=5, pady=5)
        self.camera_combobox.bind("<<ComboboxSelected>>", self.on_camera_select)

        self.btn_start = ttk.Button(control_frame, text="Iniciar", command=self.start_detection, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_stop = ttk.Button(control_frame, text="Parar", command=self.stop_detection, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_register = ttk.Button(control_frame, text="Registrar Rosto", command=self.registrar_rosto, state=tk.DISABLED)
        self.btn_register.pack(side=tk.LEFT, padx=15, pady=5)

        self.btn_list = ttk.Button(control_frame, text="Listar Pessoas", command=self.listar_pessoas)
        self.btn_list.pack(side=tk.LEFT, padx=5, pady=5)

        self.check_save = ttk.Checkbutton(control_frame, text="Salvar foto no registro", variable=self.save_photo)
        self.check_save.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Função para detectar as câmeras
    def listar_cameras_disponiveis(self):
        cameras_disponiveis = []
        print("Procurando câmeras disponíveis...")
        for i in range(10): # Testa os primeiros 10 índices
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) # Usar CAP_DSHOW no Windows ajuda a acelerar           
            # cap = cv2.VideoCapture(i, cv2.CAP_MSMF) # Mude de CAP_DSHOW para CAP_MSMF
            if cap.isOpened():
                cameras_disponiveis.append(f"Câmera {i}")
                cap.release()
        print(f"Câmeras encontradas: {cameras_disponiveis}")
        return cameras_disponiveis
    
    # Evento para quando uma câmera é selecionada no Combobox
    def on_camera_select(self, event):
        selecao = self.camera_combobox.get() # Pega o texto, ex: "Câmera 1"
        # Extrai apenas o número do índice
        indice_camera = int(selecao.split(' ')[1])
        self.video_source = indice_camera
        self.btn_start.config(state=tk.NORMAL)

    def select_video_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Arquivos de Vídeo", "*.mp4 *.avi *.mov")])
        if filepath:
            self.video_source = filepath
            self.btn_start.config(state=tk.NORMAL)
            self.camera_combobox.set("Selecione a câmera") # Limpa a seleção da câmera
 
    def start_detection(self):
        if self.video_source is None: return
        self.is_running = True
        self.toggle_controls(is_running=True)
        self.detection_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.detection_thread.start()

    def stop_detection(self):
        self.is_running = False
        self.toggle_controls(is_running=False)
        self.video_label.config(image='', text="Detecção parada.")
        self.video_label.image = None

    def toggle_controls(self, is_running):
        state_if_running = tk.DISABLED if is_running else tk.NORMAL
        state_if_stopped = tk.NORMAL if is_running else tk.DISABLED

        self.btn_select_video.config(state=state_if_running)
        self.camera_combobox.config(state=state_if_running)
        self.btn_start.config(state=state_if_running)
        self.btn_stop.config(state=state_if_stopped)
        self.btn_list.config(state=state_if_running)

    def video_loop(self):
        try:
            cap = cv2.VideoCapture(self.video_source)
            if not cap.isOpened(): raise IOError("Não foi possível abrir a fonte de vídeo.")

            while self.is_running:
                ret, frame = cap.read()
                if not ret: break
                
                self.current_frame = frame.copy()
                processed_frame, unknown_face_found = self.process_frame(frame)
                
                self.btn_register.config(state=tk.NORMAL if unknown_face_found else tk.DISABLED)

                self.update_video_label(processed_frame)

            cap.release()
        except Exception as e:
            messagebox.showerror("Erro no Vídeo", str(e))
        
        if self.is_running:
             self.root.after(10, self.stop_detection)

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        locations = face_recognition.face_locations(rgb_small_frame)
        encodings = face_recognition.face_encodings(rgb_small_frame, locations)
        
        unknown_face_found = False
        for encoding, (top, right, bottom, left) in zip(encodings, locations):
            matches = face_recognition.compare_faces(self.rostos_conhecidos_codificados, encoding, tolerance=TOLERANCIA)
            name = "Desconhecido"
            if True in matches:
                # Encontra o melhor match em vez de apenas o primeiro
                face_distances = face_recognition.face_distance(self.rostos_conhecidos_codificados, encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.nomes_conhecidos[best_match_index]
            else:
                unknown_face_found = True

            top, right, bottom, left = top*4, right*4, bottom*4, left*4
            color = (0, 0, 255) if name == "Desconhecido" else (0, 255, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
        
        return frame, unknown_face_found

    def update_video_label(self, frame):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            w, h = pil_image.size
            max_w = self.video_label.winfo_width()
            max_h = self.video_label.winfo_height()
            if w > max_w or h > max_h:
                pil_image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            
            tk_image = ImageTk.PhotoImage(image=pil_image)
            self.video_label.config(image=tk_image, text="")
            self.video_label.image = tk_image
        except:
             pass

    def registrar_rosto(self):
        if self.current_frame is None: return

        rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, locations)

        face_to_register = None
        for encoding, location in zip(encodings, locations):
            matches = face_recognition.compare_faces(self.rostos_conhecidos_codificados, encoding, tolerance=TOLERANCIA)
            if not any(matches):
                face_to_register = (encoding, location)
                break
        
        if face_to_register is None:
            messagebox.showwarning("Registro", "Nenhum rosto desconhecido encontrado para registrar.")
            return

        nome = simpledialog.askstring("Registro", "Digite o nome completo:", parent=self.root)
        if not nome: return
        codigo = simpledialog.askstring("Registro", "Digite o codigo:", parent=self.root)
        if not codigo: return

        encoding, location = face_to_register
        salvar_dados(codigo, nome, encoding)
        
        if self.save_photo.get():
            self.salvar_referencia_foto(codigo, nome, location)

        messagebox.showinfo("Sucesso", f"Pessoa '{nome}' registrada com sucesso!")
        self.carregar_dados_conhecidos()

    def salvar_referencia_foto(self, codigo, nome, location):
        if not os.path.exists(PASTA_FOTOS):
            os.makedirs(PASTA_FOTOS)
        top, right, bottom, left = location
        rosto_img = self.current_frame[top:bottom, left:right]
        caminho_foto = os.path.join(PASTA_FOTOS, f"{codigo}_{nome}.jpg")
        cv2.imwrite(caminho_foto, rosto_img)
        print(f"Foto de referência salva em: {caminho_foto}")

    def carregar_dados_conhecidos(self):
        self.rostos_conhecidos_codificados, self.codigos_conhecidos, self.nomes_conhecidos = carregar_dados_salvos()
        print(f"[Sistema] {len(self.nomes_conhecidos)} rostos conhecidos carregados.")

    def listar_pessoas(self):
        _, codigos, nomes = carregar_dados_salvos()
        if not nomes:
            messagebox.showinfo("Lista de Pessoas", "Nenhuma pessoa cadastrada.")
            return
        lista_formatada = "\n".join([f"Nome: {n}, codigo: {c}" for n, c in zip(nomes, codigos)])
        messagebox.showinfo("Pessoas Cadastradas", lista_formatada)

    def on_closing(self):
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1)
        self.root.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()