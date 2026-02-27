from __future__ import annotations

from pathlib import Path

import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class FichaCombate:
    def __init__(self, lado="esquerda"):
        self.lado = lado
        self.fonte_titulo = obter_fonte(24, negrito=True)
        self.fonte_texto = obter_fonte(18)
        self._cache = {}

    def _carregar(self, caminho, tamanho):
        chave = (str(caminho), tamanho)
        if chave in self._cache:
            return self._cache[chave]
        caminho_str = str(caminho or "").strip()
        if not caminho_str or caminho_str in {".", "./"}:
            return None

        arquivo = Path(caminho_str)
        if not arquivo.exists() or not arquivo.is_file():
            return None
        try:
            img = pygame.image.load(str(arquivo)).convert_alpha()
            img = pygame.transform.smoothscale(img, tamanho)
            self._cache[chave] = img
            return img
        except (pygame.error, FileNotFoundError, OSError):
            return None

    def desenhar_lista(self, tela, personagens, rect, titulo):
        pygame.draw.rect(tela, (28, 30, 40), rect, border_radius=12)
        pygame.draw.rect(tela, (72, 76, 94), rect, width=2, border_radius=12)
        tela.blit(self.fonte_titulo.render(titulo, True, (230, 230, 236)), (rect.x + 10, rect.y + 8))

        hover = None
        y = rect.y + 42
        for personagem in personagens:
            item = pygame.Rect(rect.x + 8, y, rect.width - 16, 62)
            y += 68
            if y > rect.bottom:
                break

            cor = (46, 54, 72) if personagem.viva else (34, 34, 42)
            pygame.draw.rect(tela, cor, item, border_radius=8)
            pygame.draw.rect(tela, (94, 106, 134), item, width=1, border_radius=8)

            img = self._carregar(personagem.carta.get("imagem"), (44, 44))
            if img is not None:
                tela.blit(img, (item.x + 8, item.y + 9))
            pygame.draw.circle(tela, (22, 22, 30), (item.x + 30, item.y + 31), 24, 2)

            tela.blit(self.fonte_texto.render(personagem.nome, True, (230, 230, 236)), (item.x + 60, item.y + 7))
            txt_hp = f"HP {int(personagem.vida)}/{personagem.vida_max}"
            tela.blit(self.fonte_texto.render(txt_hp, True, (174, 220, 174)), (item.x + 60, item.y + 30))

            if item.collidepoint(pygame.mouse.get_pos()):
                hover = personagem

        return hover

    def desenhar_ficha_hover(self, tela, personagem):
        if personagem is None:
            return

        largura, altura = 260, 180
        mx, my = pygame.mouse.get_pos()
        x = min(max(20, mx + 16), tela.get_width() - largura - 20)
        y = min(max(20, my + 16), tela.get_height() - altura - 20)
        rect = pygame.Rect(x, y, largura, altura)

        pygame.draw.rect(tela, (18, 18, 26), rect, border_radius=10)
        pygame.draw.rect(tela, (98, 98, 116), rect, width=2, border_radius=10)

        linhas = [
            personagem.nome,
            f"Vida: {int(personagem.vida)}/{personagem.vida_max}",
            f"Atk: {personagem.atk}  Def: {personagem.defesa}",
            f"SpD: {personagem.spd}  Vel: {personagem.vel}",
            f"Massa: {personagem.massa:.1f}",
        ]
        for i, linha in enumerate(linhas):
            fonte = self.fonte_titulo if i == 0 else self.fonte_texto
            tela.blit(fonte.render(linha, True, (236, 236, 236)), (rect.x + 10, rect.y + 10 + i * 30))
