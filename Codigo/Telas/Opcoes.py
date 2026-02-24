import pygame

from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Prefabs.Botao import Botao
from Codigo.Telas.Config import (
    InicializaTelaConfig,
    TelaConfig,
    aplicar_configuracoes,
    aplicar_configuracoes_em_tempo_real,
)


def InicializaTelaOpcoes(CONFIG):
    return {
        "Modo": "base",
        "Botoes": {
            "Voltar": Botao(760, 360, 400, 90, "Voltar"),
            "Configuracoes": Botao(760, 480, 400, 90, "Configurações"),
            "Sair": Botao(760, 600, 400, 90, "Sair"),
        },
        "Config": InicializaTelaConfig(CONFIG),
        "ConfigOriginal": {},
    }


def TelaOpcoes(TELA, ESTADOS, CONFIG, INFO, Parametros):
    overlay = pygame.Surface((1920, 1080), pygame.SRCALPHA)
    overlay.fill((8, 12, 20, 210))
    TELA.blit(overlay, (0, 0))

    if Parametros["Opcoes"]["Modo"] == "config":
        TelaConfig(TELA, ESTADOS, CONFIG, INFO, {"Config": Parametros["Opcoes"]["Config"]})
        return

    titulo = obter_fonte(56, negrito=True).render("Opções", True, obter_cor("titulo"))
    TELA.blit(titulo, titulo.get_rect(center=(960, 220)))

    for botao in Parametros["Opcoes"]["Botoes"].values():
        botao.desenhar(TELA)


def ProcessarEventosTelaOpcoes(evento, ESTADOS, CONFIG, INFO, Parametros, ao_sair_partida):
    opcoes = Parametros["Opcoes"]

    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
        if opcoes["Modo"] == "config":
            CONFIG.update(opcoes["ConfigOriginal"])
            opcoes["Modo"] = "base"
            opcoes["Config"] = InicializaTelaConfig(CONFIG)
            return False
        return True

    if opcoes["Modo"] == "config":
        config_tela = opcoes["Config"]
        for barra in config_tela["Barras"].values():
            barra.atualizar_evento(evento)

        for alavanca in config_tela["Alavancas"].values():
            alavanca.atualizar_evento(evento)

        aplicar_configuracoes_em_tempo_real(CONFIG, config_tela)

        if config_tela["BotaoCancelar"].atualizar_evento(evento):
            CONFIG.update(opcoes["ConfigOriginal"])
            opcoes["Modo"] = "base"
            opcoes["Config"] = InicializaTelaConfig(CONFIG)

        elif config_tela["BotaoAplicar"].atualizar_evento(evento):
            aplicar_configuracoes(CONFIG, config_tela)
            opcoes["Modo"] = "base"
            opcoes["Config"] = InicializaTelaConfig(CONFIG)

        return False

    if opcoes["Botoes"]["Voltar"].atualizar_evento(evento):
        return True

    if opcoes["Botoes"]["Configuracoes"].atualizar_evento(evento):
        opcoes["Modo"] = "config"
        opcoes["ConfigOriginal"] = {
            "Volume": CONFIG["Volume"],
            "Claridade": CONFIG["Claridade"],
            "FPS": CONFIG["FPS"],
            "MostrarFPS": CONFIG["MostrarFPS"],
            "MostrarPing": CONFIG["MostrarPing"],
            "Mudo": CONFIG["Mudo"],
        }
        return False

    if opcoes["Botoes"]["Sair"].atualizar_evento(evento):
        ao_sair_partida()
        ESTADOS["Estrategista"] = False
        ESTADOS["Batalha"] = False
        ESTADOS["Menu"] = True
        return True

    return False
