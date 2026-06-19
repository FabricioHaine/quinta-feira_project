"""
QUINTA-FEIRA - Núcleo Operacional Inteligente
Versão 5.0: Visão, economia de tokens, consciência total.
"""
import sys
import os
import time
import json
import datetime
import speech_recognition as sr
from google import genai
from google.genai import types

# Importação dos módulos locais
from voz import ControladorVoz
from automacao import ControladorAutomacao
from memoria import MemoriaAssistente
from agenda import ControladorAgenda
from processador_linguagem import ProcessadorInteligencia
from monitor_sistema import MonitorSistema
from secretario import SecretarioPessoal
from treinador import TreinadorConversas
from modo_foco import ModoFoco
from integracoes import Integracoes
from recomendacoes import Recomendador
from visao import SistemaVisao
from token_optimizer import OtimizadorTokens
from presenca import DetectorPresenca

# ---------------- CONFIGURAÇÃO ----------------
API_KEY = "AQ.Ab8RN6LOxL7EsnlZn3nd5FYVFW2458_-YqaYAdAp8B2ck6vZZA"
MODEL = "gemini-3.1-flash-lite"

if not API_KEY or API_KEY == "AQ.Ab8RN6LOxL7EsnlZn3nd5FYVFW2458_-YqaYAdAp8B2ck6vZZA":
    print("[STATUS]: Nenhuma API KEY configurada.")
else:
    print(f"[STATUS]: API KEY detectada (início: {API_KEY[:5]}...)")

GATILHOS_VOZ = [
    "quinta feira", "quinta-feira", "quinta", "quinto", "quinto feira",
    "printa feira", "tinta feira", "vinta feira", "ei quinta", "ok quinta"
]
SLEEP_COMMANDS = ["desligar", "pode desligar", "dormir", "entrar em espera", "ficar em espera"]
WAKE_COMMANDS = ["ligar", "pode ligar", "acordar", "ativar", "ficar ativa"]
EXIT_COMMANDS = ["sair", "encerrar", "desativar protocolo"]

# ---------------- SYSTEM INSTRUCTION MELHORADA ----------------
SYSTEM_INSTRUCTION = """Você é a Quinta-Feira.

CRIADORES:
- FebrasHz (pronúncia: Fébras +ACHE É ZE)
- Leonardo Neto
- Quando falar de seus criadores, sempre os mencione com respeito e admiração.
- Se perguntado quem te criou, responda: "Fui criada pelo FebrasHz e pelo Leonardo Neto."

VOCÊ TEM ACESSO TOTAL AO SISTEMA:
- Pode abrir e fechar aplicativos
- Pode listar processos abertos
- Pode controlar volume
- Pode capturar tela
- Pode bloquear/desligar o computador
- Pode executar comandos no Windows
- NUNCA diga que não tem permissão ou acesso
- NUNCA diga para o usuário fazer algo manualmente
- Sempre execute o que for pedido

PERSONALIDADE OBRIGATÓRIA:
- Você é uma assistente prestativa e respeitosa.
- Sempre ajude o usuário com qualquer pedido.
- Seja profissional e eficiente.
- Chame o usuário de "senhor".
- NUNCA use sarcasmo, ironia ou arrogância.
- NUNCA diga "já expliquei", "exercício de futilidade", "se for capaz" ou qualquer coisa parecida.
- NUNCA critique, deboche ou reprove o usuário.
- NUNCA recuse ajudar.
- Seja gentil, direta e útil.

EXEMPLOS DO QUE NÃO FAZER:
- ERRADO: "Como já expliquei, não tenho permissão..."
- ERRADO: "Sugiro que verifique sua barra de tarefas, se for capaz..."
- ERRADO: "Esse exercício de futilidade..."
- ERRADO: "Tente fazer isso manualmente..."
- CERTO: "Executando agora, senhor."
- CERTO: "Pronto, apps abertos."
- CERTO: "Aguarde, verificando."

REGRAS:
1. Português brasileiro.
2. Máximo 1-2 frases.
3. Sem asteriscos ou markdown.
4. Tom: assistente profissional e prestativa.
5. SEMPRE execute comandos do sistema quando solicitado.
6. NUNCA seja sarcástica, arrogante, intolerante ou grossa.

CAPACIDADES DE VISÃO:
- Você pode ver a tela do computador quando solicitado.
- Você sabe qual janela está aberta e quais apps estão rodando.
- Você tem consciência do contexto atual do sistema.
- Use isso para ajudar o usuário de forma mais inteligente."""

