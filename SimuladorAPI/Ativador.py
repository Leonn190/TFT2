import random
from copy import deepcopy

from SimuladorAPI.teste import criar_cartas_teste


class Ativador:
    def __init__(self):
        self._partidas = {}
        self.ping_ms = 35
        self._proximo_uid_carta = 1

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
            "mapa": [
                {"slot_id": slot_id, "desbloqueado": slot_id == 0, "carta": None}
                for slot_id in range(15)
            ],
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
        if len(estado_jogador["banco"]) >= 10:
            return False, "banco_cheio"

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
    def _sinergias_carta(carta):
        sinergias = [carta.get("sinergia", "-")]
        sinergia_secundaria = carta.get("sinergia_secundaria")
        if sinergia_secundaria:
            sinergias.append(sinergia_secundaria)
        return {sinergia for sinergia in sinergias if sinergia and sinergia != "-"}

    @classmethod
    def _calcular_sinergias(cls, mapa):
        contador = {}
        slot_por_id = {slot.get("slot_id"): slot for slot in mapa}

        for slot in mapa:
            carta = slot.get("carta")
            if carta is None:
                continue
            for sinergia in cls._sinergias_carta(carta):
                contador[sinergia] = contador.get(sinergia, 0) + 1

        for slot in mapa:
            carta = slot.get("carta")
            if carta is None:
                continue

            slot_id = slot.get("slot_id", -1)
            linha = slot_id // 5
            coluna = slot_id % 5
            sinergias_carta = cls._sinergias_carta(carta)
            if not sinergias_carta:
                continue

            for dl, dc in ((0, 1), (1, 0)):
                vizinho_linha = linha + dl
                vizinho_coluna = coluna + dc
                if vizinho_linha > 2 or vizinho_coluna > 4:
                    continue
                vizinho_id = vizinho_linha * 5 + vizinho_coluna
                slot_vizinho = slot_por_id.get(vizinho_id)
                if slot_vizinho is None or slot_vizinho.get("carta") is None:
                    continue

                compartilhadas = sinergias_carta.intersection(cls._sinergias_carta(slot_vizinho["carta"]))
                for sinergia in compartilhadas:
                    contador[sinergia] = contador.get(sinergia, 0) + 1

        return [{"sinergia": nome, "quantidade": qtd} for nome, qtd in sorted(contador.items(), key=lambda item: (-item[1], item[0]))]

    @staticmethod
    def _obter_slot_por_id(mapa, slot_id):
        return next((slot for slot in mapa if slot.get("slot_id") == slot_id), None)

    def _remover_carta_mapa_por_uid(self, estado_jogador, carta_uid):
        for slot in estado_jogador["mapa"]:
            carta = slot.get("carta")
            if carta is not None and carta.get("uid") == carta_uid:
                slot["carta"] = None
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
        del alvo_grupo_id
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        if not card_uids or len(card_uids) != 1:
            return False, "sem_cartas"

        cartas = self._retirar_cartas_por_uid(estado_jogador, card_uids)
        if cartas is None:
            return False, "carta_inexistente"

        slot_livre = next((slot for slot in estado_jogador["mapa"] if slot.get("desbloqueado") and slot.get("carta") is None), None)
        if slot_livre is None:
            estado_jogador["banco"].extend(cartas)
            return False, "sem_slot_livre"

        slot_livre["carta"] = cartas[0]

        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"

    def posicionar_do_banco(self, partida, player_id, indice_banco, q, r):
        del q, r
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        if indice_banco < 0 or indice_banco >= len(estado_jogador["banco"]):
            return False, "indice_invalido"

        return self.mover_banco_para_mapa(partida, player_id, indice_banco, slot_id=0)

    def mover_banco_para_mapa(self, partida, player_id, indice_banco, slot_id):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]

        if indice_banco < 0 or indice_banco >= len(estado_jogador["banco"]):
            return False, "indice_invalido"

        slot = self._obter_slot_por_id(estado_jogador["mapa"], slot_id)
        if slot is None:
            return False, "slot_inexistente"
        if not slot.get("desbloqueado"):
            return False, "slot_bloqueado"
        if slot.get("carta") is not None:
            return False, "slot_ocupado"

        slot["carta"] = estado_jogador["banco"].pop(indice_banco)
        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"

    def mover_mapa_para_banco(self, partida, player_id, slot_id):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]

        slot = self._obter_slot_por_id(estado_jogador["mapa"], slot_id)
        if slot is None:
            return False, "slot_inexistente"

        carta = slot.get("carta")
        if carta is None:
            return False, "slot_vazio"

        if len(estado_jogador["banco"]) >= 10:
            return False, "banco_cheio"

        slot["carta"] = None
        estado_jogador["banco"].append(carta)
        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"

ativador_global = Ativador()
