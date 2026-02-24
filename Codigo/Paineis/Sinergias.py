import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Sinergias:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(30, 120, int(largura_tela * 0.16), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(30)
        self.fonte_item = obter_fonte(22)

    def desenhar(self, tela, sinergias):
        pygame.draw.rect(tela, (48, 52, 58), self.rect, border_radius=14)
        pygame.draw.rect(tela, (124, 132, 143), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Sinergias", True, (236, 236, 236)), (self.rect.x + 10, self.rect.y + 8))

        y = self.rect.y + 52
        if not sinergias:
            vazio = self.fonte_item.render("Sem tropas", True, (184, 190, 198))
            tela.blit(vazio, (self.rect.x + 12, y))
            return

        for item in sinergias:
            linha = f"{item.get('sinergia', '-')} x{item.get('quantidade', 0)}"
            txt = self.fonte_item.render(linha, True, (226, 230, 236))
            tela.blit(txt, (self.rect.x + 12, y))
            y += 32
