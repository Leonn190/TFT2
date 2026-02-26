from copy import deepcopy

from SimuladorAPI.SimuladoCombate import SimuladoCombate


class ControladorGeral:
    """Orquestra rodadas, pareamentos e aplicação de resultados de combate."""

    def __init__(self, intervalo_acao_bot_s=5):
        self.intervalo_acao_bot_s = int(intervalo_acao_bot_s)
        self.simulador = SimuladoCombate()

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

    def pode_bot_jogar(self, estado_partida, player_id):
        proximo_tick = estado_partida.get("bot_proximo_tick", {}).get(player_id, 0)
        return self._tempo_atual_ms(estado_partida) >= int(proximo_tick)

    def registrar_acao_bot(self, estado_partida, player_id):
        estado_partida.setdefault("bot_proximo_tick", {})[player_id] = self._tempo_atual_ms(estado_partida) + self.intervalo_acao_bot_s * 1000

    def avancar_tempo(self, estado_partida, delta_ms):
        estado_partida["tempo_atual_ms"] = max(0, int(estado_partida.get("tempo_atual_ms", 0)) + int(delta_ms))

    @staticmethod
    def parear_jogadores_vivos(jogadores_ids, estado_partida):
        vivos = [jid for jid in jogadores_ids if estado_partida["jogadores"].get(jid, {}).get("vida", 0) > 0]
        vivos.sort()
        pares = []
        for i in range(0, len(vivos) - 1, 2):
            pares.append((vivos[i], vivos[i + 1]))
        return pares

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
