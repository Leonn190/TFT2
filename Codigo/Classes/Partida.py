class Partida:
    def __init__(self, partida_id, set_escolhido, tamanho_partida):
        self.partida_id = partida_id
        self.set_escolhido = set_escolhido
        self.tamanho_partida = tamanho_partida
        self.jogadores = []
        self.status = "buscando"
        self.ping_ms = 0
        self.estoque_compartilhado = {}

    def adicionar_jogador(self, jogador):
        if jogador.player_id not in [existente.player_id for existente in self.jogadores]:
            self.jogadores.append(jogador)

    def atualizar_status(self, status):
        self.status = status

    def espelho(self):
        return {
            "partida_id": self.partida_id,
            "set_escolhido": self.set_escolhido,
            "status": self.status,
            "tamanho_partida": self.tamanho_partida,
            "jogadores_na_partida": len(self.jogadores),
            "jogadores": [jogador.para_json() for jogador in self.jogadores],
            "ping_ms": self.ping_ms,
            "estoque_compartilhado": self.estoque_compartilhado,
        }
