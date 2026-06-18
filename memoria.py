"""
Módulo de Memória - QUINTA-FEIRA
Refatorado para persistência na pasta local do projeto.
"""
import json
import os

# Define o diretório base automaticamente para portabilidade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MemoriaAssistente:
    def __init__(self, nome_arquivo="memoria_quinta_feira.json"):
        # Caminho dinâmico: o arquivo será salvo no mesmo diretório do script
        self.arquivo = os.path.join(BASE_DIR, nome_arquivo)
        self.dados = self.carregar_memoria()

    def carregar_memoria(self):
        if os.path.exists(self.arquivo):
            try:
                with open(self.arquivo, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def salvar_memoria(self):
        try:
            with open(self.arquivo, "w", encoding="utf-8") as f:
                json.dump(self.dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Erro ao salvar memória: {e}]")

    def lembrar(self, chave, valor):
        self.dados[chave] = valor
        self.salvar_memoria()

    def recuperar(self, chave, padrao=None):
        return self.dados.get(chave, padrao)