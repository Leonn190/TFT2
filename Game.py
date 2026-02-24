import sys
import pygame

from Codigo.Cenas.CenaMenu import MenuLoop
from Codigo.Cenas.CenaEstrategista import EstrategistaLoop
from Codigo.Cenas.CenaBatalha import BatalhaLoop


pygame.init()

# Tela principal do jogo
TELA_LARGURA = 1920
TELA_ALTURA = 1080
TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption("TFT2")

RELOGIO = pygame.time.Clock()

CONFIG = {
    "FPS": 120,
    "Volume": 0.5,
    "Claridade": 75,
    "Mudo": False,
    "MostrarFPS": False,
    "SetsDisponiveis": ["Set 10", "Set 11", "Set 12"],
}

INFO = {
    "Escuro": 100
}

# Dicionário que controla qual cena está ativa
ESTADOS = {
    "Rodando": True,
    "Menu": True,
    "Estrategista": False,
    "Batalha": False,
}

while ESTADOS["Rodando"]:
    if ESTADOS["Menu"]:
        MenuLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO)

    elif ESTADOS["Estrategista"]:
        EstrategistaLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO)

    elif ESTADOS["Batalha"]:
        BatalhaLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO)

    else:
        # Segurança: sempre volta para o menu se nenhum estado estiver ativo
        ESTADOS["Menu"] = True

pygame.quit()
sys.exit()
