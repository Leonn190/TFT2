import uuid

from Codigo.Classes.Partida import Partida
from Codigo.Classes.Player import Player
from SimuladorAPI.APIJson import api_json_global


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

    def _detectar_categoria(self, jogador_json, jogador_local_id=None):
        if jogador_json.get("is_bot", False):
            return Player.CATEGORIA_BOT
        if jogador_json.get("player_id") == jogador_local_id:
            return Player.CATEGORIA_PLAYER
        return Player.CATEGORIA_SIMULADO

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
                    categoria=jogador_json.get("categoria")
                    or self._detectar_categoria(jogador_json, jogador_local_id="local-1"),
                )
            )

        partida.atualizar_status(resposta_api.get("status", "buscando"))
        resposta_api["partida"] = partida.espelho()
        resposta_api["partida_objeto"] = partida
        return resposta_api

    def _enviar(self, rota, payload):
        return api_json_global.enviar(rota, payload)

    def entrar_fila(self, jogador, set_escolhido):
        resposta_api = self._enviar("pareamento.entrar_na_fila", {"jogador": jogador.para_json(), "set_escolhido": set_escolhido})
        resposta_api = self._sincronizar_espelho(resposta_api, set_escolhido, jogador_entrada=jogador)
        return {
            "ticket": uuid.uuid4().hex,
            "ok": True,
            "api": resposta_api,
        }

    def atualizar(self, set_escolhido):
        resposta_api = self._enviar("pareamento.atualizar", {"set_escolhido": set_escolhido})
        resposta_api = self._sincronizar_espelho(resposta_api, set_escolhido)
        return {
            "ok": True,
            "api": resposta_api,
        }

    def cancelar_fila(self, set_escolhido, player_id="local-1"):
        retorno = self._enviar("pareamento.cancelar_fila", {"set_escolhido": set_escolhido, "player_id": player_id})
        return {
            "ok": retorno.get("ok", False),
            "api": retorno,
        }

    def registrar_saida_partida(self, partida_id, player_id="local-1"):
        retorno = self._enviar("pareamento.registrar_saida", {"partida_id": partida_id, "player_id": player_id})
        self.partidas_espelhadas.pop(partida_id, None)
        return {
            "ok": retorno.get("ok", False),
            "api": retorno,
        }

    def simular_rodada(self, partida_id):
        retorno = self._enviar("pareamento.simular_rodada", {"partida_id": partida_id})
        return {
            "ok": retorno.get("ok", False),
            "api": retorno,
        }

    def simular_partida_completa(self, partida_id, max_rodadas=100):
        retorno = self._enviar("pareamento.simular_partida", {"partida_id": partida_id, "max_rodadas": max_rodadas})
        return {
            "ok": retorno.get("ok", False),
            "api": retorno,
        }

    def estado_partida(self, partida_id):
        retorno = self._enviar("pareamento.estado_partida", {"partida_id": partida_id})
        return {
            "ok": retorno.get("ok", False),
            "api": retorno,
        }
