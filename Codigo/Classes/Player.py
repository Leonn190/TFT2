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

        self.vida = 100
        self.ouro = 0
        self.banco = []
        self.mapa = []
        self.selecao = []
        self.sinergias = []
        self.loja = []

    def para_json(self):
        return {
            "player_id": self.player_id,
            "nome": self.nome,
            "set_escolhido": self.set_escolhido,
            "is_bot": self.is_bot,
            "categoria": self.categoria,
            "vida": self.vida,
            "ouro": self.ouro,
            "banco": self.banco,
            "mapa": self.mapa,
            "selecao": self.selecao,
            "sinergias": self.sinergias,
            "loja": self.loja,
        }
