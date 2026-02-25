import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Prefabs.Botao import Botao


class Loja:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.71), int(altura_tela * 0.79), int(largura_tela * 0.27), int(altura_tela * 0.20))
        self.fonte_titulo = obter_fonte(30)
        self.fonte_carta = obter_fonte(21)
        self.botao_roletar = Botao(self.rect.x + 16, self.rect.y + self.rect.height - 44, self.rect.width - 32, 34, "Roletar (2)")

    def _rects_cartas(self):
        margem = 10
        largura = (self.rect.width - margem * 4) // 3
        altura = 82
        y = self.rect.y + 40
        return [pygame.Rect(self.rect.x + margem + i * (largura + margem), y, largura, altura) for i in range(3)]

    def processar_evento(self, evento, cartas_loja):
        if self.botao_roletar.atualizar_evento(evento):
            return {"acao": "roletar"}

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for indice, rect in enumerate(self._rects_cartas()):
                if indice < len(cartas_loja) and rect.collidepoint(evento.pos):
                    return {"acao": "comprar", "indice": indice}

        return None

    def desenhar(self, tela, cartas_loja):
        pygame.draw.rect(tela, (40, 54, 78), self.rect, border_radius=14)
        pygame.draw.rect(tela, (122, 146, 186), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Loja", True, (236, 236, 236)), (self.rect.x + 12, self.rect.y + 8))

        for indice, rect in enumerate(self._rects_cartas()):
            pygame.draw.rect(tela, (54, 72, 102), rect, border_radius=10)
            pygame.draw.rect(tela, (150, 176, 214), rect, width=2, border_radius=10)
            if indice < len(cartas_loja):
                carta = cartas_loja[indice]
                tela.blit(self.fonte_carta.render(carta.get("nome", "Carta"), True, (240, 240, 240)), (rect.x + 8, rect.y + 6))
                tela.blit(self.fonte_carta.render(carta.get("sinergia", "-"), True, (220, 220, 220)), (rect.x + 8, rect.y + 30))
                tela.blit(self.fonte_carta.render(f"{carta.get('custo', 3)} ouro", True, (231, 208, 120)), (rect.x + 8, rect.y + 54))

        self.botao_roletar.desenhar(tela)
