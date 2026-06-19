"""
Módulo de Visão - QUINTA-FEIRA
Captura tela, webcam, analisa conteúdo e fornece consciência situacional.
"""
import os
import time
import base64
import json
import pyautogui
import psutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SistemaVisao:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.arquivo_estado = os.path.join(BASE_DIR, "estado_sistema.json")
        self.estado = self._carregar_estado()
        self.historico_telas = []
        self._detector_presenca = None
        self._camera = None

    def set_detector_presenca(self, detector):
        """Define o detector de presença para verificar modo descanso."""
        self._detector_presenca = detector

    def _esta_em_descanso(self):
        """Verifica se está em modo descanso."""
        if self._detector_presenca:
            return self._detector_presenca.esta_em_descanso()
        return False

    def _carregar_estado(self):
        if os.path.exists(self.arquivo_estado):
            try:
                with open(self.arquivo_estado, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return self._estado_padrao()
        return self._estado_padrao()

    def _estado_padrao(self):
        return {
            "ultima_janela": "",
            "apps_abertos": [],
            "atividade_recente": [],
            "contexto": "",
            "timestamp": ""
        }

    def _salvar_estado(self):
        try:
            self.estado["timestamp"] = datetime.now().isoformat()
            with open(self.arquivo_estado, "w", encoding="utf-8") as f:
                json.dump(self.estado, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def _obter_camera(self):
        """Obtém a webcam de forma preguiçosa."""
        if self._camera is None:
            try:
                import cv2
                self._camera = cv2.VideoCapture(0)
                if not self._camera.isOpened():
                    self._camera = None
            except ImportError:
                print("[OpenCV não instalado - pip install opencv-python]")
                return None
        return self._camera

    def capturar_tela(self, caminho=None):
        """Captura a tela e retorna o caminho da imagem."""
        # Não captura se estiver em modo descanso
        if self._esta_em_descanso():
            return None
            
        if not caminho:
            pasta = os.path.join(BASE_DIR, "prints")
            os.makedirs(pasta, exist_ok=True)
            caminho = os.path.join(pasta, f"tela_{int(time.time())}.png")
        
        try:
            time.sleep(0.1)
            pyautogui.screenshot(caminho)
            return caminho
        except Exception as e:
            print(f"[Erro ao capturar tela: {e}]")
            return None

    def capturar_webcam(self, caminho=None):
        """Captura imagem da webcam."""
        # Não captura se estiver em modo descanso
        if self._esta_em_descanso():
            return None

        camera = self._obter_camera()
        if not camera:
            return None

        if not caminho:
            pasta = os.path.join(BASE_DIR, "prints")
            os.makedirs(pasta, exist_ok=True)
            caminho = os.path.join(pasta, f"webcam_{int(time.time())}.png")

        try:
            ret, frame = camera.read()
            if ret:
                import cv2
                cv2.imwrite(caminho, frame)
                return caminho
        except Exception as e:
            print(f"[Erro ao capturar webcam: {e}]")
        
        return None

    def liberar_webcam(self):
        """Libera a webcam."""
        if self._camera and self._camera.isOpened():
            self._camera.release()
            self._camera = None

    def capturar_tela_base64(self):
        """Captura tela e retorna em base64 para enviar à API."""
        caminho = self.capturar_tela()
        if caminho and os.path.exists(caminho):
            try:
                with open(caminho, "rb") as f:
                    dados = base64.b64encode(f.read()).decode('utf-8')
                os.remove(caminho)
                return dados
            except Exception:
                return None
        return None

    def capturar_webcam_base64(self):
        """Captura webcam e retorna em base64 para enviar à API."""
        caminho = self.capturar_webcam()
        if caminho and os.path.exists(caminho):
            try:
                with open(caminho, "rb") as f:
                    dados = base64.b64encode(f.read()).decode('utf-8')
                os.remove(caminho)
                return dados
            except Exception:
                return None
        return None

    def obter_janela_ativa(self):
        """Obtém o nome da janela ativa."""
        try:
            import subprocess
            resultado = subprocess.run(
                ['powershell', '-Command', 
                 '(Get-Process | Where-Object {$_.MainWindowTitle -ne ""}).MainWindowTitle | Select-Object -First 1'],
                capture_output=True, text=True, timeout=5
            )
            titulo = resultado.stdout.strip()
            if titulo:
                self.estado["ultima_janela"] = titulo
                return titulo
        except Exception:
            pass
        return self.estado.get("ultima_janela", "Desconhecido")

    def obter_apps_abertos(self):
        """Lista apps abertos."""
        apps = []
        for proc in psutil.process_iter(['name']):
            try:
                nome = proc.info['name']
                if nome and nome not in apps and not nome.startswith('svchost'):
                    apps.append(nome)
            except Exception:
                pass
        
        self.estado["apps_abertos"] = apps[:20]
        return apps

    def obter_contexto_completo(self):
        """Retorna contexto completo do sistema."""
        janela = self.obter_janela_ativa()
        apps = self.obter_apps_abertos()
        
        contexto = {
            "janela_ativa": janela,
            "quantidade_apps": len(apps),
            "apps_principais": [a.replace('.exe', '') for a in apps[:10]],
            "hora": datetime.now().strftime("%H:%M"),
            "data": datetime.now().strftime("%d/%m/%Y")
        }
        
        self.estado["contexto"] = json.dumps(contexto, ensure_ascii=False)
        self._salvar_estado()
        
        return contexto

    def analisar_para_api(self, pergunta_usuario):
        """Prepara contexto otimizado para enviar à API (economiza tokens)."""
        contexto = self.obter_contexto_completo()
        
        # Contexto compacto
        contexto_compacto = (
            f"Janela: {contexto['janela_ativa']}. "
            f"Apps: {', '.join(contexto['apps_principais'][:5])}. "
            f"Hora: {contexto['hora']}."
        )
        
        return contexto_compacto

    def registrar_atividade(self, atividade):
        """Registra atividade recente."""
        self.estado["atividade_recente"].append({
            "atividade": atividade,
            "hora": datetime.now().strftime("%H:%M:%S")
        })
        
        # Mantém apenas as últimas 20
        if len(self.estado["atividade_recente"]) > 20:
            self.estado["atividade_recente"] = self.estado["atividade_recente"][-20:]
        
        self._salvar_estado()

    def ver_tela(self):
        """Captura e descreve o que está na tela (para a IA)."""
        caminho = self.capturar_tela()
        if caminho:
            self.registrar_atividade("Captura de tela realizada")
            return caminho
        return None

    def ver_webcam(self):
        """Captura da webcam."""
        caminho = self.capturar_webcam()
        if caminho:
            self.registrar_atividade("Captura de webcam realizada")
            return caminho
        return None
