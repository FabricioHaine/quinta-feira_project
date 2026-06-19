"""
Módulo de Integrações - QUINTA-FEIRA
Discord, Notas, WhatsApp, e outros apps.
"""
import json
import os
import datetime
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Integracoes:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.arquivo_config = os.path.join(BASE_DIR, "integracoes.json")
        self.config = self._carregar()
        self.arquivo_notas = os.path.join(BASE_DIR, "notas_integradas.json")
        self.notas = self._carregar_notas()

    def _carregar(self):
        if os.path.exists(self.arquivo_config):
            try:
                with open(self.arquivo_config, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"webhooks": {}, "apps_favoritos": {}}
        return {"webhooks": {}, "apps_favoritos": {}}

    def _salvar(self):
        try:
            with open(self.arquivo_config, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Erro ao salvar]: {e}")

    def _carregar_notas(self):
        if os.path.exists(self.arquivo_notas):
            try:
                with open(self.arquivo_notas, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"notas": []}
        return {"notas": []}

    def _salvar_notas(self):
        try:
            with open(self.arquivo_notas, "w", encoding="utf-8") as f:
                json.dump(self.notas, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Erro ao salvar notas]: {e}")

    # --- DISCORD ---
    def configurar_webhook_discord(self, nome: str, url: str):
        self.config["webhooks"][nome] = url
        self._salvar()
        self.voz.falar(f"Webhook do Discord {nome} configurado.")
        return True

    def enviar_discord(self, webhook_nome: str, mensagem: str):
        import requests

        url = self.config["webhooks"].get(webhook_nome)
        if not url:
            self.voz.falar(f"Webhook {webhook_nome} não configurado.")
            return False

        try:
            payload = {"content": mensagem}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 204:
                self.voz.falar("Enviado.")
                return True
            else:
                self.voz.falar("Erro ao enviar.")
                return False
        except Exception:
            self.voz.falar("Erro de conexão.")
            return False

    def listar_webhooks(self):
        webhooks = self.config.get("webhooks", {})
        if not webhooks:
            self.voz.falar("Nenhum webhook configurado.")
            return []

        msg = f"Webhooks configurados: {', '.join(webhooks.keys())}."
        self.voz.falar(msg)
        return webhooks

    # --- NOTAS INTEGRADAS ---
    def criar_nota(self, titulo: str, conteudo: str, tags: list = None):
        nota = {
            "id": len(self.notas.get("notas", [])) + 1,
            "titulo": titulo,
            "conteudo": conteudo,
            "tags": tags or [],
            "criada_em": datetime.datetime.now().isoformat(),
            "editada_em": datetime.datetime.now().isoformat()
        }

        self.notas["notas"].append(nota)
        self._salvar_notas()
        self.voz.falar(f"Nota '{titulo}' criada.")
        return nota

    def listar_notas(self, tag: str = None):
        notas = self.notas.get("notas", [])

        if tag:
            notas = [n for n in notas if tag in n.get("tags", [])]

        if not notas:
            self.voz.falar("Nenhuma nota encontrada.")
            return []

        msg = f"Você tem {len(notas)} notas: "
        for n in notas[:5]:
            msg += f"{n['titulo']}. "

        self.voz.falar(msg)
        return notas

    def buscar_nota(self, termo: str):
        notas = self.notas.get("notas", [])
        encontradas = [n for n in notas if termo.lower() in n["titulo"].lower() or termo.lower() in n["conteudo"].lower()]

        if not encontradas:
            self.voz.falar(f"Nenhuma nota encontrada com '{termo}'.")
            return []

        msg = f"Notas encontradas: "
        for n in encontradas[:3]:
            msg += f"{n['titulo']}: {n['conteudo'][:50]}. "

        self.voz.falar(msg)
        return encontradas

    def excluir_nota(self, titulo: str):
        notas = self.notas.get("notas", [])
        antes = len(notas)
        self.notas["notas"] = [n for n in notas if titulo.lower() not in n["titulo"].lower()]

        if len(self.notas["notas"]) < antes:
            self._salvar_notas()
            self.voz.falar(f"Nota '{titulo}' excluída.")
            return True

        self.voz.falar(f"Nota '{titulo}' não encontrada.")
        return False

    # --- APPS FAVORITOS ---
    def adicionar_app_favorito(self, nome: str, caminho: str):
        self.config["apps_favoritos"][nome] = caminho
        self._salvar()
        self.voz.falar(f"App {nome} adicionado aos favoritos.")
        return True

    def abrir_app_favorito(self, nome: str):
        caminho = self.config["apps_favoritos"].get(nome)
        if caminho:
            try:
                os.startfile(caminho)
                self.voz.falar(f"Abrindo {nome}.")
                return True
            except Exception:
                self.voz.falar(f"Erro ao abrir {nome}.")
                return False

        self.voz.falar(f"App {nome} não encontrado nos favoritos.")
        return False

    def listar_apps_favoritos(self):
        apps = self.config.get("apps_favoritos", {})
        if not apps:
            self.voz.falar("Nenhum app favorito configurado.")
            return []

        msg = f"Apps favoritos: {', '.join(apps.keys())}."
        self.voz.falar(msg)
        return apps

    # --- ATALHOS RÁPIDOS ---
    def abrir_no_navegador(self, url: str):
        if not url.startswith("http"):
            url = "https://" + url

        webbrowser.open(url)
        self.voz.falar(f"Abrindo {url} no navegador.")
        return True

    def pesquisar_google(self, termo: str):
        url = f"https://www.google.com/search?q={termo.replace(' ', '+')}"
        webbrowser.open(url)
        self.voz.falar(f"Pesquisando '{termo}' no Google.")
        return True

    def pesquisar_youtube(self, termo: str):
        url = f"https://www.youtube.com/results?search_query={termo.replace(' ', '+')}"
        webbrowser.open(url)
        self.voz.falar(f"Pesquisando '{termo}' no YouTube.")
        return True

    def abrir_gmail(self):
        webbrowser.open("https://mail.google.com")
        self.voz.falar("Abrindo Gmail.")
        return True

    def abrir_google_drive(self):
        webbrowser.open("https://drive.google.com")
        self.voz.falar("Abrindo Google Drive.")
        return True
