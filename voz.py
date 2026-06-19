"""
Módulo de Voz - QUINTA-FEIRA
Versão 2.1: Reconhecimento de voz com sounddevice (compatível com Python 3.14).
"""
import speech_recognition as sr
import time
import os
import asyncio
import re
import edge_tts
import pyttsx3
import numpy as np
import sounddevice as sd
from pygame import mixer
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MicrofoneSoundDevice(sr.AudioSource):
    """Substituto para sr.Microphone usando sounddevice (sem pyaudio)."""
    def __init__(self, samplerate=16000, channels=1, chunk_size=1024):
        self.samplerate = samplerate
        self.channels = channels
        self.chunk_size = chunk_size
        self.CHUNK = chunk_size
        self.SAMPLE_RATE = samplerate
        self.SAMPLE_WIDTH = 2
        self.stream = None
        self._buffer = []

    def __enter__(self):
        self._buffer = []
        self.stream = _AudioStreamSD(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream:
            self.stream.close()
            self.stream = None
        return False


class _AudioStreamSD:
    """Stream compatível com a interface do speech_recognition."""
    def __init__(self, mic):
        self.mic = mic
        self._closed = False
        self._buffer = bytearray()
        self._sd_stream = None
        try:
            self._sd_stream = sd.InputStream(
                samplerate=mic.samplerate,
                channels=mic.channels,
                dtype='int16',
                blocksize=mic.chunk_size,
                callback=self._callback
            )
            self._sd_stream.start()
        except Exception as e:
            print(f"[Erro ao abrir microfone: {e}]")
            raise

    def _callback(self, indata, frames, time_info, status):
        if not self._closed:
            self._buffer.extend(indata.tobytes())

    def read(self, num_frames):
        bytes_per_frame = self.mic.SAMPLE_WIDTH * self.mic.channels
        needed = num_frames * bytes_per_frame
        while len(self._buffer) < needed and not self._closed:
            time.sleep(0.01)
        data = bytes(self._buffer[:needed])
        self._buffer = self._buffer[needed:]
        return data

    def close(self):
        self._closed = True
        if self._sd_stream:
            try:
                self._sd_stream.stop()
                self._sd_stream.close()
            except Exception:
                pass


class ControladorVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        self.VOZ_NEURAL = "pt-BR-FranciscaNeural"
        self.calibrado = False
        self.historico_erros = []
        mixer.init()

    def _limpar_texto_fala(self, texto: str) -> str:
        texto = re.sub(r'\*+', '', texto)
        texto = re.sub(r'#+\s', '', texto)
        texto = re.sub(r'`[^`]*`', '', texto)
        texto = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', texto)
        texto = texto.replace('**', '').replace('*', '')
        texto = texto.replace('FebrasHz', 'Fébras H Z')
        texto = texto.replace('FEBRASHZ', 'Fébras H Z')
        texto = texto.replace('febrashz', 'Fébras H Z')
        texto = ' '.join(texto.split())
        return texto.strip()

    def _gerar_audio_sincrono(self, texto: str, caminho: str):
        texto_limpo = self._limpar_texto_fala(texto)
        async def comunicar():
            communicate = edge_tts.Communicate(texto_limpo, self.VOZ_NEURAL, rate="+10%")
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
                except Exception: pass
                del engine

    def falar(self, texto: str):
        if not texto: return
        texto_limpo = self._limpar_texto_fala(texto)
        print(f"[Quinta-Feira]: {texto_limpo}")
        caminho_temp = os.path.join(BASE_DIR, "sons", "temp_fala.mp3")
        os.makedirs(os.path.dirname(caminho_temp), exist_ok=True)
        
        try:
            if mixer.music.get_busy(): mixer.music.stop()
            mixer.music.unload()
            self._gerar_audio_sincrono(texto_limpo, caminho_temp)
            mixer.music.load(caminho_temp)
            mixer.music.play()
            while mixer.music.get_busy(): time.sleep(0.05)
            mixer.music.unload()
            if os.path.exists(caminho_temp): os.remove(caminho_temp)
        except Exception:
            self._falar_offline_emergencia(texto_limpo)
            
    def calibrar_microfone(self, mic, duracao=2):
        """Calibra o microfone com duração maior para melhor precisão."""
        try:
            print("[Calibrando microfone...]")
            self.recognizer.adjust_for_ambient_noise(mic, duration=duracao)
            self.calibrado = True
            print(f"[Calibrado. Limiar: {self.recognizer.energy_threshold}]")
        except Exception as e:
            print(f"[Erro na calibração: {e}]")

    def _calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """Calcula similaridade entre duas strings."""
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()

    def _corrigir_reconhecimento(self, texto: str, gatilhos: list) -> str:
        """Tenta corrigir erros comuns de reconhecimento de voz."""
        texto_lower = texto.lower().strip()
        
        # Correções de erros comuns
        correcoes = {
            "printa feira": "quinta feira",
            "tinta feira": "quinta feira",
            "vinta feira": "quinta feira",
            "kinta feira": "quinta feira",
            "quinta fera": "quinta feira",
            "quinta fere": "quinta feira",
            "quinta faira": "quinta feira",
            "quinto feira": "quinta feira",
            "quinta-feira": "quinta feira",
            "ei quinta": "quinta",
            "ok quinta": "quinta",
            "hey quinta": "quinta",
        }
        
        # Aplica correções
        for erro, correcao in correcoes.items():
            if erro in texto_lower:
                texto_lower = texto_lower.replace(erro, correcao)
        
        # Tenta encontrar gatilho por similaridade
        for gatilho in gatilhos:
            if gatilho in texto_lower:
                return texto_lower
            
            # Verifica similaridade
            for palavra in texto_lower.split():
                similaridade = self._calcular_similaridade(palavra, gatilho)
                if similaridade > 0.7:
                    return texto_lower
        
        return texto_lower

    def ouvir(self, mic, gatilhos=None) -> str:
        """Método de escuta melhorado com correção automática."""
        try:
            audio = self.recognizer.listen(
                mic, 
                timeout=5, 
                phrase_time_limit=12
            )
            
            # Tenta reconhecer com Google
            try:
                texto = self.recognizer.recognize_google(
                    audio, 
                    language="pt-BR",
                    show_all=True
                )
                
                # Se retornar resultado completo, pega o mais provável
                if isinstance(texto, dict) and 'alternative' in texto:
                    texto = texto['alternative'][0]['transcript']
                
                if texto:
                    texto = texto.lower().strip()
                    
                    # Corrige erros comuns se gatilhos forem fornecidos
                    if gatilhos:
                        texto = self._corrigir_reconhecimento(texto, gatilhos)
                    
                    return texto
                    
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"[Erro na API de reconhecimento: {e}]")
                # Tenta com offline como fallback
                return ""
            
            return ""
        
        except (OSError, Exception) as e:
            if "Stream closed" in str(e) or "-9988" in str(e):
                self.recognizer = sr.Recognizer()
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 4000
                time.sleep(0.5)
            return ""

    def ouvir_comando(self, mic, gatilhos: list, timeout=5) -> str:
        """Escuta especificamente para comandos com gatilho."""
        try:
            audio = self.recognizer.listen(
                mic,
                timeout=timeout,
                phrase_time_limit=10
            )
            
            try:
                texto = self.recognizer.recognize_google(
                    audio,
                    language="pt-BR",
                    show_all=True
                )
                
                if isinstance(texto, dict) and 'alternative' in texto:
                    # Pega todas as alternativas e tenta encontrar o gatilho
                    for alt in texto['alternative']:
                        transcript = alt['transcript'].lower().strip()
                        transcript = self._corrigir_reconhecimento(transcript, gatilhos)
                        
                        for gatilho in gatilhos:
                            if gatilho in transcript:
                                return transcript
                
                elif isinstance(texto, str):
                    texto = texto.lower().strip()
                    texto = self._corrigir_reconhecimento(texto, gatilhos)
                    return texto
                
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                pass
            
            return ""
            
        except (OSError, Exception) as e:
            if "Stream closed" in str(e) or "-9988" in str(e):
                self.recognizer = sr.Recognizer()
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 4000
                time.sleep(0.5)
            return ""

    def ajustar_sensibilidade(self, nivel: str = "medio"):
        """Ajusta a sensibilidade do reconhecimento."""
        ajustes = {
            "baixo": {"energy": 3000, "pause": 1.0, "phrase": 0.3},
            "medio": {"energy": 4000, "pause": 0.8, "phrase": 0.3},
            "alto": {"energy": 5000, "pause": 0.6, "phrase": 0.2}
        }
        
        config = ajustes.get(nivel, ajustes["medio"])
        self.recognizer.energy_threshold = config["energy"]
        self.recognizer.pause_threshold = config["pause"]
        self.recognizer.phrase_threshold = config["phrase"]
        
        print(f"[Sensibilidade ajustada para: {nivel}]")
