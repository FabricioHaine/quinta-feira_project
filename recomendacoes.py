"""
Módulo de Recomendações - QUINTA-FEIRA
Sugere jogos, livros, apps, utensílios baseado no perfil do usuário.
"""
import json
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Recomendador:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.arquivo_perfil = os.path.join(BASE_DIR, "perfil_recomendacoes.json")
        self.perfil = self._carregar()

        self.banco_dados = {
            "jogos": {
                "acao": [
                    {"nome": "DOOM Eternal", "genero": "FPS", "nota": 9.5},
                    {"nome": "Cyberpunk 2077", "genero": "RPG/FPS", "nota": 8.5},
                    {"nome": "Valorant", "genero": "FPS Tático", "nota": 8.0},
                    {"nome": "Call of Duty: Warzone", "genero": "Battle Royale", "nota": 8.0},
                    {"nome": "Apex Legends", "genero": "Battle Royale", "nota": 8.5}
                ],
                "rpg": [
                    {"nome": "The Witcher 3", "genero": "RPG", "nota": 10},
                    {"nome": "Elden Ring", "genero": "RPG/Ação", "nota": 9.5},
                    {"nome": "Baldur's Gate 3", "genero": "RPG", "nota": 10},
                    {"nome": "Final Fantasy VII Remake", "genero": "RPG", "nota": 9.0},
                    {"nome": "Persona 5 Royal", "genero": "RPG", "nota": 9.5}
                ],
                "estrategia": [
                    {"nome": "Civilization VI", "genero": "Estratégia", "nota": 9.0},
                    {"nome": "StarCraft II", "genero": "RTS", "nota": 9.5},
                    {"nome": "XCOM 2", "genero": "Estratégia Tática", "nota": 9.0},
                    {"nome": "Total War: Warhammer III", "genero": "Estratégia", "nota": 8.5},
                    {"nome": "Age of Empires IV", "genero": "RTS", "nota": 8.0}
                ],
                "aventura": [
                    {"nome": "The Legend of Zelda: BOTW", "genero": "Aventura", "nota": 10},
                    {"nome": "Red Dead Redemption 2", "genero": "Aventura/Ação", "nota": 10},
                    {"nome": "God of War Ragnarök", "genero": "Aventura/Ação", "nota": 9.5},
                    {"nome": "Hades", "genero": "Roguelike", "nota": 9.0},
                    {"nome": "Hollow Knight", "genero": "Metroidvania", "nota": 9.5}
                ]
            },
            "livros": {
                "ficcao_cientifica": [
                    {"nome": "Duna", "autor": "Frank Herbert", "nota": 10},
                    {"nome": "Neuromancer", "autor": "William Gibson", "nota": 9.0},
                    {"nome": "Fundação", "autor": "Isaac Asimov", "nota": 9.5},
                    {"nome": "1984", "autor": "George Orwell", "nota": 10},
                    {"nome": "O Guia do Mochileiro das Galáxias", "autor": "Douglas Adams", "nota": 9.0}
                ],
                "fantasia": [
                    {"nome": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien", "nota": 10},
                    {"nome": "As Crônicas de Gelo e Fogo", "autor": "George R.R. Martin", "nota": 9.5},
                    {"nome": "Harry Potter", "autor": "J.K. Rowling", "nota": 9.0},
                    {"nome": "The Witcher", "autor": "Andrzej Sapkowski", "nota": 9.0},
                    {"nome": "Name of the Wind", "autor": "Patrick Rothfuss", "nota": 9.5}
                ],
                "nao_ficcao": [
                    {"nome": "Sapiens", "autor": "Yuval Noah Harari", "nota": 9.5},
                    {"nome": "Hábitos Atômicos", "autor": "James Clear", "nota": 9.0},
                    {"nome": "O Poder do Hábito", "autor": "Charles Duhigg", "nota": 8.5},
                    {"nome": "Pense de Novo", "autor": "Adam Grant", "nota": 9.0},
                    {"nome": "A Arte da Guerra", "autor": "Sun Tzu", "nota": 8.5}
                ],
                "programacao": [
                    {"nome": "Código Limpo", "autor": "Robert C. Martin", "nota": 9.0},
                    {"nome": "O Programador Pragmático", "autor": "Hunt & Thomas", "nota": 9.5},
                    {"nome": "Design Patterns", "autor": "Gang of Four", "nota": 8.5},
                    {"nome": "Refatoração", "autor": "Martin Fowler", "nota": 9.0},
                    {"nome": "Entendendo Algoritmos", "autor": "Aditya Bhargava", "nota": 9.0}
                ]
            },
            "apps": {
                "produtividade": [
                    {"nome": "Notion", "descricao": "Organização e notas"},
                    {"nome": "Obsidian", "descricao": "Notas em Markdown"},
                    {"nome": "Todoist", "descricao": "Gestão de tarefas"},
                    {"nome": "Trello", "descricao": "Quadros kanban"},
                    {"nome": "Forest", "descricao": "Foco e produtividade"}
                ],
                "desenvolvimento": [
                    {"nome": "VS Code", "descricao": "Editor de código"},
                    {"nome": "GitHub Desktop", "descricao": "Git visual"},
                    {"nome": "Docker Desktop", "descricao": "Containers"},
                    {"nome": "Postman", "descricao": "API testing"},
                    {"nome": "TablePlus", "descricao": "Banco de dados"}
                ],
                "criatividade": [
                    {"nome": "Figma", "descricao": "Design UI/UX"},
                    {"nome": "Blender", "descricao": "Modelagem 3D"},
                    {"nome": "Audacity", "descricao": "Edição de áudio"},
                    {"nome": "OBS Studio", "descricao": "Gravação de tela"},
                    {"nome": "DaVinci Resolve", "descricao": "Edição de vídeo"}
                ],
                "utilidades": [
                    {"nome": "7-Zip", "descricao": "Compactação de arquivos"},
                    {"nome": "Everything", "descricao": "Busca de arquivos"},
                    {"nome": "ShareX", "descricao": "Captura de tela"},
                    {"nome": "PowerToys", "descricao": "Utilitários Windows"},
                    {"nome": "Bitwarden", "descricao": "Gerenciador de senhas"}
                ]
            },
            "utensilios": {
                "escritorio": [
                    {"nome": "Monitor ultrawide", "descricao": "Para produtividade"},
                    {"nome": "Cadeira ergonômica", "descricao": "Postura e conforto"},
                    {"nome": "Teclado mecânico", "descricao": "Digitação precisa"},
                    {"nome": "Mouse vertical", "descricao": "Reduz fadiga"},
                    {"nome": "Luminária de mesa LED", "descricao": "Iluminação adequada"}
                ],
                "casa": [
                    {"nome": "Aspirador robô", "descricao": "Limpeza automática"},
                    {"nome": "Luminária inteligente", "descricao": "Ambiente personalizado"},
                    {"nome": "Tomada inteligente", "descricao": "Automação"},
                    {"nome": "Purificador de ar", "descricao": "Qualidade do ar"},
                    {"nome": "Cafeteira elétrica", "descricao": "Café perfeito"}
                ],
                "tecnologia": [
                    {"nome": "Power bank 20000mAh", "descricao": "Carga portátil"},
                    {"nome": "Hub USB-C", "descricao": "Conexões extras"},
                    {"nome": "Cabos braçados", "descricao": "Durabilidade"},
                    {"nome": "Suporte para notebook", "descricao": "Ergonomia"},
                    {"nome": "Webcam HD", "descricao": "Videochamadas"}
                ]
            }
        }

    def _carregar(self):
        if os.path.exists(self.arquivo_perfil):
            try:
                with open(self.arquivo_perfil, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"preferencias": {}, "historico": []}
        return {"preferencias": {}, "historico": []}

    def _salvar(self):
        try:
            with open(self.arquivo_perfil, "w", encoding="utf-8") as f:
                json.dump(self.perfil, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Erro ao salvar]: {e}")

    def registrar_preferencia(self, categoria: str, preferencia: str):
        if categoria not in self.perfil["preferencias"]:
            self.perfil["preferencias"][categoria] = []

        if preferencia not in self.perfil["preferencias"][categoria]:
            self.perfil["preferencias"][categoria].append(preferencia)
            self._salvar()

        self.voz.falar(f"Prefêrencia '{preferencia}' registrada na categoria {categoria}.")
        return True

    def recomendar(self, categoria: str, subcategoria: str = None):
        if categoria not in self.banco_dados:
            self.voz.falar(f"Categoria '{categoria}' não encontrada. Disponíveis: jogos, livros, apps, utensílios.")
            return []

        itens = self.banco_dados[categoria]

        if subcategoria and subcategoria in itens:
            itens_disponiveis = itens[subcategoria]
        else:
            itens_disponiveis = []
            for sub in itens.values():
                itens_disponiveis.extend(sub)

        # Filtra por preferências do perfil
        preferencias_usuario = self.perfil.get("preferencias", {}).get(categoria, [])
        if preferencias_usuario:
            itens_relevantes = []
            for item in itens_disponiveis:
                if any(p.lower() in str(item).lower() for p in preferencias_usuario):
                    itens_relevantes.append(item)
            if itens_relevantes:
                itens_disponiveis = itens_relevantes

        # Embaralha e pega 3
        random.shuffle(itens_disponiveis)
        recomendacoes = itens_disponiveis[:3]

        if not recomendacoes:
            self.voz.falar(f"Nenhuma recomendação encontrada para {categoria}.")
            return []

        msg = f"Recomendações de {categoria}: "
        for i, item in enumerate(recomendacoes, 1):
            nome = item.get("nome", "Desconhecido")
            nota = item.get("nota", "")
            descricao = item.get("descricao", "")

            if nota:
                msg += f"{i}: {nome}, nota {nota}. "
            elif descricao:
                msg += f"{i}: {nome}. "
            else:
                msg += f"{i}: {nome}. "

        self.voz.falar(msg)

        # Registra no histórico
        self.perfil["historico"].append({
            "categoria": categoria,
            "subcategoria": subcategoria,
            "recomendacoes": [r.get("nome") for r in recomendacoes]
        })
        self._salvar()

        return recomendacoes

    def listar_categorias(self):
        msg = "Categorias disponíveis: "
        msg += "jogos (ação, rpg, estratégia, aventura). "
        msg += "livros (ficção científica, fantasia, não-ficção, programação). "
        msg += "apps (produtividade, desenvolvimento, criatividade, utilidades). "
        msg += "utensílios (escritório, casa, tecnologia). "

        self.voz.falar(msg)
        return list(self.banco_dados.keys())

    def recomendar_por_humor(self, humor: str):
        mapeamento = {
            "estressado": {"categoria": "jogos", "subcategoria": "aventura"},
            "cansado": {"categoria": "livros", "subcategoria": "nao_ficcao"},
            "animado": {"categoria": "jogos", "subcategoria": "acao"},
            "entediado": {"categoria": "apps", "subcategoria": "criatividade"},
            "triste": {"categoria": "livros", "subcategoria": "fantasia"},
            "focado": {"categoria": "utensilios", "subcategoria": "escritorio"}
        }

        config = mapeamento.get(humor.lower(), {"categoria": "jogos", "subcategoria": "aventura"})
        self.voz.falar(f"Pelo seu humor, recomendo algo de {config['categoria']}.")
        return self.recomendar(config["categoria"], config["subcategoria"])

    def obter_historico_recomendacoes(self):
        historico = self.perfil.get("historico", [])
        if not historico:
            self.voz.falar("Nenhuma recomendação anterior registrada.")
            return []

        msg = f"Histórico: {len(historico)} recomendações feitas. "
        ultimas = historico[-3:]
        for h in ultimas:
            msg += f"{h['categoria']}: {', '.join(h['recomendacoes'][:2])}. "

        self.voz.falar(msg)
        return historico
