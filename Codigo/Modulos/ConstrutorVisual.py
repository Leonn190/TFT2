from pathlib import Path

import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


CORES_RARIDADE = {
    "comum": (112, 118, 130),
    "incomum": (78, 170, 92),
    "raro": (58, 118, 210),
    "epico": (140, 78, 186),
    "lendario": (226, 188, 58),
    "mitico": (208, 74, 74),
}


class ConstrutorVisualCartucho:
    def __init__(self):
        self._cache_imagens = {}
        self.fonte_nome = obter_fonte(20)
        self.fonte_sinergia = obter_fonte(14)

    @staticmethod
    def _obter_campo(carta, campo, padrao=None):
        if carta is None:
            return padrao
        if isinstance(carta, dict):
            return carta.get(campo, padrao)
        return getattr(carta, campo, padrao)

    def _carregar_imagem(self, caminho, tamanho):
        if not caminho:
            return None
        chave = (caminho, tamanho)
        if chave in self._cache_imagens:
            return self._cache_imagens[chave]

        arquivo = Path(caminho)
        if not arquivo.exists():
            return None

        imagem = pygame.image.load(str(arquivo)).convert_alpha()
        imagem = pygame.transform.smoothscale(imagem, tamanho)
        self._cache_imagens[chave] = imagem
        return imagem

    def desenhar_cartucho(self, tela, carta, rect, selecionada=False, destacada=False, alpha=255):
        raridade = str(self._obter_campo(carta, "raridade", "comum")).lower()
        cor_fundo = CORES_RARIDADE.get(raridade, CORES_RARIDADE["comum"])
        cor_borda = (250, 222, 94) if destacada or selecionada else (238, 238, 238)

        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (*cor_fundo, alpha), card_surface.get_rect(), border_radius=10)
        pygame.draw.rect(card_surface, (*cor_borda, alpha), card_surface.get_rect(), width=2, border_radius=10)

        imagem_rect = pygame.Rect(6, 6, rect.width - 12, rect.height - 40)
        imagem = self._carregar_imagem(self._obter_campo(carta, "imagem"), imagem_rect.size)
        if imagem is not None:
            card_surface.blit(imagem, imagem_rect)
        else:
            pygame.draw.rect(card_surface, (30, 30, 30, alpha), imagem_rect, border_radius=8)

        barra_nome = pygame.Surface((rect.width - 4, 30), pygame.SRCALPHA)
        barra_nome.fill((0, 0, 0, 110))
        card_surface.blit(barra_nome, (2, rect.height - 34))

        nome = str(self._obter_campo(carta, "nome", "Carta"))
        texto_nome = self.fonte_nome.render(nome, True, (246, 246, 246))
        card_surface.blit(texto_nome, (8, rect.height - 30))

        sinergias = [self._obter_campo(carta, "sinergia", "-")]
        secundaria = self._obter_campo(carta, "sinergia_secundaria")
        if secundaria:
            sinergias.append(secundaria)

        sinergias = [str(s) for s in sinergias if s and s != "-"]
        for indice, sinergia in enumerate(sinergias[:3]):
            txt = self.fonte_sinergia.render(sinergia, True, (242, 242, 242))
            pos_x = rect.width - txt.get_width() - 8
            pos_y = 8 + indice * (txt.get_height() + 2)
            card_surface.blit(txt, (pos_x, pos_y))

        tela.blit(card_surface, rect.topleft)


construtor_visual_cartucho = ConstrutorVisualCartucho()
