"""
Módulo de Memória - QINTA-FEIRA
Versão 2.0: Memória contextual, histórico de conversas e aprendizado.
"""
import json
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MemoriaAssistente:
    def __init__(self, nome_arquivo="memoria_quinta_feira.json"):
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

    def adicionar_historico(self, pergunta, resposta, intencao="CONVERSA_LIVRE"):
        historico = self.recuperar("historico_completo", [])
        historico.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "intencao": intencao,
            "timestamp": datetime.datetime.now().isoformat()
        })
        if len(historico) > 100:
            historico = historico[-100:]
        self.lembrar("historico_completo", historico)

    def obter_estatisticas(self):
        historico = self.recuperar("historico_completo", [])
        if not historico:
            return {"total_interacoes": 0, "intencoes": {}}

        intencoes = {}
        for item in historico:
            intencao = item.get("intencao", "DESCONHECIDA")
            intencoes[intencao] = intencoes.get(intencao, 0) + 1

        return {
            "total_interacoes": len(historico),
            "intencoes": intencoes,
            "ultima_interacao": historico[-1].get("timestamp") if historico else None
        }

    def limpar_historico(self, manter_ultimas=10):
        historico = self.recuperar("historico_completo", [])
        if len(historico) > manter_ultimas:
            self.lembrar("historico_completo", historico[-manter_ultimas:])
