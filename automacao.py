"""
Módulo de Automação de Alta Performance - QUINTA-FEIRA
Refatorado para portabilidade universal (Caminhos Relativos).
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

# Define o diretório base automaticamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ControladorAutomacao:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
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
        comando = comando.lower().replace(",", "").replace(".", "").strip()

        # 1. HORAS E DATA (Mantido)
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

        # 2. CONTROLE DE VOLUME (Mantido)
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
            except: pass
            return True

        # 3. CAPTURA DE TELA TÁTICA (Refatorado)
        if "print" in comando or "capturar tela" in comando or "screenshot" in comando:
            try:
                pasta_prints = os.path.join(BASE_DIR, "prints")
                os.makedirs(pasta_prints, exist_ok=True)
                caminho_print = os.path.join(pasta_prints, f"print_{int(time.time())}.png")
                
                time.sleep(0.1)
                pyautogui.screenshot(caminho_print)
                self.voz.falar("Captura de tela salva na pasta de registros senhor")
            except Exception as e:
                print(f"[Erro no subsistema de imagem]: {e}")
                self.voz.falar("Falha ao capturar a tela senhor")
            return True

        # 4 a 8. (Mantidos igual ao seu original, pois não possuem caminhos fixos de disco)
        # ... [omitido para brevidade, apenas garanta que os caminhos web/subprocesses permaneçam iguais] ...

        # 9. SISTEMA DE NOTAS LOCAIS (Refatorado)
        if "anote que" in comando or "criar nota" in comando:
            nota = comando.replace("anote que", "").replace("criar nota", "").strip()
            caminho_notas = os.path.join(BASE_DIR, "notas_quinta_feira.txt")
            try:
                with open(caminho_notas, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}] - {nota}\n")
                self.voz.falar("Anotei senhor")
            except:
                self.voz.falar("Erro nas notas")
            return True

        return False