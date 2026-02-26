from __future__ import annotations

import pygame


class ArenaBatalha:
    """Arena com medidas físicas em metros e projeção para pixels."""

    DIAMETRO_PERSONAGEM_M = 1.0

    def __init__(self, x_px=430, y_px=160, largura_max_px=1060, altura_max_px=700, numero_batalha=1, zoom=1.0):
        self.viewport = pygame.Rect(int(x_px), int(y_px), int(largura_max_px), int(altura_max_px))
        self.numero_batalha = max(1, int(numero_batalha))
        self.zoom = max(0.2, float(zoom))
        self.largura_m, self.altura_m = self._dimensoes_por_batalha(self.numero_batalha)

    @staticmethod
    def _dimensoes_por_batalha(numero_batalha):
        if numero_batalha <= 1:
            return 10.0, 5.0
        if numero_batalha <= 4:
            return 12.0, 6.0
        return 14.0, 7.0

    @property
    def px_por_metro(self):
        base = min(self.viewport.width / self.largura_m, self.viewport.height / self.altura_m)
        return max(1.0, base * self.zoom)

    @property
    def rect(self):
        largura_px = int(round(self.largura_m * self.px_por_metro))
        altura_px = int(round(self.altura_m * self.px_por_metro))
        return pygame.Rect(
            self.viewport.centerx - largura_px // 2,
            self.viewport.centery - altura_px // 2,
            largura_px,
            altura_px,
        )

    @property
    def raio_personagem_px(self):
        return max(8, int(round((self.DIAMETRO_PERSONAGEM_M / 2.0) * self.px_por_metro)))

    def metros_para_pixels(self, valor_m):
        return float(valor_m) * self.px_por_metro
