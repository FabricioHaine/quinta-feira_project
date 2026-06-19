"""
Módulo Secretário Pessoal - QUINTA-FEIRA
Rotinas, lembretes, lista de compras e tarefas diárias.
"""
import json
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SecretarioPessoal:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.arquivo_tarefas = os.path.join(BASE_DIR, "tarefas.json")
        self.arquivo_rotinas = os.path.join(BASE_DIR, "rotinas.json")
        self.arquivo_compras = os.path.join(BASE_DIR, "lista_compras.json")
        self.tarefas = self._carregar(self.arquivo_tarefas)
        self.rotinas = self._carregar(self.arquivo_rotinas)
        self.compras = self._carregar(self.arquivo_compras)

    def _carregar(self, caminho):
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _salvar(self, caminho, dados):
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Erro ao salvar]: {e}")

    # --- TAREFAS ---
    def adicionar_tarefa(self, descricao: str, prioridade: str = "normal", data: str = None):
        if not data:
            data = datetime.date.today().strftime("%Y-%m-%d")

        if data not in self.tarefas:
            self.tarefas[data] = []

        tarefa = {
            "descricao": descricao,
            "prioridade": prioridade,
            "concluida": False,
            "criada_em": datetime.datetime.now().isoformat()
        }

        self.tarefas[data].append(tarefa)
        self._salvar(self.arquivo_tarefas, self.tarefas)
        self.voz.falar(f"Tarefa {descricao} adicionada.")
        return True

    def listar_tarefas(self, data: str = None):
        if not data:
            data = datetime.date.today().strftime("%Y-%m-%d")

        if data not in self.tarefas or not self.tarefas[data]:
            self.voz.falar("Nenhuma tarefa.")
            return []

        pendentes = [t for t in self.tarefas[data] if not t["concluida"]]
        concluidas = [t for t in self.tarefas[data] if t["concluida"]]

        msg = f"{len(pendentes)} pendentes, {len(concluidas)} concluídas"

        if pendentes:
            msg += ". Top 3: "
            for i, t in enumerate(pendentes[:3], 1):
                msg += f"{i}: {t['descricao']}, "

        self.voz.falar(msg)
        return pendentes

    def concluir_tarefa(self, indice: int, data: str = None):
        if not data:
            data = datetime.date.today().strftime("%Y-%m-%d")

        if data in self.tarefas and indice <= len(self.tarefas[data]):
            self.tarefas[data][indice-1]["concluida"] = True
            self._salvar(self.arquivo_tarefas, self.tarefas)
            self.voz.falar("Tarefa concluída. Bom trabalho, senhor!")
            return True

        self.voz.falar("Não encontrei essa tarefa.")
        return False

    # --- ROTINAS ---
    def adicionar_rotina(self, nome: str, horario: str, acoes: list):
        rotina = {
            "nome": nome,
            "horario": horario,
            "acoes": acoes,
            "ativa": True,
            "criada_em": datetime.datetime.now().isoformat()
        }

        self.rotinas[nome] = rotina
        self._salvar(self.arquivo_rotinas, self.rotinas)
        self.voz.falar(f"Rotina {nome} criada para as {horario}.")
        return True

    def listar_rotinas(self):
        if not self.rotinas:
            self.voz.falar("Nenhuma rotina configurada.")
            return []

        msg = f"Você tem {len(self.rotinas)} rotinas: "
        for nome, r in self.rotinas.items():
            status = "ativa" if r["ativa"] else "pausada"
            msg += f"{nome} às {r['horario']}, {status}. "

        self.voz.falar(msg)
        return self.rotinas

    def pausar_rotina(self, nome: str):
        if nome in self.rotinas:
            self.rotinas[nome]["ativa"] = False
            self._salvar(self.arquivo_rotinas, self.rotinas)
            self.voz.falar(f"Rotina {nome} pausada.")
            return True

        self.voz.falar(f"Rotina {nome} não encontrada.")
        return False

    def ativar_rotina(self, nome: str):
        if nome in self.rotinas:
            self.rotinas[nome]["ativa"] = True
            self._salvar(self.arquivo_rotinas, self.rotinas)
            self.voz.falar(f"Rotina {nome} ativada.")
            return True

        self.voz.falar(f"Rotina {nome} não encontrada.")
        return False

    # --- LISTA DE COMPRAS ---
    def adicionar_item_compra(self, item: str, quantidade: str = "1"):
        if "itens" not in self.compras:
            self.compras["itens"] = []

        item_compra = {
            "item": item,
            "quantidade": quantidade,
            "comprado": False,
            "adicionado_em": datetime.datetime.now().isoformat()
        }

        self.compras["itens"].append(item_compra)
        self._salvar(self.arquivo_compras, self.compras)
        self.voz.falar(f"{quantidade} {item} adicionado à lista de compras.")
        return True

    def listar_compras(self):
        itens = self.compras.get("itens", [])
        pendentes = [i for i in itens if not i["comprado"]]
        comprados = [i for i in itens if i["comprado"]]

        if not pendentes:
            self.voz.falar("Lista de compras vazia ou todos os itens foram comprados.")
            return []

        msg = f"Lista de compras: {len(pendentes)} itens pendentes. "
        for i, item in enumerate(pendentes[:10], 1):
            msg += f"{i}: {item['quantidade']} {item['item']}. "

        self.voz.falar(msg)
        return pendentes

    def marcar_comprado(self, indice: int):
        itens = self.compras.get("itens", [])
        pendentes = [i for i in itens if not i["comprado"]]

        if indice <= len(pendentes):
            for i, item in enumerate(itens):
                if item == pendentes[indice-1]:
                    item["comprado"] = True
                    break

            self._salvar(self.arquivo_compras, self.compras)
            self.voz.falar("Item marcado como comprado.")
            return True

        self.voz.falar("Item não encontrado na lista.")
        return False

    def limpar_lista_compras(self):
        self.compras = {"itens": []}
        self._salvar(self.arquivo_compras, self.compras)
        self.voz.falar("Lista de compras limpa.")
        return True

    # --- RESUMO DIÁRIO ---
    def resumo_diarho(self):
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        tarefas_hoje = self.tarefas.get(hoje, [])
        pendentes = [t for t in tarefas_hoje if not t["concluida"]]
        itens_compra = [i for i in self.compras.get("itens", []) if not i["comprado"]]

        msg = f"Resumo do dia {hoje}: "
        msg += f"{len(pendentes)} tarefas pendentes. "
        msg += f"{len(itens_compra)} itens na lista de compras. "

        if pendentes:
            msg += "Próximas tarefas: "
            for t in pendentes[:3]:
                msg += f"{t['descricao']}. "

        self.voz.falar(msg)
        return {
            "tarefas_pendentes": len(pendentes),
            "itens_compra": len(itens_compra)
        }
