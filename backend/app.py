import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from security import autenticar, criar_senha, carregar_senha
from fileoperations import ler_arquivo_cifrado, escrever_arquivo_cifrado, SEPARADOR, FORMATO_DATA, FUSO

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diário Digital")
        self.geometry("800x600")
        self.chave = None
        
        # Container principal
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Frames
        self.frames = {}
        for F in (LoginFrame, MenuFrame, ViewFrame, CreateFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(LoginFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if cont == MenuFrame:
            frame.update_entries()

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        lbl_title = tk.Label(self, text="Meu Notebook", font=("Arial", 24))
        lbl_title.pack(pady=40)
        
        self.lbl_senha = tk.Label(self, text="Senha:")
        self.ent_senha = tk.Entry(self, show="*", width=25)
        btn_login = tk.Button(self, text="Entrar", command=self.authenticate, width=15)
        
        # Botão para mostrar senha
        self.show_var = tk.BooleanVar()
        btn_show = tk.Checkbutton(self, text="Mostrar senha", variable=self.show_var, command=self.toggle_show)
        
        # Layout
        self.lbl_senha.pack(pady=5)
        self.ent_senha.pack(pady=5)
        btn_login.pack(pady=15)
        btn_show.pack(pady=5)
        
        # Eventos
        self.ent_senha.bind("<Return>", lambda e: self.authenticate())

    def toggle_show(self):
        self.ent_senha.config(show="" if self.show_var.get() else "*")

    def authenticate(self):
        senha = self.ent_senha.get()
        salt, senha_hash = carregar_senha()
        
        if salt:  # Modo login
            chave = autenticar(senha)
            if chave:
                self.controller.chave = chave
                self.controller.show_frame(MenuFrame)
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
                self.ent_senha.delete(0, 'end')
        else:  # Primeiro uso
            if len(senha) < 8:
                messagebox.showerror("Erro", "A senha deve ter pelo menos 8 caracteres!")
                return
            self.controller.chave = criar_senha(senha)
            self.controller.show_frame(MenuFrame)

class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Botões
        btn_frame = tk.Frame(self)
        btn_new = tk.Button(btn_frame, text="Nova Anotação", command=lambda: controller.show_frame(CreateFrame))
        btn_exit = tk.Button(btn_frame, text="Sair", command=self.controller.destroy)
        
        # Lista de entradas
        self.tree = ttk.Treeview(self, columns=("Data",), show="headings", height=15)
        self.tree.heading("Data", text="Notas")
        
        # Layout
        btn_new.pack(side="left", padx=10)
        btn_exit.pack(side="right", padx=10)
        btn_frame.pack(fill="x", pady=10)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Eventos
        self.tree.bind("<Double-1>", self.on_double_click)

    def update_entries(self):
        self.tree.delete(*self.tree.get_children())
        conteudo = ler_arquivo_cifrado(self.controller.chave)
        entradas = [e.strip() for e in conteudo.split(SEPARADOR) if e.strip()]
        
        for entrada in reversed(entradas):
            data = entrada.split("\n", 1)[0][1:-1]
            self.tree.insert("", "end", values=(data,))
            
    def on_double_click(self, event):
        item = self.tree.selection()[0]
        data = self.tree.item(item, "values")[0]
        self.controller.show_frame(ViewFrame)
        self.controller.frames[ViewFrame].display_entry(data)

class ViewFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Área de texto
        self.txt_content = tk.Text(self, wrap="word", font=("Arial", 12))
        scroll = tk.Scrollbar(self, command=self.txt_content.yview)
        self.txt_content.configure(yscrollcommand=scroll.set)
        
        # Botão de voltar
        btn_back = tk.Button(self, text="Voltar", command=lambda: controller.show_frame(MenuFrame))
        
        # Layout
        scroll.pack(side="right", fill="y")
        self.txt_content.pack(fill="both", expand=True, padx=20, pady=10)
        btn_back.pack(pady=10)

    def display_entry(self, data):
        conteudo = ler_arquivo_cifrado(self.controller.chave)
        entradas = [e.strip() for e in conteudo.split(SEPARADOR) if e.strip()]
        
        for entrada in entradas:
            if entrada.startswith(f"[{data}]"):
                self.txt_content.delete(1.0, "end")
                self.txt_content.insert("end", entrada.split("\n", 1)[1])
                break

class CreateFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Editor de texto
        self.txt_entry = tk.Text(self, wrap="word", font=("Arial", 12))
        scroll = tk.Scrollbar(self, command=self.txt_entry.yview)
        self.txt_entry.configure(yscrollcommand=scroll.set)
        
        # Botões
        btn_frame = tk.Frame(self)
        btn_save = tk.Button(btn_frame, text="Salvar", command=self.save_entry, width=10)
        btn_back = tk.Button(btn_frame, text="Cancelar", command=lambda: controller.show_frame(MenuFrame), width=10)
        
        # Layout
        scroll.pack(side="right", fill="y")
        self.txt_entry.pack(fill="both", expand=True, padx=20, pady=10)
        btn_save.pack(side="right", padx=10)
        btn_back.pack(side="left", padx=10)
        btn_frame.pack(fill="x", pady=10)

    def save_entry(self):
        texto = self.txt_entry.get(1.0, "end-1c")
        if not texto.strip():
            messagebox.showerror("Erro", "Digite algo antes de salvar!")
            return
            
        data_hora = datetime.now(FUSO).strftime(FORMATO_DATA)
        conteudo_existente = ler_arquivo_cifrado(self.controller.chave)
        novo_conteudo = f"[{data_hora}]\n{texto}{SEPARADOR}"
        
        try:
            escrever_arquivo_cifrado(conteudo_existente + novo_conteudo, self.controller.chave)
            self.txt_entry.delete(1.0, "end")
            self.controller.show_frame(MenuFrame)
            messagebox.showinfo("Sucesso", "Anotação salva com segurança!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha crítica: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()