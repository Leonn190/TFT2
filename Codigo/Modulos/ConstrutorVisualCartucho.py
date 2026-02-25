from pathlib import Path

import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


CORES_RARIDADE = {
    "comum": (114, 114, 114),
    "incomum": (58, 152, 73),
    "raro": (56, 103, 186),
    "epico": (126, 67, 176),
    "lendario": (214, 180, 52),
    "mitico": (190, 62, 62),
}

_cache_imagens = {}


def _carregar_imagem_carta(carta):
    set_nome = carta.get("set_nome", "BrawlStars")
    imagem_rel = carta.get("imagem", "Brawl_Stars_iOS_ícone.jpg")
    caminho = Path("Sets") / set_nome / "Imagens" / imagem_rel
    if not caminho.exists():
        caminho = Path("Sets") / "BrawlStars" / "Imagens" / "Brawl_Stars_iOS_ícone.jpg"

    chave = str(caminho)
    if chave not in _cache_imagens:
        _cache_imagens[chave] = pygame.image.load(str(caminho)).convert_alpha()
    return _cache_imagens[chave]


def _lista_sinergias(carta):
    sins = []
    if carta.get("sinergia") and carta.get("sinergia") != "-":
        sins.append(carta["sinergia"])
    if carta.get("sinergia_secundaria") and carta.get("sinergia_secundaria") != "-":
        sins.append(carta["sinergia_secundaria"])
    return sins


def desenhar_cartucho(tela, rect, carta, selecionado=False):
    raridade = (carta.get("raridade") or "comum").lower()
    cor_fundo = CORES_RARIDADE.get(raridade, CORES_RARIDADE["comum"])
    cor_borda = (248, 224, 92) if selecionado else (220, 226, 236)

    pygame.draw.rect(tela, cor_fundo, rect, border_radius=10)
    pygame.draw.rect(tela, cor_borda, rect, width=2, border_radius=10)

    faixa_nome_altura = max(20, int(rect.height * 0.24))
    area_img = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, rect.height - faixa_nome_altura - 8)
    imagem = _carregar_imagem_carta(carta)
    imagem_escalada = pygame.transform.smoothscale(imagem, (area_img.width, area_img.height))
    tela.blit(imagem_escalada, area_img)

    sins = _lista_sinergias(carta)
    if sins:
        fonte_sinergia = obter_fonte(max(10, int(rect.height * 0.11)))
        y = rect.y + 6
        for sinergia in sins:
            txt = fonte_sinergia.render(sinergia, True, (244, 244, 244))
            caixa = pygame.Rect(rect.right - txt.get_width() - 10, y, txt.get_width() + 6, txt.get_height() + 2)
            pygame.draw.rect(tela, (0, 0, 0, 120), caixa, border_radius=4)
            tela.blit(txt, (caixa.x + 3, caixa.y + 1))
            y += txt.get_height() + 4

    faixa = pygame.Surface((rect.width - 8, faixa_nome_altura), pygame.SRCALPHA)
    faixa.fill((0, 0, 0, 150))
    tela.blit(faixa, (rect.x + 4, rect.bottom - faixa_nome_altura - 4))

    fonte_nome = obter_fonte(max(12, int(rect.height * 0.15)), negrito=True)
    nome = fonte_nome.render(carta.get("nome", "Carta"), True, (244, 244, 244))
    tela.blit(nome, (rect.x + 10, rect.bottom - faixa_nome_altura + (faixa_nome_altura - nome.get_height()) // 2 - 4))
