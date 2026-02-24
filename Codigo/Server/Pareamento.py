import uuid

from Codigo.Classes.Partida import Partida
from Codigo.Classes.Player import Player
from SimuladorAPI.GerenciadorPartidas import gerenciador_partidas


class ServidorPareamento:
    def __init__(self):
        self.partidas_espelhadas = {}

    def _obter_ou_criar_partida(self, resposta_api, set_escolhido):
        partida_id = resposta_api.get("partida_id") or f"espelho-{set_escolhido}"
        if partida_id not in self.partidas_espelhadas:
            self.partidas_espelhadas[partida_id] = Partida(
                partida_id=partida_id,
                set_escolhido=set_escolhido,
                tamanho_partida=resposta_api.get("tamanho_partida", 10),
            )
        return self.partidas_espelhadas[partida_id]

    def _sincronizar_espelho(self, resposta_api, set_escolhido, jogador_entrada=None):
        partida = self._obter_ou_criar_partida(resposta_api, set_escolhido)
        partida.tamanho_partida = resposta_api.get("tamanho_partida", partida.tamanho_partida)
        partida.jogadores = []

        jogadores_api = resposta_api.get("jogadores", [])
        if not jogadores_api and jogador_entrada is not None:
            jogadores_api = [jogador_entrada.para_json()]

        for jogador_json in jogadores_api:
            partida.adicionar_jogador(
                Player(
                    player_id=jogador_json["player_id"],
                    nome=jogador_json["nome"],
                    set_escolhido=jogador_json.get("set_escolhido"),
                    is_bot=jogador_json.get("is_bot", False),
                )
            )

        partida.atualizar_status(resposta_api.get("status", "buscando"))
        resposta_api["partida"] = partida.espelho()
        return resposta_api

    def entrar_fila(self, jogador, set_escolhido):
        resposta_api = gerenciador_partidas.entrar_na_fila(jogador, set_escolhido)
        resposta_api = self._sincronizar_espelho(resposta_api, set_escolhido, jogador_entrada=jogador)
        return {
            "ticket": uuid.uuid4().hex,
            "ok": True,
            "api": resposta_api,
        }

    def atualizar(self, set_escolhido):
        resposta_api = gerenciador_partidas.atualizar_pareamento(set_escolhido=set_escolhido)
        resposta_api = self._sincronizar_espelho(resposta_api, set_escolhido)
        return {
            "ok": True,
            "api": resposta_api,
        }
