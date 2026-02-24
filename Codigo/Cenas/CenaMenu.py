import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, Escurecer


def TelaMenu(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((22, 26, 44))


def InicializaMenu(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100

    return {
        "TelaAtiva": TelaMenu,
        "TelaBase": TelaMenu,
    }


def MenuLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):
    Parametros = InicializaMenu(TELA, ESTADOS, CONFIG, INFO)

    while ESTADOS["Menu"] and ESTADOS["Rodando"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                ESTADOS["Menu"] = False
                ESTADOS["Rodando"] = False
                return

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                Escurecer(TELA, INFO, fps=CONFIG["FPS"])
                ESTADOS["Menu"] = False
                ESTADOS["Estrategista"] = True
                return

        Parametros["TelaBase"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)

        Clarear(TELA, INFO, velocidade=4)
        AplicarClaridade(TELA, CONFIG["Claridade"])
        DesenharFPS(TELA, RELOGIO, CONFIG)

        pygame.display.update()
        RELOGIO.tick(CONFIG["FPS"])
