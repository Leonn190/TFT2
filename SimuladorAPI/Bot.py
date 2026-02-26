import random
from copy import deepcopy


class Player:
    CATEGORIA_PLAYER = "player"
    CATEGORIA_SIMULADO = "simulado"
    CATEGORIA_BOT = "bot"

    def __init__(self, player_id, nome, set_escolhido=None, is_bot=False, categoria=None):
        self.player_id = player_id
        self.nome = nome
        self.set_escolhido = set_escolhido
        self.is_bot = is_bot
        self.categoria = categoria or (self.CATEGORIA_BOT if is_bot else self.CATEGORIA_SIMULADO)

    def para_json(self):
        return {
            "player_id": self.player_id,
            "nome": self.nome,
            "set_escolhido": self.set_escolhido,
            "is_bot": self.is_bot,
            "categoria": self.categoria,
        }


class Bot(Player):
    def __init__(self, player_id, nome, set_escolhido=None):
        super().__init__(
            player_id=player_id,
            nome=nome,
            set_escolhido=set_escolhido,
            is_bot=True,
            categoria=Player.CATEGORIA_BOT,
        )

    @staticmethod
    def gerar_loja(catalogo, quantidade=5):
        if not catalogo:
            return []
        return [deepcopy(random.choice(catalogo)) for _ in range(quantidade)]

    @staticmethod
    def sinergias_ativas(tabuleiro):
        contador = {}
        for carta in tabuleiro:
            for sinergia in carta.get("sinergias", []):
                if sinergia and sinergia != "-":
                    contador[sinergia] = contador.get(sinergia, 0) + 1
        return {nome: qtd for nome, qtd in contador.items() if qtd >= 2}

    @staticmethod
    def _sinergias_carta(carta):
        sinergias = []
        if not isinstance(carta, dict):
            return sinergias

        for campo in ("sinergia", "sinergia_secundaria", "sinergia_terciaria", "sinergia_quaternaria"):
            valor = carta.get(campo)
            if valor and valor != "-":
                sinergias.append(str(valor))

        for valor in carta.get("sinergias", []):
            if valor and valor != "-":
                sinergias.append(str(valor))

        return sinergias

    @classmethod
    def _pontuacao_sinergia(cls, carta, sinergias_atuais):
        pontuacao = 0
        for sinergia in cls._sinergias_carta(carta):
            quantidade_atual = sinergias_atuais.get(sinergia, 0)
            if quantidade_atual >= 2:
                pontuacao += 4
            elif quantidade_atual == 1:
                pontuacao += 8
            else:
                pontuacao += 2
        return pontuacao

    def jogar_turno(self, ativador, partida, player_id):
        estado = ativador._partidas[ativador._chave(partida)]["jogadores"].get(player_id)
        if estado is None:
            return False, "jogador_inexistente"

        if not estado.get("loja"):
            ativador.roletar_loja(partida, player_id, custo=0)

        cartas_em_campo = [slot.get("carta") for slot in estado.get("mapa", []) if slot.get("carta") is not None]
        sinergias_atuais = {}
        for carta in cartas_em_campo:
            for sinergia in self._sinergias_carta(carta):
                sinergias_atuais[sinergia] = sinergias_atuais.get(sinergia, 0) + 1

        compras_realizadas = 0
        while estado.get("loja") and len(estado.get("banco", [])) < 10 and compras_realizadas < 3:
            candidatos = []
            for indice, carta in enumerate(estado["loja"]):
                custo = int(carta.get("custo", 999))
                if custo > estado.get("ouro", 0):
                    continue
                candidatos.append((self._pontuacao_sinergia(carta, sinergias_atuais), -custo, indice))

            if not candidatos:
                break

            candidatos.sort(reverse=True)
            _, _, indice_escolhido = candidatos[0]
            ok, _ = ativador.comprar_carta_loja(partida, player_id, indice_escolhido)
            if not ok:
                break

            compras_realizadas += 1
            carta_comprada = estado["banco"][-1] if estado.get("banco") else None
            for sinergia in self._sinergias_carta(carta_comprada):
                sinergias_atuais[sinergia] = sinergias_atuais.get(sinergia, 0) + 1

        while True:
            slot_livre = next((slot for slot in estado["mapa"] if slot.get("desbloqueado") and slot.get("carta") is None), None)
            if slot_livre is not None:
                break

            slot_desbloqueavel = next(
                (
                    slot for slot in estado["mapa"]
                    if (not slot.get("desbloqueado"))
                    and slot.get("custo_desbloqueio") is not None
                    and ativador._slot_pode_desbloquear(estado["mapa"], slot)
                    and estado["ouro"] >= slot.get("custo_desbloqueio", 0)
                ),
                None,
            )
            if slot_desbloqueavel is None:
                break
            ativador.desbloquear_slot_mapa(partida, player_id, slot_desbloqueavel.get("slot_id", -1))

        while estado.get("banco"):
            slot_livre = next((slot for slot in estado["mapa"] if slot.get("desbloqueado") and slot.get("carta") is None), None)
            if slot_livre is None:
                break

            melhor_indice = max(
                range(len(estado["banco"])),
                key=lambda indice: self._pontuacao_sinergia(estado["banco"][indice], sinergias_atuais),
            )
            ok, _ = ativador.mover_banco_para_mapa(partida, player_id, melhor_indice, slot_livre.get("slot_id", 0))
            if not ok:
                break

            carta_campo = slot_livre.get("carta")
            for sinergia in self._sinergias_carta(carta_campo):
                sinergias_atuais[sinergia] = sinergias_atuais.get(sinergia, 0) + 1

        while len(estado.get("banco", [])) > 8:
            ativador.vender_do_banco(partida, player_id, len(estado["banco"]) - 1)

        if estado.get("ouro", 0) >= 2 and len(estado.get("banco", [])) < 3:
            ativador.roletar_loja(partida, player_id, custo=2)

        return True, "ok"
