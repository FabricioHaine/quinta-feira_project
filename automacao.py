"""
Módulo de Automação de Alta Performance - QUINTA-FEIRA
Ajuste de textos para fala contínua e fluida, sem pausas artificiais.
Inclusão de ferramentas de diagnóstico de campo e captura de tela tática.
"""
import os
import time
import datetime
import webbrowser
import subprocess
import urllib.parse
import pyautogui
import wikipediaapi
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class ControladorAutomacao:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        # Inicializa a API da Wikipédia com cabeçalho de requisição limpo
        self.wiki = wikipediaapi.Wikipedia(
            user_agent="QuintaFeiraAssistente/2.0 (contato@laboratorio.com)",
            language="pt"
        )

    def _alterar_volume(self, nivel: float) -> bool:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(nivel, None)
            return True
        except:
            return False

    def executar_comando_local(self, comando: str) -> bool:
        # Limpeza padrão do buffer de entrada para evitar falsos negativos
        comando = comando.lower().replace(",", "").replace(".", "").strip()

        # 1. HORAS E DATA
        if "que horas são" in comando or "hora atual" in comando or "horas" in comando:
            hora = datetime.datetime.now().strftime("%H:%M")
            self.voz.falar(f"Agora são {hora} senhor")
            return True
            
        if "que dia é hoje" in comando or "data de hoje" in comando:
            meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
                     "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
            hoje = datetime.datetime.now()
            data_atual = f"{hoje.day} de {meses[hoje.month - 1]}"
            self.voz.falar(f"Hoje é dia {data_atual} senhor")
            return True

        # 2. CONTROLE DE VOLUME DO PC
        if "volume" in comando or "mutar" in comando or "silenciar" in comando:
            try:
                numeros = [int(s) for s in comando.split() if s.isdigit()]
                if numeros:
                    porcentagem = numeros[0]
                    if 0 <= porcentagem <= 100:
                        self._alterar_volume(porcentagem / 100.0)
                        self.voz.falar(f"Volume em {porcentagem} por cento senhor")
                    else:
                        self.voz.falar("Escolha entre zero e cem")
                else:
                    if "mutar" in comando or "silenciar" in comando:
                        self._alterar_volume(0.0)
                        self.voz.falar("Áudio silenciado senhor")
            except:
                pass
            return True

        # 3. CAPTURA DE TELA TÁTICA (Prioridade de hardware redefinida)
        if "print" in comando or "capturar tela" in comando or "screenshot" in comando:
            try:
                pasta_prints = "D:\\quinta-feira_project\\prints"
                os.makedirs(pasta_prints, exist_ok=True)
                
                caminho_print = os.path.join(pasta_prints, f"print_{int(time.time())}.png")
                
                # Minimiza interferências de hardware dando um breve respiro ao buffer
                time.sleep(0.1)
                pyautogui.screenshot(caminho_print)
                self.voz.falar("Captura de tela salva na pasta de registros senhor")
            except Exception as e:
                print(f"[Erro no subsistema de imagem]: {e}")
                self.voz.falar("Falha ao capturar a tela senhor")
            return True

        # 4. PREVISÃO DO TEMPO
        if "previsão do tempo" in comando or "clima" in comando or "tempo" in comando:
            self.voz.falar("Verificando o clima atual senhor")
            webbrowser.open_new_tab("https://www.google.com/search?q=previsao+do+tempo+atual")
            return True

        # 5. PESQUISA DIRETA DE CAMPO (WIKIPÉDIA EM BACKGROUND)
        if "pesquise sobre" in comando or "resuma sobre" in comando:
            termo = comando.replace("pesquise sobre", "").replace("resuma sobre", "").strip()
            if termo:
                try:
                    page = self.wiki.page(termo)
                    if page.exists():
                        resumo = page.summary.split('\n')[0]
                        frase_curta = resumo.split('.')[0] + "."
                        self.voz.falar(frase_curta)
                    else:
                        self.voz.falar("Sem registros locais buscando na malha externa")
                        termo_url = urllib.parse.quote(termo)
                        webbrowser.open_new_tab(f"https://www.google.com/search?q={termo_url}")
                except:
                    self.voz.falar("Erro no canal de pesquisa abrindo navegador")
                    webbrowser.open_new_tab(f"https://www.google.com/search?q={urllib.parse.quote(termo)}")
                return True

        # 6. SUÍTE DE APLICATIVOS
        if "code" in comando or "vs code" in comando:
            self.voz.falar("Iniciando o VS Code senhor")
            subprocess.Popen("code", shell=True)
            return True

        if "chrome" in comando or "navegador" in comando:
            self.voz.falar("Abrindo o Chrome senhor")
            subprocess.Popen("start chrome", shell=True)
            return True

        if "discord" in comando:
            self.voz.falar("Conectando ao Discord senhor")
            subprocess.Popen("start discord", shell=True)
            return True

        if "biblioteca" in comando:
            self.voz.falar("Abrindo a sua biblioteca de jogos senhor")
            webbrowser.open_new_tab("steam://open/main")
            return True

        if "epic" in comando:
            self.voz.falar("Iniciando a Epic Games senhor")
            webbrowser.open_new_tab("com.epicgames.launcher://")
            return True

        if "spotify" in comando:
            self.voz.falar("Abrindo o Spotify senhor")
            subprocess.Popen("start spotify", shell=True)
            return True

        if "instagram" in comando:
            self.voz.falar("Abrindo o Instagram senhor")
            webbrowser.open_new_tab("https://www.instagram.com")
            return True

        if "whatsapp" in comando or "whats" in comando:
            self.voz.falar("Acessando o WhatsApp senhor")
            webbrowser.open_new_tab("https://web.whatsapp.com")
            return True

        # 7. UTILITÁRIOS BÁSICOS
        if "bloco de notas" in comando or "notepad" in comando:
            self.voz.falar("Abrindo o Bloco de Notas senhor")
            subprocess.Popen("notepad", shell=True)
            return True

        if "calculadora" in comando:
            self.voz.falar("Abrindo a Calculadora senhor")
            subprocess.Popen("calc", shell=True)
            return True

        # 8. CENTRAL DE PESQUISAS WEB (YOUTUBE / GOOGLE)
        if "youtube" in comando:
            busca_limpa = comando
            for termo in ["pesquise no youtube por", "pesquisar no youtube por", "procure no youtube por", "busque no youtube por", "no youtube", "pesquise", "pesquisar", "procure", "busca", "buscar"]:
                busca_limpa = busca_limpa.replace(termo, "")
            busca_limpa = busca_limpa.strip()
            
            if busca_limpa:
                self.voz.falar("Buscando no YouTube senhor")
                termo_url = urllib.parse.quote(busca_limpa)
                webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={termo_url}")
                return True

        gatilhos_google = ["pesquise no google por", "pesquisar no google por", "pesquise por", "pesquisar por", "procure por", "buscar por", "busque por", "pesquisa sobre", "procure sobre"]
        for gatilho in gatilhos_google:
            if gatilho in comando:
                busca_limpa = comando.split(gatilho)[-1].strip()
                if busca_limpa:
                    self.voz.falar("Pesquisando no Google senhor")
                    termo_url = urllib.parse.quote(busca_limpa)
                    webbrowser.open_new_tab(f"https://www.google.com/search?q={termo_url}")
                    return True

        perguntas_diretas = ["como fazer", "o que é", "o que significa", "quem foi", "onde fica", "por que"]
        for gatilho in perguntas_diretas:
            if gatilho in comando:
                busca_limpa = comando[comando.index(gatilho):].strip()
                if busca_limpa:
                    self.voz.falar("Pesquisando no Google senhor")
                    termo_url = urllib.parse.quote(busca_limpa)
                    webbrowser.open_new_tab(f"https://www.google.com/search?q={termo_url}")
                    return True

        # 9. SISTEMA DE NOTAS LOCAIS
        if "anote que" in comando or "criar nota" in comando:
            nota = comando.replace("anote que", "").replace("criar nota", "").strip()
            try:
                with open("notas_quinta_feira.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}] - {nota}\n")
                self.voz.falar("Anotei senhor")
            except:
                self.voz.falar("Erro nas notas")
            return True

        return False