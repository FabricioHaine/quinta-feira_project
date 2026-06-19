"""
Módulo de Otimização de Tokens - QUINTA-FEIRA
Economiza tokens da API com cache e respostas locais.
"""
import json
import os
import hashlib
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class OtimizadorTokens:
    def __init__(self):
        self.arquivo_cache = os.path.join(BASE_DIR, "cache_respostas.json")
        self.cache = self._carregar_cache()
        self.estatisticas = {"tokens_economizados": 0, "respostas_cache": 0}

    def _carregar_cache(self):
        if os.path.exists(self.arquivo_cache):
            try:
                with open(self.arquivo_cache, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _salvar_cache(self):
        try:
            with open(self.arquivo_cache, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=4, ensure_ascii=False)
        except:
            pass

    def _gerar_chave(self, texto):
        return hashlib.md5(texto.lower().strip().encode()).hexdigest()

    def obter_resposta_cache(self, pergunta):
        """Busca resposta no cache."""
        chave = self._gerar_chave(pergunta)
        
        if chave in self.cache:
            entrada = self.cache[chave]
            # Cache válido por 24 horas
            if datetime.fromisoformat(entrada["timestamp"]) > datetime.now() - timedelta(hours=24):
                self.estatisticas["respostas_cache"] += 1
                self.estatisticas["tokens_economizados"] += len(entrada["resposta"].split()) * 2
                return entrada["resposta"]
        
        return None

    def salvar_resposta_cache(self, pergunta, resposta):
        """Salva resposta no cache."""
        chave = self._gerar_chave(pergunta)
        self.cache[chave] = {
            "pergunta": pergunta,
            "resposta": resposta,
            "timestamp": datetime.now().isoformat()
        }
        
        # Limpa cache antigo (mais de 7 dias)
        self._limpar_cache_antigo()
        self._salvar_cache()

    def _limpar_cache_antigo(self):
        """Remove entradas antigas do cache."""
        chaves_para_remover = []
        for chave, entrada in self.cache.items():
            try:
                if datetime.fromisoformat(entrada["timestamp"]) < datetime.now() - timedelta(days=7):
                    chaves_para_remover.append(chave)
            except:
                chaves_para_remover.append(chave)
        
        for chave in chaves_para_remover:
            del self.cache[chave]

    def comprimir_historico(self, historico, max_itens=5):
        """Comprime histórico para economizar tokens."""
        if not historico or len(historico) <= max_itens:
            return historico
        
        # Mantém apenas os mais recentes
        return historico[-max_itens:]

    def comprimir_contexto(self, contexto):
        """Comprime contexto para enviar menos tokens."""
        if not contexto:
            return ""
        
        # Remove informações desnecessárias
        partes = contexto.split(". ")
        partes_importantes = []
        
        for parte in partes:
            # Mantém apenas informações relevantes
            if any(palavra in parte.lower() for palavra in ["janela", "app", "hora", "sistema"]):
                partes_importantes.append(parte)
        
        return ". ".join(partes_importantes[:3])

    def obter_estatisticas(self):
        """Retorna estatísticas de uso."""
        return {
            "respostas_cache": self.estatisticas["respostas_cache"],
            "tokens_economizados": self.estatisticas["tokens_economizados"],
            "tamanho_cache": len(self.cache)
        }

    def otimizar_prompt(self, prompt):
        """Otimiza prompt para usar menos tokens."""
        # Remove espaços extras
        prompt = " ".join(prompt.split())
        
        # Remove palavras desnecessárias
        palavras_remover = ["por favor", "obrigado", "senhor", "quinta-feira"]
        for palavra in palavras_remover:
            prompt = prompt.replace(palavra, "")
        
        return prompt.strip()
