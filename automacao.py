"""
Módulo de Automação - QUINTA-FEIRA
Versão 2.0: Controle completo de aplicativos do sistema.
"""
import os
import time
import datetime
import subprocess
import pyautogui
import psutil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ControladorAutomacao:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        
        # Mapeamento completo de apps
        self.apps_mapeados = {
            # Navegadores
            "chrome": "chrome",
            "navegador": "chrome",
            "google chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "opera": "opera",
            
            # Mídia
            "spotify": "spotify",
            "vlc": "vlc",
            "youtube": "chrome https://youtube.com",
            
            # Produtividade
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "notion": "notion",
            "obsidian": "obsidian",
            
            # Sistema
            "calculadora": "calc",
            "bloc de notas": "notepad",
            "notas": "notepad",
            "explorer": "explorer",
            "gerenciador": "explorer",
            "paint": "mspaint",
            "terminal": "cmd",
            "powershell": "powershell",
            "configurações": "ms-settings:",
            
            # Comunicação
            "discord": "discord",
            "teams": "teams",
            "slack": "slack",
            "zoom": "zoom",
            "whatsapp": "whatsapp:",
            
            # Desenvolvimento
            "vscode": "code",
            "visual studio code": "code",
            "git": "git",
            "python": "python",
            "node": "node",
            
            # Design
            "figma": "figma",
            "photoshop": "photoshop",
            "blender": "blender",
            
            # Games
            "steam": "steam",
            "epic": "epicgames",
        }

    def _alterar_volume(self, nivel: float) -> bool:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(nivel, None)
            return True
        except:
            return False

    def _obter_volume(self) -> float:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            return volume.GetMasterVolumeLevelScalar() * 100
        except:
            return 0

    def _listar_processos(self) -> list:
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['name'] and info['cpu_percent'] and info['cpu_percent'] > 0.1:
                    processos.append(info)
            except:
                pass
        return processos

    def _fechar_processo(self, nome: str) -> bool:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if nome.lower() in proc.info['name'].lower():
                    proc.kill()
                    return True
            except:
                pass
        return False

    def _abrir_app(self, app_nome: str) -> bool:
        # Verifica no mapeamento
        alvo = self.apps_mapeados.get(app_nome.lower(), app_nome)
        
        try:
            # Tenta abrir com start
            subprocess.Popen(f"start {alvo}", shell=True)
            return True
        except:
            pass
        
        try:
            # Tenta abrir com os.startfile
            os.startfile(alvo)
            return True
        except:
            pass
        
        try:
            # Tenta com subprocess.Popen direto
            subprocess.Popen(alvo)
            return True
        except:
            return False

    def executar_comando_local(self, comando: str) -> bool:
        comando = comando.lower().replace(",", "").replace(".", "").strip()

        # --- ABERTURA DE APLICATIVOS ---
        if "abrir" in comando:
            app_nome = comando.replace("abrir", "").strip()
            if self._abrir_app(app_nome):
                self.voz.falar(f"{app_nome} aberto.")
            else:
                self.voz.falar(f"Não consegui abrir {app_nome}.")
            return True

        # --- FECHAR APLICATIVO ---
        if "fechar" in comando or "sair do" in comando:
            app_nome = comando.replace("fechar", "").replace("sair do", "").strip()
            if self._fechar_processo(app_nome):
                self.voz.falar(f"{app_nome} fechado.")
            else:
                self.voz.falar(f"Não encontrei {app_nome} aberto.")
            return True

        # --- LISTAR APPS ABERTOS ---
        if "apps abertos" in comando or "o que está aberto" in comando or "processos" in comando:
            processos = self._listar_processos()
            nomes = list(set([p['name'].replace('.exe', '') for p in processos[:10]]))
            if nomes:
                self.voz.falar(f"Apps abertos: {', '.join(nomes[:5])}.")
            else:
                self.voz.falar("Nenhum app pesado aberto.")
            return True

        # --- HORAS E DATA ---
        if "que horas são" in comando or "hora atual" in comando or "horas" in comando:
            hora = datetime.datetime.now().strftime("%H:%M")
            self.voz.falar(f"São {hora}.")
            return True
            
        if "que dia é hoje" in comando or "data de hoje" in comando:
            hoje = datetime.datetime.now()
            self.voz.falar(f"{hoje.day} de {hoje.strftime('%B')}.")
            return True

        # --- CONTROLE DE VOLUME ---
        if "volume" in comando or "mutar" in comando or "silenciar" in comando:
            try:
                numeros = [int(s) for s in comando.split() if s.isdigit()]
                if numeros:
                    porcentagem = numeros[0]
                    self._alterar_volume(porcentagem / 100.0)
                    self.voz.falar(f"Volume em {porcentagem} por cento.")
                elif "mutar" in comando or "silenciar" in comando:
                    self._alterar_volume(0.0)
                    self.voz.falar("Silenciado.")
                elif "aumentar" in comando:
                    atual = self._obter_volume()
                    novo = min(100, atual + 10)
                    self._alterar_volume(novo / 100.0)
                    self.voz.falar(f"Volume em {int(novo)} por cento.")
                elif "diminuir" in comando:
                    atual = self._obter_volume()
                    novo = max(0, atual - 10)
                    self._alterar_volume(novo / 100.0)
                    self.voz.falar(f"Volume em {int(novo)} por cento.")
                elif "quanto" in comando or "qual" in comando:
                    atual = self._obter_volume()
                    self.voz.falar(f"Volume em {int(atual)} por cento.")
            except: pass
            return True

        # --- CAPTURA DE TELA ---
        if "print" in comando or "capturar tela" in comando:
            try:
                pasta_prints = os.path.join(BASE_DIR, "prints")
                os.makedirs(pasta_prints, exist_ok=True)
                caminho_print = os.path.join(pasta_prints, f"print_{int(time.time())}.png")
                time.sleep(0.1)
                pyautogui.screenshot(caminho_print)
                self.voz.falar("Captura salva.")
            except:
                self.voz.falar("Falha ao capturar.")
            return True

        # --- NOTAS ---
        if "anote que" in comando or "criar nota" in comando:
            nota = comando.replace("anote que", "").replace("criar nota", "").strip()
            caminho_notas = os.path.join(BASE_DIR, "notas_quinta_feira.txt")
            with open(caminho_notas, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}] - {nota}\n")
            self.voz.falar("Anotado.")
            return True

        # --- CONTROLE DO SISTEMA ---
        if "desligar computador" in comando or "desligar pc" in comando:
            self.voz.falar("Desligando o computador.")
            os.system("shutdown /s /t 60")
            return True

        if "reiniciar" in comando or "reiniciar computador" in comando:
            self.voz.falar("Reiniciando o computador.")
            os.system("shutdown /r /t 60")
            return True

        if "cancelar desligamento" in comando:
            os.system("shutdown /a")
            self.voz.falar("Desligamento cancelado.")
            return True

        if "bloquear" in comando or "travar pc" in comando:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            self.voz.falar("Computador bloqueado.")
            return True

        # --- ATALHOS DO WINDOWS ---
        if "alt tab" in comando or "alternar janela" in comando:
            pyautogui.hotkey('alt', 'tab')
            self.voz.falar("Alternando janela.")
            return True

        if "fechar janela" in comando or "ctrl w" in comando:
            pyautogui.hotkey('ctrl', 'w')
            self.voz.falar("Janela fechada.")
            return True

        if "minimizar tudo" in comando or "mostrar área de trabalho" in comando or "area de trabalho" in comando or "minimizar" in comando:
            try:
                pyautogui.hotkey('win', 'd')
                time.sleep(0.2)
                self.voz.falar("Pronto.")
            except:
                self.voz.falar("Erro ao minimizar.")
            return True

        if "maximizar" in comando or "aumentar janela" in comando:
            try:
                pyautogui.hotkey('win', 'up')
                self.voz.falar("Maximizado.")
            except:
                self.voz.falar("Erro ao maximizar.")
            return True

        if "restaurar janela" in comando or "normalizar" in comando:
            try:
                pyautogui.hotkey('win', 'down')
                self.voz.falar("Restaurado.")
            except:
                self.voz.falar("Erro ao restaurar.")
            return True

        if "fechar tudo" in comando or "matar todos" in comando:
            try:
                pyautogui.hotkey('alt', 'f4')
                self.voz.falar("Fechando janela atual.")
            except:
                self.voz.falar("Erro ao fechar.")
            return True

        return False
