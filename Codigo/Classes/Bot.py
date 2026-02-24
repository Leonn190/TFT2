from Codigo.Classes.Player import Player


class Bot(Player):
    def __init__(self, player_id, nome, set_escolhido=None):
        super().__init__(player_id=player_id, nome=nome, set_escolhido=set_escolhido, is_bot=True)
