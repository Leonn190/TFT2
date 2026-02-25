import sys

import pygame

from Codigo.Cenas.CenaBatalha import BatalhaLoop
from Codigo.Cenas.CenaEstrategista import EstrategistaLoop
from Codigo.Cenas.CenaMenu import MenuLoop
from Codigo.Modulos.DiscordPresence import DiscordPresence
from Codigo.Telas.TelaEscolhaSet import listar_sets_existentes
from ConfigFixa import carregar_configuracoes_fixas
from Codigo.Modulos.Sonoridades import VerificaSonoridade

pygame.init()

# Tela principal do jogo
TELA_LARGURA = 1920
TELA_ALTURA = 1080
TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption("TFT2")

RELOGIO = pygame.time.Clock()

sets_encontrados = listar_sets_existentes()

CONFIG = carregar_configuracoes_fixas()
VerificaSonoridade(CONFIG)
CONFIG["SetsDisponiveis"] = sets_encontrados or ["BrawlStars"]

INFO = {"Escuro": 100}
INFO["DiscordPresence"] = DiscordPresence()

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

discord_presence = INFO.get("DiscordPresence")
if discord_presence is not None:
    discord_presence.desconectar()

pygame.quit()
sys.exit()
