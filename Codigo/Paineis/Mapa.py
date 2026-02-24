import math

import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Mapa:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.20), 120, int(largura_tela * 0.58), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(30, negrito=True)
        self.fonte_carta = obter_fonte(20)
        self.raio_hex = 42
        self.slots = self._gerar_grade_hex(linhas=4, colunas=7)

    def _gerar_grade_hex(self, linhas, colunas):
        slots = []
        largura = math.sqrt(3) * self.raio_hex
        altura = self.raio_hex * 1.5
        origem_x = self.rect.centerx - int((colunas - 1) * largura / 2)
        origem_y = self.rect.centery - int((linhas - 1) * altura / 2)

        for r in range(linhas):
            for q in range(colunas):
                x = origem_x + q * largura + (r % 2) * (largura / 2)
                y = origem_y + r * altura
                slots.append({"q": q, "r": r, "centro": (int(x), int(y))})
        return slots

    def _pontos_hex(self, centro):
        cx, cy = centro
        return [
            (int(cx + self.raio_hex * math.cos(math.radians(60 * i - 30))), int(cy + self.raio_hex * math.sin(math.radians(60 * i - 30))))
            for i in range(6)
        ]

    def slot_para_posicao(self, pos):
        melhor = None
        melhor_dist = 10_000
        for slot in self.slots:
            dist = math.dist(pos, slot["centro"])
            if dist < melhor_dist:
                melhor_dist = dist
                melhor = slot

        if melhor is None or melhor_dist > self.raio_hex:
            return None
        return melhor["q"], melhor["r"]

    def tropa_por_posicao(self, pos, cartas_mapa):
        pos_hex = self.slot_para_posicao(pos)
        if pos_hex is None:
            return None
        q, r = pos_hex
        for entry in cartas_mapa:
            if entry["q"] == q and entry["r"] == r:
                return entry
        return None

    def desenhar(self, tela, cartas_mapa, mostrar_grade=False, carta_drag=None):
        tela.blit(self.fonte_titulo.render("Mapa", True, (236, 236, 236)), (self.rect.x + 14, self.rect.y + 8))

        if mostrar_grade:
            for slot in self.slots:
                pygame.draw.polygon(tela, (92, 140, 113), self._pontos_hex(slot["centro"]), width=2)

        mapa_por_pos = {(entry["q"], entry["r"]): entry["carta"] for entry in cartas_mapa}

        for slot in self.slots:
            carta = mapa_por_pos.get((slot["q"], slot["r"]))
            if carta is None:
                continue
            poly = self._pontos_hex(slot["centro"])
            pygame.draw.polygon(tela, (72, 104, 84), poly)
            pygame.draw.polygon(tela, (160, 198, 173), poly, width=2)
            texto_nome = self.fonte_carta.render(carta.get("nome", "Carta"), True, (245, 245, 245))
            sinergia = carta.get("sinergia", "-")
            sinergia_secundaria = carta.get("sinergia_secundaria")
            if sinergia_secundaria:
                sinergia = f"{sinergia}/{sinergia_secundaria}"
            texto_sin = self.fonte_carta.render(sinergia, True, (224, 233, 217))
            tela.blit(texto_nome, (slot["centro"][0] - texto_nome.get_width() // 2, slot["centro"][1] - 18))
            tela.blit(texto_sin, (slot["centro"][0] - texto_sin.get_width() // 2, slot["centro"][1] + 2))

        if mostrar_grade and carta_drag is not None:
            mouse = pygame.mouse.get_pos()
            texto = self.fonte_carta.render(carta_drag.get("sinergia", "-"), True, (250, 250, 250))
            tela.blit(texto, (mouse[0] - texto.get_width() // 2, mouse[1] - 8))
