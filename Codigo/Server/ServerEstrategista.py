from copy import deepcopy

from SimuladorAPI.APIJson import api_json_global


class ServidorEstrategista:
    def _enviar(self, rota, payload):
        return api_json_global.enviar(rota, payload)

    @staticmethod
    def _aplicar_snapshot(partida, snapshot):
        if partida is None or not snapshot:
            return

        partida.estoque_compartilhado = deepcopy(snapshot.get("estoque_compartilhado", {}))
        partida.seed_combate = int(snapshot.get("seed_combate", getattr(partida, "seed_combate", 1337)))
        partida.log_eventos = deepcopy(snapshot.get("log_eventos", []))

        jogadores_snapshot = snapshot.get("jogadores", {})
        for jogador in getattr(partida, "jogadores", []):
            dados = jogadores_snapshot.get(jogador.player_id)
            if not isinstance(dados, dict):
                continue
            jogador.vida = dados.get("vida", jogador.vida)
            jogador.ouro = dados.get("ouro", jogador.ouro)
            jogador.banco = deepcopy(dados.get("banco", []))
            jogador.loja = deepcopy(dados.get("loja", []))
            jogador.mapa = deepcopy(dados.get("mapa", []))
            jogador.selecao = deepcopy(dados.get("selecao", []))
            jogador.sinergias = deepcopy(dados.get("sinergias", []))
            jogador.slots_adquiridos = dados.get("slots_adquiridos", jogador.slots_adquiridos)
            jogador.chances_loja = deepcopy(dados.get("chances_loja", jogador.chances_loja))

    def sincronizar_partida(self, partida, player_local_id="local-1"):
        resposta = self._enviar("estrategista.sincronizar", {"partida": partida, "player_local_id": player_local_id})
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def definir_ping(self, ping_ms):
        self._enviar("estrategista.definir_ping", {"ping_ms": ping_ms})

    def comprar_carta_loja(self, partida, player_id, indice_loja):
        resposta = self._enviar(
            "estrategista.comprar_loja",
            {"partida": partida, "player_id": player_id, "indice_loja": indice_loja},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def roletar_loja(self, partida, player_id):
        resposta = self._enviar("estrategista.roletar", {"partida": partida, "player_id": player_id})
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def vender_do_banco(self, partida, player_id, indice_banco):
        resposta = self._enviar(
            "estrategista.vender_banco",
            {"partida": partida, "player_id": player_id, "indice_banco": indice_banco},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def posicionar_do_banco(self, partida, player_id, indice_banco, q, r):
        resposta = self._enviar(
            "estrategista.posicionar_banco",
            {"partida": partida, "player_id": player_id, "indice_banco": indice_banco, "q": q, "r": r},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def alocar_cartas_sinergia(self, partida, player_id, card_uids, alvo_grupo_id=None):
        resposta = self._enviar(
            "estrategista.alocar_sinergia",
            {"partida": partida, "player_id": player_id, "card_uids": card_uids, "alvo_grupo_id": alvo_grupo_id},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def desbloquear_slot_mapa(self, partida, player_id, slot_id):
        resposta = self._enviar(
            "estrategista.desbloquear_slot",
            {"partida": partida, "player_id": player_id, "slot_id": slot_id},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def mover_banco_para_mapa(self, partida, player_id, indice_banco, slot_id):
        resposta = self._enviar(
            "estrategista.banco_para_mapa",
            {"partida": partida, "player_id": player_id, "indice_banco": indice_banco, "slot_id": slot_id},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def mover_mapa_para_banco(self, partida, player_id, slot_id):
        resposta = self._enviar(
            "estrategista.mapa_para_banco",
            {"partida": partida, "player_id": player_id, "slot_id": slot_id},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def mover_mapa_para_mapa(self, partida, player_id, slot_origem_id, slot_destino_id):
        resposta = self._enviar(
            "estrategista.mapa_para_mapa",
            {
                "partida": partida,
                "player_id": player_id,
                "slot_origem_id": slot_origem_id,
                "slot_destino_id": slot_destino_id,
            },
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta

    def registrar_fim_batalha(self, partida, player_id):
        resposta = self._enviar(
            "estrategista.registrar_fim_batalha",
            {"partida": partida, "player_id": player_id},
        )
        self._aplicar_snapshot(partida, resposta.get("snapshot"))
        return resposta
