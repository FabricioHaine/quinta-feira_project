import speech_recognition as sr
import time
import os
import asyncio
import edge_tts
import pyttsx3  # Chamado estritamente em caso de falha de rede
from pygame import mixer

class ControladorVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000
        
        # Voz principal (Online/Neural)
        self.VOZ_NEURAL = "pt-BR-FranciscaNeural"
        
        # Inicializa o mixer de áudio do pygame de forma segura
        mixer.init()

    def _gerar_audio_sincrono(self, texto: str, caminho: str):
        """Gera o áudio neural via internet utilizando edge-tts"""
        async def comunicar():
            communicate = edge_tts.Communicate(texto, self.VOZ_NEURAL, rate="+10%")
            await communicate.save(caminho)
        
        asyncio.run(comunicar())

    def _falar_offline_emergencia(self, texto: str):
        """Protocolo de Contingência: Executa a Maria limpando a memória para evitar duplicação"""
        engine = None
        try:
            engine = pyttsx3.init('sapi5')
            engine.setProperty('rate', 215)  # Ritmo tático acelerado
            engine.setProperty('volume', 1.0)
            
            voices = engine.getProperty('voices')
            for voice in voices:
                if "maria" in voice.name.lower() or "brazil" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
                    
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"[Erro Crítico no Motor Offline]: {e}")
        finally:
            # Garante que a Maria morra aqui e não fique rodando em segundo plano
            if engine is not None:
                try:
                    engine.stop()
                except:
                    pass
                del engine

    def falar(self, texto: str):
        if not texto:
            return
            
        print(f"[Quinta-Feira]: {texto}")
        caminho_temp = "D:\\quinta-feira_project\\sons\\temp_fala.mp3"
        
        # Cria a pasta de sons se ela não existir
        os.makedirs(os.path.dirname(caminho_temp), exist_ok=True)
        
        # --- TRAVA DE SEGURANÇA ANTIDUPLICAÇÃO (FRANCISCA) ---
        try:
            if mixer.music.get_busy():
                mixer.music.stop()
            mixer.music.unload()  # Descarrega o áudio anterior da memória do pygame
        except:
            pass

        try:
            # 1. TENTA O PROCESSO NEURAL (FRANCISCA)
            self._gerar_audio_sincrono(texto, caminho_temp)
            
            # Reproduz o áudio gerado
            mixer.music.load(caminho_temp)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.05)
                
            mixer.music.unload()  # Libera o arquivo imediatamente após terminar
            
            # Remove o arquivo temporário para evitar conflitos na próxima resposta
            if os.path.exists(caminho_temp):
                try:
                    os.remove(caminho_temp)
                except:
                    pass
                
        except Exception as e:
            # 2. SE A INTERNET FALHAR, ENTRA A MARIA ISOLADA
            print(f"\n[Sistemas]: Instabilidade de rede detectada. Mudando para contingência...")
            self._falar_offline_emergencia(texto)
            
    def calibrar_microfone(self, mic):
        print("[Sistemas]: Ajustando microfone rapidamente...")
        try:
            self.recognizer.adjust_for_ambient_noise(mic, duration=0.5)
            print("[Sistemas]: Microfone pronto!")
        except Exception as e:
            print(f"[Aviso]: Falha ao calibrar. {e}")

    def ouvir(self, mic) -> str:
        try:
            audio = self.recognizer.listen(mic, timeout=4, phrase_time_limit=10)
            texto = self.recognizer.recognize_google(audio, language="pt-BR")
            return texto.lower().strip()
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except sr.RequestError:
            print("[Erro]: Falha de conexão na captura.")
            return ""