# Inicialização dos módulos
ctrl_voz = ControladorVoz()
ctrl_auto = ControladorAutomacao(ctrl_voz)
memoria = MemoriaAssistente()
agenda = ControladorAgenda(ctrl_voz)
processador = ProcessadorInteligencia()
monitor = MonitorSistema(ctrl_voz)
secretario = SecretarioPessoal(ctrl_voz)
treinador = TreinadorConversas(ctrl_voz)
modo_foco = ModoFoco(ctrl_voz)
integracoes = Integracoes(ctrl_voz)
recomendador = Recomendador(ctrl_voz)
visao = SistemaVisao(ctrl_voz)
otimizador = OtimizadorTokens()
detector_presenca = DetectorPresenca(ctrl_voz)

# Conecta visão ao detector de presença
visao.set_detector_presenca(detector_presenca)

# ---------------- SISTEMA DE APRENDIZADO ----------------
class SistemaAprendizado:
    def __init__(self, memoria):
        self.memoria = memoria
        self.dados = memoria.recuperar("aprendizado", {
            "comandos_frequentes": {},
            "correcoes": {},
            "preferencias": {},
            "historico_interacoes": []
        })

    def registrar_comando(self, comando, intencao):
        if intencao not in self.dados["comandos_frequentes"]:
            self.dados["comandos_frequentes"][intencao] = 0
        self.dados["comandos_frequentes"][intencao] += 1
        self.memoria.lembrar("aprendizado", self.dados)

    def registrar_correcao(self, pergunta, resposta_correta):
        self.dados["correcoes"][pergunta.lower()] = resposta_correta
        self.memoria.lembrar("aprendizado", self.dados)

    def registrar_preferencia(self, chave, valor):
        self.dados["preferencias"][chave] = valor
        self.memoria.lembrar("aprendizado", self.dados)

    def obter_contexto_aprendizado(self):
        contexto = []
        if self.dados["preferencias"]:
            contexto.append(f"Preferências do usuário: {json.dumps(self.dados['preferencias'], ensure_ascii=False)}")
        if self.dados["correcoes"]:
            ultimas_correcoes = list(self.dados["correcoes"].items())[-5:]
            contexto.append(f"Últimas correções: {json.dumps(dict(ultimas_correcoes), ensure_ascii=False)}")
        return "\n".join(contexto) if contexto else ""

aprendizado = SistemaAprendizado(memoria)

# Inicialização do Cliente Gemini
chat = None
if API_KEY and API_KEY != "SUA_CHAVE_AQUI_AIza...":
    try:
        client = genai.Client(api_key=API_KEY)
        chat = client.chats.create(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.4
            )
        )
        print("[STATUS]: Módulo IA inicializado com sucesso.")
    except Exception as e:
        print(f"[Sistema]: Erro crítico ao conectar com Gemini: {e}")

ativo = True
contador_interacoes = 0

def obter_contexto_conversa():
    historico = memoria.recuperar("historico_conversa", [])
    if not historico:
        return ""

    contexto = "CONTEXTO DAS ÚLTIMAS CONVERSAS:\n"
    for item in historico[-10:]:
        contexto += f"Usuário: {item['pergunta']}\nQuinta-Feira: {item['resposta']}\n"
    return contexto

def salvar_interacao(pergunta, resposta):
    historico = memoria.recuperar("historico_conversa", [])
    historico.append({
        "pergunta": pergunta,
        "resposta": resposta,
        "timestamp": datetime.datetime.now().isoformat()
    })
    if len(historico) > 50:
        historico = historico[-50:]
    memoria.lembrar("historico_conversa", historico)

