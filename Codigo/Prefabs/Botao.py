import pygame


class Botao:
    def __init__(self, x, y, largura, altura, texto, fonte=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.fonte = fonte or pygame.font.SysFont("arial", 32)
        self.cor_base = (63, 98, 166)
        self.cor_hover = (86, 128, 212)
        self.cor_texto = (240, 240, 240)

    def desenhar(self, tela):
        mouse_pos = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(mouse_pos) else self.cor_base

        pygame.draw.rect(tela, cor, self.rect, border_radius=12)
        pygame.draw.rect(tela, (20, 24, 30), self.rect, width=3, border_radius=12)

        texto_render = self.fonte.render(self.texto, True, self.cor_texto)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        tela.blit(texto_render, texto_rect)

    def atualizar_evento(self, evento):
        return (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.rect.collidepoint(evento.pos)
        )
