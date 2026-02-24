import uuid

from SimuladorAPI.GerenciadorPartidas import gerenciador_partidas


class ServidorPareamento:
    def entrar_fila(self, jogador, set_escolhido):
        resposta_api = gerenciador_partidas.entrar_na_fila(jogador, set_escolhido)
        return {
            "ticket": uuid.uuid4().hex,
            "ok": True,
            "api": resposta_api,
        }

    def atualizar(self, set_escolhido):
        resposta_api = gerenciador_partidas.atualizar_pareamento(set_escolhido=set_escolhido)
        return {
            "ok": True,
            "api": resposta_api,
        }
