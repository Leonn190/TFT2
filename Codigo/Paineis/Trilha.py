import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Trilha:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect_trilha = pygame.Rect(int(largura_tela * 0.20), 26, int(largura_tela * 0.58), 80)
        self.rect_tempo = pygame.Rect(largura_tela - 350, 24, 310, 26)
        self.ordem_formato = ["circulo", "quadrado", "circulo", "circulo", "quadrado", "circulo", "circulo", "quadrado", "circulo"]
        self.fonte_tempo = obter_fonte(24, negrito=True)

    def desenhar_trilha(self, tela, trilha_batalhas, indice_atual=0):
        margem_x = 36
        y_formas = self.rect_trilha.y + 42
        espacamento = (self.rect_trilha.width - margem_x * 2) / (len(self.ordem_formato) - 1)

        for indice in range(len(self.ordem_formato) - 1):
            x_atual = int(self.rect_trilha.x + margem_x + indice * espacamento)
            x_prox = int(self.rect_trilha.x + margem_x + (indice + 1) * espacamento)
            pygame.draw.line(tela, (102, 110, 124), (x_atual, y_formas), (x_prox, y_formas), 3)

        for indice, formato in enumerate(self.ordem_formato):
            x = int(self.rect_trilha.x + margem_x + indice * espacamento)
            dados = trilha_batalhas[indice] if indice < len(trilha_batalhas) else {}
            resultado = dados.get("resultado")

            if resultado == "vitoria":
                cor = (72, 140, 246)
            elif resultado == "derrota":
                cor = (216, 76, 76)
            elif indice == indice_atual:
                cor = (242, 214, 72)
            else:
                cor = (164, 172, 184)

            if formato == "quadrado":
                forma = pygame.Rect(x - 11, y_formas - 11, 22, 22)
                pygame.draw.rect(tela, cor, forma, border_radius=4)
                pygame.draw.rect(tela, (230, 234, 240), forma, width=2, border_radius=4)
            else:
                pygame.draw.circle(tela, cor, (x, y_formas), 11)
                pygame.draw.circle(tela, (230, 234, 240), (x, y_formas), 11, width=2)

    def desenhar_temporizador(self, tela, tempo_restante_ms, duracao_total_ms=40000):
        pygame.draw.rect(tela, (34, 38, 48), self.rect_tempo, border_radius=13)
        pygame.draw.rect(tela, (120, 130, 146), self.rect_tempo, width=2, border_radius=13)

        proporcao = 0 if duracao_total_ms <= 0 else max(0.0, min(1.0, tempo_restante_ms / duracao_total_ms))
        largura_preenchimento = int((self.rect_tempo.width - 8) * proporcao)
        preenchimento = pygame.Rect(
            self.rect_tempo.x + 4,
            self.rect_tempo.y + 4,
            largura_preenchimento,
            self.rect_tempo.height - 8,
        )

        if proporcao > 0:
            pygame.draw.rect(tela, (80, 148, 246), preenchimento, border_radius=9)

        segundos = max(0, tempo_restante_ms // 1000)
        texto = self.fonte_tempo.render(f"{segundos:02d}s", True, (232, 236, 244))
        tela.blit(texto, texto.get_rect(midright=(self.rect_tempo.x - 10, self.rect_tempo.centery)))
