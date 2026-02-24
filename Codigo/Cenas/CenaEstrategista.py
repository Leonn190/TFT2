import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, Escurecer, FecharIris
from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte


def TelaEstrategista(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill(obter_cor("fundo_estrategista"))

    partida = Parametros.get("PartidaAtual")
    if partida is not None:
        texto = obter_fonte(28).render(
            f"Partida carregada: {partida.partida_id} ({len(partida.jogadores)} jogadores)",
            True,
            (236, 236, 236),
        )
        TELA.blit(texto, (40, 40))


def InicializaEstrategista(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100

    return {
        "TelaAtiva": TelaEstrategista,
        "TelaBase": TelaEstrategista,
        "PartidaAtual": INFO.get("PartidaAtual"),
    }


def EstrategistaLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):
    Parametros = InicializaEstrategista(TELA, ESTADOS, CONFIG, INFO)

    while ESTADOS["Estrategista"] and ESTADOS["Rodando"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                ESTADOS["Estrategista"] = False
                ESTADOS["Rodando"] = False
                return

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_c:
                    FecharIris(TELA, INFO, fps=CONFIG["FPS"])
                    ESTADOS["Estrategista"] = False
                    ESTADOS["Batalha"] = True
                    return

                if evento.key == pygame.K_ESCAPE:
                    Escurecer(TELA, INFO, fps=CONFIG["FPS"])
                    ESTADOS["Estrategista"] = False
                    ESTADOS["Menu"] = True
                    return

        Parametros["TelaBase"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)

        Clarear(TELA, INFO, velocidade=4)
        AplicarClaridade(TELA, CONFIG["Claridade"])
        DesenharFPS(TELA, RELOGIO, CONFIG)

        pygame.display.update()
        RELOGIO.tick(CONFIG["FPS"])
