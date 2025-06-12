import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os
from datetime import datetime
import threading

class CarDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Carros")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # --- Variáveis de Estado ---
        self.video_source = None
        self.is_running = False
        self.detection_thread = None
        self.save_images = tk.BooleanVar(value=True)

        # --- Estilos TTK ---
        style = ttk.Style(self.root)
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Status.TLabel', font=('Helvetica', 9), foreground='grey')

        # --- Layout da Interface ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Painel de Vídeo
        self.video_label = ttk.Label(main_frame, text="Selecione uma fonte de vídeo para começar", anchor=tk.CENTER, background="black")
        self.video_label.pack(fill=tk.BOTH, expand=True, pady=5)

        # Painel de Controle
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Botões
        self.btn_select_video = ttk.Button(control_frame, text="Selecionar Vídeo", command=self.select_video_file)
        self.btn_select_video.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_use_webcam = ttk.Button(control_frame, text="Usar Webcam", command=self.use_webcam)
        self.btn_use_webcam.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_start = ttk.Button(control_frame, text="Iniciar Detecção", command=self.start_detection, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_stop = ttk.Button(control_frame, text="Parar Detecção", command=self.stop_detection, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Checkbox para salvar imagens
        self.check_save = ttk.Checkbutton(control_frame, text="Salvar Imagens Detectadas", variable=self.save_images)
        self.check_save.pack(side=tk.RIGHT, padx=10, pady=5)

        # Rótulo de Status
        self.status_label = ttk.Label(control_frame, text="Nenhuma fonte selecionada", style='Status.TLabel')
        self.status_label.pack(side=tk.RIGHT, padx=10, expand=True)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_video_file(self):
        """Abre um diálogo para o usuário selecionar um arquivo de vídeo."""
        filepath = filedialog.askopenfilename(
            title="Selecione um arquivo de vídeo",
            filetypes=(("Arquivos de Vídeo", "*.mp4 *.avi *.mov"), ("Todos os arquivos", "*.*"))
        )
        if filepath:
            self.video_source = filepath
            self.status_label.config(text=f"Vídeo: {os.path.basename(filepath)}")
            self.btn_start.config(state=tk.NORMAL)

    def use_webcam(self):
        """Configura a fonte de vídeo para a webcam padrão."""
        self.video_source = 0  # 0 para a webcam padrão
        self.status_label.config(text="Fonte: Webcam")
        self.btn_start.config(state=tk.NORMAL)

    def start_detection(self):
        """Inicia a thread de detecção de vídeo."""
        if self.video_source is None:
            messagebox.showwarning("Aviso", "Por favor, selecione uma fonte de vídeo primeiro.")
            return

        self.is_running = True
        self.toggle_controls(is_running=True)
        
        # Usamos uma thread para não travar a GUI
        self.detection_thread = threading.Thread(target=self.video_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def stop_detection(self):
        """Para a detecção de vídeo."""
        self.is_running = False
        self.toggle_controls(is_running=False)
        self.video_label.config(image='', text="Detecção parada. Selecione uma fonte de vídeo.")
        self.video_label.image = None

    def toggle_controls(self, is_running):
        """Habilita/desabilita os botões com base no estado da detecção."""
        if is_running:
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_select_video.config(state=tk.DISABLED)
            self.btn_use_webcam.config(state=tk.DISABLED)
        else:
            self.btn_start.config(state=tk.NORMAL if self.video_source is not None else tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_select_video.config(state=tk.NORMAL)
            self.btn_use_webcam.config(state=tk.NORMAL)

    def video_loop(self):
        """O loop principal que processa o vídeo."""
        # --- Configurações do Detector ---
        CLASSIFICADOR_PATH = 'detection_haarcascades/cars.xml'
        PASTA_SAIDA = 'carros_detectados'
        SCALE_FACTOR = 1.05
        MIN_NEIGHBORS = 5

        try:
            classificador_carro = cv2.CascadeClassifier(CLASSIFICADOR_PATH)
            if classificador_carro.empty():
                raise IOError("Não foi possível carregar o classificador Haar Cascade.")
            
            cap = cv2.VideoCapture(self.video_source)
            if not cap.isOpened():
                raise IOError(f"Não foi possível abrir a fonte de vídeo: {self.video_source}")

            if not os.path.exists(PASTA_SAIDA):
                os.makedirs(PASTA_SAIDA)

            self.status_label.config(text="Detectando...")

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    self.status_label.config(text="Fim do vídeo.")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                carros_detectados = classificador_carro.detectMultiScale(
                    gray, scaleFactor=SCALE_FACTOR, minNeighbors=MIN_NEIGHBORS, minSize=(50, 50))

                for (x, y, w, h) in carros_detectados:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, 'Carro', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if self.save_images.get():
                        carro_recortado = frame[y:y+h, x:x+w]
                        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
                        nome_arquivo = f'carro_{timestamp}.jpg'
                        caminho_completo = os.path.join(PASTA_SAIDA, nome_arquivo)
                        cv2.imwrite(caminho_completo, carro_recortado)

                # Converte o frame para exibição no Tkinter
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                
                # Redimensiona a imagem para caber no label, mantendo a proporção
                w, h = pil_image.size
                max_w = self.video_label.winfo_width()
                max_h = self.video_label.winfo_height()
                if w > max_w or h > max_h:
                    pil_image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                
                tk_image = ImageTk.PhotoImage(image=pil_image)

                self.video_label.config(image=tk_image, text="")
                self.video_label.image = tk_image # Mantém a referência

            cap.release()
            if self.is_running: # Se parou por fim de vídeo, e não por botão
                self.root.after(100, self.stop_detection)

        except Exception as e:
            messagebox.showerror("Erro", str(e))
            if self.is_running:
                self.root.after(100, self.stop_detection)
    
    def on_closing(self):
        """Garante que a thread pare ao fechar a janela."""
        self.stop_detection()
        self.root.destroy()

# --- Ponto de Entrada da Aplicação ---
if __name__ == '__main__':
    root = tk.Tk()
    app = CarDetectorApp(root)
    root.mainloop()