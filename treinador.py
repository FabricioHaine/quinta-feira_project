"""
Módulo Treinador de Conversas - QUINTA-FEIRA
Prática de conversação para tímidos, simulação de diálogos.
"""
import json
import os
import datetime
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TreinadorConversas:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.arquivo_historico = os.path.join(BASE_DIR, "treinador_historico.json")
        self.historico = self._carregar()

        self.cenarios = {
            "entrevista_emprego": {
                "nome": "Entrevista de Emprego",
                "dicas": [
                    "Mantenha contato visual",
                    "Fale com calma e clareza",
                    "Destaque suas qualidades",
                    "Seja honesto sobre suas experiência"
                ],
                "papeis": ["entrevistador", "candidato"]
            },
            "apresentacao_pessoal": {
                "nome": "Apresentação Pessoal",
                "dicas": [
                    "Seja breve e direto",
                    "Mencione interesses relevantes",
                    "Sorria e seja acolhedor",
                    "Faça perguntas sobre a outra pessoa"
                ],
                "papeis": ["conhecido", "novo_contato"]
            },
            "conflito_resolucao": {
                "nome": "Resolução de Conflitos",
                "dicas": [
                    "Ouça antes de responder",
                    "Use 'eu sinto' em vez de 'você faz'",
                    "Busque soluções, não culpados",
                    "Mantenha a calma"
                ],
                "papeis": ["pessoa_irritada", "mediador"]
            },
            "networking": {
                "nome": "Networking / Eventos",
                "dicas": [
                    "Tenha uma apresentação curta pronta",
                    "Faça perguntas abertas",
                    "Escute ativamente",
                    "Troque contatos"
                ],
                "papeis": ["contato_profissional", "conhecedor"]
            },
            "pedido_salario": {
                "nome": "Pedido de Aumento",
                "dicas": [
                    "Prepare argumentos sólidos",
                    "Seja específico sobre valores",
                    "Mostre seu valor para a empresa",
                    "Escolha o momento certo"
                ],
                "papeis": ["gerente", "funcionario"]
            },
            "conversa_casual": {
                "nome": "Conversa Casual",
                "dicas": [
                    "Seja autêntico",
                    "Encontre interesses em comum",
                    "Mantenha o assunto leve",
                    "Seja um bom ouvinte"
                ],
                "papeis": ["amigo", "conhecido"]
            }
        }

    def _carregar(self):
        if os.path.exists(self.arquivo_historico):
            try:
                with open(self.arquivo_historico, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"treinos": [], "estatisticas": {}}
        return {"treinos": [], "estatisticas": {}}

    def _salvar(self):
        try:
            with open(self.arquivo_historico, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Erro ao salvar]: {e}")

    def listar_cenarios(self):
        msg = "Cenários disponíveis para treino: "
        for i, (chave, cenario) in enumerate(self.cenarios.items(), 1):
            msg += f"{i}: {cenario['nome']}. "

        msg += "Escolha um cenário para começarmos."
        self.voz.falar(msg)
        return self.cenarios

    def iniciar_treino(self, cenario_nome: str):
        cenario = None
        for chave, c in self.cenarios.items():
            if cenario_nome.lower() in c["nome"].lower() or cenario_nome.lower() == chave:
                cenario = c
                break

        if not cenario:
            self.voz.falar("Cenário não encontrado. Liste os cenários primeiro.")
            return False

        self.voz.falar(f"Iniciando treino: {cenario['nome']}. ")
        self.voz.falar("Dicas: " + ". ".join(cenario['dicas']))

        self.estado_treino = {
            "cenario": cenario["nome"],
            "papeis": cenario["papeis"],
            "rodada": 0,
            "historico": []
        }

        self.voz.falar("Vou fazer o papel de {cenario['papeis'][0]}. Você será {cenario['papeis'][1]}. Comece a conversa quando quiser.")
        return True

    def gerar_resposta_ia(self, mensagem_usuario: str, chat) -> str:
        if not hasattr(self, 'estado_treino') or not self.estado_treino:
            return "Primeiro escolha um cenário de treino."

        prompt = f"""Você está em um treino de conversação. 
Cenário: {self.estado_treino['cenario']}
Seu papel: {self.estado_treino['papeis'][0]}
Papel do usuário: {self.estado_treino['papeis'][1]}

Responda de forma natural, como se estivesse realmente nessa situação. 
Seja realista e desafiador, mas educado. 
Máximo 2-3 frases."""

        if chat:
            try:
                response = chat.send_message(prompt)
                return response.text.strip()
            except:
                return "Não consegui gerar uma resposta. Tente novamente."

        return "Modo offline. Não posso simular a conversa sem a IA."

    def registrar_treino(self, cenario: str, pontuacao: int = 0):
        registro = {
            "cenario": cenario,
            "data": datetime.datetime.now().isoformat(),
            "pontuacao": pontuacao
        }

        self.historico["treinos"].append(registro)

        if cenario not in self.historico["estatisticas"]:
            self.historico["estatisticas"][cenario] = {"total": 0, "pontuacao_media": 0}

        stats = self.historico["estatisticas"][cenario]
        stats["total"] += 1
        stats["pontuacao_media"] = (stats["pontuacao_media"] * (stats["total"] - 1) + pontuacao) / stats["total"]

        self._salvar()
        return registro

    def obter_estatisticas(self):
        stats = self.historico.get("estatisticas", {})
        total_treinos = sum(s["total"] for s in stats.values())

        msg = f"Estatísticas de treino: {total_treinos} treinos realizados. "
        for cenario, s in stats.items():
            msg += f"{cenario}: {s['total']} vezes, média {s['pontuacao_media']:.1f} pontos. "

        if total_treinos == 0:
            msg = "Nenhum treino realizado ainda. Comece agora!"

        self.voz.falar(msg)
        return stats

    def dica_rapida(self):
        dicas_gerais = [
            "Pratique mant contato visual mesmo por voz",
            "Fale com ritmo natural, não apresse",
            "Use pausas para pensar, isso é normal",
            "Seja autêntico, não tente ser perfeito",
            "Escute mais do que fale",
            "Faça perguntas abertas",
            "Demonstre interesse genuíno",
            "Mantenha postura ereta, isso afeta sua voz",
            "Respire fundo antes de falar",
            "Sorria enquanto fala, melhora o tom"
        ]

        dica = random.choice(dicas_gerais)
        self.voz.falar(f"Dica rápida: {dica}")
        return dica
