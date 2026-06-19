"""
Módulo de Monitoramento do Sistema - QUINTA-FEIRA
Monitora CPU, RAM, disco, processos e temperatura.
"""
import psutil
import platform
import time
import os

class MonitorSistema:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz

    def obter_status_completo(self) -> dict:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disco = psutil.disk_usage('C:\\')

        return {
            "cpu_porcentagem": cpu_percent,
            "cpu_nucleos": psutil.cpu_count(),
            "ram_total_gb": round(ram.total / (1024**3), 1),
            "ram_usada_gb": round(ram.used / (1024**3), 1),
            "ram_porcentagem": ram.percent,
            "disco_total_gb": round(disco.total / (1024**3), 1),
            "disco_usado_gb": round(disco.used / (1024**3), 1),
            "disco_porcentagem": round(disco.percent, 1),
            "temperatura_cpu": self._obter_temperatura()
        }

    def _obter_temperatura(self):
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current
        except:
            pass
        return None

    def relatorio_voz(self):
        status = self.obter_status_completo()

        msg = f"CPU {status['cpu_porcentagem']}%, "
        msg += f"RAM {status['ram_porcentagem']}%, "
        msg += f"Disco {status['disco_porcentagem']}%"

        if status['temperatura_cpu']:
            msg += f", {status['temperatura_cpu']} graus"

        if status['cpu_porcentagem'] > 80:
            msg += ". CPU alta!"
        elif status['ram_porcentagem'] > 80:
            msg += ". RAM alta!"

        self.voz.falar(msg)
        return status

    def listar_processos_pesados(self, top_n=5):
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['cpu_percent'] and info['cpu_percent'] > 0:
                    processos.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        processos.sort(key=lambda x: x['cpu_percent'], reverse=True)
        top = processos[:top_n]

        msg = f"Os {top_n} processos mais pesados: "
        for i, p in enumerate(top, 1):
            nome = p['name'][:20]
            cpu = round(p['cpu_percent'], 1)
            ram = round(p['memory_percent'], 1)
            msg += f"{i}: {nome}, CPU {cpu} por cento, RAM {ram} por cento. "

        self.voz.falar(msg)
        return top

    def fechar_processo(self, nome_processo: str) -> bool:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if nome_processo.lower() in proc.info['name'].lower():
                    proc.kill()
                    self.voz.falar(f"Processo {proc.info['name']} finalizado.")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        self.voz.falar(f"Não encontrei o processo {nome_processo}.")
        return False

    def monitorar_em_tempo_real(self, duracao_segundos=10, intervalo=2):
        self.voz.falar(f"Monitorando o sistema por {duracao_segundos} segundos.")
        inicio = time.time()

        while time.time() - inicio < duracao_segundos:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            print(f"CPU: {cpu}% | RAM: {ram}%")
            time.sleep(intervalo)

        self.voz.falar("Monitoramento concluído.")

    def verificar_saude(self) -> dict:
        status = self.obter_status_completo()
        problemas = []

        if status['cpu_porcentagem'] > 90:
            problemas.append("CPU crítica")
        if status['ram_porcentagem'] > 90:
            problemas.append("RAM crítica")
        if status['disco_porcentagem'] > 90:
            problemas.append("Disco cheio")

        resultado = {
            "saudavel": len(problemas) == 0,
            "problemas": problemas,
            "status": status
        }

        if problemas:
            self.voz.falar(f"Alerta! Problemas detectados: {', '.join(problemas)}.")
        else:
            self.voz.falar("Sistema saudável. Todos os componentes normais.")

        return resultado
