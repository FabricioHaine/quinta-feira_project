"""
Módulo de Memória - QUINTA-FEIRA
Responsável por persistir dados do usuário em um arquivo JSON.
"""
import json
import os

class MemoriaAssistente:
    def __init__(self, arquivo_json="memoria_quinta_feira.json"):
        self.arquivo = arquivo_json
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