"""
Módulo Modo Foco - QUINTA-FEIRA
Bloqueio de distrações, Pomodoro, produtividade.
"""
import json
import os
import time
import threading
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ModoFoco:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.arquivo_foco = os.path.join(BASE_DIR, "foco.json")
        self.dados = self._carregar()
        self.modo_ativo = False
        self.timer_pomodoro = None

        self.sites_distracao = [
            "facebook.com", "instagram.com", "twitter.com", "x.com",
            "tiktok.com", "youtube.com", "reddit.com", "netflix.com",
            "twitch.tv", "discord.com", "whatsapp.com", "telegram.org"
        ]

        self.apps_distracao = [
            "chrome", "firefox", "edge", "opera",
            "spotify", "discord", "slack", "teams"
        ]

    def _carregar(self):
        if os.path.exists(self.arquivo_foco):
            try:
                with open(self.arquivo_foco, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"sessoes": [], "config": {"sites_bloqueados": [], "apps_bloqueados": []}}
        return {"sessoes": [], "config": {"sites_bloqueados": [], "apps_bloqueados": []}}

    def _salvar(self):
        try:
            with open(self.arquivo_foco, "w", encoding="utf-8") as f:
                json.dump(self.dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Erro ao salvar]: {e}")

    def ativar_modo_foco(self, duracao_minutos: int = 25):
        self.modo_ativo = True
        self.duracao_foco = duracao_minutos
        self.inicio_foco = datetime.datetime.now()

        self.voz.falar(f"Foco ativado por {duracao_minutos} minutos.")

        self._iniciar_pomodoro(duracao_minutos)
        return True

    def desativar_modo_foco(self):
        self.modo_ativo = False
        if self.timer_pomodoro:
            self.timer_pomodoro.cancel()

        self._registrar_sessao()
        self.voz.falar("Foco desativado.")
        return True

    def _iniciar_pomodoro(self, minutos):
        def callback():
            self.voz.falar("Tempo acabou. Pausa.")
            self.modo_ativo = False
            self._registrar_sessao()

        self.timer_pomodoro = threading.Timer(minutos * 60, callback)
        self.timer_pomodoro.daemon = True
        self.timer_pomodoro.start()

    def _registrar_sessao(self):
        if hasattr(self, 'inicio_foco'):
            duracao = (datetime.datetime.now() - self.inicio_foco).total_seconds() / 60

            sessao = {
                "data": self.inicio_foco.isoformat(),
                "duracao_minutos": round(duracao, 1),
                "completa": duracao >= self.duracao_foco * 0.8
            }

            self.dados["sessoes"].append(sessao)
            self._salvar()

    def bloquear_site(self, site: str):
        if site not in self.dados["config"]["sites_bloqueados"]:
            self.dados["config"]["sites_bloqueados"].append(site)
            self._salvar()
            self.voz.falar(f"Site {site} bloqueado durante o modo foco.")
            return True

        self.voz.falar(f"Site {site} já está bloqueado.")
        return False

    def desbloquear_site(self, site: str):
        if site in self.dados["config"]["sites_bloqueados"]:
            self.dados["config"]["sites_bloqueados"].remove(site)
            self._salvar()
            self.voz.falar(f"Site {site} desbloqueado.")
            return True

        self.voz.falar(f"Site {site} não estava bloqueado.")
        return False

    def bloquear_app(self, app: str):
        if app not in self.dados["config"]["apps_bloqueados"]:
            self.dados["config"]["apps_bloqueados"].append(app)
            self._salvar()
            self.voz.falar(f"Aplicativo {app} bloqueado.")
            return True

        self.voz.falar(f"Aplicativo {app} já está bloqueado.")
        return False

    def adicionar_sites_distracao(self):
        sites_padrao = [
            "facebook.com", "instagram.com", "twitter.com", "x.com",
            "tiktok.com", "youtube.com", "reddit.com", "netflix.com"
        ]

        for site in sites_padrao:
            if site not in self.dados["config"]["sites_bloqueados"]:
                self.dados["config"]["sites_bloqueados"].append(site)

        self._salvar()
        self.voz.falar(f"{len(sites_padrao)} sites de distração bloqueados.")
        return True

    def listar_sites_bloqueados(self):
        sites = self.dados["config"]["sites_bloqueados"]
        if not sites:
            self.voz.falar("Nenhum site bloqueado.")
            return []

        msg = f"Sites bloqueados: {', '.join(sites[:10])}"
        if len(sites) > 10:
            msg += f" e mais {len(sites) - 10}."

        self.voz.falar(msg)
        return sites

    def pomodoro_customizado(self, trabalho_min: int, pausa_min: int, ciclos: int = 4):
        self.voz.falar(f"Pomodoro personalizado: {trabalho_min} minutos de trabalho, {pausa_min} minutos de pausa, {ciclos} ciclos.")

        def executar_ciclos():
            for i in range(ciclos):
                self.voz.falar(f"Ciclo {i+1} de {ciclos}. Foco por {trabalho_min} minutos!")
                time.sleep(trabalho_min * 60)

                if i < ciclos - 1:
                    self.voz.falar(f"Pausa de {pausa_min} minutos. Levante e estique!")
                    time.sleep(pausa_min * 60)

            self.voz.falar("Todos os ciclos concluídos! Excelente trabalho, senhor!")

        thread = threading.Thread(target=executar_ciclos)
        thread.daemon = True
        thread.start()
        return True

    def estatisticas_foco(self):
        sessoes = self.dados.get("sessoes", [])
        if not sessoes:
            self.voz.falar("Nenhuma sessão de foco registrada ainda.")
            return {}

        total_minutos = sum(s["duracao_minutos"] for s in sessoes)
        completas = sum(1 for s in sessoes if s["completa"])

        stats = {
            "total_sessoes": len(sessoes),
            "total_minutos": round(total_minutos, 1),
            "total_horas": round(total_minutos / 60, 1),
            "sessoes_completas": completas,
            "taxa_sucesso": round(completas / len(sessoes) * 100, 1) if sessoes else 0
        }

        msg = f"Estatísticas de foco: {stats['total_sessoes']} sessões, {stats['total_horas']} horas totais. "
        msg += f"Taxa de sucesso: {stats['taxa_sucesso']} por cento."

        self.voz.falar(msg)
        return stats

    def verificar_modo_foco(self):
        return self.modo_ativo
