"""
Módulo de Detecção de Presença - QUINTA-FEIRA
Detecta se o usuário está presente e entra em modo descanso.
"""
import time
import threading
from datetime import datetime

class DetectorPresenca:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.usuario_presente = True
        self.tempo_ultimo_movimento = time.time()
        self.tempo_descanso = 300  # 5 minutos sem atividade = descanso
        self.intervalo_verificacao = 10  # Verifica a cada 10 segundos
        self.modo_descanso = False
        self.monitorando = False
        self._thread = None

    def _verificar_atividade(self):
        """Verifica se houve movimento do mouse ou teclado."""
        try:
            import pyautogui
            # Pega posição atual do mouse
            pos_atual = pyautogui.position()
            
            # Se a posição mudou, houve atividade
            if not hasattr(self, '_ultima_posicao'):
                self._ultima_posicao = pos_atual
                return True
            
            if pos_atual != self._ultima_posicao:
                self._ultima_posicao = pos_atual
                self.tempo_ultimo_movimento = time.time()
                return True
            
            return False
        except:
            return True

    def _monitorar_presenca(self):
        """Monitora presença do usuário em background."""
        while self.monitorando:
            try:
                atividade = self._verificar_atividade()
                tempo_sem_atividade = time.time() - self.tempo_ultimo_movimento
                
                if atividade:
                    if self.modo_descanso:
                        self._sair_descanso()
                    self.usuario_presente = True
                else:
                    if tempo_sem_atividade >= self.tempo_descanso:
                        if not self.modo_descanso:
                            self._entrar_descanso()
                        self.usuario_presente = False
                
                time.sleep(self.intervalo_verificacao)
            except:
                time.sleep(self.intervalo_verificacao)

    def _entrar_descanso(self):
        """Entra em modo descanso."""
        self.modo_descanso = True
        print("[Modo descanso ativado - sem atividade detectada]")

    def _sair_descanso(self):
        """Sai do modo descanso."""
        self.modo_descanso = False
        print("[Modo descanso desativado - atividade detectada]")

    def iniciar_monitoramento(self):
        """Inicia o monitoramento de presença."""
        if not self.monitorando:
            self.monitorando = True
            self._thread = threading.Thread(target=self._monitorar_presenca, daemon=True)
            self._thread.start()
            print("[Monitoramento de presença iniciado]")

    def parar_monitoramento(self):
        """Para o monitoramento de presença."""
        self.monitorando = False
        print("[Monitoramento de presença parado]")

    def esta_em_descanso(self):
        """Verifica se está em modo descanso."""
        return self.modo_descanso

    def usuario_esta_presente(self):
        """Verifica se o usuário está presente."""
        return self.usuario_presente

    def configurar_tempo_descanso(self, segundos):
        """Configura o tempo sem atividade para entrar em descanso."""
        self.tempo_descanso = segundos
        print(f"[Tempo de descanso configurado para {segundos} segundos]")

    def obter_status(self):
        """Retorna status atual."""
        tempo_sem_atividade = time.time() - self.tempo_ultimo_movimento
        return {
            "presente": self.usuario_presente,
            "modo_descanso": self.modo_descanso,
            "tempo_sem_atividade": int(tempo_sem_atividade),
            "tempo_descanso_configurado": self.tempo_descanso
        }
