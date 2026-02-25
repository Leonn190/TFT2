import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Combatentes:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.24), int(altura_tela * 0.69), int(largura_tela * 0.50), int(altura_tela * 0.09))
        self.fonte_item = obter_fonte(18)

    def _slots(self):
        margem = 8
        largura_slot = (self.rect.width - margem * 4) // 5
        altura_slot = self.rect.height - 14
        y = self.rect.y + 7
        return [
            pygame.Rect(self.rect.x + i * (largura_slot + margem), y, largura_slot, altura_slot)
            for i in range(5)
        ]

    def slot_por_posicao(self, pos):
        for indice, slot in enumerate(self._slots()):
            if slot.collidepoint(pos):
                return indice
        return None

    def desenhar(self, tela, selecao, carta_drag=None):
        dados = list(selecao[:5]) + [None] * (5 - len(selecao))
        for indice, (slot, carta) in enumerate(zip(self._slots(), dados)):
            bloqueado = indice >= 1
            cor_slot = (56, 60, 68) if not bloqueado else (42, 44, 49)
            borda = (126, 134, 146) if not bloqueado else (92, 98, 108)
            pygame.draw.rect(tela, cor_slot, slot, border_radius=8)
            pygame.draw.rect(tela, borda, slot, width=2, border_radius=8)

            if bloqueado:
                texto = self.fonte_item.render("Bloq.", True, (132, 140, 148))
                tela.blit(texto, (slot.centerx - texto.get_width() // 2, slot.centery - texto.get_height() // 2))
                continue

            if carta is None:
                texto = self.fonte_item.render("Arraste", True, (180, 186, 194))
                tela.blit(texto, (slot.centerx - texto.get_width() // 2, slot.centery - texto.get_height() // 2))
                continue

            nome = self.fonte_item.render(carta.get("nome", "Carta"), True, (236, 236, 236))
            sinergia = self.fonte_item.render(carta.get("sinergia", "-"), True, (206, 212, 220))
            tela.blit(nome, (slot.x + 8, slot.y + 6))
            tela.blit(sinergia, (slot.x + 8, slot.y + 24))

        if carta_drag is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            largura_drag, altura_drag = 150, 52
            card = pygame.Rect(mouse_x - largura_drag // 2, mouse_y - altura_drag // 2, largura_drag, altura_drag)
            pygame.draw.rect(tela, (76, 84, 94), card, border_radius=8)
            pygame.draw.rect(tela, (186, 196, 208), card, width=2, border_radius=8)
            nome = self.fonte_item.render(carta_drag.get("nome", "Carta"), True, (244, 244, 244))
            sinergia = self.fonte_item.render(carta_drag.get("sinergia", "-"), True, (220, 226, 234))
            tela.blit(nome, (card.x + 8, card.y + 6))
            tela.blit(sinergia, (card.x + 8, card.y + 26))


Selecao = Combatentes
