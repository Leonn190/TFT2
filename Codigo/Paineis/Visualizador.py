import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Visualizador:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.89), 120, int(largura_tela * 0.10), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(24, negrito=True)
        self.fonte_item = obter_fonte(18)

    def _linhas(self, quantidade):
        margem = 10
        h = 44
        return [
            pygame.Rect(self.rect.x + margem, self.rect.y + 44 + margem + i * (h + 8), self.rect.width - margem * 2, h)
            for i in range(quantidade)
        ]

    def jogador_clicado(self, pos, jogadores):
        for jogador, linha in zip(jogadores, self._linhas(len(jogadores))):
            if linha.collidepoint(pos):
                return jogador.player_id
        return None

    def desenhar(self, tela, jogadores, jogador_ativo_id):
        pygame.draw.rect(tela, (20, 28, 36), self.rect, border_radius=14)
        pygame.draw.rect(tela, (86, 102, 122), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Players", True, (236, 236, 236)), (self.rect.x + 10, self.rect.y + 10))

        for jogador, linha in zip(jogadores, self._linhas(len(jogadores))):
            ativo = jogador.player_id == jogador_ativo_id
            pygame.draw.rect(tela, (64, 92, 122) if ativo else (40, 52, 62), linha, border_radius=8)
            pygame.draw.rect(tela, (128, 174, 212) if ativo else (82, 96, 108), linha, width=2, border_radius=8)
            nome = self.fonte_item.render(jogador.nome, True, (240, 240, 240))
            tela.blit(nome, (linha.x + 8, linha.y + 6))
            vida = self.fonte_item.render(f"Vida {jogador.vida}", True, (214, 214, 214))
            tela.blit(vida, (linha.x + 8, linha.y + 22))