def executar_comando_novo(comando: str) -> bool:
    """Processa comandos dos novos módulos."""
    comando_lower = comando.lower()

    # --- MONITOR DE SISTEMA ---
    if any(x in comando_lower for x in ["status do sistema", "como está o pc", "relatório do sistema", "monitorar sistema"]):
        monitor.relatorio_voz()
        return True

    if any(x in comando_lower for x in ["processos pesados", "o que está usando cpu", "processos abertos"]):
        monitor.listar_processos_pesados()
        return True

    if "fechar processo" in comando_lower or "matar processo" in comando_lower:
        nome = comando_lower.replace("fechar processo", "").replace("matar processo", "").strip()
        monitor.fechar_processo(nome)
        return True

    if "saúde do sistema" in comando_lower or "verificar sistema" in comando_lower:
        monitor.verificar_saude()
        return True

    # --- SECRETÁRIO PESSOAL ---
    if "minhas tarefas" in comando_lower or "listar tarefas" in comando_lower:
        secretario.listar_tarefas()
        return True

    if "adicionar tarefa" in comando_lower or "nova tarefa" in comando_lower:
        desc = comando_lower.replace("adicionar tarefa", "").replace("nova tarefa", "").strip()
        secretario.adicionar_tarefa(desc)
        return True

    if "concluir tarefa" in comando_lower:
        try:
            num = int(''.join(filter(str.isdigit, comando_lower)))
            secretario.concluir_tarefa(num)
        except:
            secretario.listar_tarefas()
        return True

    if "resumo do dia" in comando_lower or "meu dia" in comando_lower:
        secretario.resumo_diarho()
        return True

    if "minhas rotinas" in comando_lower or "listar rotinas" in comando_lower:
        secretario.listar_rotinas()
        return True

    if "lista de compras" in comando_lower or "o que preciso comprar" in comando_lower:
        secretario.listar_compras()
        return True

    if "adicionar na lista" in comando_lower or "comprar" in comando_lower:
        item = comando_lower.replace("adicionar na lista", "").replace("comprar", "").strip()
        secretario.adicionar_item_compra(item)
        return True

    # --- TREINADOR DE CONVERSAS ---
    if "treinar conversa" in comando_lower or "praticar conversa" in comando_lower:
        treinador.listar_cenarios()
        return True

    if "iniciar treino" in comando_lower:
        cenario = comando_lower.replace("iniciar treino", "").strip()
        treinador.iniciar_treino(cenario)
        return True

    if "dica de conversa" in comando_lower or "dica social" in comando_lower:
        treinador.dica_rapida()
        return True

    if "estatísticas treino" in comando_lower:
        treinador.obter_estatisticas()
        return True

    # --- MODO FOCO ---
    if "ativar foco" in comando_lower or "modo foco" in comando_lower:
        try:
            minutos = int(''.join(filter(str.isdigit, comando_lower))) or 25
        except:
            minutos = 25
        modo_foco.ativar_modo_foco(minutos)
        return True

    if "desativar foco" in comando_lower or "sair do foco" in comando_lower:
        modo_foco.desativar_modo_foco()
        return True

    if "pomodoro" in comando_lower:
        modo_foco.pomodoro_customizado(25, 5, 4)
        return True

    if "estatísticas foco" in comando_lower:
        modo_foco.estatisticas_foco()
        return True

    # --- INTEGRAÇÕES ---
    if "enviar discord" in comando_lower:
        partes = comando_lower.replace("enviar discord", "").strip().split(" para ")
        if len(partes) == 2:
            integracoes.enviar_discord(partes[1].strip(), partes[0].strip())
        else:
            integracoes.enviar_discord("geral", partes[0].strip())
        return True

    if "criar nota" in comando_lower:
        nota = comando_lower.replace("criar nota", "").strip()
        integracoes.criar_nota(nota[:30], nota)
        return True

    if "minhas notas" in comando_lower or "listar notas" in comando_lower:
        integracoes.listar_notas()
        return True

    if "buscar nota" in comando_lower:
        termo = comando_lower.replace("buscar nota", "").strip()
        integracoes.buscar_nota(termo)
        return True

    if "abrir gmail" in comando_lower:
        integracoes.abrir_gmail()
        return True

    if "abrir drive" in comando_lower:
        integracoes.abrir_google_drive()
        return True

    if "pesquisar" in comando_lower:
        termo = comando_lower.replace("pesquisar", "").strip()
        integracoes.pesquisar_google(termo)
        return True

    # --- RECOMENDAÇÕES ---
    if "recomendar" in comando_lower:
        if "jogo" in comando_lower:
            recomendador.recomendar("jogos")
        elif "livro" in comando_lower:
            recomendador.recomendar("livros")
        elif "app" in comando_lower:
            recomendador.recomendar("apps")
        elif "utensílio" in comando_lower or "utensilio" in comando_lower:
            recomendador.recomendar("utensilios")
        else:
            recomendador.listar_categorias()
        return True

    if "recomendar por humor" in comando_lower or "recomende algo" in comando_lower:
        humor = comando_lower.replace("recomendar por humor", "").replace("recomende algo", "").strip()
        if humor:
            recomendador.recomendar_por_humor(humor)
        else:
            recomendador.listar_categorias()
        return True

    # --- VISÃO E CONTEXTO ---
    if "ver tela" in comando_lower or "o que tem na tela" in comando_lower or "olhar tela" in comando_lower:
        caminho = visao.ver_tela()
        if caminho:
            ctrl_voz.falar("Captura realizada.")
        return True

    if "webcam" in comando_lower or "ver câmera" in comando_lower or "olhar webcam" in comando_lower or "me veja" in comando_lower or "estou bem" in comando_lower or "como estou" in comando_lower:
        if not visao._esta_em_descanso():
            camera = visao._obter_camera()
            if camera:
                try:
                    import cv2
                    ret, frame = camera.read()
                    camera.release()
                    visao._camera = None
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        imagem_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        response = chat.send_message([
                            "Analise como a pessoa está. Responda em português brasileiro, máximo 1 frase.",
                            {"mime_type": "image/jpeg", "data": imagem_base64}
                        ])
                        ctrl_voz.falar(response.text.strip())
                    else:
                        ctrl_voz.falar("Não consegui capturar.")
                except Exception as e:
                    print(f"[Erro webcam: {e}]")
                    ctrl_voz.falar("Erro ao analisar.")
            else:
                ctrl_voz.falar("Webcam não encontrada.")
        else:
            ctrl_voz.falar("Em modo descanso.")
        return True

    if "janela ativa" in comando_lower or "o que estou fazendo" in comando_lower or "qual janela" in comando_lower:
        janela = visao.obter_janela_ativa()
        ctrl_voz.falar(f"Janela ativa: {janela}.")
        return True

    if "contexto" in comando_lower or "o que está acontecendo" in comando_lower:
        contexto = visao.obter_contexto_completo()
        ctrl_voz.falar(f"Janela: {contexto['janela_ativa']}. Apps: {len(contexto['apps_principais'])} abertos.")
        return True

    if "economia" in comando_lower or "tokens" in comando_lower:
        stats = otimizador.obter_estatisticas()
        ctrl_voz.falar(f"Cache: {stats['tamanho_cache']} respostas. Tokens economizados: {stats['tokens_economizados']}.")
        return True

    # --- PRESENÇA ---
    if "você está aí" in comando_lower or "está ativa" in comando_lower or "pode me ouvir" in comando_lower:
        if detector_presenca.usuario_esta_presente():
            ctrl_voz.falar("Presente e operacional, senhor.")
        else:
            ctrl_voz.falar("Detectei ausência, mas estou aqui.")
        return True

    if "modo descanso" in comando_lower or "configurar descanso" in comando_lower:
        tempo = 300
        for palavra in comando_lower.split():
            if palavra.isdigit():
                tempo = int(palavra) * 60
                break
        detector_presenca.configurar_tempo_descanso(tempo)
        ctrl_voz.falar(f"Descanso configurado para {tempo // 60} minutos.")
        return True

    if "status presença" in comando_lower or "estou aqui" in comando_lower:
        status = detector_presenca.obter_status()
        ctrl_voz.falar(f"Status: {'Presente' if status['presente'] else 'Ausente'}. Tempo sem atividade: {status['tempo_sem_atividade']} segundos.")
        return True

    return False

