import json
import random
import tkinter as tk
import os
import re
from tkinter import messagebox, ttk
from difflib import SequenceMatcher
import unicodedata

class QuizGame:
    def __init__(self, root, modo_jogo="normal"):
        self.root = root
        self.root.title("Quiz de História da Computação")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.modo_jogo = modo_jogo
        self.arquivo_json = "perguntas.json" if modo_jogo == "normal" else "PerguntasComputadores.json"
        
        # Obter o diretório do script atual
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, self.arquivo_json)
        
        # Verificar se o arquivo existe
        if not os.path.exists(json_path):
            messagebox.showerror("Erro", f"Arquivo {json_path} não encontrado!")
            self.root.destroy()
            return
        
        # Carregar perguntas do arquivo JSON
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.perguntas = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar perguntas: {str(e)}")
            self.root.destroy()
            return
        
        self.pontuacao = 0
        self.vidas = 3
        self.pergunta_atual = 0
        self.total_perguntas = len(self.perguntas)
        
        # Embaralhar perguntas
        random.shuffle(self.perguntas)
        
        # Criar dicionário de palavras-chave a partir do JSON
        self.palavras_chave = {}
        for pergunta in self.perguntas:
            if "palavras_chave" in pergunta:
                self.palavras_chave[pergunta["pergunta"]] = pergunta["palavras_chave"]
        
        self.setup_ui()
        self.mostrar_proxima_pergunta()
    
    def normalizar_texto(self, texto):
        """Remove acentos, converte para minúsculas e remove caracteres especiais"""
        # Remove acentos
        texto = unicodedata.normalize('NFD', texto)
        texto = texto.encode('ascii', 'ignore').decode('utf-8')
        # Remove caracteres especiais e converte para minúsculas
        texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto.lower())
        return texto
    
    def similaridade(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
    
    def verificar_resposta(self, resposta_usuario, resposta_correta, pergunta):
        # Normalizar textos
        resposta_usuario_norm = self.normalizar_texto(resposta_usuario)
        resposta_correta_norm = self.normalizar_texto(resposta_correta)
        
        # Verificação direta com tolerância a erros de digitação
        if self.similaridade(resposta_usuario_norm, resposta_correta_norm) > 0.7:
            return True
        
        # Verificação por palavras-chave
        if pergunta in self.palavras_chave:
            palavras_necessarias = [self.normalizar_texto(p) for p in self.palavras_chave[pergunta]]
            palavras_usuario = resposta_usuario_norm.split()
            
            # Verificar se as palavras-chave estão presentes (em qualquer ordem)
            palavras_encontradas = 0
            for palavra in palavras_necessarias:
                # Verificar se a palavra está presente com alta similaridade
                for p_usuario in palavras_usuario:
                    if self.similaridade(palavra, p_usuario) > 0.7:
                        palavras_encontradas += 1
                        break
            
            # Se pelo menos 60% das palavras-chave estiverem presentes, considerar correto
            if palavras_encontradas >= len(palavras_necessarias) * 0.6:
                return True
        
        return False
    
    def setup_ui(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header com pontuação e vidas
        self.header_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.pontuacao_label = tk.Label(
            self.header_frame, 
            text=f"Pontuação: {self.pontuacao}", 
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        self.pontuacao_label.pack(side=tk.LEFT)
        
        self.vidas_label = tk.Label(
            self.header_frame, 
            text=f"Vidas: {'❤️' * self.vidas}", 
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#d33"
        )
        self.vidas_label.pack(side=tk.RIGHT)
        
        # Modo de jogo
        self.modo_label = tk.Label(
            self.header_frame,
            text=f"Modo: {'Computadores' if self.modo_jogo == 'computadores' else 'Normal'}",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666"
        )
        self.modo_label.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Área da pergunta
        self.pergunta_frame = tk.Frame(self.main_frame, bg="#fff", relief=tk.RAISED, bd=2)
        self.pergunta_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.dificuldade_label = tk.Label(
            self.pergunta_frame,
            text="",
            font=("Arial", 10),
            bg="#e0e0e0",
            fg="#666",
            pady=5
        )
        self.dificuldade_label.pack(fill=tk.X)
        
        self.pergunta_label = tk.Label(
            self.pergunta_frame,
            text="",
            font=("Arial", 16),
            bg="#fff",
            wraplength=700,
            justify=tk.CENTER,
            pady=20
        )
        self.pergunta_label.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Área de resposta
        self.resposta_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.resposta_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            self.resposta_frame,
            text="Sua resposta:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.resposta_entry = tk.Entry(
            self.resposta_frame,
            font=("Arial", 14),
            width=50
        )
        self.resposta_entry.pack(fill=tk.X, pady=(0, 10))
        self.resposta_entry.bind("<Return>", lambda event: self.verificar_resposta_ui())
        
        # Botão de verificação
        self.verificar_btn = tk.Button(
            self.resposta_frame,
            text="Verificar Resposta",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.verificar_resposta_ui,
            padx=20,
            pady=10
        )
        self.verificar_btn.pack(pady=10)
        
        # Barra de progresso
        self.progresso_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.progresso_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.progresso_label = tk.Label(
            self.progresso_frame,
            text="Progresso: 0%",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.progresso_label.pack(anchor=tk.W)
        
        self.barra_progresso = ttk.Progressbar(
            self.progresso_frame,
            orient=tk.HORIZONTAL,
            length=700,
            mode='determinate'
        )
        self.barra_progresso.pack(fill=tk.X, pady=(5, 0))
    
    def mostrar_proxima_pergunta(self):
        if self.pergunta_atual >= self.total_perguntas or self.vidas <= 0:
            self.finalizar_jogo()
            return
        
        pergunta = self.perguntas[self.pergunta_atual]
        self.pergunta_label.config(text=pergunta["pergunta"])
        self.dificuldade_label.config(text=f"Dificuldade: {pergunta['dificuldade']}")
        
        # Atualizar barra de progresso
        progresso = (self.pergunta_atual / self.total_perguntas) * 100
        self.barra_progresso['value'] = progresso
        self.progresso_label.config(text=f"Progresso: {int(progresso)}%")
        
        self.resposta_entry.delete(0, tk.END)
        self.resposta_entry.focus()
    
    def verificar_resposta_ui(self):
        resposta_usuario = self.resposta_entry.get().strip()
        if not resposta_usuario:
            messagebox.showwarning("Aviso", "Por favor, digite uma resposta!")
            return
            
        resposta_correta = self.perguntas[self.pergunta_atual]["resposta"]
        pergunta_atual = self.perguntas[self.pergunta_atual]["pergunta"]
        
        # Verificar resposta usando o sistema de palavras-chave
        if self.verificar_resposta(resposta_usuario, resposta_correta, pergunta_atual):
            self.pontuacao += 10
            self.pontuacao_label.config(text=f"Pontuação: {self.pontuacao}")
            messagebox.showinfo("Correto!", "✅ Resposta correta! +10 pontos")
        else:
            self.vidas -= 1
            self.vidas_label.config(text=f"Vidas: {'❤️' * self.vidas}")
            
            # Mostrar palavras-chave importantes para esta pergunta
            palavras_chave = self.palavras_chave.get(pergunta_atual, [])
            dica = f"A resposta deveria conter palavras como: {', '.join(palavras_chave)}" if palavras_chave else ""
            
            messagebox.showerror("Errado!", 
                                f"❌ Resposta incorreta!\nA resposta correta era: {resposta_correta}\n\n{dica}")
        
        self.pergunta_atual += 1
        self.mostrar_proxima_pergunta()
    
    def finalizar_jogo(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Tela final
        tk.Label(
            self.main_frame,
            text="Fim do Jogo!",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            pady=20
        ).pack()
        
        tk.Label(
            self.main_frame,
            text=f"Pontuação final: {self.pontuacao}",
            font=("Arial", 18),
            bg="#f0f0f0",
            pady=10
        ).pack()
        
        if self.pontuacao >= 70:
            mensagem = "🎉 Excelente! Você é um expert no assunto!"
            cor = "#4CAF50"
        elif self.pontuacao >= 40:
            mensagem = "👍 Bom trabalho! Você conhece bem o conteúdo."
            cor = "#FFC107"
        else:
            mensagem = "📚 Estude um pouco mais e tente novamente!"
            cor = "#F44336"
        
        tk.Label(
            self.main_frame,
            text=mensagem,
            font=("Arial", 14),
            bg="#f0f0f0",
            fg=cor,
            pady=10
        ).pack()
        
        # Botão para voltar ao menu principal
        tk.Button(
            self.main_frame,
            text="Voltar ao Menu Principal",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            command=self.voltar_ao_menu,
            pady=10,
            padx=20
        ).pack(pady=10)
        
        # Botão para jogar novamente no mesmo modo
        tk.Button(
            self.main_frame,
            text="Jogar Novamente",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.reiniciar_jogo,
            pady=10,
            padx=20
        ).pack(pady=10)
    
    def reiniciar_jogo(self):
        self.main_frame.destroy()
        self.__init__(self.root, self.modo_jogo)
    
    def voltar_ao_menu(self):
        self.main_frame.destroy()
        TelaInicial(self.root)

class TelaInicial:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz de História da Computação")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Limpar a tela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            self.main_frame,
            text="Quiz de História da Computação",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            pady=30
        ).pack()
        
        # Subtítulo
        tk.Label(
            self.main_frame,
            text="Escolha o modo de jogo:",
            font=("Arial", 16),
            bg="#f0f0f0",
            pady=20
        ).pack()
        
        # Frame para os botões
        botoes_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        botoes_frame.pack(pady=30)
        
        # Botão Modo Normal
        tk.Button(
            botoes_frame,
            text="Modo Normal",
            font=("Arial", 16, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            height=2,
            command=lambda: self.iniciar_jogo("normal"),
            padx=20,
            pady=10
        ).pack(pady=15)
        
        # Botão Modo Computadores
        tk.Button(
            botoes_frame,
            text="Modo Computadores",
            font=("Arial", 16, "bold"),
            bg="#FF9800",
            fg="white",
            width=20,
            height=2,
            command=lambda: self.iniciar_jogo("computadores"),
            padx=20,
            pady=10
        ).pack(pady=15)
        
        # Instruções
        tk.Label(
            self.main_frame,
            text="Modo Normal: Perguntas gerais sobre história da computação\nModo Computadores: Perguntas específicas sobre computadores históricos",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666",
            pady=20
        ).pack()
    
    def iniciar_jogo(self, modo):
        self.main_frame.destroy()
        QuizGame(self.root, modo)

if __name__ == "__main__":
    root = tk.Tk()
    tela_inicial = TelaInicial(root)
    root.mainloop()