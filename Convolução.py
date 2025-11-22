import numpy as np
from scipy import integrate, signal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel

def gerar_sinal(func, xmin, xmax, N=1000):
    t = np.linspace(xmin, xmax, N)
    x = func(t)
    return t, x

def conv_continua(f, g, t_output):
    # A função conv_continua agora recebe t_output, que é o domínio para a convolução
    # Para cada ponto ti em t_output, calculamos a integral
    y = np.array([
        integrate.quad(lambda tau: f(tau) * g(ti - tau), -np.inf, np.inf)[0]
        for ti in t_output
    ])
    return y

class HelpDialog:
    def __init__(self, parent, title, content):
        self.dialog = Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Texto de ajuda com scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)
        
        self.text_widget.insert(tk.END, content)
        self.text_widget.config(state=tk.DISABLED)
        
        # Botão fechar
        ttk.Button(main_frame, text="Fechar", command=self.dialog.destroy).pack(pady=(10, 0))

class ExamplesDialog:
    def __init__(self, parent, callback):
        self.callback = callback
        self.dialog = Toplevel(parent)
        self.dialog.title("Exemplos de Convolução")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de exemplos
        ttk.Label(main_frame, text="Selecione um exemplo para carregar:", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Frame para lista
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox com scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Exemplos criativos
        self.examples = [
            {
                "name": "🔔 Sino e Pulso - Reverberação",
                "description": "Simula o eco de um sino tocando em um ambiente fechado",
                "f1": "np.exp(-t**2) * np.cos(5*t)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "1",
                "f2_interval": "finito", "f2_x1": "-0.5", "f2_x2": "0.5"
            },
            {
                "name": "📡 Radar - Pulso e Eco",
                "description": "Sistema de radar detectando um objeto distante",
                "f1": "1",
                "f1_interval": "finito", "f1_x1": "-1", "f1_x2": "1",
                "f2": "np.exp(-2*t**2)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🎵 Nota Musical - Harmônicos",
                "description": "Convolução de duas ondas senoidais com frequências diferentes",
                "f1": "np.cos(2*np.pi*t)",
                "f1_interval": "finito", "f1_x1": "-2", "f1_x2": "2",
                "f2": "np.cos(4*np.pi*t)",
                "f2_interval": "finito", "f2_x1": "-1", "f2_x2": "1"
            },
            {
                "name": "⚡ Circuito RC - Resposta ao Impulso",
                "description": "Resposta de um circuito RC a um pulso de entrada",
                "f1": "1",
                "f1_interval": "finito", "f1_x1": "0", "f1_x2": "1",
                "f2": "np.exp(-t)",
                "f2_interval": "semi_inf_dir", "f2_x1": "0", "f2_x2": ""
            },
            {
                "name": "🌊 Onda Modulada - AM",
                "description": "Modulação em amplitude de uma portadora senoidal",
                "f1": "np.cos(10*np.pi*t)",
                "f1_interval": "finito", "f1_x1": "-1", "f1_x2": "1",
                "f2": "np.exp(-t**2/2)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🔊 Alto-falante - Resposta de Frequência",
                "description": "Resposta de um alto-falante a diferentes frequências",
                "f1": "np.sin(3*np.pi*t) * np.exp(-0.5*t**2)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.cos(np.pi*t)",
                "f2_interval": "finito", "f2_x1": "-2", "f2_x2": "2"
            },
            {
                "name": "📶 Filtro Passa-Baixa",
                "description": "Filtragem de um sinal ruidoso com filtro gaussiano",
                "f1": "np.cos(8*np.pi*t) + 0.5*np.cos(20*np.pi*t)",
                "f1_interval": "finito", "f1_x1": "-2", "f1_x2": "2",
                "f2": "np.exp(-4*t**2)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🎯 Detecção de Borda",
                "description": "Operação de detecção de bordas em processamento de sinais",
                "f1": "np.where((t>-1)&(t<0), 1, np.where((t>=0)&(t<1), -1, 0))",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where((t>-2)&(t<2), 1, 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🌡️ Sensor de Temperatura",
                "description": "Resposta de um sensor térmico a mudanças de temperatura",
                "f1": "np.where(t>=0, t*np.exp(-t), 0)",
                "f1_interval": "semi_inf_dir", "f1_x1": "0", "f1_x2": "",
                "f2": "np.exp(-2*t**2)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🎸 Corda de Violão",
                "description": "Vibração de uma corda com amortecimento",
                "f1": "np.cos(6*np.pi*t) * np.exp(-0.2*np.abs(t))",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.exp(-t**2)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "📸 Flash Fotográfico",
                "description": "Resposta de um sensor de imagem a um flash de luz",
                "f1": "np.exp(-5*t**2)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where((t>=0)&(t<0.1), 10, 0)",
                "f2_interval": "semi_inf_dir", "f2_x1": "0", "f2_x2": ""
            },
            {
                "name": "🚗 Suspensão Automotiva",
                "description": "Resposta de um amortecedor a um impacto na estrada",
                "f1": "np.where(t>=0, np.exp(-3*t) * np.cos(8*t), 0)",
                "f1_interval": "semi_inf_dir", "f1_x1": "0", "f1_x2": "",
                "f2": "np.where((t>-0.2)&(t<0.2), 1, 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🌐 Antena de Rádio",
                "description": "Transmissão de sinal através de uma antena dipolo",
                "f1": "np.cos(20*np.pi*t)",
                "f1_interval": "finito", "f1_x1": "-0.5", "f1_x2": "0.5",
                "f2": "np.sinc(5*t)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🏥 Eletrocardiograma",
                "description": "Processamento de sinal cardíaco através de filtro",
                "f1": "np.exp(-t**2) * (1 + 0.5*np.cos(4*np.pi*t))",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where((t>-0.1)&(t<0.1), 1, 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🌊 Tsunami - Propagação",
                "description": "Propagação de ondas sísmicas no oceano",
                "f1": "np.exp(-0.1*t**2) * np.cos(np.pi*t)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where(t>=0, t**2 * np.exp(-t), 0)",
                "f2_interval": "semi_inf_dir", "f2_x1": "0", "f2_x2": ""
            },
            {
                "name": "🎤 Microfone Direcional",
                "description": "Captação de som com padrão direcional",
                "f1": "np.cos(15*np.pi*t) * np.exp(-2*np.abs(t))",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.exp(-t**2/4)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🛰️ Comunicação Satelital",
                "description": "Modulação de sinal para transmissão espacial",
                "f1": "np.cos(50*np.pi*t)",
                "f1_interval": "finito", "f1_x1": "-1", "f1_x2": "1",
                "f2": "np.where((t>-0.05)&(t<0.05), np.cos(100*np.pi*t), 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "⚙️ Engrenagem Mecânica",
                "description": "Vibração de engrenagens em transmissão",
                "f1": "np.where(t>=0, np.exp(-0.5*t) * np.sin(12*np.pi*t), 0)",
                "f1_interval": "semi_inf_dir", "f1_x1": "0", "f1_x2": "",
                "f2": "np.sum([np.where((t>k*0.1)&(t<k*0.1+0.05), 1, 0) for k in range(20)], axis=0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🔬 Microscópio Óptico",
                "description": "Função de espalhamento pontual de lente",
                "f1": "np.exp(-25*t**2)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where((t>-0.1)&(t<0.1), np.sinc(20*t), 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🌡️ Termopar Industrial",
                "description": "Resposta térmica com constante de tempo",
                "f1": "np.where(t>=0, 1 - np.exp(-2*t), 0)",
                "f1_interval": "semi_inf_dir", "f1_x1": "0", "f1_x2": "",
                "f2": "np.where((t>0)&(t<5), 1, 0)",
                "f2_interval": "semi_inf_dir", "f2_x1": "0", "f2_x2": ""
            },
            {
                "name": "🎺 Instrumento de Sopro",
                "description": "Resposta acústica de tubo ressonante",
                "f1": "np.cos(8*np.pi*t) * np.exp(-np.abs(t)/2)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where((t>-1)&(t<1), np.cos(np.pi*t/2), 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🌪️ Detector de Turbulência",
                "description": "Análise de fluxo de ar turbulento",
                "f1": "np.random.normal(0, 0.1, len(t)) + np.cos(3*np.pi*t)",
                "f1_interval": "finito", "f1_x1": "-3", "f1_x2": "3",
                "f2": "np.exp(-t**2/0.5)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🔋 Carregador de Bateria",
                "description": "Curva de carga com controle de corrente",
                "f1": "np.where(t>=0, np.exp(-0.3*t), 0)",
                "f1_interval": "semi_inf_dir", "f1_x1": "0", "f1_x2": "",
                "f2": "np.where((t>0)&(t<2), t/2, np.where((t>=2)&(t<4), 1, 0))",
                "f2_interval": "semi_inf_dir", "f2_x1": "0", "f2_x2": ""
            },
            {
                "name": "🎨 Scanner de Imagem",
                "description": "Varredura óptica com função de linha",
                "f1": "np.where((t>-0.5)&(t<0.5), 1, 0)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.exp(-10*t**2) * np.cos(30*np.pi*t)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🌈 Prisma Óptico",
                "description": "Dispersão cromática da luz branca",
                "f1": "np.sum([np.cos(2*np.pi*f*t) for f in [1,2,3,4,5]], axis=0)",
                "f1_interval": "finito", "f1_x1": "-2", "f1_x2": "2",
                "f2": "np.exp(-t**2) * np.cos(np.pi*t)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🚀 Propulsão de Foguete",
                "description": "Impulso específico com queima de combustível",
                "f1": "np.where((t>=0)&(t<10), np.exp(-t/5), 0)",
                "f1_interval": "semi_inf_dir", "f1_x1": "0", "f1_x2": "",
                "f2": "np.where((t>-1)&(t<1), 1-np.abs(t), 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🧲 Campo Magnético",
                "description": "Resposta de bobina a campo magnético variável",
                "f1": "np.cos(2*np.pi*t) * np.exp(-0.1*t**2)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where(t>=0, t * np.exp(-4*t), 0)",
                "f2_interval": "semi_inf_dir", "f2_x1": "0", "f2_x2": ""
            },
            {
                "name": "🌊 Sonar Submarino",
                "description": "Ecolocalização em ambiente aquático",
                "f1": "np.cos(40*np.pi*t) * np.exp(-t**2/0.1)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where((t>2)&(t<2.1), 0.5, 0)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            },
            {
                "name": "🎯 Laser Pulsado",
                "description": "Pulso de laser com dispersão temporal",
                "f1": "np.exp(-50*t**2)",
                "f1_interval": "infinito", "f1_x1": "", "f1_x2": "",
                "f2": "np.where(t>=0, np.exp(-10*t) * np.cos(100*np.pi*t), 0)",
                "f2_interval": "semi_inf_dir", "f2_x1": "0", "f2_x2": ""
            },
            {
                "name": "🔊 Cancelamento de Ruído",
                "description": "Filtro adaptativo para cancelar ruído ambiente",
                "f1": "np.cos(6*np.pi*t) + 0.3*np.cos(18*np.pi*t)",
                "f1_interval": "finito", "f1_x1": "-1", "f1_x2": "1",
                "f2": "np.exp(-2*t**2) * np.cos(6*np.pi*t)",
                "f2_interval": "infinito", "f2_x1": "", "f2_x2": ""
            }
        ]
        
        # Adicionar exemplos à lista
        for i, example in enumerate(self.examples):
            self.listbox.insert(tk.END, example["name"])
        
        # Frame para descrição
        desc_frame = ttk.LabelFrame(main_frame, text="Descrição do Exemplo")
        desc_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.desc_label = ttk.Label(desc_frame, text="Selecione um exemplo para ver a descrição", 
                                   wraplength=650, justify=tk.LEFT)
        self.desc_label.pack(padx=10, pady=10)
        
        # Bind para mostrar descrição
        self.listbox.bind('<<ListboxSelect>>', self.show_description)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Carregar Exemplo", command=self.load_example).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Fechar", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def show_description(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            example = self.examples[index]
            self.desc_label.config(text=example["description"])
    
    def load_example(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            example = self.examples[index]
            self.callback(example)
            self.dialog.destroy()
        else:
            messagebox.showwarning("Aviso", "Por favor, selecione um exemplo primeiro.")

class ConvolutionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convolução de Sinais Contínuos")
        
        # Configurar a janela principal para ser responsiva
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configuração da figura matplotlib
        self.fig, self.axes = plt.subplots(3, 1, figsize=(10, 8))
        self.ax1, self.ax2, self.ax3 = self.axes
        
        # Inicialização dos plots vazios
        self.l1, = self.ax1.plot([], [], label='f(t)', color='blue')
        self.l2, = self.ax2.plot([], [], label='g(t)', color='red')
        self.l3, = self.ax3.plot([], [], label='f * g', color='green')
        
        for ax in self.axes:
            ax.legend()
            ax.grid(True)
        
        self.ax1.set_title('Função f(t)')
        self.ax2.set_title('Função g(t)')
        self.ax3.set_title('Convolução f * g')
        
        self.fig.tight_layout()
        
        self.setup_gui()
    
    def setup_gui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10) # Usando grid para o main_frame
        
        # Configurar main_frame para ser responsivo
        main_frame.grid_rowconfigure(1, weight=1) # Linha do canvas
        main_frame.grid_columnconfigure(0, weight=1) # Coluna única
        
        # Frame de entradas
        input_frame = ttk.LabelFrame(main_frame, text="Parâmetros de Entrada")
        input_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 10))
        
        # Configurar input_frame para ser responsivo
        # A coluna 0 do input_frame deve expandir para que os sub-frames dentro dela se expandam
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Função 1
        func1_frame = ttk.Frame(input_frame)
        func1_frame.grid(row=0, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        func1_frame.grid_columnconfigure(1, weight=1) # Faz o entry expandir
        
        ttk.Label(func1_frame, text="Função f(t):").grid(row=0, column=0, sticky=tk.W)
        self.func1_var = tk.StringVar(value="np.exp(-t**2)")
        self.func1_entry = ttk.Entry(func1_frame, textvariable=self.func1_var)
        self.func1_entry.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        
        help_f1_btn = ttk.Button(func1_frame, text="?", width=3, 
                                command=lambda: self.show_help("Função f(t)", self.get_function_help()))
        help_f1_btn.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        
        # Intervalo da Função 1
        interval1_frame = ttk.Frame(input_frame)
        interval1_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        # Colunas para os labels e entries dentro de interval1_frame
        interval1_frame.grid_columnconfigure(1, weight=1) # Combobox
        interval1_frame.grid_columnconfigure(3, weight=1) # x1_entry
        interval1_frame.grid_columnconfigure(5, weight=1) # x2_entry
        
        ttk.Label(interval1_frame, text="Intervalo f(t):").grid(row=0, column=0, sticky=tk.W)
        
        self.f1_interval_type = tk.StringVar(value="infinito")
        interval_f1_combo = ttk.Combobox(interval1_frame, textvariable=self.f1_interval_type, 
                                        values=["infinito", "semi_inf_esq", "semi_inf_dir", "finito"], 
                                        state="readonly", width=12)
        interval_f1_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        interval_f1_combo.bind('<<ComboboxSelected>>', self.update_f1_interval_fields)
        
        ttk.Label(interval1_frame, text="x1:").grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        self.f1_x1_var = tk.StringVar(value="")
        self.f1_x1_entry = ttk.Entry(interval1_frame, textvariable=self.f1_x1_var, width=8, state="disabled")
        self.f1_x1_entry.grid(row=0, column=3, sticky=tk.EW, padx=(5, 0))
        
        ttk.Label(interval1_frame, text="x2:").grid(row=0, column=4, sticky=tk.E, padx=(10, 0))
        self.f1_x2_var = tk.StringVar(value="")
        self.f1_x2_entry = ttk.Entry(interval1_frame, textvariable=self.f1_x2_var, width=8, state="disabled")
        self.f1_x2_entry.grid(row=0, column=5, sticky=tk.EW, padx=(5, 0))
        
        help_int1_btn = ttk.Button(interval1_frame, text="?", width=3,
                                  command=lambda: self.show_help("Intervalos", self.get_interval_help()))
        help_int1_btn.grid(row=0, column=6, sticky=tk.E, padx=(5, 0))
        
        # Função 2
        func2_frame = ttk.Frame(input_frame)
        func2_frame.grid(row=2, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        func2_frame.grid_columnconfigure(1, weight=1) # Faz o entry expandir
        
        ttk.Label(func2_frame, text="Função g(t):").grid(row=0, column=0, sticky=tk.W)
        self.func2_var = tk.StringVar(value="np.exp(-2*t**2)")
        self.func2_entry = ttk.Entry(func2_frame, textvariable=self.func2_var)
        self.func2_entry.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        
        help_f2_btn = ttk.Button(func2_frame, text="?", width=3,
                                command=lambda: self.show_help("Função g(t)", self.get_function_help()))
        help_f2_btn.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        
        # Intervalo da Função 2
        interval2_frame = ttk.Frame(input_frame)
        interval2_frame.grid(row=3, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        interval2_frame.grid_columnconfigure(1, weight=1) # Combobox
        interval2_frame.grid_columnconfigure(3, weight=1) # x1_entry
        interval2_frame.grid_columnconfigure(5, weight=1) # x2_entry
        
        ttk.Label(interval2_frame, text="Intervalo g(t):").grid(row=0, column=0, sticky=tk.W)
        
        self.f2_interval_type = tk.StringVar(value="infinito")
        interval_f2_combo = ttk.Combobox(interval2_frame, textvariable=self.f2_interval_type, 
                                        values=["infinito", "semi_inf_esq", "semi_inf_dir", "finito"], 
                                        state="readonly", width=12)
        interval_f2_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        interval_f2_combo.bind('<<ComboboxSelected>>', self.update_f2_interval_fields)
        
        ttk.Label(interval2_frame, text="x1:").grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        self.f2_x1_var = tk.StringVar(value="")
        self.f2_x1_entry = ttk.Entry(interval2_frame, textvariable=self.f2_x1_var, width=8, state="disabled")
        self.f2_x1_entry.grid(row=0, column=3, sticky=tk.EW, padx=(5, 0))
        
        ttk.Label(interval2_frame, text="x2:").grid(row=0, column=4, sticky=tk.E, padx=(10, 0))
        self.f2_x2_var = tk.StringVar(value="")
        self.f2_x2_entry = ttk.Entry(interval2_frame, textvariable=self.f2_x2_var, width=8, state="disabled")
        self.f2_x2_entry.grid(row=0, column=5, sticky=tk.EW, padx=(5, 0))
        
        help_int2_btn = ttk.Button(interval2_frame, text="?", width=3,
                                  command=lambda: self.show_help("Intervalos", self.get_interval_help()))
        help_int2_btn.grid(row=0, column=6, sticky=tk.E, padx=(5, 0))
        
        # Parâmetros de domínio
        domain_frame = ttk.Frame(input_frame)
        domain_frame.grid(row=4, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        domain_frame.grid_columnconfigure(1, weight=1) # xmin_entry
        domain_frame.grid_columnconfigure(3, weight=1) # xmax_entry
        domain_frame.grid_columnconfigure(5, weight=1) # n_entry
        
        ttk.Label(domain_frame, text="xmin:").grid(row=0, column=0, sticky=tk.W)
        self.xmin_var = tk.StringVar(value="-5")
        self.xmin_entry = ttk.Entry(domain_frame, textvariable=self.xmin_var, width=10)
        self.xmin_entry.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        
        ttk.Label(domain_frame, text="xmax:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.xmax_var = tk.StringVar(value="5")
        self.xmax_entry = ttk.Entry(domain_frame, textvariable=self.xmax_var, width=10)
        self.xmax_entry.grid(row=0, column=3, sticky=tk.EW, padx=(5, 0))
        
        ttk.Label(domain_frame, text="N pontos:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
        self.n_var = tk.StringVar(value="1000")
        self.n_entry = ttk.Entry(domain_frame, textvariable=self.n_var, width=10)
        self.n_entry.grid(row=0, column=5, sticky=tk.EW, padx=(5, 0))
        
        help_domain_btn = ttk.Button(domain_frame, text="?", width=3,
                                    command=lambda: self.show_help("Parâmetros de Domínio", self.get_domain_help()))
        help_domain_btn.grid(row=0, column=6, sticky=tk.E, padx=(5, 0))
        
        # Método de convolução
        method_frame = ttk.Frame(input_frame)
        method_frame.grid(row=5, column=0, sticky=tk.W+tk.E, padx=5, pady=5)
        method_frame.grid_columnconfigure(1, weight=1) # Faz o combobox expandir
        
        ttk.Label(method_frame, text="Método:").grid(row=0, column=0, sticky=tk.W)
        self.method_var = tk.StringVar(value="numpy")
        method_combo = ttk.Combobox(method_frame, textvariable=self.method_var, 
                                   values=["numpy", "scipy"], state="readonly", width=15)
        method_combo.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        
        help_method_btn = ttk.Button(method_frame, text="?", width=3,
                                    command=lambda: self.show_help("Métodos de Convolução", self.get_method_help()))
        help_method_btn.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        
        # Botões principais
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=6, column=0, sticky=tk.W+tk.E, pady=10)
        # Configurar colunas para os botões expandirem igualmente
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        self.plot_button = ttk.Button(button_frame, text="Plotar/Convoluir", 
                                     command=self.plotar_convolucao)
        self.plot_button.grid(row=0, column=0, sticky=tk.EW, padx=(0, 10))
        
        examples_button = ttk.Button(button_frame, text="📚 Exemplos", 
                                    command=self.show_examples)
        examples_button.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10))
        
        help_general_btn = ttk.Button(button_frame, text="❓ Ajuda Geral", 
                                     command=lambda: self.show_help("Ajuda Geral", self.get_general_help()))
        help_general_btn.grid(row=0, column=2, sticky=tk.EW)
        
        # Canvas matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=tk.NSEW)
    
    def update_f1_interval_fields(self, event=None):
        interval_type = self.f1_interval_type.get()
        
        if interval_type == "infinito":
            self.f1_x1_entry.config(state="disabled")
            self.f1_x2_entry.config(state="disabled")
            self.f1_x1_var.set("")
            self.f1_x2_var.set("")
        elif interval_type == "semi_inf_esq":
            self.f1_x1_entry.config(state="disabled")
            self.f1_x2_entry.config(state="normal")
            self.f1_x1_var.set("")
            self.f1_x2_var.set("0")
        elif interval_type == "semi_inf_dir":
            self.f1_x1_entry.config(state="normal")
            self.f1_x2_entry.config(state="disabled")
            self.f1_x1_var.set("0")
            self.f1_x2_var.set("")
        elif interval_type == "finito":
            self.f1_x1_entry.config(state="normal")
            self.f1_x2_entry.config(state="normal")
            self.f1_x1_var.set("-1")
            self.f1_x2_var.set("1")
    
    def update_f2_interval_fields(self, event=None):
        interval_type = self.f2_interval_type.get()
        
        if interval_type == "infinito":
            self.f2_x1_entry.config(state="disabled")
            self.f2_x2_entry.config(state="disabled")
            self.f2_x1_var.set("")
            self.f2_x2_var.set("")
        elif interval_type == "semi_inf_esq":
            self.f2_x1_entry.config(state="disabled")
            self.f2_x2_entry.config(state="normal")
            self.f2_x1_var.set("")
            self.f2_x2_var.set("0")
        elif interval_type == "semi_inf_dir":
            self.f2_x1_entry.config(state="normal")
            self.f2_x2_entry.config(state="disabled")
            self.f2_x1_var.set("0")
            self.f2_x2_var.set("")
        elif interval_type == "finito":
            self.f2_x1_entry.config(state="normal")
            self.f2_x2_entry.config(state="normal")
            self.f2_x1_var.set("-1")
            self.f2_x2_var.set("1")
    
    def show_help(self, title, content):
        HelpDialog(self.root, title, content)
    
    def show_examples(self):
        ExamplesDialog(self.root, self.load_example)
    
    def load_example(self, example):
        # Carregar função 1
        self.func1_var.set(example["f1"])
        self.f1_interval_type.set(example["f1_interval"])
        self.f1_x1_var.set(example["f1_x1"])
        self.f1_x2_var.set(example["f1_x2"])
        self.update_f1_interval_fields()
        
        # Carregar função 2
        self.func2_var.set(example["f2"])
        self.f2_interval_type.set(example["f2_interval"])
        self.f2_x1_var.set(example["f2_x1"])
        self.f2_x2_var.set(example["f2_x2"])
        self.update_f2_interval_fields()
        
        messagebox.showinfo("Exemplo Carregado", f"Exemplo '{example['name']}' carregado com sucesso!")
    
    def get_function_help(self):
        return """AJUDA - FUNÇÕES MATEMÁTICAS\n\nComo escrever funções:\n• Use 't' como variável independente\n• Utilize funções NumPy com prefixo 'np.'\n\nFunções disponíveis:\n• np.sin(t), np.cos(t), np.tan(t) - Funções trigonométricas\n• np.exp(t) - Função exponencial\n• np.log(t), np.log10(t) - Logaritmos natural e base 10\n• np.sqrt(t), np.abs(t) - Raiz quadrada e valor absoluto\n• np.where(condição, valor_se_verdadeiro, valor_se_falso) - Função condicional\n\nOperadores matemáticos:\n• + - * / ** (potência)\n• > < >= <= == != (comparação)\n• & | (and, or lógicos)\n\nExemplos de funções:\n• np.exp(-t**2) - Gaussiana\n• np.cos(2*np.pi*t) - Cosseno\n• np.sin(5*t) * np.exp(-0.1*t) - Senoide amortecida\n• np.where(t>=0, np.exp(-t), 0) - Exponencial causal\n• np.where((t>-1)&(t<1), 1, 0) - Pulso retangular\n• t * np.exp(-t**2) - Pulso derivativo\n• np.cos(t) + 0.5*np.cos(3*t) - Soma de harmônicos\n\nDicas importantes:\n• Use parênteses para agrupar operações\n• Para pulsos, use np.where() com condições\n• Para funções causais, use np.where(t>=0, função, 0)\n• Teste sempre com valores simples primeiro"""
    
    def get_interval_help(self):
        return """AJUDA - INTERVALOS DE FUNÇÃO\n\nOs intervalos definem onde a função é diferente de zero:\n\nTIPOS DE INTERVALO:\n\n1. infinito: (-∞, +∞)\n   • A função é definida em todo o domínio\n   • Não requer valores x1 ou x2\n   • Exemplo: Gaussiana np.exp(-t**2)\n\n2. semi_inf_esq: (-∞, x2]\n   • A função existe de -∞ até x2\n   • Requer apenas o valor x2\n   • Exemplo: Degrau negativo até x2\n\n3. semi_inf_dir: [x1, +∞)\n   • A função existe de x1 até +∞\n   • Requer apenas o valor x1\n   • Exemplo: Degrau positivo a partir de x1\n\n4. finito: [x1, x2]\n   • A função existe apenas entre x1 e x2\n   • Requer ambos os valores x1 e x2\n   • Exemplo: Pulso retangular\n\nCOMO USAR:\n1. Selecione o tipo de intervalo no menu dropdown\n2. Os campos x1 e x2 serão habilitados automaticamente\n3. Digite os valores dos limites quando necessário\n4. A função será automaticamente zerada fora do intervalo\n\nEXEMPLOS PRÁTICOS:\n• Pulso: função=1, intervalo=finito, x1=-1, x2=1\n• Degrau: função=1, intervalo=semi_inf_dir, x1=0\n• Exponencial causal: função=np.exp(-t), intervalo=semi_inf_dir, x1=0\n• Janela gaussiana: função=np.exp(-t**2), intervalo=finito, x1=-2, x2=2"""
    
    def get_domain_help(self):
        return """AJUDA - PARÂMETROS DE DOMÍNIO\n\nEstes parâmetros controlam a visualização e cálculo:\n\nxmin: Limite inferior do eixo temporal\n• Valor mínimo de t para plotagem\n• Recomendado: -5 a -10 para funções simétricas\n• Para funções causais: pode ser 0 ou negativo\n\nxmax: Limite superior do eixo temporal  \n• Valor máximo de t para plotagem\n• Recomendado: 5 a 10 para funções simétricas\n• Deve ser maior que xmin\n\nN pontos: Número de pontos de amostragem\n• Controla a resolução da discretização\n• Valores típicos: 500-2000\n• Mais pontos = maior precisão, mais lento\n• Menos pontos = menor precisão, mais rápido\n\nDICAS DE CONFIGURAÇÃO:\n• Para funções rápidas: xmin=-2, xmax=2, N=500\n• Para funções lentas: xmin=-10, xmax=10, N=1000\n• Para alta precisão: N=2000 ou mais\n• Para testes rápidos: N=200-500\n\nEFEITOS NA CONVOLUÇÃO:\n• O domínio da convolução será aproximadamente [2*xmin, 2*xmax]\n• Certifique-se de que o domínio capture toda a função\n• Para funções com suporte limitado, ajuste xmin/xmax adequadamente"""
    
    def get_method_help(self):
        return """AJUDA - MÉTODOS DE CONVOLUÇÃO\n\nDois métodos estão disponíveis para calcular a convolução:\n\nNUMPY (Discreto):\n• Usa np.convolve() para convolução discreta\n• Mais rápido para a maioria dos casos\n• Adequado para funções bem amostradas\n• Resultado: convolução dos sinais discretizados\n• Recomendado para: testes rápidos, funções suaves\n\nSCIPY (Contínuo):\n• Usa integração numérica (quad) para cada ponto\n• Mais preciso matematicamente\n• Mais lento, especialmente para muitos pontos\n• Resultado: aproximação da convolução contínua\n• Recomendado para: máxima precisão, funções complexas\n\nQUANDO USAR CADA UM:\n\nUse NUMPY quando:\n• Quiser resultados rápidos\n• As funções forem suaves e bem comportadas\n• N pontos for alto (>1000)\n• Estiver fazendo testes iniciais\n\nUse SCIPY quando:\n• Precisar de máxima precisão\n• As funções tiverem descontinuidades\n• Quiser o resultado matematicamente exato\n• Tiver tempo para esperar o cálculo\n\nDICAS:\n• Comece sempre com NUMPY para testes\n• Use SCIPY para resultados finais importantes\n• Para N>1000, SCIPY pode ser muito lento\n• Ambos os métodos devem dar resultados similares para funções suaves"""
    
    def get_general_help(self):
        return """AJUDA GERAL - CONVOLUÇÃO DE SINAIS\n\nCOMO USAR A APLICAÇÃO:\n\n1. DEFINIR FUNÇÕES:\n   • Digite as funções f(t) e g(t) usando sintaxe Python/NumPy\n   • Use 't' como variável independente\n   • Clique no botão '?' ao lado para ajuda específica\n\n2. CONFIGURAR INTERVALOS:\n   • Escolha o tipo de intervalo para cada função\n   • Configure os limites x1 e x2 quando necessário\n   • Use '?' para entender cada tipo de intervalo\n\n3. AJUSTAR PARÂMETROS:\n   • Configure xmin, xmax para o domínio de visualização\n   • Ajuste N pontos para controlar a resolução\n   • Escolha o método de convolução (NumPy ou SciPy)\n\n4. PLOTAR E ANALISAR:\n   • Clique em 'Plotar/Convoluir' para gerar os gráficos\n   • Observe os três gráficos: f(t), g(t) e f*g\n   • Analise o resultado da convolução\n\n5. USAR EXEMPLOS:\n   • Clique em '📚 Exemplos' para ver casos pré-configurados\n   • Selecione um exemplo e clique 'Carregar Exemplo'\n   • Modifique os parâmetros conforme necessário\n\nCONCEITOS IMPORTANTES:\n\nConvolução: Operação matemática que combina duas funções\n• Resultado: (f * g)(t) = ∫ f(τ)g(t-τ) dτ\n• Aplicações: filtros, sistemas lineares, processamento de sinais\n\nInterpretação física:\n• f(t): sinal de entrada\n• g(t): resposta ao impulso do sistema\n• f*g: resposta do sistema ao sinal de entrada\n\nSOLUÇÃO DE PROBLEMAS:\n• Erro de sintaxe: verifique a função digitada\n• Gráfico vazio: ajuste o domínio xmin/xmax\n• Cálculo lento: reduza N pontos ou use método NumPy\n• Resultado inesperado: verifique os intervalos das funções\n\nATALHOS:\n• F1: Esta ajuda\n• Ctrl+E: Abrir exemplos\n• Enter: Plotar (quando em um campo de entrada)"""

    def create_interval_function(self, func_str, interval_type, x1_str, x2_str):
        """Cria uma função que considera o intervalo especificado"""
        # Define uma função auxiliar para avaliar a string da função
        # Isso é necessário para que eval() possa acessar 't' e 'np' dentro do escopo da função lambda
        def evaluate_func(t_val):
            # Garante que 't' e 'np' estejam disponíveis no ambiente de eval
            _t = t_val
            _np = np
            return eval(func_str, {'np': _np, 't': _t})

        if interval_type == "infinito":
            return evaluate_func
        elif interval_type == "semi_inf_esq":
            x2 = float(x2_str)
            return lambda t: np.where(t <= x2, evaluate_func(t), 0)
        elif interval_type == "semi_inf_dir":
            x1 = float(x1_str)
            return lambda t: np.where(t >= x1, evaluate_func(t), 0)
        elif interval_type == "finito":
            x1 = float(x1_str)
            x2 = float(x2_str)
            return lambda t: np.where((t >= x1) & (t <= x2), evaluate_func(t), 0)
        else:
            # Retorna a função base se o tipo de intervalo for desconhecido ou inválido
            return evaluate_func
    
    def plotar_convolucao(self):
        try:
            # Ler e parsear entradas
            func1_str = self.func1_var.get()
            func2_str = self.func2_var.get()
            
            f1_interval_type = self.f1_interval_type.get()
            f1_x1_str = self.f1_x1_var.get()
            f1_x2_str = self.f1_x2_var.get()
            
            f2_interval_type = self.f2_interval_type.get()
            f2_x1_str = self.f2_x1_var.get()
            f2_x2_str = self.f2_x2_var.get()
            
            xmin = float(self.xmin_var.get())
            xmax = float(self.xmax_var.get())
            N = int(self.n_var.get())
            method = self.method_var.get()
            
            # Criar funções lambda com intervalos
            func1_with_interval = self.create_interval_function(func1_str, f1_interval_type, f1_x1_str, f1_x2_str)
            func2_with_interval = self.create_interval_function(func2_str, f2_interval_type, f2_x1_str, f2_x2_str)
            
            # Gerar sinais
            t1, x1 = gerar_sinal(func1_with_interval, xmin, xmax, N)
            t2, x2 = gerar_sinal(func2_with_interval, xmin, xmax, N)
            
            # Calcular convolução
            if method == "numpy":
                dt = t1[1] - t1[0]
                y = np.convolve(x1, x2, mode='full') * dt
                ty = np.linspace(t1[0] + t2[0], t1[-1] + t2[-1], len(y))
            else:  # scipy
                # Para convolução contínua, precisamos de uma função que aceite t como argumento
                # e que já incorpore os intervalos. A função conv_continua já espera isso.
                # O domínio da convolução contínua é a soma dos domínios das funções originais.
                # Ajuste o domínio de ty para ser mais abrangente para a convolução contínua.
                ty_start = xmin + xmin # ou t1[0] + t2[0]
                ty_end = xmax + xmax # ou t1[-1] + t2[-1]
                ty = np.linspace(ty_start, ty_end, N * 2) # Dobrar o número de pontos para melhor resolução
                y = conv_continua(func1_with_interval, func2_with_interval, ty)
            
            # Atualizar plots
            self.l1.set_data(t1, x1)
            self.l2.set_data(t2, x2)
            self.l3.set_data(ty, y)
            
            # Ajustar limites dos eixos
            for ax in self.axes:
                ax.relim()
                ax.autoscale_view()
            
            # Redesenhar canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular convolução: {str(e)}")

def main():
    root = tk.Tk()
    app = ConvolutionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
