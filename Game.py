import sys

import pygame

from Codigo.Cenas.CenaBatalha import BatalhaLoop
from Codigo.Cenas.CenaEstrategista import EstrategistaLoop
from Codigo.Cenas.CenaMenu import MenuLoop
from Codigo.Telas.TelaEscolhaSet import listar_sets_existentes
from ConfigFixa import carregar_configuracoes_fixas


pygame.init()

# Tela principal do jogo
TELA_LARGURA = 1920
TELA_ALTURA = 1080
TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption("TFT2")

RELOGIO = pygame.time.Clock()

sets_encontrados = listar_sets_existentes()

CONFIG = carregar_configuracoes_fixas()
CONFIG["SetsDisponiveis"] = sets_encontrados or ["Set 10", "Set 11", "Set 12"]

INFO = {"Escuro": 100}

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
