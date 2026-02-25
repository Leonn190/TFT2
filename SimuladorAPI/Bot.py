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
