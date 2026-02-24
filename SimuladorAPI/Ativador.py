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

    @staticmethod
    def _eh_adjacente(origem, destino):
        q1, r1 = origem
        q2, r2 = destino
        deltas_validos = {(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)}
        return (q2 - q1, r2 - r1) in deltas_validos

    @staticmethod
    def _em_reta_hex(posicoes):
        if len(posicoes) <= 2:
            return True
        qs = {q for q, _ in posicoes}
        rs = {r for _, r in posicoes}
        ss = {q + r for q, r in posicoes}
        return len(qs) == 1 or len(rs) == 1 or len(ss) == 1

    @staticmethod
    def _calcular_sinergias(mapa):
        contador = {}
        for entry in mapa:
            sinergia = entry["carta"].get("sinergia", "-")
            contador[sinergia] = contador.get(sinergia, 0) + 1
        return [{"sinergia": nome, "quantidade": qtd} for nome, qtd in sorted(contador.items(), key=lambda item: (-item[1], item[0]))]

    def posicionar_do_banco(self, partida, player_id, indice_banco, q, r):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]

        if indice_banco < 0 or indice_banco >= len(estado_jogador["banco"]):
            return False, "indice_invalido"

        if any(entry["q"] == q and entry["r"] == r for entry in estado_jogador["mapa"]):
            return False, "slot_ocupado"

        carta = estado_jogador["banco"][indice_banco]
        sinergia = carta.get("sinergia", "-")
        entradas_mesma_sinergia = [entry for entry in estado_jogador["mapa"] if entry["carta"].get("sinergia", "-") == sinergia]

        if estado_jogador["mapa"]:
            if not any(self._eh_adjacente((entry["q"], entry["r"]), (q, r)) and entry["carta"].get("sinergia", "-") == sinergia for entry in estado_jogador["mapa"]):
                return False, "sinergia_desconectada"

        if entradas_mesma_sinergia:
            if not any(self._eh_adjacente((entry["q"], entry["r"]), (q, r)) for entry in entradas_mesma_sinergia):
                return False, "nao_adj_mesma_sinergia"

            posicoes = [(entry["q"], entry["r"]) for entry in entradas_mesma_sinergia] + [(q, r)]
            if not self._em_reta_hex(posicoes):
                return False, "fora_da_reta"

        estado_jogador["banco"].pop(indice_banco)
        estado_jogador["mapa"].append({"carta": carta, "q": q, "r": r})
        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"


ativador_global = Ativador()
