from __future__ import annotations

from Codigo.Classes.PersonagemCombate import PersonagemCombate


class PlayerCombate:
    def __init__(self, jogador_base):
        self.jogador_base = jogador_base
        self.player_id = jogador_base.player_id
        self.nome = jogador_base.nome

    def _cartas_por_linha(self, indice_linha):
        cartas = []
        for slot in self.jogador_base.mapa:
            if slot.get("slot_id", -1) // 5 != indice_linha:
                continue
            if not slot.get("desbloqueado"):
                continue
            carta = slot.get("carta")
            if carta:
                cartas.append(carta)
        return cartas

    def montar_time_linha(self, indice_linha, equipe, arena_rect):
        personagens = []
        for indice, carta in enumerate(self._cartas_por_linha(indice_linha)):
            personagens.append(PersonagemCombate(carta=carta, equipe=equipe, arena_rect=arena_rect, indice=indice))
        return personagens
