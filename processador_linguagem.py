"""
Processador de Linguagem - QUINTA-FEIRA
Versão 2.0: Análise mais inteligente com suporte a contextos e entidades.
"""
import re
import json

class ProcessadorInteligencia:
    def __init__(self):
        self.intencoes = {
            "CONTROLE_SISTEMA": r"\b(abrir|fechar|executar|minimizar|iniciar|encerrar)\b",
            "PESQUISA_WEB": r"\b(pesquisar|buscar|procurar no google|youtube)\b",
            "CONHECIMENTO_GERAL": r"\b(quem|como|por que|o que|explique|defina|resuma|diferença)\b",
            "GESTAO_TAREFAS": r"\b(lembrete|agendar|lista|nota|anotar|lembrar)\b",
            "DEV_CODIFICACAO": r"\b(código|script|python|java|html|css|lógica|banco de dados|api)\b",
            "SENTIMENTOS": r"\b(triste|feliz|cansado|estressado|ansioso|animado|entediado)\b",
            "PREGUNTAS pessoais": r"\b(você|sua vida|seu nome|quem é você|história)\b",
            "COMANDOS especiais": r"\b(diga|fale|repeta|resuma|explique como)\b"
        }

        self.respostas_rapidas = {
            "horas": "HORA_ATUAL",
            "hora atual": "HORA_ATUAL",
            "que horas são": "HORA_ATUAL",
            "data": "DATA_ATUAL",
            "que dia é hoje": "DATA_ATUAL",
            "obrigado": "DE_NADA",
            "valeu": "DE_NADA",
            "tchau": "ADEUS",
            "até logo": "ADEUS"
        }

    def analisar_comando(self, texto: str) -> dict:
        texto = texto.lower().strip()
        intencao_detectada = "CONVERSA_LIVRE"
        entidade = None
        contexto_adicional = None

        # Verifica respostas rápidas primeiro
        for padrao, resposta in self.respostas_rapidas.items():
            if padrao in texto:
                return {
                    "texto_original": texto,
                    "intencao": "RESPOSTA_RAPIDA",
                    "entidade": resposta,
                    "contexto": None
                }

        # Identifica a Intenção
        for intencao, padrao in self.intencoes.items():
            if re.search(padrao, texto):
                intencao_detectada = intencao
                break

        # Extrai a Entidade com mais contexto
        if intencao_detectada == "CONTROLE_SISTEMA":
            match = re.search(r"(abrir|fechar|executar)\s+(o\s+|a\s+)?(.*)", texto)
            if match:
                entidade = match.group(3).strip()

        elif intencao_detectada == "PESQUISA_WEB":
            match = re.search(r"(pesquisar por|buscar por|sobre|busque)\s+(.*)", texto)
            if match:
                entidade = match.group(2).strip()

        elif intencao_detectada == "SENTIMENTOS":
            # Extrai o sentimento mencionado
            for sentimento in ["triste", "feliz", "cansado", "estressado", "ansioso", "animado", "entediado"]:
                if sentimento in texto:
                    entidade = sentimento
                    break

        elif intencao_detectada == "PREGUNTAS pessoais":
            contexto_adicional = "O usuário está perguntando sobre você pessoalmente."

        return {
            "texto_original": texto,
            "intencao": intencao_detectada,
            "entidade": entidade,
            "contexto": contexto_adicional
        }

    def gerar_prompt_gemini(self, analise: dict) -> str:
        intencao = analise["intencao"]
        texto = analise["texto_original"]
        entidade = analise["entidade"]
        contexto = analise.get("contexto")

        prompts = {
            "CONTROLE_SISTEMA": f"Atue como o terminal do sistema operacional. O usuário quer realizar a ação com o alvo: '{entidade}'. Forneça apenas o comando técnico em Python ou terminal para executar isso, sem explicações.",

            "CONHECIMENTO_GERAL": f"Atue como uma IA de conhecimento enciclopédico. Responda de forma direta e inteligente a esta pergunta: '{texto}'",

            "DEV_CODIFICACAO": f"Atue como um Engenheiro de Software Sênior. Analise e responda a esta dúvida técnica com precisão lógica: '{texto}'",

            "SENTIMENTOS": f"O usuário está expressando que está {entidade}. Responda com empatia e, se apropriado, sugira algo para ajudá-lo a se sentir melhor. Seja genuína e humana na sua resposta.",

            "PREGUNTAS pessoais": f"O usuário está perguntando sobre você pessoalmente. Responda de forma natural e com personalidade, contando um pouco sobre quem você é como assistente. Seja autêntica e interessante.",

            "RESPOSTA_RAPIDA": f"O usuário disse algo simples como obrigado, tchau, etc. Responda de forma natural e amigável, mantendo sua personalidade militar.",

            "CONVERSA_LIVRE": f"Atue como a assistente de IA 'Quinta-Feira'. Mantenha um tom profissional, leal, eficiente e levemente sarcástico se apropriado. Responda naturalmente: '{texto}'"
        }

        prompt_base = prompts.get(intencao, prompts["CONVERSA_LIVRE"])

        if contexto:
            prompt_base += f"\n\nContexto adicional: {contexto}"

        return prompt_base

# Teste rápido de lógica (só roda se executar este arquivo diretamente)
if __name__ == "__main__":
    processador = ProcessadorInteligencia()

    testes = [
        "Quinta-Feira, preciso que você explique como funciona o encapsulamento",
        "quinta-feira, estou me sentindo cansado",
        "quinta, obrigado pela ajuda",
        "ei quinta, quem é você?",
        "quinta, abrir o chrome"
    ]

    for teste in testes:
        print(f"\nTeste: {teste}")
        resultado = processador.analisar_comando(teste)
        print("Análise:", json.dumps(resultado, indent=4, ensure_ascii=False))
        print("Prompt:", processador.gerar_prompt_gemini(resultado)[:100] + "...")
