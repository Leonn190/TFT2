import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Mapa:
    LINHAS = 3
    COLUNAS = 5

    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.20), 120, int(largura_tela * 0.58), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(30, negrito=True)
        self.fonte_carta = obter_fonte(19)

    def _slots(self, mapa_slots):
        margem_x = 22
        margem_top = 58
        gap_x = 16
        gap_y = 18
        largura_total = self.rect.width - margem_x * 2 - gap_x * (self.COLUNAS - 1)
        altura_total = self.rect.height - margem_top - 26 - gap_y * (self.LINHAS - 1)
        largura_slot = largura_total // self.COLUNAS
        altura_slot = altura_total // self.LINHAS

        slots = []
        for item in mapa_slots:
            slot_id = item.get("slot_id", 0)
            linha = slot_id // self.COLUNAS
            coluna = slot_id % self.COLUNAS
            x = self.rect.x + margem_x + coluna * (largura_slot + gap_x)
            y = self.rect.y + margem_top + linha * (altura_slot + gap_y)
            slots.append({"slot": item, "rect": pygame.Rect(x, y, largura_slot, altura_slot), "linha": linha, "coluna": coluna})
        return slots

    def slot_por_posicao(self, pos, mapa_slots):
        for item in self._slots(mapa_slots):
            if item["rect"].collidepoint(pos):
                return item["slot"]
        return None

    def desenhar(self, tela, mapa_slots, carta_drag=None, slot_destacado=None):
        pygame.draw.rect(tela, (52, 56, 62), self.rect, border_radius=14)
        pygame.draw.rect(tela, (124, 132, 143), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Mapa", True, (236, 236, 236)), (self.rect.x + 14, self.rect.y + 8))

        slots = self._slots(mapa_slots)
        centros = {(item["linha"], item["coluna"]): item["rect"].center for item in slots}

        for item in slots:
            for dl, dc in ((0, 1), (1, 0)):
                destino = (item["linha"] + dl, item["coluna"] + dc)
                if destino in centros:
                    pygame.draw.line(tela, (112, 120, 132), item["rect"].center, centros[destino], 3)

        for item in slots:
            slot = item["slot"]
            rect = item["rect"]
            carta = slot.get("carta")
            destacado = slot_destacado is not None and slot.get("slot_id") == slot_destacado

            if not slot.get("desbloqueado"):
                cor_slot = (40, 42, 47)
                cor_borda = (80, 86, 96)
            else:
                cor_slot = (70, 76, 84) if carta is None else (86, 94, 104)
                cor_borda = (246, 216, 84) if destacado else (164, 172, 184)

            pygame.draw.rect(tela, cor_slot, rect, border_radius=10)
            pygame.draw.rect(tela, cor_borda, rect, width=2, border_radius=10)

            if not slot.get("desbloqueado"):
                txt = self.fonte_carta.render("Bloq.", True, (142, 148, 156))
                tela.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
                continue

            if carta is None:
                txt = self.fonte_carta.render("Livre", True, (192, 198, 206))
                tela.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
                continue

            nome = self.fonte_carta.render(carta.get("nome", "Carta"), True, (246, 246, 246))
            sinergia = carta.get("sinergia", "-")
            if carta.get("sinergia_secundaria"):
                sinergia = f"{sinergia}/{carta.get('sinergia_secundaria')}"
            sin = self.fonte_carta.render(sinergia, True, (214, 220, 228))
            tela.blit(nome, (rect.x + 8, rect.y + 6))
            tela.blit(sin, (rect.x + 8, rect.y + 30))

        if carta_drag is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            card = pygame.Rect(mouse_x - 82, mouse_y - 34, 164, 68)
            pygame.draw.rect(tela, (76, 84, 94), card, border_radius=9)
            pygame.draw.rect(tela, (186, 196, 208), card, width=2, border_radius=9)
            nome = self.fonte_carta.render(carta_drag.get("nome", "Carta"), True, (244, 244, 244))
            sinergia = self.fonte_carta.render(carta_drag.get("sinergia", "-"), True, (220, 226, 234))
            tela.blit(nome, (card.x + 8, card.y + 6))
            tela.blit(sinergia, (card.x + 8, card.y + 30))
