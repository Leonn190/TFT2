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

    @staticmethod
    def _sinergias_carta(carta):
        sinergias = {carta.get("sinergia", "-")}
        if carta.get("sinergia_secundaria"):
            sinergias.add(carta["sinergia_secundaria"])
        return sinergias

    def _sinergia_comum_selecao(self, selecao):
        comum = None
        for item in selecao:
            atual = self._sinergias_carta(item["carta"])
            comum = atual if comum is None else comum.intersection(atual)
        return sorted(comum)[0] if comum else None

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
            carta = entry["carta"]
            sinergias = [carta.get("sinergia", "-")]
            sinergia_secundaria = carta.get("sinergia_secundaria")
            if sinergia_secundaria:
                sinergias.append(sinergia_secundaria)

            for sinergia in sinergias:
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

    def mover_mapa_para_selecao(self, partida, player_id, q, r, indice_selecao):
        # Mantido por compatibilidade com chamadas antigas.
        return self.alternar_selecao_mapa(partida, player_id, q, r)

    def alternar_selecao_banco(self, partida, player_id, indice_banco):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        if indice_banco < 0 or indice_banco >= len(estado_jogador["banco"]):
            return False, "indice_invalido"

        selecao = estado_jogador["selecao"]
        for i, item in enumerate(selecao):
            if item["origem"] == "banco" and item["indice"] == indice_banco:
                del selecao[i]
                return True, "removido"

        if len(selecao) >= 3:
            return False, "selecao_cheia"

        novo_item = {"origem": "banco", "indice": indice_banco, "carta": deepcopy(estado_jogador["banco"][indice_banco])}
        if selecao and self._sinergia_comum_selecao(selecao + [novo_item]) is None:
            return False, "sinergia_invalida"

        selecao.append(novo_item)
        return True, "ok"

    def alternar_selecao_mapa(self, partida, player_id, q, r):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        indice_mapa = next((i for i, entry in enumerate(estado_jogador["mapa"]) if entry["q"] == q and entry["r"] == r), -1)
        if indice_mapa < 0:
            return False, "tropa_inexistente"

        selecao = estado_jogador["selecao"]
        for i, item in enumerate(selecao):
            if item["origem"] == "mapa" and item["indice"] == indice_mapa:
                del selecao[i]
                return True, "removido"

        if len(selecao) >= 3:
            return False, "selecao_cheia"

        novo_item = {"origem": "mapa", "indice": indice_mapa, "carta": deepcopy(estado_jogador["mapa"][indice_mapa]["carta"])}
        if selecao and self._sinergia_comum_selecao(selecao + [novo_item]) is None:
            return False, "sinergia_invalida"

        selecao.append(novo_item)
        return True, "ok"

    def posicionar_selecao_no_mapa(self, partida, player_id, q_base, r_base):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        selecao = estado_jogador["selecao"]
        if len(selecao) != 3:
            return False, "selecao_incompleta"

        sinergia = self._sinergia_comum_selecao(selecao)
        if sinergia is None:
            return False, "sinergia_invalida"

        ocupados = {(entry["q"], entry["r"]) for entry in estado_jogador["mapa"]}
        entradas_sinergia = [entry for entry in estado_jogador["mapa"] if sinergia in self._sinergias_carta(entry["carta"]) and entry["r"] == r_base]

        destino = []
        if entradas_sinergia:
            q_min = min(entry["q"] for entry in entradas_sinergia)
            q_max = max(entry["q"] for entry in entradas_sinergia)
            tentativa_direita = [(q_max + i + 1, r_base) for i in range(3)]
            if all(0 <= q < 12 and 0 <= r_base < 8 and (q, r_base) not in ocupados for q, _ in tentativa_direita):
                destino = tentativa_direita
            else:
                tentativa_esquerda = [(q_min - i - 1, r_base) for i in range(3)]
                tentativa_esquerda.reverse()
                if all(0 <= q < 12 and 0 <= r_base < 8 and (q, r_base) not in ocupados for q, _ in tentativa_esquerda):
                    destino = tentativa_esquerda
        else:
            q_inicio = max(0, min(9, q_base - 1))
            tentativa = [(q_inicio + i, r_base) for i in range(3)]
            if all(0 <= q < 12 and 0 <= r_base < 8 and (q, r_base) not in ocupados for q, _ in tentativa):
                destino = tentativa

        if len(destino) != 3:
            return False, "sem_espaco"

        indices_banco = sorted([item["indice"] for item in selecao if item["origem"] == "banco"], reverse=True)
        for indice in indices_banco:
            if indice >= len(estado_jogador["banco"]):
                return False, "indice_invalido"

        cartas_posicionadas = []
        for item in selecao:
            if item["origem"] == "banco":
                cartas_posicionadas.append(deepcopy(estado_jogador["banco"][item["indice"]]))
            else:
                cartas_posicionadas.append(deepcopy(item["carta"]))

        for indice in indices_banco:
            estado_jogador["banco"].pop(indice)

        for carta, (q, r) in zip(cartas_posicionadas, destino):
            estado_jogador["mapa"].append({"carta": carta, "q": q, "r": r})

        estado_jogador["selecao"] = []
        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"


ativador_global = Ativador()
