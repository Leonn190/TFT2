import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Telas.Opcoes import InicializaTelaOpcoes, ProcessarEventosTelaOpcoes, TelaOpcoes


servico_pareamento = ServidorPareamento()


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
        "Opcoes": InicializaTelaOpcoes(CONFIG),
        "MostrarOpcoes": False,
    }


def EstrategistaLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):
    Parametros = InicializaEstrategista(TELA, ESTADOS, CONFIG, INFO)

    def ao_sair_partida():
        partida = Parametros.get("PartidaAtual")
        if partida is not None:
            servico_pareamento.registrar_saida_partida(partida.partida_id, player_id="local-1")
        INFO["PartidaAtual"] = None
        Parametros["PartidaAtual"] = None

    while ESTADOS["Estrategista"] and ESTADOS["Rodando"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                ESTADOS["Estrategista"] = False
                ESTADOS["Rodando"] = False
                return

            if Parametros["MostrarOpcoes"]:
                if ProcessarEventosTelaOpcoes(evento, ESTADOS, CONFIG, INFO, Parametros, ao_sair_partida):
                    Parametros["MostrarOpcoes"] = False
                continue

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_c:
                    FecharIris(TELA, INFO, fps=CONFIG["FPS"])
                    ESTADOS["Estrategista"] = False
                    ESTADOS["Batalha"] = True
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
