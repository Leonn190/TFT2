import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Prefabs.Botao import Botao
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Telas.Opcoes import InicializaTelaOpcoes, ProcessarEventosTelaOpcoes, TelaOpcoes


servico_pareamento = ServidorPareamento()


def _obter_jogador_local(partida):
    if partida is None:
        return None
    for jogador in partida.jogadores:
        if jogador.categoria == "player" or jogador.player_id == "local-1":
            return jogador
    return partida.jogadores[0] if partida.jogadores else None


def _registrar_resultado_batalha(INFO, resultado):
    trilha = INFO.get("TrilhaBatalhas", [])
    indice = INFO.get("IndiceBatalhaAtual", 0)
    if 0 <= indice < len(trilha):
        trilha[indice]["resultado"] = resultado

    INFO["IndiceBatalhaAtual"] = min(indice + 1, max(0, len(trilha) - 1))
    INFO["TempoRestanteBatalhaMs"] = 40000


def TelaBatalha(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((74, 26, 30))

    titulo = Parametros["FonteTitulo"].render("Batalha (temporária)", True, (236, 236, 236))
    TELA.blit(titulo, titulo.get_rect(center=(960, 260)))

    Parametros["BotoesResultado"]["Vitoria"].desenhar(TELA)
    Parametros["BotoesResultado"]["Derrota"].desenhar(TELA)


def InicializaBatalha(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100

    return {
        "TelaAtiva": TelaBatalha,
        "TelaBase": TelaBatalha,
        "PartidaAtual": INFO.get("PartidaAtual"),
        "Opcoes": InicializaTelaOpcoes(CONFIG),
        "MostrarOpcoes": False,
        "FonteTitulo": obter_fonte(48, negrito=True),
        "BotoesResultado": {
            "Vitoria": Botao(720, 420, 220, 90, "Vitória"),
            "Derrota": Botao(980, 420, 220, 90, "Derrota"),
        },
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

            if Parametros["BotoesResultado"]["Vitoria"].atualizar_evento(evento):
                partida = Parametros.get("PartidaAtual")
                jogador_local = _obter_jogador_local(partida)
                if jogador_local is not None:
                    jogador_local.vida = min(100, jogador_local.vida + 2)
                _registrar_resultado_batalha(INFO, "vitoria")
                FecharIris(TELA, INFO, fps=CONFIG["FPS"])
                ESTADOS["Batalha"] = False
                ESTADOS["Estrategista"] = True
                return

            if Parametros["BotoesResultado"]["Derrota"].atualizar_evento(evento):
                partida = Parametros.get("PartidaAtual")
                jogador_local = _obter_jogador_local(partida)
                if jogador_local is not None:
                    jogador_local.vida = max(0, jogador_local.vida - 10)
                _registrar_resultado_batalha(INFO, "derrota")
                FecharIris(TELA, INFO, fps=CONFIG["FPS"])
                ESTADOS["Batalha"] = False
                ESTADOS["Estrategista"] = True
                return

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
