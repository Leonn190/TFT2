import pygame

from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte


class BarraArrastavel:
    def __init__(self, x, y, largura, texto, valor_inicial, minimo=0, maximo=100, casas_decimais=0):
        self.x = x
        self.y = y
        self.largura = largura
        self.texto = texto
        self.minimo = minimo
        self.maximo = maximo
        self.casas_decimais = casas_decimais
        self.fonte = obter_fonte(28)
        self.arrastando = False

        self.rect_trilho = pygame.Rect(x, y + 38, largura, 12)
        self.raio = 14
        self.valor = valor_inicial

    def desenhar(self, tela):
        titulo = self.fonte.render(f"{self.texto}: {self._valor_formatado()}", True, obter_cor("texto"))
        tela.blit(titulo, (self.x, self.y))

        pygame.draw.rect(tela, (94, 98, 112), self.rect_trilho, border_radius=6)

        preenchido = self.rect_trilho.copy()
        preenchido.width = max(4, int(self._proporcao() * self.rect_trilho.width))
        pygame.draw.rect(tela, obter_cor("botao_hover"), preenchido, border_radius=6)

        pygame.draw.circle(tela, (232, 232, 232), self._centro_knob(), self.raio)
        pygame.draw.circle(tela, obter_cor("botao_borda"), self._centro_knob(), self.raio, width=2)

    def atualizar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            knob_rect = pygame.Rect(0, 0, self.raio * 2, self.raio * 2)
            knob_rect.center = self._centro_knob()
            if knob_rect.collidepoint(evento.pos) or self.rect_trilho.collidepoint(evento.pos):
                self.arrastando = True
                self._atualizar_por_mouse(evento.pos[0])
                return True

        if evento.type == pygame.MOUSEMOTION and self.arrastando:
            self._atualizar_por_mouse(evento.pos[0])
            return True

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastando = False

        return False

    def _atualizar_por_mouse(self, mouse_x):
        proporcao = (mouse_x - self.rect_trilho.left) / self.rect_trilho.width
        proporcao = max(0, min(1, proporcao))
        valor = self.minimo + proporcao * (self.maximo - self.minimo)
        if self.casas_decimais == 0:
            self.valor = int(round(valor))
        else:
            self.valor = round(valor, self.casas_decimais)

    def _proporcao(self):
        return (self.valor - self.minimo) / (self.maximo - self.minimo)

    def _centro_knob(self):
        x = self.rect_trilho.left + int(self._proporcao() * self.rect_trilho.width)
        return (x, self.rect_trilho.centery)

    def _valor_formatado(self):
        return f"{self.valor:.{self.casas_decimais}f}" if self.casas_decimais else str(self.valor)