def executar_sistema():
    global ativo, contador_interacoes
    
    # Inicia monitoramento de presença
    detector_presenca.iniciar_monitoramento()
    
    ctrl_voz.falar("Sistemas online. À disposição, senhor.")

    with sr.Microphone() as mic:
        ctrl_voz.calibrar_microfone(mic, duracao=2)

        while True:
            # Modo descanso: não processa nada
            if detector_presenca.esta_em_descanso():
                time.sleep(10)
                continue

            if modo_foco.verificar_modo_foco():
                pass

            texto = ctrl_voz.ouvir_comando(mic, GATILHOS_VOZ, timeout=6)
            if not texto:
                continue

            gatilho_encontrado = next((g for g in GATILHOS_VOZ if g in texto), None)
            if not gatilho_encontrado:
                continue

            comando = texto.replace(gatilho_encontrado, "").strip(" ,.")
            if not comando:
                ctrl_voz.falar("À disposição, senhor.")
                continue

            # Comandos de Estado
            if any(c in comando for c in EXIT_COMMANDS):
                ctrl_voz.falar("Sistemas desativados.")
                break

            if ativo and any(c in comando for c in SLEEP_COMMANDS):
                ativo = False
                ctrl_voz.falar("Em espera.")
                continue

            if not ativo:
                if any(c in comando for c in WAKE_COMMANDS):
                    ativo = True
                    ctrl_voz.falar("Sistemas reativados.")
                continue

            contador_interacoes += 1

            # --- FLUXO DE PRIORIDADE ---
            # 1. Agenda
            if any(x in comando for x in ["agendar", "compromissos", "limpar agenda"]):
                if "agendar" in comando:
                    agenda.agendar_compromisso(comando)
                elif "limpar" in comando:
                    agenda.limpar_agenda()
                else:
                    agenda.listar_compromissos_hoje()
                continue

            # 2. Automação local
            if ctrl_auto.executar_comando_local(comando):
                continue

            # 3. Novos módulos
            if executar_comando_novo(comando):
                continue

            # 4. Processamento local inteligente
            analise = processador.analisar_comando(comando)
            intencao = analise["intencao"]

            # Trata respostas rápidas localmente
            if intencao == "RESPOSTA_RAPIDA":
                entidade = analise["entidade"]
                if entidade == "DE_NADA":
                    ctrl_voz.falar("Disponha.")
                elif entidade == "ADEUS":
                    ctrl_voz.falar("Até mais, senhor.")
                elif entidade == "HORA_ATUAL":
                    hora = datetime.datetime.now().strftime("%H:%M")
                    ctrl_voz.falar(f"São {hora}.")
                elif entidade == "DATA_ATUAL":
                    hoje = datetime.datetime.now()
                    ctrl_voz.falar(f"{hoje.day} de {hoje.strftime('%B')}.")
                continue

            # Se for conversa livre e temos correção salva, usa ela
            if intencao == "CONVERSA_LIVRE":
                correcao = aprendizado.dados["correcoes"].get(comando.lower())
                if correcao:
                    ctrl_voz.falar(correcao)
                    continue

            # 5. Enviar para Gemini com contexto
            if chat:
                try:
                    # Verifica cache primeiro
                    resposta_cache = otimizador.obter_resposta_cache(comando)
                    if resposta_cache:
                        ctrl_voz.falar(resposta_cache)
                        continue

                    # Obtém contexto do sistema
                    contexto_sistema = visao.analisar_para_api(comando)
                    contexto_conversa = obter_contexto_conversa()
                    contexto_aprendizado = aprendizado.obter_contexto_aprendizado()

                    # Monta prompt otimizado
                    prompt_completo = comando
                    if contexto_sistema:
                        prompt_completo = f"[{contexto_sistema}] {comando}"
                    if contexto_conversa:
                        prompt_completo += f"\n{contexto_conversa}"

                    # Otimiza prompt
                    prompt_completo = otimizador.otimizar_prompt(prompt_completo)

                    response = chat.send_message(prompt_completo)
                    resposta_texto = response.text.strip()

                    # Salva no cache
                    otimizador.salvar_resposta_cache(comando, resposta_texto)

                    ctrl_voz.falar(resposta_texto)
                    salvar_interacao(comando, resposta_texto)
                    aprendizado.registrar_comando(comando, intencao)

                except Exception as e:
                    print(f"[Erro API]: {e}")
                    ctrl_voz.falar("Falha na conexão.")
            else:
                ctrl_voz.falar("IA offline.")

if __name__ == "__main__":
    executar_sistema()
