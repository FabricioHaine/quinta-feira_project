"""
QUINTA-FEIRA - Núcleo Operacional Resumido e Paciente
Integrado com Agenda Tática e Módulos de Automação de Alta Performance.
"""
import sys
import time
import speech_recognition as sr
from google import genai
from google.genai import types

from voz import ControladorVoz
from automacao import ControladorAutomacao
from memoria import MemoriaAssistente
from agenda import ControladorAgenda  # Novo módulo integrado

# ---------------- CONFIGURAÇÃO ----------------
API_KEY = "AQ.Ab8RN6K92X5Yw1cYIjOMG1yoLffQA7fR4Hfx9H6g8HuZUxn6lg"
MODEL = "gemini-3.1-flash-lite"

GATILHOS_VOZ = [
    "quinta feira", "quinta-feira", "quinta", "quinto", "quinto feira",
    "printa feira", "tinta feira", "vinta feira", "ei quinta", "ok quinta"
]

SLEEP_COMMANDS = ["desligar", "pode desligar", "dormir", "entrar em espera", "ficar em espera"]
WAKE_COMMANDS = ["ligar", "pode ligar", "acordar", "ativar", "ficar ativa"]
EXIT_COMMANDS = ["sair", "encerrar", "desativar protocolo"]

# Inicialização dos módulos
ctrl_voz = ControladorVoz()
ctrl_auto = ControladorAutomacao(ctrl_voz)
memoria = MemoriaAssistente()
agenda = ControladorAgenda(ctrl_voz) # Instância da Agenda

dados_salvos = memoria.dados
contexto_memorias = f" Memórias salvas: {dados_salvos}." if dados_salvos else ""

SYSTEM_PROMPT = (
    "Você é a Quinta-Feira, uma inteligência artificial direta, breve e militar. "
    "Responda SEMPRE em no máximo UMA FRASE CURTA. Seja cirúrgica. "
    "Nunca use listas, markdown ou explicações longas. Trate o usuário como 'senhor'."
    f"{contexto_memorias}"
)

client = genai.Client(api_key=API_KEY)
chat = client.chats.create(
    model=MODEL,
    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.4)
)

ativo = True

def verificar_e_guardar_memoria(comando: str):
    if "lembre que" in comando or "guarde que" in comando:
        info = comando.replace("lembre que", "").replace("guarde que", "").strip()
        if "meu nome é" in info or "me chamo" in info:
            nome = info.replace("meu nome é", "").replace("me chamo", "").strip()
            memoria.lembrar("nome_usuario", nome)
        else:
            idx = len(memoria.dados) + 1
            memoria.lembrar(f"fato_{idx}", info)
        return True
    return False

def executar_sistema():
    global ativo
    
    nome_usuario = memoria.recuperar("nome_usuario", "senhor")
    ctrl_voz.falar(f"Protocolo de resposta rápida ativo, {nome_usuario}.")
    
    with sr.Microphone() as mic:
        ctrl_voz.calibrar_microfone(mic)
        
        while True:
            texto = ctrl_voz.ouvir(mic)
            if not texto: continue
                
            print(f"[Ouvido]: {texto}")

            gatilho_encontrado = next((g for g in GATILHOS_VOZ if g in texto), None)
            if not gatilho_encontrado: continue

            comando = texto.replace(gatilho_encontrado, "").strip(" ,.")

            # Comandos de Estado
            if any(c in comando for c in EXIT_COMMANDS):
                ctrl_voz.falar("Desativando sistemas táticos. Até mais, senhor.")
                break

            if ativo and any(c in comando for c in SLEEP_COMMANDS):
                ativo = False
                ctrl_voz.falar("Entrando em modo de espera.")
                continue

            if not ativo:
                if any(c in comando for c in WAKE_COMMANDS):
                    ativo = True
                    ctrl_voz.falar("Sistemas reativados.")
                continue

            # --- FLUXO DE PRIORIDADE DE COMANDOS ---
            if not comando:
                ctrl_voz.falar("Sim, senhor?")
                continue

            # 1. Agenda Tática
            if "agendar" in comando:
                agenda.agendar_compromisso(comando)
                continue
            if "compromissos" in comando or "agenda de hoje" in comando:
                agenda.listar_compromissos_hoje()
                continue
            if "limpar agenda" in comando:
                agenda.limpar_agenda()
                continue

            # 2. Memória Local
            if verificar_e_guardar_memoria(comando):
                ctrl_voz.falar("Registrado.")
                continue

            # 3. Automação de Hardware
            if ctrl_auto.executar_comando_local(comando):
                continue
            
            # 4. Processamento Generativo (Gemini)
            try:
                response = chat.send_message(comando)
                texto_resposta = response.text.strip() if response.text else "Sem processamento."
                ctrl_voz.falar(texto_resposta)
            except Exception as e:
                print(f"[Erro na API]: {e}")
                ctrl_voz.falar("Falha de conexão.")

if __name__ == "__main__":
    executar_sistema()