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
