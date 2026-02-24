import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, Escurecer, FecharIris


def TelaBatalha(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((74, 26, 30))


def InicializaBatalha(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100

    return {
        "TelaAtiva": TelaBatalha,
        "TelaBase": TelaBatalha,
    }


def BatalhaLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):
    Parametros = InicializaBatalha(TELA, ESTADOS, CONFIG, INFO)

    while ESTADOS["Batalha"] and ESTADOS["Rodando"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                ESTADOS["Batalha"] = False
                ESTADOS["Rodando"] = False
                return

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:
                    FecharIris(TELA, INFO, fps=CONFIG["FPS"])
                    ESTADOS["Batalha"] = False
                    ESTADOS["Estrategista"] = True
                    return

                if evento.key == pygame.K_ESCAPE:
                    Escurecer(TELA, INFO, fps=CONFIG["FPS"])
                    ESTADOS["Batalha"] = False
                    ESTADOS["Menu"] = True
                    return

        Parametros["TelaBase"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)

        Clarear(TELA, INFO, velocidade=4)
        AplicarClaridade(TELA, CONFIG["Claridade"])
        DesenharFPS(TELA, RELOGIO, CONFIG)

        pygame.display.update()
        RELOGIO.tick(CONFIG["FPS"])
