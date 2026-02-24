import pygame

from Codigo.Classes.Player import Player
from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, Escurecer
from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Prefabs.Botao import Botao
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Telas.TelaEscolhaSet import InicializaTelaEscolhaSet, TelaEscolhaSet
from Codigo.Telas.TelaPareamento import InicializaTelaPareamento, TelaPareamento


servico_pareamento = ServidorPareamento()


def TelaMenu(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill(obter_cor("fundo_menu"))

    fonte_titulo = obter_fonte(70, negrito=True)
    titulo = fonte_titulo.render("TFT2", True, obter_cor("titulo"))
    TELA.blit(titulo, titulo.get_rect(center=(960, 220)))

    Parametros["BotoesBase"]["Jogar"].desenhar(TELA)
    Parametros["BotoesBase"]["Sair"].desenhar(TELA)


def InicializaMenu(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100

    return {
        "TelaAtiva": TelaMenu,
        "TelaBase": TelaMenu,
        "ModoMenu": "base",
        "BotoesBase": {
            "Jogar": Botao(760, 410, 400, 90, "Jogar"),
            "Sair": Botao(760, 530, 400, 90, "Sair"),
        },
        "EscolhaSet": InicializaTelaEscolhaSet(CONFIG),
        "Pareamento": InicializaTelaPareamento(),
        "SetSelecionado": None,
        "ResultadoPareamento": {},
        "Ticket": None,
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

            if Parametros["ModoMenu"] == "base":
                if Parametros["BotoesBase"]["Jogar"].atualizar_evento(evento):
                    Parametros["ModoMenu"] = "escolha_set"
                    Parametros["TelaAtiva"] = TelaEscolhaSet

                elif Parametros["BotoesBase"]["Sair"].atualizar_evento(evento):
                    ESTADOS["Menu"] = False
                    ESTADOS["Rodando"] = False
                    return

            elif Parametros["ModoMenu"] == "escolha_set":
                if Parametros["EscolhaSet"]["BotaoVoltar"].atualizar_evento(evento):
                    Parametros["ModoMenu"] = "base"
                    Parametros["TelaAtiva"] = TelaMenu
                    continue

                for botao_set in Parametros["EscolhaSet"]["BotoesSets"]:
                    if botao_set.atualizar_evento(evento):
                        Parametros["SetSelecionado"] = botao_set.texto
                        jogador = Player(player_id="local-1", nome="Jogador Local", set_escolhido=botao_set.texto)
                        resposta = servico_pareamento.entrar_fila(jogador, botao_set.texto)
                        Parametros["Ticket"] = resposta["ticket"]
                        Parametros["ModoMenu"] = "pareamento"
                        Parametros["TelaAtiva"] = TelaPareamento
                        break

            elif Parametros["ModoMenu"] == "pareamento":
                if Parametros["Pareamento"]["BotaoCancelar"].atualizar_evento(evento):
                    Parametros["ModoMenu"] = "escolha_set"
                    Parametros["TelaAtiva"] = TelaEscolhaSet
                    Parametros["ResultadoPareamento"] = {}
                    Parametros["SetSelecionado"] = None

        if Parametros["ModoMenu"] == "pareamento" and Parametros["SetSelecionado"]:
            retorno = servico_pareamento.atualizar(Parametros["SetSelecionado"])
            Parametros["ResultadoPareamento"] = retorno["api"]

            if retorno["api"]["status"] == "partida_encontrada":
                INFO["LobbyAtual"] = retorno["api"]
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
