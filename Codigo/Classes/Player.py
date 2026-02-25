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
        self.slots_adquiridos = 1
        self.chances_loja = {}

    @staticmethod
    def _serializar_lista_cartas(lista_cartas):
        serializadas = []
        for carta in lista_cartas:
            if hasattr(carta, "para_dict"):
                serializadas.append(carta.para_dict())
            else:
                serializadas.append(carta)
        return serializadas

    def para_json(self):
        mapa_serializado = []
        for slot in self.mapa:
            carta = slot.get("carta")
            if hasattr(carta, "para_dict"):
                carta = carta.para_dict()
            mapa_serializado.append({**slot, "carta": carta})

        return {
            "player_id": self.player_id,
            "nome": self.nome,
            "set_escolhido": self.set_escolhido,
            "is_bot": self.is_bot,
            "categoria": self.categoria,
            "vida": self.vida,
            "ouro": self.ouro,
            "banco": self._serializar_lista_cartas(self.banco),
            "mapa": mapa_serializado,
            "selecao": self.selecao,
            "sinergias": self.sinergias,
            "loja": self._serializar_lista_cartas(self.loja),
            "slots_adquiridos": self.slots_adquiridos,
            "chances_loja": self.chances_loja,
        }
