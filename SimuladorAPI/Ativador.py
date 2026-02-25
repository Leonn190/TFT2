import random
from copy import deepcopy

from SimuladorAPI.teste import criar_cartas_teste


class Ativador:
    def __init__(self):
        self._partidas = {}
        self.ping_ms = 35
        self._proximo_uid_carta = 1
        self._proximo_uid_grupo = 1

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

    def _clonar_carta_catalogo(self, carta):
        clone = deepcopy(carta)
        clone["uid"] = self._proximo_uid_carta
        self._proximo_uid_carta += 1
        return clone

    def _comprar_cartas_estoque(self, partida_id, quantidade):
        partida_estado = self._partidas[partida_id]
        cartas = []
        for _ in range(quantidade):
            disponiveis = [cid for cid, qtd in partida_estado["estoque"].items() if qtd > 0]
            if not disponiveis:
                break
            carta_id = random.choice(disponiveis)
            partida_estado["estoque"][carta_id] -= 1
            cartas.append(self._clonar_carta_catalogo(partida_estado["catalogo"][carta_id]))
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
        for grupo in mapa:
            for carta in grupo.get("cartas", []):
                sinergias = [carta.get("sinergia", "-")]
                sinergia_secundaria = carta.get("sinergia_secundaria")
                if sinergia_secundaria:
                    sinergias.append(sinergia_secundaria)

                for sinergia in sinergias:
                    contador[sinergia] = contador.get(sinergia, 0) + 1
        return [{"sinergia": nome, "quantidade": qtd} for nome, qtd in sorted(contador.items(), key=lambda item: (-item[1], item[0]))]

    @staticmethod
    def _sinergias_da_carta(carta):
        sinergias = {carta.get("sinergia", "-")}
        secundaria = carta.get("sinergia_secundaria")
        if secundaria:
            sinergias.add(secundaria)
        return sinergias

    def _remover_carta_mapa_por_uid(self, estado_jogador, carta_uid):
        for grupo in list(estado_jogador["mapa"]):
            for indice, carta in enumerate(grupo.get("cartas", [])):
                if carta.get("uid") == carta_uid:
                    grupo["cartas"].pop(indice)
                    if not grupo["cartas"]:
                        estado_jogador["mapa"].remove(grupo)
                    return carta
        return None

    def _retirar_cartas_por_uid(self, estado_jogador, card_uids):
        retiradas = []
        restantes = list(card_uids)

        for uid in list(restantes):
            indice_banco = next((i for i, carta in enumerate(estado_jogador["banco"]) if carta.get("uid") == uid), -1)
            if indice_banco >= 0:
                retiradas.append(estado_jogador["banco"].pop(indice_banco))
                restantes.remove(uid)

        for uid in list(restantes):
            carta = self._remover_carta_mapa_por_uid(estado_jogador, uid)
            if carta is not None:
                retiradas.append(carta)
                restantes.remove(uid)

        if restantes:
            return None
        return retiradas

    def alocar_cartas_sinergia(self, partida, player_id, card_uids, alvo_grupo_id=None):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        if not card_uids:
            return False, "sem_cartas"

        cartas = self._retirar_cartas_por_uid(estado_jogador, card_uids)
        if cartas is None:
            return False, "carta_inexistente"

        if alvo_grupo_id is not None:
            grupo = next((item for item in estado_jogador["mapa"] if item.get("grupo_id") == alvo_grupo_id), None)
            if grupo is None:
                estado_jogador["banco"].extend(cartas)
                return False, "grupo_inexistente"
            sinergia_alvo = grupo.get("sinergia", "-")
            if not all(sinergia_alvo in self._sinergias_da_carta(carta) for carta in cartas):
                estado_jogador["banco"].extend(cartas)
                return False, "sinergia_invalida"
            grupo["cartas"].extend(cartas)
        else:
            if len(cartas) < 3:
                estado_jogador["banco"].extend(cartas)
                return False, "minimo_tres_cartas"

            sinergia_comum = set.intersection(*(self._sinergias_da_carta(carta) for carta in cartas))
            sinergia_comum.discard("-")
            if not sinergia_comum:
                estado_jogador["banco"].extend(cartas)
                return False, "sem_sinergia_comum"

            grupo = {
                "grupo_id": self._proximo_uid_grupo,
                "sinergia": sorted(sinergia_comum)[0],
                "cartas": cartas,
            }
            self._proximo_uid_grupo += 1
            estado_jogador["mapa"].append(grupo)

        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"

    def posicionar_do_banco(self, partida, player_id, indice_banco, q, r):
        del q, r
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        if indice_banco < 0 or indice_banco >= len(estado_jogador["banco"]):
            return False, "indice_invalido"

        carta = estado_jogador["banco"][indice_banco]
        carta_uid = carta.get("uid")
        grupos_compativeis = [
            grupo for grupo in estado_jogador["mapa"] if grupo.get("sinergia", "-") in self._sinergias_da_carta(carta)
        ]
        if not grupos_compativeis:
            return False, "minimo_tres_cartas"
        return self.alocar_cartas_sinergia(partida, player_id, [carta_uid], alvo_grupo_id=grupos_compativeis[0].get("grupo_id"))

    def mover_mapa_para_selecao(self, partida, player_id, carta_uid, indice_selecao):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]

        if indice_selecao < 0 or indice_selecao >= 1:
            return False, "slot_bloqueado"

        carta = None
        for grupo in estado_jogador["mapa"]:
            carta = next((item for item in grupo.get("cartas", []) if item.get("uid") == carta_uid), None)
            if carta is not None:
                break
        if carta is None:
            return False, "tropa_inexistente"

        while len(estado_jogador["selecao"]) < 5:
            estado_jogador["selecao"].append(None)

        if estado_jogador["selecao"][indice_selecao] is not None:
            return False, "slot_ocupado"

        estado_jogador["selecao"][indice_selecao] = deepcopy(carta)
        # A seleção apenas referencia a tropa escolhida; ela continua no mapa e nas sinergias.
        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"


ativador_global = Ativador()
