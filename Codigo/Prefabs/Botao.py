from pathlib import Path

import pygame

from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Modulos.Sonoridades import tocar


class Botao:
    def __init__(self, x, y, largura, altura, texto, fonte=None, estilo="padrao", valor=False, icone_path=None):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = texto
        self.fonte = fonte or obter_fonte(32)
        self.cor_base = obter_cor("botao_base")
        self.cor_hover = obter_cor("botao_hover")
        self.cor_texto = obter_cor("botao_texto")
        self.cor_borda = obter_cor("botao_borda")
        self.estilo = estilo
        self.ativo = valor
        self.icone_path = Path(icone_path) if icone_path else None
        self._icone_surface = None

    def _obter_icone(self, tamanho):
        if self.icone_path is None or not self.icone_path.exists():
            return None
        if self._icone_surface is None or self._icone_surface.get_size() != tamanho:
            imagem = pygame.image.load(str(self.icone_path)).convert_alpha()
            self._icone_surface = pygame.transform.smoothscale(imagem, tamanho)
        return self._icone_surface

    def desenhar(self, tela):
        if self.estilo == "alavanca":
            self._desenhar_alavanca(tela)
            return

        if self.estilo == "selecao":
            self._desenhar_selecao(tela)
            return

        mouse_pos = pygame.mouse.get_pos()
        cor = self.cor_hover if self.rect.collidepoint(mouse_pos) else self.cor_base

        pygame.draw.rect(tela, cor, self.rect, border_radius=12)
        pygame.draw.rect(tela, self.cor_borda, self.rect, width=3, border_radius=12)

        texto_render = self.fonte.render(self.texto, True, self.cor_texto)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        tela.blit(texto_render, texto_rect)

    def _desenhar_alavanca(self, tela):
        texto_render = self.fonte.render(self.texto, True, self.cor_texto)
        texto_rect = texto_render.get_rect(midleft=(self.rect.x, self.rect.centery))
        tela.blit(texto_render, texto_rect)

        largura_trilho = 90
        altura_trilho = 42
        trilho_rect = pygame.Rect(0, 0, largura_trilho, altura_trilho)
        trilho_rect.midright = self.rect.midright

        cor_trilho = (78, 164, 104) if self.ativo else (110, 110, 110)
        pygame.draw.rect(tela, cor_trilho, trilho_rect, border_radius=20)
        pygame.draw.rect(tela, self.cor_borda, trilho_rect, width=2, border_radius=20)

        raio = 16
        centro_x = trilho_rect.right - raio - 5 if self.ativo else trilho_rect.left + raio + 5
        centro = (centro_x, trilho_rect.centery)
        pygame.draw.circle(tela, (232, 232, 232), centro, raio)
        pygame.draw.circle(tela, self.cor_borda, centro, raio, width=2)

    def _desenhar_selecao(self, tela):
        mouse_pos = pygame.mouse.get_pos()
        em_hover = self.rect.collidepoint(mouse_pos)

        if self.ativo:
            cor = self.cor_hover
        elif em_hover:
            cor = (74, 112, 186)
        else:
            cor = self.cor_base

        pygame.draw.rect(tela, cor, self.rect, border_radius=12)
        pygame.draw.rect(tela, self.cor_borda, self.rect, width=3, border_radius=12)

        icone = self._obter_icone((56, 56))
        centro_texto_x = self.rect.centerx
        if icone is not None:
            icone_rect = icone.get_rect(midleft=(self.rect.x + 14, self.rect.centery))
            tela.blit(icone, icone_rect)
            centro_texto_x = self.rect.centerx + 20

        texto_render = self.fonte.render(self.texto, True, self.cor_texto)
        texto_rect = texto_render.get_rect(center=(centro_texto_x, self.rect.centery))
        tela.blit(texto_render, texto_rect)

    def atualizar_evento(self, evento):
        clicou = (
            evento.type == pygame.MOUSEBUTTONDOWN
            and evento.button == 1
            and self.rect.collidepoint(evento.pos)
        )

        if clicou and self.estilo in {"alavanca", "selecao"}:
            self.ativo = not self.ativo

        if clicou:
            tocar("Clique")
        return clicou

    def definir_valor(self, valor):
        self.ativo = bool(valor)
