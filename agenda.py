"""
Módulo de Agenda Tática - QUINTA-FEIRA
Gerenciamento inteligente de prazos, datas e compromissos.
"""
import os
import json
import datetime

class ControladorAgenda:
    def __init__(self, controlador_voz):
        self.voz = controlador_voz
        self.caminho_banco = "D:\\quinta-feira_project\\agenda.json"
        self.compromissos = self._carregar_banco()

    def _carregar_banco(self):
        if os.path.exists(self.caminho_banco):
            try:
                with open(self.caminho_banco, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _salvar_banco(self):
        try:
            with open(self.caminho_banco, "w", encoding="utf-8") as f:
                json.dump(self.compromissos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[Erro ao salvar agenda]: {e}")

    def _calcular_data(self, comando: str) -> datetime.date:
        """Calcula a data alvo com base em termos falados"""
        hoje = datetime.date.today()
        
        if "hoje" in comando:
            return hoje
        if "amanhã" in comando or "amanha" in comando:
            return hoje + datetime.timedelta(days=1)
            
        # Dicionário de mapeamento de dias da semana
        dias_semana = {
            "segunda": 0, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sábado": 5, "domingo": 6,
            "terca": 1, "sabado": 5
        }
        
        for termo, num_dia in dias_semana.items():
            if termo in comando:
                # Se for "que vem", adiciona 7 dias ao cálculo básico se o dia já passou ou é hoje
                dias_para_frente = (num_dia - hoje.weekday() + 7) % 7
                if "que vem" in comando or "próxima" in comando or "proxima" in comando:
                    if dias_para_frente == 0:
                        dias_para_frente = 7
                    else:
                        dias_para_frente += 7
                elif dias_para_frente == 0:
                    # Se o usuário disse o dia de hoje sem especificar "que vem", assume hoje
                    dias_para_frente = 0
                    
                return hoje + datetime.timedelta(days=dias_para_frente)
                
        return hoje # Padrão de segurança

    def agendar_compromisso(self, comando: str) -> bool:
        # Remove os gatilhos para extrair a descrição do evento
        descricao = comando.replace("quinta-feira", "").replace("agendar", "").replace("agenda", "").strip()
        
        # Determina a data alvo
        data_alvo = self._calcular_data(comando)
        data_str = data_alvo.strftime("%Y-%m-%d")
        
        # Limpa termos de tempo da descrição para o registro ficar limpo
        for termo in ["para hoje", "para amanhã", "para amanha", "para quinta-feira que vem", "na terça-feira", "na terça", "na quinta"]:
            descricao = descricao.replace(termo, "")
        descricao = descricao.strip().capitalize()

        if not descricao:
            self.voz.falar("O senhor não especificou o compromisso.")
            return True

        if data_str not in self.compromissos:
            self.compromissos[data_str] = []
            
        self.compromissos[data_str].append(descricao)
        self._salvar_banco()
        
        data_falada = data_alvo.strftime("%d de %B")
        # Correção rápida de português para os meses
        meses_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        for en, pt in zip(meses_en, meses_pt):
            data_falada = data_falada.replace(en, pt)
            
        self.voz.falar(f"Registrado senhor: {descricao} para o dia {data_falada}.")
        return True

    def listar_compromissos_hoje(self) -> bool:
        hoje_str = datetime.date.today().strftime("%Y-%m-%d")
        
        if hoje_str in self.compromissos and self.compromissos[hoje_str]:
            tarefas = ", ".join(self.compromissos[hoje_str])
            self.voz.falar(f"O senhor possui os seguintes compromissos para hoje: {tarefas}.")
        else:
            self.voz.falar("Agenda limpa para o dia de hoje, senhor.")
        return True

    def limpar_agenda(self) -> bool:
        self.compromissos = {}
        self._salvar_banco()
        self.voz.falar("Todos os bancos de dados da agenda foram resetados, senhor.")
        return True