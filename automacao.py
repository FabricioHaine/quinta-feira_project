"""
Módulo de Automação - QUINTA-FEIRA
Versão 2.1: Controle completo de apps com ctypes (compatível com Python 3.14).
"""
import os
import time
import datetime
import subprocess
import ctypes
import pyautogui
import psutil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Constantes do Windows para ShowWindow
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE = 9
SW_SHOW = 5

class ControladorAutomacao:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.user32 = ctypes.windll.user32
        
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
            
            # Gravação
            "obs": "obs-studio",
            "obs studio": "obs-studio",
            
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
        except Exception:
            return False

    def _obter_volume(self) -> float:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            return volume.GetMasterVolumeLevelScalar() * 100
        except Exception:
            return 0

    def _maximizar_janela(self):
        """Maximiza a janela ativa usando ctypes."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            self.user32.ShowWindow(hwnd, SW_MAXIMIZE)
            return True
        except Exception:
            return False

    def _minimizar_janela(self):
        """Minimiza a janela ativa usando ctypes."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            self.user32.ShowWindow(hwnd, SW_MINIMIZE)
            return True
        except Exception:
            return False

    def _restaurar_janela(self):
        """Restaura a janela ativa usando ctypes."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            self.user32.ShowWindow(hwnd, SW_RESTORE)
            return True
        except Exception:
            return False

    def _mostrar_area_trabalho(self):
        """Mostra a área de trabalho (minimiza tudo)."""
        try:
            # Alternativa: Win+D via ctypes
            VK_LWIN = 0x5B
            VK_D = 0x44
            self.user32.keybd_event(VK_LWIN, 0, 0, 0)
            self.user32.keybd_event(VK_D, 0, 0, 0)
            self.user32.keybd_event(VK_D, 0, 2, 0)
            self.user32.keybd_event(VK_LWIN, 0, 2, 0)
            return True
        except Exception:
            return False

    def _encontrar_obs(self) -> str:
        """Encontra o caminho do executável do OBS Studio."""
        import glob
        
        # Caminhos comuns do OBS no Windows
        caminhos_padrao = [
            os.path.expandvars(r"%ProgramFiles%\OBS Studio\bin\64bit\obs64.exe"),
            os.path.expandvars(r"%ProgramFiles%\obs-studio\bin\64bit\obs64.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\OBS Studio\bin\32bit\obs32.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\OBS Studio\bin\64bit\obs64.exe"),
            os.path.expandvars(r"%ProgramFiles%\OBS Studio\bin\obs64.exe"),
            os.path.expandvars(r"%ProgramFiles%\obs-studio\bin\obs64.exe"),
        ]
        
        for caminho in caminhos_padrao:
            if os.path.exists(caminho):
                return caminho
        
        # Tenta encontrar via where
        try:
            resultado = subprocess.run(
                ["where", "obs64"], capture_output=True, text=True, timeout=5
            )
            if resultado.returncode == 0:
                return resultado.stdout.strip().split("\n")[0]
        except Exception:
            pass
        
        # Busca em pastas comuns
        try:
            padroes = [
                os.path.expandvars(r"%ProgramFiles%\OBS Studio\bin\*\obs*.exe"),
                os.path.expandvars(r"%ProgramFiles%\obs-studio\bin\*\obs*.exe"),
            ]
            for padrao in padroes:
                encontrados = glob.glob(padrao)
                # Filtra apenas obs64.exe ou obs32.exe (ignora testes)
                for e in encontrados:
                    nome = os.path.basename(e).lower()
                    if nome in ['obs64.exe', 'obs32.exe']:
                        return e
        except Exception:
            pass
        
        return None

    def _obs_esta_aberto(self) -> bool:
        """Verifica se o OBS Studio está rodando."""
        for proc in psutil.process_iter(['name']):
            try:
                nome = proc.info['name'].lower()
                if 'obs' in nome and ('studio' in nome or nome in ['obs64.exe', 'obs32.exe']):
                    return True
            except Exception:
                pass
        return False

    def _iniciar_gravacao_obs(self) -> bool:
        """Inicia gravação no OBS Studio via WebSocket."""
        import socket
        import json
        import time
        
        # Tenta conectar via WebSocket (padrão: 4455)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("127.0.0.1", 4455))
            
            # Handshake WebSocket
            handshake = json.dumps({
                "op": 1,
                "d": {
                    "rpcVersion": 1,
                    "authentication": ""
                }
            })
            
            # Envia handshake
            sock.send(handshake.encode())
            time.sleep(0.5)
            
            # Recebe resposta
            resposta = sock.recv(4096).decode()
            
            # Envia comando para iniciar gravação
            comando = json.dumps({
                "op": 6,
                "d": {
                    "requestType": "StartRecord",
                    "requestId": "start_recording"
                }
            })
            
            sock.send(comando.encode())
            time.sleep(0.5)
            resposta = sock.recv(4096).decode()
            sock.close()
            
            return True
            
        except ConnectionRefusedError:
            # WebSocket não disponível, tenta via atalho de teclado
            return self._iniciar_gravacao_obs_teclado()
        except Exception:
            return self._iniciar_gravacao_obs_teclado()

    def _iniciar_gravacao_obs_teclado(self) -> bool:
        """Inicia gravação no OBS via atalho de teclado (F9 padrão)."""
        try:
            import time
            # F9 é o atalho padrão para gravar no OBS
            pyautogui.press('f9')
            time.sleep(0.5)
            return True
        except Exception:
            return False

    def _parar_gravacao_obs(self) -> bool:
        """Para gravação no OBS Studio."""
        import socket
        import json
        import time
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("127.0.0.1", 4455))
            
            handshake = json.dumps({
                "op": 1,
                "d": {
                    "rpcVersion": 1,
                    "authentication": ""
                }
            })
            
            sock.send(handshake.encode())
            time.sleep(0.5)
            sock.recv(4096)
            
            comando = json.dumps({
                "op": 6,
                "d": {
                    "requestType": "StopRecord",
                    "requestId": "stop_recording"
                }
            })
            
            sock.send(comando.encode())
            time.sleep(0.5)
            sock.recv(4096)
            sock.close()
            
            return True
            
        except Exception:
            # F9 para gravar/parar no OBS
            pyautogui.press('f9')
            time.sleep(0.5)
            return True

    def _listar_processos(self) -> list:
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['name'] and info['cpu_percent'] and info['cpu_percent'] > 0.1:
                    processos.append(info)
            except Exception:
                pass
        return processos

    def _fechar_processo(self, nome: str) -> bool:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if nome.lower() in proc.info['name'].lower():
                    proc.kill()
                    return True
            except Exception:
                pass
        return False

    def _abrir_app(self, app_nome: str) -> bool:
        import webbrowser
        
        alvo = self.apps_mapeados.get(app_nome.lower(), app_nome)
        
        # Se for URL, abre no navegador padrão
        if alvo.startswith("http"):
            try:
                webbrowser.open(alvo)
                return True
            except Exception:
                pass

        # Se for protocolo (ex: whatsapp:, ms-settings:)
        if ":" in alvo and not alvo.startswith("http"):
            try:
                os.startfile(alvo)
                return True
            except Exception:
                pass

        # Tenta encontrar o executável no PATH do sistema
        try:
            resultado = subprocess.run(
                ["where", alvo], capture_output=True, text=True, timeout=5
            )
            if resultado.returncode == 0:
                caminho = resultado.stdout.strip().split("\n")[0]
                subprocess.Popen([caminho])
                return True
        except Exception:
            pass

        # Tenta abrir com start (funciona para apps do Windows)
        try:
            subprocess.Popen(f'start "" "{alvo}"', shell=True)
            return True
        except Exception:
            pass

        # Tenta com os.startfile
        try:
            os.startfile(alvo)
            return True
        except Exception:
            pass

        # Último recurso: tenta abrir como executável direto
        try:
            subprocess.Popen(alvo)
            return True
        except Exception:
            return False

    def executar_comando_local(self, comando: str) -> bool:
        import webbrowser
        comando = comando.lower().replace(",", "").replace(".", "").strip()

        # --- OBS STUDIO ---
        if "iniciar gravação" in comando or "começar a gravar" in comando or "começar gravação" in comando:
            if not self._obs_esta_aberto():
                caminho_obs = self._encontrar_obs()
                if caminho_obs:
                    subprocess.Popen([caminho_obs])
                    self.voz.falar("Abrindo OBS Studio. Aguarde um momento.")
                    time.sleep(5)  # Espera o OBS carregar
                else:
                    self.voz.falar("OBS Studio não encontrado. Instale o OBS primeiro.")
                    return True
            
            if self._iniciar_gravacao_obs():
                self.voz.falar("Gravação iniciada.")
            else:
                self.voz.falar("Erro ao iniciar gravação.")
            return True

        if "parar gravação" in comando or "parar de gravar" in comando:
            if self._parar_gravacao_obs():
                self.voz.falar("Gravação parada.")
            else:
                self.voz.falar("Erro ao parar gravação.")
            return True

        if "abrir obs" in comando or "abrir obs studio" in comando:
            caminho_obs = self._encontrar_obs()
            if caminho_obs:
                subprocess.Popen([caminho_obs])
                self.voz.falar("Abrindo OBS Studio.")
            else:
                self.voz.falar("OBS Studio não encontrado.")
            return True

        # --- ABERTURA DE APLICATIVOS ---
        if "abrir" in comando:
            app_nome = comando.replace("abrir", "").strip()
            
            # Deixa módulos especiais tratarem (gmail, drive, etc.)
            comandos_especiais = ["gmail", "drive", "google drive", "google mail"]
            if any(x in app_nome for x in comandos_especiais):
                return False
            
            # Comandos especiais para navegador
            if any(x in app_nome for x in ["navegador", "google", "chrome", "firefox", "edge", "opera"]):
                webbrowser.open("https://www.google.com")
                self.voz.falar("Abrindo navegador.")
                return True
            
            if self._abrir_app(app_nome):
                self.voz.falar(f"{app_nome} aberto.")
            else:
                self.voz.falar(f"Não consegui abrir {app_nome}.")
            return True

        # --- FECHAR APLICATIVO ---
        if "fechar janela" in comando or "ctrl w" in comando:
            pyautogui.hotkey('ctrl', 'w')
            self.voz.falar("Janela fechada.")
            return True

        if "fechar tudo" in comando or "matar todos" in comando or "fechar programa" in comando:
            pyautogui.hotkey('alt', 'f4')
            self.voz.falar("Fechando janela atual.")
            return True

        if "fechar" in comando or "sair do" in comando:
            app_nome = comando.replace("fechar", "").replace("sair do", "").strip()
            if not app_nome:
                pyautogui.hotkey('alt', 'f4')
                self.voz.falar("Fechando.")
            elif self._fechar_processo(app_nome):
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
            except Exception: pass
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
            except Exception:
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

        if "minimizar tudo" in comando or "mostrar área de trabalho" in comando or "area de trabalho" in comando:
            if self._mostrar_area_trabalho():
                self.voz.falar("Pronto.")
            else:
                self.voz.falar("Erro ao minimizar.")
            return True

        if "minimizar" in comando:
            if self._minimizar_janela():
                self.voz.falar("Minimizado.")
            else:
                self.voz.falar("Erro ao minimizar.")
            return True

        if "maximizar" in comando or "aumentar janela" in comando:
            if self._maximizar_janela():
                self.voz.falar("Maximizado.")
            else:
                self.voz.falar("Erro ao maximizar.")
            return True

        if "restaurar janela" in comando or "normalizar" in comando:
            if self._restaurar_janela():
                self.voz.falar("Restaurado.")
            else:
                self.voz.falar("Erro ao restaurar.")
            return True

        return False
