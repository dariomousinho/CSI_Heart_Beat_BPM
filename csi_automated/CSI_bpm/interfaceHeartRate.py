import sys
from tkinter import *
from PIL import Image, ImageTk, ImageSequence
import os

# Definição das constantes
BT_FONT = ('arial', 12, 'bold')
WINDOW_COLOR = '#1e3743'
BACKGROUND_COLOR = 'white'
BT_BACKGROUND_COLOR = '#103d72'
BT_FOREGROUND_COLOR = 'white'
BT_BORDER = 3
global ROOT

class Logger():
    def __init__(self, widget):
        self.widget = widget
        self.terminal = sys.stdout
        sys.stdout = self

    def write(self, message):
        self.widget.config(state=NORMAL)
        self.widget.insert(END, message)
        self.widget.see(END)  # Auto-scroll to the end
        self.widget.config(state=DISABLED)

    def flush(self):
        pass

class InterfaceHeartRate():
    def __init__(self):
        # Cria a janela de monitoramento
        self.root = Tk()
        global ROOT
        ROOT = self.root

        self.params = None

        self.active_button = None

        # Configurações básicas da janela
        self.root.title("Vital Signs Monitor")
        self.root.configure(background=WINDOW_COLOR)
        self.root.geometry("380x280+0+0")
        self.root.maxsize(width=380, height=280)
        self.root.minsize(width=380, height=280)


        # Criação dos componentes da janela
        self.criar_menubar()
        self.criar_frame()

        # labels iniciais
        self.load_animated_gif("heartbeat.gif")

        lbl2 = Label(ROOT, text='-', fg="#FF6666", bg="white", font=(None, 15)).place(x = 190, y = 50, width=40, height=20)
        lbl1 = Label(ROOT, text='bpm', bg="white", font=(None, 15)).place(x = 240, y = 50, width=100, height=20)

        # Adicionar botão de Debug
        self.debug_button = Button(self.root, text="Debug",bg="red",fg="white", command=self.show_debug_console)
        self.debug_button.place(x=140, y=100, width=100, height=30)

        # Adicionar botões de configuração
        self.create_buttons()

        # Define uma função a ser executada ao fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.sair)

        self.set_active_button(self.config8_button)
    
    # Criação da barra de menu
    def criar_menubar(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        menubar.add_cascade(label="Sair", command=self.sair)

    def show_heart_rate(self, heart_rate):
        lbl2 = Label(ROOT, text=heart_rate, fg="red", bg="white", font=(None, 15)).place(x = 190, y = 50, width=30, height=20)


    # Carregar o GIF animado
    def load_animated_gif(self, gif_path):
        try:
            gif_path = os.path.join(os.path.dirname(__file__), gif_path)  # Usar caminho relativo ao script
            gif_path = os.path.abspath(gif_path)  # Garantir o caminho absoluto completo
            print(f"Tentando carregar o GIF do caminho completo: {gif_path}")  # Imprime o caminho completo do GIF
            self.gif = Image.open(gif_path)  # Abre o GIF
            print(f"Formato do arquivo: {self.gif.format}, Tamanho: {self.gif.size}, Frames: {self.gif.n_frames}")

            # Redimensionar os frames para caber no espaço definido (por exemplo 150x80)
            target_size = (120, 70)  # Tamanho alvo para o GIF na interface
            self.frames = [ImageTk.PhotoImage(frame.resize(target_size, Image.ANTIALIAS)) 
                        for frame in ImageSequence.Iterator(self.gif)]  # Carregar e redimensionar os frames

            self.gif_label = Label(ROOT)
            self.gif_label.place(x=50, y=20, width=120, height=70)  # Ajuste o tamanho do gif aqui
            self.animate_gif(0)  # Começar a animação do gif
        except Exception as e:
            print(f"Erro ao carregar o GIF: {e}")

    # Função para animar o gif
    def animate_gif(self, frame_index):
        frame = self.frames[frame_index]
        self.gif_label.configure(image=frame)
        frame_index = (frame_index + 1) % len(self.frames)  # Loop nos frames
        self.root.after(50, self.animate_gif, frame_index)  # Controlar a velocidade da animação


    def create_buttons(self):
        # Adding buttons at the bottom of the interface
        self.config8_button = Button(self.root, text="Standing", command=lambda: self.activate_config(self.config8_button, 6, 0.8, 3.3, 3, 0.8))
        self.config8_button.place(x=20, y=150, width=160, height=30)

        self.config5_button = Button(self.root, text="Sitting", command=lambda: self.activate_config(self.config5_button, 6, 0.8, 3.3, 2, 0.5))
        self.config5_button.place(x=200, y=150, width=160, height=30)

        self.config4_button = Button(self.root, text="Lying Down", command=lambda: self.activate_config(self.config4_button, 6, 0.8, 3.3, 1, 0.5))
        self.config4_button.place(x=110, y=185, width=160, height=30)

    
    def activate_config(self, button, w_size, l_freq, h_freq, p, limiar):
        self.set_params(w_size, l_freq, h_freq, p, limiar)
        self.set_active_button(button)

    def set_active_button(self, button):
        # Redefinir a cor de todos os botões para o padrão
        self.config8_button.config(bg="lightgray")
        self.config5_button.config(bg="lightgray")
        self.config4_button.config(bg="lightgray")

        # Definir o botão ativo para vermelho
        button.config(bg="red")
        self.active_button = button

    def set_params(self, w_size, l_freq, h_freq, p):
        self.params = {
            'window_size': w_size,
            'lowfreq': l_freq,
            'highfreq': h_freq,
            'peak': p
        }
        print(f"Parâmetros definidos: {self.params}")

    def get_params(self):
        params = self.params
        return params
    
    # Criação do frame
    def criar_frame(self):
        self.frame = Frame(self.root, bg=BACKGROUND_COLOR)
        self.frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_debug_console(self):
        # Cria uma nova janela para o console de debug
        self.debug_window = Toplevel(self.root)
        self.debug_window.title("Debug Console")
        self.debug_window.geometry("500x300")
        self.text_area = Text(self.debug_window, state=DISABLED)
        self.text_area.pack(expand=True, fill=BOTH)

        # Redirecionar stdout para a janela de debug
        self.logger = Logger(self.text_area)
        print("Debug window...")


    # Fecha o programa
    def sair(self):
        sys.stdout = sys.__stdout__
        self.root.destroy()

if __name__ == "__main__":
    # Chama a janela de batimento
    InterfaceHeartRate()