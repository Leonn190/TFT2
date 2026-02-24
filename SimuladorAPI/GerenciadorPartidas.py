import time
import uuid

from SimuladorAPI.Bot import Bot


class GerenciadorPartidas:
    def __init__(self):
        self.filas = {}
        self.partidas_ativas = {}

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

        if fila["pareada"]:
            self.partidas_ativas[fila["partida_id"]] = {
                "set_escolhido": set_escolhido,
                "jogadores": [jogador.para_json() for jogador in fila["jogadores"]],
            }

        return {
            "status": "partida_encontrada" if fila["pareada"] else "buscando",
            "set_escolhido": set_escolhido,
            "partida_id": fila["partida_id"],
            "tempo_espera": round(tempo_em_fila, 1),
            "jogadores_na_fila": len(fila["jogadores"]),
            "jogadores": [jogador.para_json() for jogador in fila["jogadores"]],
            "tamanho_partida": tamanho_partida,
        }

    def registrar_saida_da_partida(self, partida_id, player_id):
        partida = self.partidas_ativas.get(partida_id)
        if not partida:
            return {
                "ok": False,
                "status": "partida_inexistente",
                "partida_id": partida_id,
            }

        jogadores = partida["jogadores"]
        for jogador in jogadores:
            if jogador["player_id"] == player_id:
                jogador["vida"] = 0

        jogadores_reais = [
            jogador
            for jogador in jogadores
            if not jogador.get("is_bot", False) and jogador.get("categoria") != "simulado"
        ]

        removeu_partida = len(jogadores_reais) <= 1
        if removeu_partida:
            del self.partidas_ativas[partida_id]

        return {
            "ok": True,
            "status": "saida_registrada",
            "partida_id": partida_id,
            "partida_apagada": removeu_partida,
        }


gerenciador_partidas = GerenciadorPartidas()
