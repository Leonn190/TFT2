import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Tooltip:
    def __init__(self):
        self.fonte_titulo = obter_fonte(20, negrito=True)
        self.fonte_texto = obter_fonte(16)

    def _quebrar_linhas(self, texto, largura_max):
        texto = str(texto or "").strip()
        if not texto:
            return []

        linhas = []
        for bloco in texto.splitlines():
            palavras = bloco.split()
            if not palavras:
                linhas.append("")
                continue

            atual = palavras[0]
            for palavra in palavras[1:]:
                candidato = f"{atual} {palavra}"
                if self.fonte_texto.size(candidato)[0] <= largura_max:
                    atual = candidato
                else:
                    linhas.append(atual)
                    atual = palavra
            linhas.append(atual)
        return linhas

    def desenhar(self, tela, titulo, linhas_texto, cards=None, posicao=(0, 0), largura=360):
        cards = cards or []
        padding = 12
        espacamento = 4
        grid_tamanho = 42
        grid_gap = 6

        conteudo = []
        for linha in linhas_texto:
            conteudo.extend(self._quebrar_linhas(linha, largura - padding * 2))

        altura_texto = len(conteudo) * (self.fonte_texto.get_height() + espacamento)
        altura = padding + self.fonte_titulo.get_height() + 8 + altura_texto + padding

        if cards:
            linhas_grid = (len(cards) + 5) // 6
            altura += 8 + linhas_grid * grid_tamanho + max(0, linhas_grid - 1) * grid_gap + padding

        largura_real = largura
        x, y = posicao
        if x + largura_real > tela.get_width() - 6:
            x = tela.get_width() - largura_real - 6
        if y + altura > tela.get_height() - 6:
            y = tela.get_height() - altura - 6

        rect = pygame.Rect(x, y, largura_real, altura)
        caixa = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(caixa, (16, 20, 28, 238), caixa.get_rect(), border_radius=10)
        pygame.draw.rect(caixa, (0, 0, 0, 255), caixa.get_rect(), width=1, border_radius=10)

        cursor_y = padding
        caixa.blit(self.fonte_titulo.render(str(titulo), True, (238, 242, 248)), (padding, cursor_y))
        cursor_y += self.fonte_titulo.get_height() + 8

        for linha in conteudo:
            cor = (204, 212, 222)
            caixa.blit(self.fonte_texto.render(linha, True, cor), (padding, cursor_y))
            cursor_y += self.fonte_texto.get_height() + espacamento

        if cards:
            cursor_y += 8
            for indice, card in enumerate(cards):
                linha = indice // 6
                coluna = indice % 6
                cx = padding + coluna * (grid_tamanho + grid_gap)
                cy = cursor_y + linha * (grid_tamanho + grid_gap)
                card_surface = pygame.transform.smoothscale(card, (grid_tamanho, grid_tamanho))
                caixa.blit(card_surface, (cx, cy))

        tela.blit(caixa, rect.topleft)
        return rect


tooltip_padrao = Tooltip()
