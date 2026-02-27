from __future__ import annotations

from Codigo.Classes.PersonagemCombate import PersonagemCombate


class PlayerCombate:
    def __init__(self, jogador_base, rng=None):
        self.jogador_base = jogador_base
        self.player_id = jogador_base.player_id
        self.nome = jogador_base.nome
        self.vida = getattr(jogador_base, "vida", 100)
        self.rng = rng

    def _cartas_por_linha(self, indice_linha):
        cartas = []
        for slot in self.jogador_base.mapa:
            if slot.get("slot_id", -1) // 4 != indice_linha:
                continue
            if not slot.get("desbloqueado"):
                continue
            carta = slot.get("carta")
            if carta:
                cartas.append(carta)
        return cartas

    def montar_time_linha(self, indice_linha, equipe, arena):
        personagens = []
        for indice, carta in enumerate(self._cartas_por_linha(indice_linha)):
            personagens.append(PersonagemCombate(carta=carta, equipe=equipe, arena=arena, indice=indice, rng=self.rng))
        return personagens
