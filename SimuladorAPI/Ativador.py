import random
from copy import deepcopy

from SimuladorAPI.teste import criar_cartas_teste, criar_estoque_por_raridade


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

        regras_partida = deepcopy(getattr(partida, "regras", {}) or {})
        set_escolhido = getattr(partida, "set_escolhido", "BrawlStars") or "BrawlStars"

        cartas_base = criar_cartas_teste(set_escolhido=set_escolhido, regras=regras_partida)
        estoque = criar_estoque_por_raridade(cartas_base, regras=regras_partida)
        catalogo = {carta["id"]: carta for carta in cartas_base}

        self._partidas[partida_id] = {
            "catalogo": catalogo,
            "estoque": estoque,
            "jogadores": {},
            "regras": regras_partida,
        }

        for jogador in partida.jogadores:
            self._partidas[partida_id]["jogadores"][jogador.player_id] = self._estado_inicial_jogador(partida_id)

        for jogador in partida.jogadores:
            estado = self._partidas[partida_id]["jogadores"][jogador.player_id]
            self._atualizar_progresso_jogador(partida_id, estado)
            raridades_bloqueadas = set(self._obter_regra_partida(partida_id, "raridades_bloqueadas_banco_inicial", ["epico", "lendario", "mitico"]))
            estado["banco"] = self._comprar_cartas_estoque(partida_id, quantidade=3, raridades_bloqueadas=raridades_bloqueadas)
            estado["loja"] = self._comprar_cartas_estoque(partida_id, quantidade=3, chances_loja=estado.get("chances_loja"))

    def _estado_inicial_jogador(self, partida_id):
        return {
            "vida": 100,
            "ouro": 1000,
            "banco": [],
            "loja": [],
            "mapa": [
                {"slot_id": slot_id, "desbloqueado": slot_id == 0, "custo_desbloqueio": 0 if slot_id == 0 else None, "carta": None}
                for slot_id in range(15)
            ],
            "batalhas_finalizadas": 0,
            "selecao": [],
            "sinergias": [],
            "slots_adquiridos": 1,
            "chances_loja": self._obter_chances_loja_por_slots(partida_id, 1),
        }

    @staticmethod
    def _custo_coluna_mapa(coluna):
        custos = {1: 10, 2: 15, 3: 20, 4: 25}
        return custos.get(coluna)

    def _configurar_slots_pos_batalha(self, estado_jogador):
        for slot in estado_jogador["mapa"]:
            slot_id = slot.get("slot_id", 0)
            coluna = slot_id % 5
            if coluna == 0:
                slot["desbloqueado"] = True
                slot["custo_desbloqueio"] = 0
            else:
                slot["desbloqueado"] = False
                slot["custo_desbloqueio"] = self._custo_coluna_mapa(coluna) if coluna == 1 else None

    @staticmethod
    def _contar_slots_adquiridos(estado_jogador):
        return sum(1 for slot in estado_jogador["mapa"] if slot.get("desbloqueado"))

    def _obter_regra_partida(self, partida_id, chave, padrao=None):
        return self._partidas.get(partida_id, {}).get("regras", {}).get(chave, padrao)

    def _obter_tabela_chances_loja(self, partida_id):
        tabela = self._obter_regra_partida(partida_id, "chances_loja_por_slots", {})
        return tabela if isinstance(tabela, dict) and tabela else {
            1: {"comum": 80, "incomum": 15, "raro": 5, "epico": 0, "lendario": 0, "mitico": 0},
            15: {"comum": 8, "incomum": 9, "raro": 10, "epico": 16, "lendario": 32, "mitico": 25},
        }

    def _obter_chances_loja_por_slots(self, partida_id, slots_adquiridos):
        tabela_chances = self._obter_tabela_chances_loja(partida_id)
        slots_normalizados = max(1, min(15, int(slots_adquiridos)))
        if slots_normalizados == 2:
            slots_normalizados = 3
        chave_maxima = max(tabela_chances.keys())
        return deepcopy(tabela_chances.get(slots_normalizados, tabela_chances[chave_maxima]))

    def _atualizar_progresso_jogador(self, partida_id, estado_jogador):
        slots_adquiridos = self._contar_slots_adquiridos(estado_jogador)
        estado_jogador["slots_adquiridos"] = slots_adquiridos
        estado_jogador["chances_loja"] = self._obter_chances_loja_por_slots(partida_id, slots_adquiridos)

    @staticmethod
    def _raridade_carta(carta):
        return str(Ativador._obter_campo(carta, "raridade", "comum")).strip().lower()

    def _sortear_raridade_loja(self, chances):
        if not chances:
            return "comum"
        raridades = list(chances.keys())
        pesos = [max(0, int(chances[raridade])) for raridade in raridades]
        if sum(pesos) <= 0:
            return "comum"
        return random.choices(raridades, weights=pesos, k=1)[0]

    def _clonar_carta_catalogo(self, carta):
        clone = deepcopy(carta)
        clone["uid"] = self._proximo_uid_carta
        self._proximo_uid_carta += 1
        return clone

    def _comprar_cartas_estoque(self, partida_id, quantidade, chances_loja=None, raridades_bloqueadas=None):
        partida_estado = self._partidas[partida_id]
        raridades_bloqueadas = {str(r).strip().lower() for r in (raridades_bloqueadas or set())}
        cartas = []
        for _ in range(quantidade):
            disponiveis = [
                cid
                for cid, qtd in partida_estado["estoque"].items()
                if qtd > 0 and self._raridade_carta(partida_estado["catalogo"].get(cid, {})) not in raridades_bloqueadas
            ]
            if not disponiveis:
                break

            carta_id = None
            if chances_loja:
                raridade_escolhida = self._sortear_raridade_loja(chances_loja)
                disponiveis_raridade = [
                    cid
                    for cid in disponiveis
                    if self._raridade_carta(partida_estado["catalogo"].get(cid, {})) == raridade_escolhida
                ]
                if disponiveis_raridade:
                    carta_id = random.choice(disponiveis_raridade)

            if carta_id is None:
                carta_id = random.choice(disponiveis)

            partida_estado["estoque"][carta_id] -= 1
            base = self._clonar_carta_catalogo(partida_estado["catalogo"][carta_id])
            cartas.append(base)
        return cartas

    @staticmethod
    def _obter_campo(carta, campo, padrao=None):
        if carta is None:
            return padrao
        if isinstance(carta, dict):
            return carta.get(campo, padrao)
        return getattr(carta, campo, padrao)

    def _devolver_ao_estoque(self, partida_id, carta):
        carta_id = self._obter_campo(carta, "id")
        if carta_id in self._partidas[partida_id]["estoque"]:
            self._partidas[partida_id]["estoque"][carta_id] += 1

    def sincronizar_partida(self, partida, player_local_id="local-1"):
        self._inicializar_partida(partida)
        partida_id = self._chave(partida)
        estado = self._partidas[partida_id]

        for jogador in partida.jogadores:
            dados = estado["jogadores"].setdefault(jogador.player_id, self._estado_inicial_jogador(partida_id))
            self._atualizar_progresso_jogador(partida_id, dados)
            jogador.vida = dados["vida"]
            jogador.ouro = dados["ouro"]
            jogador.banco = deepcopy(dados["banco"])
            jogador.loja = deepcopy(dados["loja"])
            jogador.mapa = deepcopy(dados["mapa"])
            jogador.selecao = deepcopy(dados["selecao"])
            jogador.sinergias = deepcopy(dados["sinergias"])
            jogador.slots_adquiridos = dados.get("slots_adquiridos", 1)
            jogador.chances_loja = deepcopy(dados.get("chances_loja", self._obter_chances_loja_por_slots(partida_id, 1)))

        self.atualizar_outros_players(partida, player_local_id)
        partida.ping_ms = self.ping_ms
        partida.estoque_compartilhado = deepcopy(estado["estoque"])
        return partida

    def atualizar_outros_players(self, partida, player_local_id="local-1"):
        return

    def comprar_carta_loja(self, partida, player_id, indice_loja):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        if indice_loja < 0 or indice_loja >= len(estado_jogador["loja"]):
            return False, "indice_invalido"
        carta = estado_jogador["loja"][indice_loja]
        custo = self._obter_campo(carta, "custo", 3)
        if estado_jogador["ouro"] < custo:
            return False, "ouro_insuficiente"
        if len(estado_jogador["banco"]) >= 10:
            return False, "banco_cheio"

        estado_jogador["ouro"] -= custo
        estado_jogador["banco"].append(deepcopy(carta))
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
        self._atualizar_progresso_jogador(estado_jogador)
        estado_jogador["loja"] = self._comprar_cartas_estoque(partida_id, quantidade=3, chances_loja=estado_jogador.get("chances_loja"))
        return True, "ok"

    def _slot_pode_desbloquear(self, mapa, slot):
        slot_id = slot.get("slot_id", -1)
        coluna = slot_id % 5
        if coluna <= 0:
            return False
        slot_anterior = self._obter_slot_por_id(mapa, slot_id - 1)
        return bool(slot_anterior and slot_anterior.get("desbloqueado"))

    def _desbloquear_slot(self, estado_jogador, slot):
        if slot.get("desbloqueado"):
            return True, "ok"

        if not self._slot_pode_desbloquear(estado_jogador["mapa"], slot):
            return False, "desbloqueio_progressivo"

        custo = slot.get("custo_desbloqueio")
        if custo is None:
            return False, "slot_bloqueado"
        if estado_jogador["ouro"] < custo:
            return False, "ouro_insuficiente"

        estado_jogador["ouro"] -= custo
        slot["desbloqueado"] = True
        proximo_slot = self._obter_slot_por_id(estado_jogador["mapa"], slot.get("slot_id", -1) + 1)
        if proximo_slot is not None and not proximo_slot.get("desbloqueado") and proximo_slot.get("custo_desbloqueio") is None:
            proximo_slot["custo_desbloqueio"] = self._custo_coluna_mapa(proximo_slot.get("slot_id", 0) % 5)

        self._atualizar_progresso_jogador(estado_jogador)
        return True, "ok"

    def desbloquear_slot_mapa(self, partida, player_id, slot_id):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        slot = self._obter_slot_por_id(estado_jogador["mapa"], slot_id)
        if slot is None:
            return False, "slot_inexistente"
        return self._desbloquear_slot(estado_jogador, slot)

    def vender_do_banco(self, partida, player_id, indice_banco):
        self._inicializar_partida(partida)
        partida_id = self._chave(partida)
        estado_jogador = self._partidas[partida_id]["jogadores"][player_id]
        if indice_banco < 0 or indice_banco >= len(estado_jogador["banco"]):
            return False, "indice_invalido"

        carta = estado_jogador["banco"].pop(indice_banco)
        carta_dict = carta.para_dict() if hasattr(carta, "para_dict") else carta
        estado_jogador["ouro"] += self._obter_campo(carta_dict, "custo", 1)
        self._devolver_ao_estoque(partida_id, carta_dict)
        return True, "ok"

    @classmethod
    def _sinergias_carta(cls, carta):
        sinergias = []
        for campo in ("sinergia", "sinergia_secundaria", "sinergia_terciaria", "sinergia_quaternaria"):
            valor = cls._obter_campo(carta, campo)
            if valor and valor != "-":
                sinergias.append(str(valor))
        extras = cls._obter_campo(carta, "sinergias", [])
        if isinstance(extras, (list, tuple)):
            for item in extras:
                if item and item != "-":
                    sinergias.append(str(item))
        return set(sinergias)

    @classmethod
    def _calcular_sinergias(cls, mapa):
        contador = {}
        slot_por_id = {slot.get("slot_id"): slot for slot in mapa}
        vistos_por_sinergia = {}

        for slot in mapa:
            carta = slot.get("carta")
            if carta is None:
                continue
            carta_id = cls._obter_campo(carta, "id")
            for sinergia in cls._sinergias_carta(carta):
                ids = vistos_por_sinergia.setdefault(sinergia, set())
                if carta_id not in ids:
                    ids.add(carta_id)
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
                carta_vizinha = slot_vizinho.get("carta") if slot_vizinho else None
                if carta_vizinha is None:
                    continue
                if cls._obter_campo(carta, "id") == cls._obter_campo(carta_vizinha, "id"):
                    continue

                compartilhadas = sinergias_carta.intersection(cls._sinergias_carta(carta_vizinha))
                for sinergia in compartilhadas:
                    contador[sinergia] = contador.get(sinergia, 0) + 1

        return [{"sinergia": nome, "quantidade": qtd} for nome, qtd in sorted(contador.items(), key=lambda item: (-item[1], item[0]))]

    @staticmethod
    def _obter_slot_por_id(mapa, slot_id):
        return next((slot for slot in mapa if slot.get("slot_id") == slot_id), None)

    def _remover_carta_mapa_por_uid(self, estado_jogador, carta_uid):
        for slot in estado_jogador["mapa"]:
            carta = slot.get("carta")
            uid = self._obter_campo(carta, "uid")
            if carta is not None and uid == carta_uid:
                slot["carta"] = None
                return carta
        return None

    def _retirar_cartas_por_uid(self, estado_jogador, card_uids):
        retiradas = []
        restantes = list(card_uids)

        for uid in list(restantes):
            indice_banco = next((i for i, carta in enumerate(estado_jogador["banco"]) if self._obter_campo(carta, "uid") == uid), -1)
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
            ok, motivo = self._desbloquear_slot(estado_jogador, slot)
            if not ok:
                return False, motivo

        carta_banco = estado_jogador["banco"][indice_banco]
        carta_slot = slot.get("carta")

        if carta_slot is None:
            slot["carta"] = estado_jogador["banco"].pop(indice_banco)
        else:
            slot["carta"] = carta_banco
            estado_jogador["banco"][indice_banco] = carta_slot

        estado_jogador["sinergias"] = self._calcular_sinergias(estado_jogador["mapa"])
        return True, "ok"

    def mover_mapa_para_mapa(self, partida, player_id, slot_origem_id, slot_destino_id):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]

        slot_origem = self._obter_slot_por_id(estado_jogador["mapa"], slot_origem_id)
        slot_destino = self._obter_slot_por_id(estado_jogador["mapa"], slot_destino_id)
        if slot_origem is None or slot_destino is None:
            return False, "slot_inexistente"

        if not slot_destino.get("desbloqueado"):
            ok, motivo = self._desbloquear_slot(estado_jogador, slot_destino)
            if not ok:
                return False, motivo

        carta_origem = slot_origem.get("carta")
        if carta_origem is None:
            return False, "slot_origem_vazio"

        carta_destino = slot_destino.get("carta")
        slot_origem["carta"] = carta_destino
        slot_destino["carta"] = carta_origem

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


    def registrar_fim_batalha(self, partida, player_id):
        self._inicializar_partida(partida)
        estado_jogador = self._partidas[self._chave(partida)]["jogadores"][player_id]
        estado_jogador["batalhas_finalizadas"] = estado_jogador.get("batalhas_finalizadas", 0) + 1
        if estado_jogador["batalhas_finalizadas"] == 1:
            self._configurar_slots_pos_batalha(estado_jogador)
        self._atualizar_progresso_jogador(estado_jogador)
        return True, "ok"

ativador_global = Ativador()
