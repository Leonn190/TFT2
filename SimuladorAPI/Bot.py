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

    @classmethod
    def forca_tabuleiro(cls, tabuleiro):
        if not tabuleiro:
            return 0

        forca_base = sum(int(carta.get("custo", 1)) for carta in tabuleiro)
        sinergias = cls.sinergias_ativas(tabuleiro)
        bonus_sinergia = sum(qtd * 2 for qtd in sinergias.values())
        bonus_diversidade = len(sinergias)
        return forca_base + bonus_sinergia + bonus_diversidade

    @classmethod
    def pontuar_compra(cls, jogador_estado, carta):
        custo = int(carta.get("custo", 1))
        sinergias_atuais = cls.sinergias_ativas(jogador_estado["tabuleiro"])
        sinergias_carta = [s for s in carta.get("sinergias", []) if s and s != "-"]
        pontos_sinergia = sum(2 for s in sinergias_carta if s in sinergias_atuais)
        return pontos_sinergia + max(0, 4 - custo)

    @classmethod
    def executar_turno(cls, jogador_estado, catalogo_cartas):
        if jogador_estado["vida"] <= 0:
            return

        jogador_estado["ouro"] += 5
        jogador_estado["loja"] = cls.gerar_loja(catalogo_cartas, quantidade=5)

        compras = 0
        while jogador_estado["ouro"] > 0 and len(jogador_estado["banco"]) < 9 and jogador_estado["loja"] and compras < 5:
            melhor_indice = max(
                range(len(jogador_estado["loja"])),
                key=lambda i: cls.pontuar_compra(jogador_estado, jogador_estado["loja"][i]),
            )
            carta = jogador_estado["loja"][melhor_indice]
            custo = int(carta.get("custo", 1))
            if custo > jogador_estado["ouro"]:
                break

            jogador_estado["ouro"] -= custo
            jogador_estado["banco"].append(carta)
            jogador_estado["loja"].pop(melhor_indice)
            compras += 1

        precisa_roletar = cls.forca_tabuleiro(jogador_estado["tabuleiro"]) < 12 and jogador_estado["ouro"] >= 2
        if precisa_roletar:
            jogador_estado["ouro"] -= 2
            jogador_estado["loja"] = cls.gerar_loja(catalogo_cartas, quantidade=5)

        if jogador_estado["ouro"] <= 1 and jogador_estado["banco"]:
            carta_vendida = jogador_estado["banco"].pop(0)
            jogador_estado["ouro"] += max(1, int(carta_vendida.get("custo", 1)) - 1)

        capacidade_tabuleiro = min(9, 1 + jogador_estado["rodada"] // 2)
        while len(jogador_estado["tabuleiro"]) < capacidade_tabuleiro and jogador_estado["banco"]:
            melhor_indice = max(
                range(len(jogador_estado["banco"])),
                key=lambda i: cls.pontuar_compra(jogador_estado, jogador_estado["banco"][i]),
            )
            jogador_estado["tabuleiro"].append(jogador_estado["banco"].pop(melhor_indice))

        jogador_estado["sinergias"] = [
            {"sinergia": nome, "quantidade": qtd}
            for nome, qtd in sorted(cls.sinergias_ativas(jogador_estado["tabuleiro"]).items(), key=lambda item: (-item[1], item[0]))
        ]
