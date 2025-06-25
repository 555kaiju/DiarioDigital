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
        
        # Container principal com centralização
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
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
        
        # Frame interno para centralização
        center_frame = tk.Frame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Widgets
        lbl_title = tk.Label(center_frame, text="Meu Notebook", font=("Arial", 24))
        self.lbl_senha = tk.Label(center_frame, text="Senha:")
        self.ent_senha = tk.Entry(center_frame, show="*", width=25)
        btn_login = tk.Button(center_frame, text="Entrar", command=self.authenticate, width=15)
        self.show_var = tk.BooleanVar()
        btn_show = tk.Checkbutton(center_frame, text="Mostrar senha", variable=self.show_var, command=self.toggle_show)
        
        # Layout
        lbl_title.pack(pady=40)
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
        
        if salt:
            chave = autenticar(senha)
            if chave:
                self.controller.chave = chave
                self.controller.show_frame(MenuFrame)
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
                self.ent_senha.delete(0, 'end')
        else:
            if len(senha) < 8:
                messagebox.showerror("Erro", "A senha deve ter pelo menos 8 caracteres!")
                return
            self.controller.chave = criar_senha(senha)
            self.controller.show_frame(MenuFrame)

class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_item = None
        
        # Configuração de grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Top frame
        top_frame = tk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", pady=10)
        
        # Botões de ação
        btn_action_frame = tk.Frame(top_frame)
        btn_new = tk.Button(btn_action_frame, text="Nova Anotação", command=lambda: controller.show_frame(CreateFrame))
        self.btn_edit = tk.Button(btn_action_frame, text="Editar", state='disabled', command=self.edit_entry)
        self.btn_delete = tk.Button(btn_action_frame, text="Excluir", state='disabled', command=self.delete_entry)
        
        # Campo de busca
        search_frame = tk.Frame(top_frame)
        self.search_var = tk.StringVar()
        ent_search = tk.Entry(search_frame, textvariable=self.search_var, width=25)
        
        # Layout top frame
        btn_new.pack(side="left", padx=5)
        self.btn_edit.pack(side="left", padx=5)
        self.btn_delete.pack(side="left", padx=5)
        btn_action_frame.pack(side="left", pady=5)
        
        ent_search.pack(side="left", padx=5)
        search_frame.pack(side="right", pady=5)
        
        # Container para Treeview e Scrollbar
        tree_container = tk.Frame(self)
        tree_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Treeview com Scrollbar
        self.tree = ttk.Treeview(
            tree_container,
            columns=("Data",),
            show="headings",
            height=10,
            selectmode="browse"
        )
        self.tree.heading("Data", text="Notas")
        
        scroll = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)
        
        # Layout dos componentes
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        # Botão Sair
        btn_exit = tk.Button(self, text="Sair", command=self.controller.destroy)
        btn_exit.grid(row=2, column=0, pady=10)
        
        # Eventos
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.search_var.trace_add("write", lambda *args: self.search_entries())

    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            self.selected_item = selection[0]
            self.btn_edit.config(state='normal')
            self.btn_delete.config(state='normal')
        else:
            self.selected_item = None
            self.btn_edit.config(state='disabled')
            self.btn_delete.config(state='disabled')

    def edit_entry(self):
        if self.selected_item:
            data = self.tree.item(self.selected_item, "values")[0]
            self.controller.show_frame(CreateFrame)
            create_frame = self.controller.frames[CreateFrame]
            create_frame.load_entry_for_editing(data)

    def delete_entry(self):
        if self.selected_item and messagebox.askyesno("Confirmar", "Excluir esta entrada permanentemente?"):
            data = self.tree.item(self.selected_item, "values")[0]
            conteudo = ler_arquivo_cifrado(self.controller.chave)
            entradas = [e.strip() for e in conteudo.split(SEPARADOR) if e.strip()]
            
            new_entries = [ent for ent in entradas if not ent.startswith(f"[{data}]")]
            
            escrever_arquivo_cifrado(SEPARADOR.join(new_entries), self.controller.chave)
            self.update_entries()
            messagebox.showinfo("Sucesso", "Entrada excluída!")

    def search_entries(self):
        termo = self.search_var.get().lower()
        conteudo = ler_arquivo_cifrado(self.controller.chave)
        todas_entradas = [e.strip() for e in conteudo.split(SEPARADOR) if e.strip()]
        
        self.tree.delete(*self.tree.get_children())
        for entrada in reversed(todas_entradas):
            if termo in entrada.lower():
                data = entrada.split("\n", 1)[0][1:-1]
                self.tree.insert("", "end", values=(data,))

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
        
        # Configuração de grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Área de texto
        self.txt_content = tk.Text(self, wrap="word", font=("Arial", 12))
        scroll = tk.Scrollbar(self, command=self.txt_content.yview)
        self.txt_content.configure(yscrollcommand=scroll.set)
        
        # Layout
        scroll.grid(row=0, column=1, sticky="ns")
        self.txt_content.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        
        # Botão de voltar
        btn_back = tk.Button(self, text="Voltar", command=lambda: controller.show_frame(MenuFrame))
        btn_back.grid(row=1, column=0, pady=10)

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
        self.editing = False
        self.current_data = None
        
        # Configuração de grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Editor de texto
        self.txt_entry = tk.Text(self, wrap="word", font=("Arial", 12))
        scroll = tk.Scrollbar(self, command=self.txt_entry.yview)
        self.txt_entry.configure(yscrollcommand=scroll.set)
        
        # Botões
        btn_frame = tk.Frame(self)
        btn_save = tk.Button(btn_frame, text="Salvar", command=self.save_entry, width=10)
        btn_back = tk.Button(btn_frame, text="Cancelar", command=self.cancel_edit, width=10)
        
        # Layout
        scroll.grid(row=0, column=1, sticky="ns")
        self.txt_entry.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=10)
        btn_save.pack(side="right", padx=10)
        btn_back.pack(side="left", padx=10)

    def load_entry_for_editing(self, data):
        self.editing = True
        self.current_data = data
        conteudo = ler_arquivo_cifrado(self.controller.chave)
        entradas = [e.strip() for e in conteudo.split(SEPARADOR) if e.strip()]
        
        for entrada in entradas:
            if entrada.startswith(f"[{data}]"):
                self.txt_entry.delete(1.0, "end")
                self.txt_entry.insert("end", entrada.split("\n", 1)[1])
                break

    def cancel_edit(self):
        self.editing = False
        self.current_data = None
        self.txt_entry.delete(1.0, "end")
        self.controller.show_frame(MenuFrame)

    def save_entry(self):
        texto = self.txt_entry.get(1.0, "end-1c")
        if not texto.strip():
            messagebox.showerror("Erro", "Digite algo antes de salvar!")
            return
            
        conteudo_existente = ler_arquivo_cifrado(self.controller.chave)
        entradas = [e.strip() for e in conteudo_existente.split(SEPARADOR) if e.strip()]

        if self.editing:
            for idx, entrada in enumerate(entradas):
                if entrada.startswith(f"[{self.current_data}]"):
                    entradas[idx] = f"[{self.current_data}]\n{texto}"
                    break
            novo_conteudo = SEPARADOR.join(entradas)
            self.editing = False
            self.current_data = None
        else:
            data_hora = datetime.now(FUSO).strftime(FORMATO_DATA)
            novo_conteudo = conteudo_existente + f"[{data_hora}]\n{texto}{SEPARADOR}"

        try:
            escrever_arquivo_cifrado(novo_conteudo, self.controller.chave)
            self.txt_entry.delete(1.0, "end")
            self.controller.show_frame(MenuFrame)
            messagebox.showinfo("Sucesso", "Anotação salva com segurança!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha crítica: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()