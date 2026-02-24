import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Selecao:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.77), 120, int(largura_tela * 0.11), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(28, negrito=True)
        self.fonte_item = obter_fonte(18)

    def _slots(self):
        margem = 10
        h_slot = (self.rect.height - 60 - margem * 6) // 5
        return [
            pygame.Rect(self.rect.x + margem, self.rect.y + 46 + margem + i * (h_slot + margem), self.rect.width - margem * 2, h_slot)
            for i in range(5)
        ]

    def slot_por_posicao(self, pos):
        for indice, slot in enumerate(self._slots()):
            if slot.collidepoint(pos):
                return indice
        return None

    def desenhar(self, tela, selecao):
        pygame.draw.rect(tela, (22, 36, 28), self.rect, border_radius=14)
        pygame.draw.rect(tela, (84, 122, 98), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Seleção", True, (236, 236, 236)), (self.rect.x + 10, self.rect.y + 8))

        dados = list(selecao[:5]) + [None] * (5 - len(selecao))
        for indice, (slot, carta) in enumerate(zip(self._slots(), dados)):
            bloqueado = indice >= 1
            cor_slot = (38, 54, 43) if not bloqueado else (28, 31, 34)
            borda = (106, 140, 117) if not bloqueado else (72, 78, 84)
            pygame.draw.rect(tela, cor_slot, slot, border_radius=8)
            pygame.draw.rect(tela, borda, slot, width=2, border_radius=8)

            if bloqueado:
                texto = self.fonte_item.render("Bloqueado", True, (132, 140, 148))
                tela.blit(texto, (slot.centerx - texto.get_width() // 2, slot.centery - texto.get_height() // 2))
                continue

            if carta is None:
                texto = self.fonte_item.render("Arraste aqui", True, (172, 184, 172))
                tela.blit(texto, (slot.centerx - texto.get_width() // 2, slot.centery - texto.get_height() // 2))
                continue

            nome = self.fonte_item.render(carta.get("nome", "Carta"), True, (236, 236, 236))
            sinergia = self.fonte_item.render(carta.get("sinergia", "-"), True, (198, 214, 196))
            tela.blit(nome, (slot.x + 8, slot.y + 8))
            tela.blit(sinergia, (slot.x + 8, slot.y + 28))
