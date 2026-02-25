import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Mapa:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.20), 120, int(largura_tela * 0.58), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(30, negrito=True)
        self.fonte_carta = obter_fonte(18)
        self.colunas = 12
        self.linhas = 8
        self.slots = self._gerar_grade(self.linhas, self.colunas)
        self.slots_validos = {(slot["q"], slot["r"]) for slot in self.slots}

    def _gerar_grade(self, linhas, colunas):
        slots = []
        largura_celula = (self.rect.width - 28) // colunas
        altura_celula = (self.rect.height - 58) // linhas
        inicio_x = self.rect.x + 14
        inicio_y = self.rect.y + 40

        for r in range(linhas):
            for q in range(colunas):
                celula = pygame.Rect(inicio_x + q * largura_celula, inicio_y + r * altura_celula, largura_celula - 4, altura_celula - 4)
                slots.append({"q": q, "r": r, "rect": celula, "centro": celula.center})
        return slots

    def contem_posicao(self, pos):
        return self.rect.collidepoint(pos)

    def slot_para_posicao(self, pos):
        for slot in self.slots:
            if (slot["q"], slot["r"]) in self.slots_validos and slot["rect"].collidepoint(pos):
                return slot["q"], slot["r"]
        return None

    def tropa_por_posicao(self, pos, cartas_mapa):
        pos_slot = self.slot_para_posicao(pos)
        if pos_slot is None:
            return None
        q, r = pos_slot
        for entry in cartas_mapa:
            if entry["q"] == q and entry["r"] == r:
                return entry
        return None

    def desenhar(self, tela, cartas_mapa, mostrar_grade=False, carta_drag=None):
        pygame.draw.rect(tela, (52, 56, 62), self.rect, border_radius=14)
        pygame.draw.rect(tela, (124, 132, 143), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Mapa", True, (236, 236, 236)), (self.rect.x + 14, self.rect.y + 8))

        mapa_por_pos = {(entry["q"], entry["r"]): entry["carta"] for entry in cartas_mapa}

        for slot in self.slots:
            if (slot["q"], slot["r"]) not in self.slots_validos:
                continue
            cor_base = (66, 72, 80) if mostrar_grade else (56, 62, 70)
            pygame.draw.rect(tela, cor_base, slot["rect"], border_radius=6)
            pygame.draw.rect(tela, (112, 120, 132), slot["rect"], width=1, border_radius=6)

            carta = mapa_por_pos.get((slot["q"], slot["r"]))
            if carta is None:
                continue

            pygame.draw.rect(tela, (84, 90, 98), slot["rect"], border_radius=6)
            pygame.draw.rect(tela, (178, 186, 196), slot["rect"], width=2, border_radius=6)
            texto_nome = self.fonte_carta.render(carta.get("nome", "Carta"), True, (245, 245, 245))
            sinergia = carta.get("sinergia", "-")
            sinergia_secundaria = carta.get("sinergia_secundaria")
            if sinergia_secundaria:
                sinergia = f"{sinergia}/{sinergia_secundaria}"
            texto_sin = self.fonte_carta.render(sinergia, True, (216, 220, 226))
            tela.blit(texto_nome, (slot["rect"].centerx - texto_nome.get_width() // 2, slot["rect"].y + 6))
            tela.blit(texto_sin, (slot["rect"].centerx - texto_sin.get_width() // 2, slot["rect"].y + 26))

        if mostrar_grade and carta_drag is not None:
            mouse = pygame.mouse.get_pos()
            texto = self.fonte_carta.render(carta_drag.get("sinergia", "-"), True, (250, 250, 250))
            tela.blit(texto, (mouse[0] - texto.get_width() // 2, mouse[1] - 8))
