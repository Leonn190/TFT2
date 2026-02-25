from pathlib import Path

import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Prefabs.Tooltip import tooltip_padrao


class Ficha:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.79), 120, int(largura_tela * 0.19), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(24, negrito=True)
        self.fonte_nome = obter_fonte(22, negrito=True)
        self.fonte_attr = obter_fonte(18)
        self._cache_imagens = {}

    @staticmethod
    def _obter(carta, campo, padrao=""):
        if isinstance(carta, dict):
            return carta.get(campo, padrao)
        return getattr(carta, campo, padrao)

    def _carregar_imagem(self, caminho, tamanho):
        chave = (str(caminho), tamanho)
        if chave in self._cache_imagens:
            return self._cache_imagens[chave]

        arquivo = Path(str(caminho or ""))
        if not arquivo.exists():
            return None

        imagem = pygame.image.load(str(arquivo)).convert_alpha()
        imagem = pygame.transform.smoothscale(imagem, tamanho)
        self._cache_imagens[chave] = imagem
        return imagem

    def gerar_ficha(self, carta):
        if not carta:
            return None

        habilidade = str(self._obter(carta, "descricao", "")).strip()
        if not habilidade or habilidade == "-":
            habilidade = "Sem descrição de habilidade"

        return {
            "nome": str(self._obter(carta, "nome", "Brawler")),
            "imagem": str(self._obter(carta, "imagem", "")),
            "stats": [
                ("Vida", self._obter(carta, "vida", self._obter(carta, "Vida", "-"))),
                ("Atk", self._obter(carta, "atk", self._obter(carta, "Atk", "-"))),
                ("SpD", self._obter(carta, "spd", self._obter(carta, "SpD", "-"))),
                ("SpA", self._obter(carta, "spa", self._obter(carta, "SpA", "-"))),
                ("Vel", self._obter(carta, "vel", self._obter(carta, "Vel", "-"))),
                ("Def", self._obter(carta, "def", self._obter(carta, "Def", "-"))),
            ],
            "habilidade": habilidade,
        }

    def desenhar(self, tela, carta_hover=None):
        if not carta_hover:
            return

        pygame.draw.rect(tela, (38, 42, 52), self.rect, border_radius=12)
        pygame.draw.rect(tela, (0, 0, 0), self.rect, width=2, border_radius=12)
        titulo = self.fonte_titulo.render("Ficha", True, (236, 236, 236))
        tela.blit(titulo, (self.rect.x + 12, self.rect.y + 8))

        ficha = self.gerar_ficha(carta_hover)
        if ficha is None:
            return

        y = self.rect.y + 50
        largura_imagem = min(self.rect.width - 24, 190)
        x_imagem = self.rect.centerx - largura_imagem // 2
        img_rect = pygame.Rect(x_imagem, y, largura_imagem, 140)
        pygame.draw.rect(tela, (24, 28, 34), img_rect, border_radius=8)
        pygame.draw.rect(tela, (0, 0, 0), img_rect, width=1, border_radius=8)

        imagem = self._carregar_imagem(ficha["imagem"], (img_rect.width - 8, img_rect.height - 8))
        if imagem is not None:
            tela.blit(imagem, (img_rect.x + 4, img_rect.y + 4))

        y = img_rect.bottom + 10
        nome = self.fonte_nome.render(ficha["nome"], True, (246, 246, 246))
        tela.blit(nome, (self.rect.x + 12, y))
        y += nome.get_height() + 8

        for chave, valor in ficha["stats"]:
            linha = self.fonte_attr.render(f"{chave}: {valor}", True, (220, 224, 234))
            tela.blit(linha, (self.rect.x + 12, y))
            y += linha.get_height() + 2

        tooltip_padrao.desenhar(
            tela,
            titulo="Habilidade",
            linhas_texto=[ficha["habilidade"]],
            posicao=(self.rect.x + 10, y + 4),
            largura=self.rect.width - 20,
        )
