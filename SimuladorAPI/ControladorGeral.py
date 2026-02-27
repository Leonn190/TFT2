import random
from copy import deepcopy

from SimuladorAPI.SimuladoCombate import SimuladoCombate


class ControladorGeral:
    """Orquestra rodadas, pareamentos e aplicação de resultados de combate."""

    def __init__(self, intervalo_acao_bot_s=5):
        self.intervalo_acao_bot_s = int(intervalo_acao_bot_s)
        self.simulador = SimuladoCombate()
        self.chance_base_acao_bot = 95
        self.reducao_chance_por_acao = 10

    @staticmethod
    def _jogador_eh_bot(jogador):
        if jogador is None:
            return False
        if isinstance(jogador, dict):
            return bool(jogador.get("is_bot")) or jogador.get("categoria") == "bot"
        return bool(getattr(jogador, "is_bot", False)) or getattr(jogador, "categoria", None) == "bot"

    @staticmethod
    def _tempo_atual_ms(estado_partida):
        return int(estado_partida.get("tempo_atual_ms", 0))

    def _estado_bot(self, estado_partida, player_id):
        return estado_partida.setdefault("bot_estados", {}).setdefault(player_id, {"chance_acao": self.chance_base_acao_bot})

    def resetar_turno_bot(self, estado_partida, player_id):
        self._estado_bot(estado_partida, player_id)["chance_acao"] = self.chance_base_acao_bot

    def deve_tentar_acao_bot(self, estado_partida, player_id):
        chance = int(self._estado_bot(estado_partida, player_id).get("chance_acao", self.chance_base_acao_bot))
        chance = max(0, min(100, chance))
        return random.random() * 100 < chance

    def pode_bot_jogar(self, estado_partida, player_id):
        proximo_tick = estado_partida.get("bot_proximo_tick", {}).get(player_id, 0)
        return self._tempo_atual_ms(estado_partida) >= int(proximo_tick)

    def registrar_acao_bot(self, estado_partida, player_id, reduzir_intervalo=False):
        intervalo_ms = self.intervalo_acao_bot_s * 1000
        if reduzir_intervalo:
            intervalo_ms = max(1000, intervalo_ms // 2)
        estado_partida.setdefault("bot_proximo_tick", {})[player_id] = self._tempo_atual_ms(estado_partida) + intervalo_ms
        estado_bot = self._estado_bot(estado_partida, player_id)
        estado_bot["chance_acao"] = max(0, int(estado_bot.get("chance_acao", self.chance_base_acao_bot)) - self.reducao_chance_por_acao)

    def avancar_tempo(self, estado_partida, delta_ms):
        estado_partida["tempo_atual_ms"] = max(0, int(estado_partida.get("tempo_atual_ms", 0)) + int(delta_ms))

    @staticmethod
    def parear_jogadores_vivos(jogadores_ids, estado_partida):
        vivos = [jid for jid in jogadores_ids if estado_partida["jogadores"].get(jid, {}).get("vida", 0) > 0]
        vivos.sort()
        return [(vivos[i], vivos[i + 1]) for i in range(0, len(vivos) - 1, 2)]

    def simular_e_aplicar_batalhas(self, estado_partida, jogadores_ids):
        batalhas = []
        for jogador_a, jogador_b in self.parear_jogadores_vivos(jogadores_ids, estado_partida):
            estado_a = estado_partida["jogadores"][jogador_a]
            estado_b = estado_partida["jogadores"][jogador_b]
            resultado = self.simulador.simular(jogador_a, estado_a, jogador_b, estado_b)

            perdedor_id = resultado["perdedor_id"]
            estado_perdedor = estado_partida["jogadores"][perdedor_id]
            estado_perdedor["vida"] = max(0, int(estado_perdedor.get("vida", 0)) - int(resultado["dano"]))

            estado_partida.setdefault("historico_batalhas", []).append(deepcopy(resultado))
            batalhas.append(resultado)

        return batalhas
