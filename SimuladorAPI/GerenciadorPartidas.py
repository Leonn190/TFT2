import time
import uuid

from SimuladorAPI.Bot import Bot


class GerenciadorPartidas:
    def __init__(self):
        self.filas = {}

    def _obter_fila(self, set_escolhido):
        if set_escolhido not in self.filas:
            self.filas[set_escolhido] = {
                "partida_id": uuid.uuid4().hex,
                "criado_em": time.time(),
                "jogadores": [],
                "pareada": False,
            }
        return self.filas[set_escolhido]

    def entrar_na_fila(self, jogador, set_escolhido):
        fila = self._obter_fila(set_escolhido)
        fila["jogadores"].append(jogador)
        return {
            "status": "na_fila",
            "set_escolhido": set_escolhido,
            "partida_id": fila["partida_id"],
            "jogadores_na_fila": len(fila["jogadores"]),
        }

    def atualizar_pareamento(self, set_escolhido, tamanho_partida=10, timeout_segundos=20):
        fila = self._obter_fila(set_escolhido)

        if len(fila["jogadores"]) >= tamanho_partida:
            fila["pareada"] = True

        tempo_em_fila = time.time() - fila["criado_em"]
        if not fila["pareada"] and tempo_em_fila >= timeout_segundos:
            faltantes = tamanho_partida - len(fila["jogadores"])
            for indice in range(max(0, faltantes)):
                fila["jogadores"].append(
                    Bot(
                        player_id=f"bot-{uuid.uuid4().hex[:8]}",
                        nome=f"Bot {indice + 1}",
                        set_escolhido=set_escolhido,
                    )
                )
            fila["pareada"] = True

        return {
            "status": "partida_encontrada" if fila["pareada"] else "buscando",
            "set_escolhido": set_escolhido,
            "partida_id": fila["partida_id"],
            "tempo_espera": round(tempo_em_fila, 1),
            "jogadores_na_fila": len(fila["jogadores"]),
            "jogadores": [jogador.para_json() for jogador in fila["jogadores"]],
            "tamanho_partida": tamanho_partida,
        }


gerenciador_partidas = GerenciadorPartidas()
