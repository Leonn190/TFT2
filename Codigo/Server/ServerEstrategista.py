from SimuladorAPI.Ativador import ativador_global


class ServidorEstrategista:
    def sincronizar_partida(self, partida, player_local_id="local-1"):
        return ativador_global.sincronizar_partida(partida, player_local_id=player_local_id)

    def definir_ping(self, ping_ms):
        ativador_global.definir_ping(ping_ms)

    def comprar_carta_loja(self, partida, player_id, indice_loja):
        return ativador_global.comprar_carta_loja(partida, player_id, indice_loja)

    def roletar_loja(self, partida, player_id):
        return ativador_global.roletar_loja(partida, player_id)

    def vender_do_banco(self, partida, player_id, indice_banco):
        return ativador_global.vender_do_banco(partida, player_id, indice_banco)

    def posicionar_do_banco(self, partida, player_id, indice_banco, q, r):
        return ativador_global.posicionar_do_banco(partida, player_id, indice_banco, q, r)

    def alocar_cartas_sinergia(self, partida, player_id, card_uids, alvo_grupo_id=None):
        return ativador_global.alocar_cartas_sinergia(partida, player_id, card_uids, alvo_grupo_id=alvo_grupo_id)

    def mover_banco_para_mapa(self, partida, player_id, indice_banco, slot_id):
        return ativador_global.mover_banco_para_mapa(partida, player_id, indice_banco, slot_id)

    def mover_mapa_para_banco(self, partida, player_id, slot_id):
        return ativador_global.mover_mapa_para_banco(partida, player_id, slot_id)
