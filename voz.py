"""
Módulo de Voz - QUINTA-FEIRA
Refatorado para portabilidade universal (Caminhos Relativos).
"""
import speech_recognition as sr
import time
import os
import asyncio
import edge_tts
import pyttsx3
from pygame import mixer

# Define o diretório base automaticamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ControladorVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000
        
        self.VOZ_NEURAL = "pt-BR-FranciscaNeural"
        mixer.init()

    def _gerar_audio_sincrono(self, texto: str, caminho: str):
        async def comunicar():
            communicate = edge_tts.Communicate(texto, self.VOZ_NEURAL, rate="+10%")
            await communicate.save(caminho)
        asyncio.run(comunicar())

    def _falar_offline_emergencia(self, texto: str):
        engine = None
        try:
            engine = pyttsx3.init('sapi5')
            engine.setProperty('rate', 215)
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
            if engine is not None:
                try: engine.stop()
                except: pass
                del engine

    def falar(self, texto: str):
        if not texto: return
            
        print(f"[Quinta-Feira]: {texto}")
        # Caminho dinâmico: pasta 'sons' dentro da pasta raiz do projeto
        caminho_temp = os.path.join(BASE_DIR, "sons", "temp_fala.mp3")
        
        os.makedirs(os.path.dirname(caminho_temp), exist_ok=True)
        
        try:
            if mixer.music.get_busy():
                mixer.music.stop()
            mixer.music.unload()
        except: pass

        try:
            self._gerar_audio_sincrono(texto, caminho_temp)
            mixer.music.load(caminho_temp)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.05)
            mixer.music.unload()
            
            if os.path.exists(caminho_temp):
                try: os.remove(caminho_temp)
                except: pass
        except Exception as e:
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