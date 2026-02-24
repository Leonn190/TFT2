import random
from copy import deepcopy

from SimuladorAPI.teste import criar_cartas_teste


class Ativador:
    def __init__(self):
        self._partidas = {}
        self.ping_ms = 35

    def definir_ping(self, ping_ms):
        self.ping_ms = max(0, int(ping_ms))

    def _chave(self, partida):
        return partida.partida_id

    def _inicializar_partida(self, partida):
        partida_id = self._chave(partida)
        if partida_id in self._partidas:
            return

        cartas_base = criar_cartas_teste()
        estoque = {carta["id"]: 5 for carta in cartas_base}
        catalogo = {carta["id"]: carta for carta in cartas_base}

        self._partidas[partida_id] = {
            "catalogo": catalogo,
            "estoque": estoque,
            "jogadores": {},
        }

        for jogador in partida.jogadores:
            self._partidas[partida_id]["jogadores"][jogador.player_id] = self._estado_inicial_jogador()

        for jogador in partida.jogadores:
            estado = self._partidas[partida_id]["jogadores"][jogador.player_id]
            estado["banco"] = self._comprar_cartas_estoque(partida_id, quantidade=6)
            estado["loja"] = self._comprar_cartas_estoque(partida_id, quantidade=3)

    def _estado_inicial_jogador(self):
        return {
            "vida": 100,
            "ouro": 20,
            "banco": [],
            "loja": [],
            "mapa": [],
            "selecao": [],
            "sinergias": [],
        }

    def _comprar_cartas_estoque(self, partida_id, quantidade):
        partida_estado = self._partidas[partida_id]
        cartas = []
        for _ in range(quantidade):
            disponiveis = [cid for cid, qtd in partida_estado["estoque"].items() if qtd > 0]
            if not disponiveis:
                break
            carta_id = random.choice(disponiveis)
            partida_estado["estoque"][carta_id] -= 1
            cartas.append(deepcopy(partida_estado["catalogo"][carta_id]))
        return cartas

    def _devolver_ao_estoque(self, partida_id, carta):
        self._partidas[partida_id]["estoque"][carta["id"]] += 1

    def sincronizar_partida(self, partida, player_local_id="local-1"):
        self._inicializar_partida(partida)
        partida_id = self._chave(partida)
        estado = self._partidas[partida_id]

        for jogador in partida.jogadores:
            dados = estado["jogadores"].setdefault(jogador.player_id, self._estado_inicial_jogador())
            jogador.vida = dados["vida"]
            jogador.ouro = dados["ouro"]
            jogador.banco = deepcopy(dados["banco"])
            jogador.loja = deepcopy(dados["loja"])
            jogador.mapa = deepcopy(dados["mapa"])
            jogador.selecao = deepcopy(dados["selecao"])
            jogador.sinergias = deepcopy(dados["sinergias"])

        self.atualizar_outros_players(partida, player_local_id)
        partida.ping_ms = self.ping_ms
        partida.estoque_compartilhado = deepcopy(estado["estoque"])
        return partida

    def atualizar_outros_players(self, partida, player_local_id="local-1"):
        partida_id = self._chave(partida)
        estado = self._partidas[partida_id]
        for jogador in partida.jogadores:
            if jogador.player_id == player_local_id:
                continue
            dados = estado["jogadores"][jogador.player_id]
            dados["ouro"] = max(0, min(50, dados["ouro"] + random.randint(-1, 2)))
            if random.random() < 0.05:
                dados["vida"] = max(1, dados["vida"] - 1)

    def comprar_carta_loja(self, partida, player_id, indice_loja):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        if indice_loja < 0 or indice_loja >= len(estado_jogador["loja"]):
            return False, "indice_invalido"
        carta = estado_jogador["loja"][indice_loja]
        custo = carta.get("custo", 3)
        if estado_jogador["ouro"] < custo:
            return False, "ouro_insuficiente"
        estado_jogador["ouro"] -= custo
        estado_jogador["banco"].append(carta)
        del estado_jogador["loja"][indice_loja]
        return True, "ok"

    def roletar_loja(self, partida, player_id, custo=2):
        self._inicializar_partida(partida)
        partida_id = self._chave(partida)
        estado_jogador = self._partidas[partida_id]["jogadores"][player_id]
        if estado_jogador["ouro"] < custo:
            return False, "ouro_insuficiente"

        estado_jogador["ouro"] -= custo
        for carta in estado_jogador["loja"]:
            self._devolver_ao_estoque(partida_id, carta)
        estado_jogador["loja"] = self._comprar_cartas_estoque(partida_id, quantidade=3)
        return True, "ok"

    def vender_do_banco(self, partida, player_id, indice_banco, retorno_ouro=1):
        self._inicializar_partida(partida)
        partida_id = self._chave(partida)
        estado_jogador = self._partidas[partida_id]["jogadores"][player_id]
        if indice_banco < 0 or indice_banco >= len(estado_jogador["banco"]):
            return False, "indice_invalido"

        carta = estado_jogador["banco"].pop(indice_banco)
        estado_jogador["ouro"] += retorno_ouro
        self._devolver_ao_estoque(partida_id, carta)
        return True, "ok"


ativador_global = Ativador()
