
# Sistema de Login Facial e Hub de Aplicações de Visão Computacional

Este projeto é uma suíte integrada de aplicações de visão computacional desenvolvida em **Python**, com uma interface gráfica moderna construída com **Tkinter (TTK)**.  
O sistema é protegido por um **login de reconhecimento facial**, que, após uma autenticação bem-sucedida, dá acesso a um hub central para lançar diferentes módulos de IA.

---

## 🚀 Funcionalidades Principais

- **Login Seguro por Reconhecimento Facial**  
  Acesso ao sistema através da câmera, com um tempo limite de 5 segundos para a tentativa de autenticação.

- **Hub de Aplicações**  
  Uma tela principal (Home) que serve como um lançador para outros módulos de visão computacional.

- **Módulo de Reconhecimento Facial Completo**:
  - Reconhecimento em tempo real a partir de múltiplas fontes (webcam ou arquivos de vídeo).
  - Seleção dinâmica de câmera, caso o computador tenha mais de uma.
  - Cadastro de novos usuários (nome e CPF) com captura de rosto.
  - Opção para salvar ou não uma foto de referência do usuário no momento do cadastro.
  - Listagem de todos os usuários cadastrados.

- **Módulo de Detecção de Carros**:
  - Detecção de veículos em tempo real usando Haar Cascades.
  - Opção de usar webcam ou arquivos de vídeo.
  - Salvamento automático de uma imagem de cada carro detectado, com nome de arquivo contendo data e hora exatas.

- **Interface Gráfica Intuitiva**  
  Todas as aplicações possuem uma interface gráfica construída com `tkinter.ttk`, garantindo uma experiência de usuário amigável e responsiva.

---

## 🛠️ Tecnologias Utilizadas

- Python 3.x  
- OpenCV (`opencv-python`) — Processamento de imagem e captura de vídeo  
- Face Recognition (`face-recognition`) — Codificação e comparação de rostos  
- dlib — Dependência principal da biblioteca face-recognition  
- Pillow (PIL) — Integração de imagens com Tkinter  
- NumPy — Manipulação de arrays e cálculos numéricos  
- Tkinter (ttk) — Interface gráfica  

---

## ⚙️ Configuração do Ambiente

### 1. Pré-requisitos

É altamente recomendado o uso de um ambiente virtual para evitar conflitos de pacotes.

```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate

# No macOS/Linux:
source venv/bin/activate
```

### 2. Instalação das Dependências

A instalação do `dlib` e `face-recognition` pode ser complexa no Windows e exigir a instalação do CMake e de um compilador C++.

```bash
pip install opencv-python
pip install face-recognition
pip install Pillow
pip install numpy
```

### 3. Arquivos Necessários

Certifique-se de que os seguintes arquivos e pastas (quando aplicável) estão na pasta raiz do seu projeto:

- `login_system.py` — Script principal  
- `gui_reconhecimento.py` — App de gerenciamento facial  
- `gui_detector.py` — App de detecção de carros  
- `camera_off.png` — Imagem para exibir quando a câmera está desligada  
- Pasta `detection_haarcascades/` contendo o arquivo `cars.xml`

---

## 🚀 Como Usar a Aplicação

### 1. Primeiro Uso: Cadastrando um Rosto

Antes de usar o login, você precisa ter pelo menos um rosto cadastrado.

Execute o aplicativo de gerenciamento facial:

```bash
python gui_reconhecimento.py
```

- Use a interface para selecionar sua câmera e clique em **"Iniciar"**.
- Quando um rosto *Desconhecido* for detectado, o botão **"Registrar Rosto"** ficará ativo.
- Clique no botão, preencha seu nome e CPF. Isso criará o arquivo `dados_registrados.json` que o sistema de login usará.

---

### 2. Executando o Sistema de Login

Com pelo menos um usuário cadastrado, você pode iniciar o sistema principal:

```bash
python login_system.py
```

- A janela de login com a câmera será aberta.
- Posicione seu rosto e clique em **"Login com Rosto"**.
- Se o seu rosto for reconhecido em até 5 segundos, a janela de login se fechará e a **Tela Principal (Home)** será aberta.

---

### 3. Navegando na Tela Principal

Na Tela Principal, você verá uma mensagem de boas-vindas e os botões para os aplicativos.  
Clique em qualquer um deles para iniciar o módulo correspondente em uma nova janela.

---

## 📁 Estrutura do Projeto

```
.
├── detection_haarcascades/
│   └── cars.xml
├── fotos_registro/         # Criada automaticamente para salvar fotos de referência
├── carros_detectados/      # Criada automaticamente para salvar imagens de carros
├── venv/                   # Pasta do ambiente virtual
├── login_system.py         # Ponto de entrada principal da aplicação
├── gui_reconhecimento.py   # Módulo de reconhecimento e cadastro facial
├── gui_detector.py         # Módulo de detecção de carros
├── camera_off.png          # Imagem padrão para quando a câmera está desligada
├── dados_registrados.json  # "Banco de dados" com os dados faciais (criado automaticamente)
└── README.md               # Este arquivo
```

### 🤝 Contribuições

Contribuições são bem-vindas!  
Sinta-se à vontade para abrir *Issues*, sugerir melhorias ou enviar *Pull Requests*.

1. Fork este repositório
2. Crie sua branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: nova funcionalidade'`)
4. Push na sua branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 👨‍💻 Autor

- Desenvolvido por [Faguiro](https://github.com/Faguiro) 🚀  
- Entre em contato: faguiro2005@gmail.com
- Linkedin: [faguiro](https://linkedin.com/in/faguiro)


