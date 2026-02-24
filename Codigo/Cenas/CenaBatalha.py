import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Telas.Opcoes import InicializaTelaOpcoes, ProcessarEventosTelaOpcoes, TelaOpcoes


servico_pareamento = ServidorPareamento()


def TelaBatalha(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((74, 26, 30))


def InicializaBatalha(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100

    return {
        "TelaAtiva": TelaBatalha,
        "TelaBase": TelaBatalha,
        "PartidaAtual": INFO.get("PartidaAtual"),
        "Opcoes": InicializaTelaOpcoes(CONFIG),
        "MostrarOpcoes": False,
    }


def BatalhaLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):
    Parametros = InicializaBatalha(TELA, ESTADOS, CONFIG, INFO)

    def ao_sair_partida():
        partida = Parametros.get("PartidaAtual")
        if partida is not None:
            servico_pareamento.registrar_saida_partida(partida.partida_id, player_id="local-1")
        INFO["PartidaAtual"] = None
        Parametros["PartidaAtual"] = None

    while ESTADOS["Batalha"] and ESTADOS["Rodando"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                ESTADOS["Batalha"] = False
                ESTADOS["Rodando"] = False
                return

            if Parametros["MostrarOpcoes"]:
                if ProcessarEventosTelaOpcoes(evento, ESTADOS, CONFIG, INFO, Parametros, ao_sair_partida):
                    Parametros["MostrarOpcoes"] = False
                continue

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:
                    FecharIris(TELA, INFO, fps=CONFIG["FPS"])
                    ESTADOS["Batalha"] = False
                    ESTADOS["Estrategista"] = True
                    return

                if evento.key == pygame.K_ESCAPE:
                    Parametros["MostrarOpcoes"] = True

        Parametros["TelaBase"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        if Parametros["MostrarOpcoes"]:
            TelaOpcoes(TELA, ESTADOS, CONFIG, INFO, Parametros)

        Clarear(TELA, INFO, velocidade=4)
        AplicarClaridade(TELA, CONFIG["Claridade"])
        DesenharFPS(TELA, RELOGIO, CONFIG)

        pygame.display.update()
        RELOGIO.tick(CONFIG["FPS"])
