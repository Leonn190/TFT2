import time
import uuid
import random
from copy import deepcopy

from SimuladorAPI.Bot import Bot
from SimuladorAPI.teste import criar_cartas_teste


class GerenciadorPartidas:
    def __init__(self):
        self.filas = {}
        self.partidas_ativas = {}

    @staticmethod
    def _sinergias_ativas(tabuleiro):
        return Bot.sinergias_ativas(tabuleiro)

    @staticmethod
    def _forca_tabuleiro(tabuleiro):
        return Bot.forca_tabuleiro(tabuleiro)

    def _executar_turno_bot(self, partida, jogador):
        Bot.executar_turno(jogador, partida["catalogo"])

    @staticmethod
    def _aplicar_dano(vencedor, perdedor, diferenca_forca):
        dano = 5 + max(0, diferenca_forca // 3)
        perdedor["vida"] = max(0, perdedor["vida"] - dano)
        vencedor["vitorias"] += 1
        perdedor["derrotas"] += 1

    def _simular_batalhas(self, partida):
        vivos = [j for j in partida["jogadores"] if j["vida"] > 0]
        random.shuffle(vivos)

        historico = []
        for indice in range(0, len(vivos) - 1, 2):
            jogador_a = vivos[indice]
            jogador_b = vivos[indice + 1]
            forca_a = self._forca_tabuleiro(jogador_a["tabuleiro"])
            forca_b = self._forca_tabuleiro(jogador_b["tabuleiro"])

            if forca_a > forca_b:
                self._aplicar_dano(jogador_a, jogador_b, forca_a - forca_b)
                vencedor_id = jogador_a["player_id"]
            elif forca_b > forca_a:
                self._aplicar_dano(jogador_b, jogador_a, forca_b - forca_a)
                vencedor_id = jogador_b["player_id"]
            else:
                jogador_a["vida"] = max(0, jogador_a["vida"] - 2)
                jogador_b["vida"] = max(0, jogador_b["vida"] - 2)
                jogador_a["empates"] += 1
                jogador_b["empates"] += 1
                vencedor_id = None

            historico.append(
                {
                    "dupla": [jogador_a["player_id"], jogador_b["player_id"]],
                    "forcas": [forca_a, forca_b],
                    "vencedor_id": vencedor_id,
                }
            )

        if len(vivos) % 2 == 1:
            bye = vivos[-1]
            bye["ouro"] += 1
            historico.append({"dupla": [bye["player_id"]], "bye": True})

        return historico

    def _inicializar_estado_partida(self, partida_id):
        partida = self.partidas_ativas.get(partida_id)
        if not partida or "catalogo" in partida:
            return

        catalogo = criar_cartas_teste(partida.get("set_escolhido") or "BrawlStars")
        partida["catalogo"] = catalogo
        partida["rodada"] = 0
        partida["status_simulacao"] = "em_andamento"
        partida["historico_rodadas"] = []

        jogadores_estado = []
        for jogador in partida.get("jogadores", []):
            jogadores_estado.append(
                {
                    "player_id": jogador["player_id"],
                    "nome": jogador["nome"],
                    "is_bot": jogador.get("is_bot", False),
                    "categoria": jogador.get("categoria"),
                    "vida": 100,
                    "ouro": 10,
                    "banco": [],
                    "loja": [],
                    "tabuleiro": [],
                    "sinergias": [],
                    "vitorias": 0,
                    "derrotas": 0,
                    "empates": 0,
                    "rodada": 0,
                }
            )

        partida["jogadores"] = jogadores_estado

    def obter_estado_partida(self, partida_id):
        partida = self.partidas_ativas.get(partida_id)
        if not partida:
            return {"ok": False, "status": "partida_inexistente", "partida_id": partida_id}

        self._inicializar_estado_partida(partida_id)
        vivos = [j for j in partida["jogadores"] if j["vida"] > 0]
        vencedor = vivos[0]["player_id"] if len(vivos) == 1 else None
        return {
            "ok": True,
            "status": "finalizada" if vencedor else "em_andamento",
            "partida_id": partida_id,
            "rodada": partida.get("rodada", 0),
            "jogadores_vivos": len(vivos),
            "vencedor_id": vencedor,
            "jogadores": deepcopy(partida["jogadores"]),
            "historico_rodadas": deepcopy(partida.get("historico_rodadas", [])),
        }

    def simular_rodada(self, partida_id):
        partida = self.partidas_ativas.get(partida_id)
        if not partida:
            return {"ok": False, "status": "partida_inexistente", "partida_id": partida_id}

        self._inicializar_estado_partida(partida_id)
        vivos = [j for j in partida["jogadores"] if j["vida"] > 0]
        if len(vivos) <= 1:
            return self.obter_estado_partida(partida_id)

        partida["rodada"] += 1
        for jogador in vivos:
            jogador["rodada"] = partida["rodada"]
            self._executar_turno_bot(partida, jogador)

        historico_batalhas = self._simular_batalhas(partida)
        eliminados_rodada = [j["player_id"] for j in partida["jogadores"] if j["vida"] <= 0]

        resumo_rodada = {
            "rodada": partida["rodada"],
            "batalhas": historico_batalhas,
            "eliminados": eliminados_rodada,
        }
        partida["historico_rodadas"].append(resumo_rodada)
        return {
            "ok": True,
            "status": "rodada_simulada",
            "partida_id": partida_id,
            "rodada": partida["rodada"],
            "resumo": resumo_rodada,
        }

    def simular_partida_completa(self, partida_id, max_rodadas=100):
        partida = self.partidas_ativas.get(partida_id)
        if not partida:
            return {"ok": False, "status": "partida_inexistente", "partida_id": partida_id}

        self._inicializar_estado_partida(partida_id)
        for _ in range(max_rodadas):
            estado = self.obter_estado_partida(partida_id)
            if estado.get("status") == "finalizada":
                return estado
            self.simular_rodada(partida_id)

        estado = self.obter_estado_partida(partida_id)
        estado["status"] = "limite_rodadas"
        return estado

    def _criar_fila(self):
        return {
            "partida_id": uuid.uuid4().hex,
            "criado_em": time.time(),
            "jogadores": [],
            "pareada": False,
        }

    def _obter_fila(self, set_escolhido):
        if set_escolhido not in self.filas:
            self.filas[set_escolhido] = self._criar_fila()
        return self.filas[set_escolhido]

    def entrar_na_fila(self, jogador, set_escolhido):
        fila = self._obter_fila(set_escolhido)
        if fila.get("pareada"):
            fila = self._criar_fila()
            self.filas[set_escolhido] = fila

        fila["jogadores"].append(jogador)
        return {
            "status": "na_fila",
            "set_escolhido": set_escolhido,
            "partida_id": fila["partida_id"],
            "jogadores_na_fila": len(fila["jogadores"]),
        }

    def atualizar_pareamento(self, set_escolhido, tamanho_partida=10, timeout_segundos=10):
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

    def cancelar_busca_fila(self, set_escolhido, player_id):
        fila = self.filas.get(set_escolhido)
        if not fila or fila.get("pareada"):
            return {
                "ok": False,
                "status": "fila_inexistente",
                "set_escolhido": set_escolhido,
            }

        fila["jogadores"] = [j for j in fila["jogadores"] if j.player_id != player_id]
        if not fila["jogadores"]:
            del self.filas[set_escolhido]
            return {
                "ok": True,
                "status": "fila_cancelada",
                "set_escolhido": set_escolhido,
                "fila_reiniciada": True,
            }

        return {
            "ok": True,
            "status": "saida_fila_registrada",
            "set_escolhido": set_escolhido,
            "jogadores_na_fila": len(fila["jogadores"]),
            "fila_reiniciada": False,
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
        partida["jogadores"] = [j for j in jogadores if j["player_id"] != player_id]
        jogadores = partida["jogadores"]

        jogadores_reais = [
            jogador
            for jogador in jogadores
            if not jogador.get("is_bot", False) and jogador.get("categoria") != "simulado"
        ]

        removeu_partida = len(jogadores_reais) == 0
        if removeu_partida:
            del self.partidas_ativas[partida_id]
            for set_escolhido, fila in list(self.filas.items()):
                if fila.get("partida_id") == partida_id:
                    del self.filas[set_escolhido]

        return {
            "ok": True,
            "status": "saida_registrada",
            "partida_id": partida_id,
            "partida_apagada": removeu_partida,
        }


gerenciador_partidas = GerenciadorPartidas()
