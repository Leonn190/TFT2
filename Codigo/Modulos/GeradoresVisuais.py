from pathlib import Path

import pygame


CORES = {
    "fundo_menu": (22, 26, 44),
    "fundo_pareamento": (18, 24, 40),
    "fundo_estrategista": (44, 46, 50),
    "titulo": (244, 244, 244),
    "texto": (210, 220, 238),
    "subtitulo": (180, 190, 212),
    "botao_base": (63, 98, 166),
    "botao_hover": (86, 128, 212),
    "botao_borda": (20, 24, 30),
    "botao_texto": (240, 240, 240),
}

CAMINHO_FONTE_PADRAO = Path("Recursos/Visual/Fontes/FontePadrão.ttf")
_CACHE_FONTES = {}


def obter_cor(nome):
    if nome not in CORES:
        raise KeyError(f"Cor '{nome}' não cadastrada em GeradoresVisuais.")
    return CORES[nome]


def obter_fonte(tamanho, negrito=False):
    # Garante que o módulo de fonte está pronto mesmo se alguém chamar isso antes do pygame.init()
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()

    chave = (tamanho, negrito)
    if chave not in _CACHE_FONTES:
        if CAMINHO_FONTE_PADRAO.exists():
            fonte = pygame.font.Font(str(CAMINHO_FONTE_PADRAO), tamanho)
            # Evita bold sintético na fonte customizada, que deixava títulos serrilhados/ilegíveis.
            fonte.set_bold(False)
            _CACHE_FONTES[chave] = fonte
        else:
            _CACHE_FONTES[chave] = pygame.font.SysFont("arial", tamanho, bold=negrito)
    return _CACHE_FONTES[chave]
