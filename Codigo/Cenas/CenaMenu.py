import pygame

from Codigo.Classes.Player import Player
from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, Escurecer
from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Modulos.Sonoridades import atualizar_musica, parar_musica, tocar_musica
from Codigo.Prefabs.Botao import Botao
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Telas.Config import (
    InicializaTelaConfig,
    TelaConfig,
    aplicar_configuracoes,
    aplicar_configuracoes_em_tempo_real,
)
from Codigo.Telas.TelaEscolhaSet import InicializaTelaEscolhaSet, TelaEscolhaSet
from Codigo.Telas.TelaPareamento import InicializaTelaPareamento, TelaPareamento


servico_pareamento = ServidorPareamento()

def _carregar_logo_menu():
    caminho = "Recursos/Visual/Icones/TFT2_Icone.png"
    try:
        imagem = pygame.image.load(caminho).convert_alpha()
    except Exception:
        return None
    return pygame.transform.smoothscale(imagem, (220, 220))


def _atualizar_discord_presence_menu(INFO, modo):
    discord_presence = INFO.get("DiscordPresence")
    if discord_presence is not None:
        discord_presence.atualizar_menu(modo)


def TelaMenu(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill(obter_cor("fundo_menu"))

    fonte_titulo = obter_fonte(70, negrito=False)
    titulo = fonte_titulo.render("TFT2", True, obter_cor("titulo"))
    TELA.blit(titulo, titulo.get_rect(center=(960, 220)))

    logo = Parametros.get("LogoMenu")
    if logo is not None:
        TELA.blit(logo, logo.get_rect(center=(960, 320)))

    Parametros["BotoesBase"]["Jogar"].desenhar(TELA)
    Parametros["BotoesBase"]["Configuracoes"].desenhar(TELA)
    Parametros["BotoesBase"]["Sair"].desenhar(TELA)


def InicializaMenu(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100

    return {
        "TelaAtiva": TelaMenu,
        "TelaBase": TelaMenu,
        "ModoMenu": "base",
        "BotoesBase": {
            "Jogar": Botao(760, 400, 400, 90, "Jogar"),
            "Configuracoes": Botao(760, 510, 400, 90, "Configurações"),
            "Sair": Botao(760, 620, 400, 90, "Sair"),
        },
        "EscolhaSet": InicializaTelaEscolhaSet(CONFIG),
        "Pareamento": InicializaTelaPareamento(),
        "Config": InicializaTelaConfig(CONFIG),
        "ConfigOriginal": {},
        "SetsSelecionados": [],
        "ResultadoPareamento": {},
        "Ticket": None,
        "LogoMenu": _carregar_logo_menu(),
    }


def MenuLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):
    Parametros = InicializaMenu(TELA, ESTADOS, CONFIG, INFO)
    tocar_musica("Menu1")

    while ESTADOS["Menu"] and ESTADOS["Rodando"]:
        _atualizar_discord_presence_menu(INFO, Parametros.get("ModoMenu", "base"))
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

                elif Parametros["BotoesBase"]["Configuracoes"].atualizar_evento(evento):
                    Parametros["ModoMenu"] = "config"
                    Parametros["TelaAtiva"] = TelaConfig
                    Parametros["ConfigOriginal"] = {
                        "Volume": CONFIG["Volume"],
                        "Claridade": CONFIG["Claridade"],
                        "FPS": CONFIG["FPS"],
                        "MostrarFPS": CONFIG["MostrarFPS"],
                        "MostrarPing": CONFIG["MostrarPing"],
                        "Mudo": CONFIG["Mudo"],
                    }

                elif Parametros["BotoesBase"]["Sair"].atualizar_evento(evento):
                    parar_musica()
                    ESTADOS["Menu"] = False
                    ESTADOS["Rodando"] = False
                    return

            elif Parametros["ModoMenu"] == "config":
                config_tela = Parametros["Config"]
                for barra in config_tela["Barras"].values():
                    barra.atualizar_evento(evento)

                for alavanca in config_tela["Alavancas"].values():
                    alavanca.atualizar_evento(evento)

                aplicar_configuracoes_em_tempo_real(CONFIG, config_tela)

                if config_tela["BotaoCancelar"].atualizar_evento(evento):
                    CONFIG.update(Parametros["ConfigOriginal"])
                    Parametros["ModoMenu"] = "base"
                    Parametros["TelaAtiva"] = TelaMenu
                    Parametros["Config"] = InicializaTelaConfig(CONFIG)

                elif config_tela["BotaoAplicar"].atualizar_evento(evento):
                    aplicar_configuracoes(CONFIG, config_tela)
                    Parametros["ModoMenu"] = "base"
                    Parametros["TelaAtiva"] = TelaMenu
                    Parametros["Config"] = InicializaTelaConfig(CONFIG)

            elif Parametros["ModoMenu"] == "escolha_set":
                if Parametros["EscolhaSet"]["BotaoVoltar"].atualizar_evento(evento):
                    Parametros["ModoMenu"] = "base"
                    Parametros["TelaAtiva"] = TelaMenu
                    continue

                for botao_set in Parametros["EscolhaSet"]["BotoesSets"]:
                    if botao_set.atualizar_evento(evento):
                        break

                if Parametros["EscolhaSet"]["BotaoBuscar"].atualizar_evento(evento):
                    sets_escolhidos = [botao.texto for botao in Parametros["EscolhaSet"]["BotoesSets"] if botao.ativo]
                    if not sets_escolhidos:
                        continue

                    tickets = []
                    for set_nome in sets_escolhidos:
                        jogador = Player(
                            player_id="local-1",
                            nome="Jogador Local",
                            set_escolhido=set_nome,
                            categoria="player",
                        )
                        resposta = servico_pareamento.entrar_fila(jogador, set_nome)
                        tickets.append(resposta["ticket"])

                    Parametros["SetsSelecionados"] = sets_escolhidos
                    Parametros["Ticket"] = tickets
                    Parametros["ResultadoPareamento"] = {}
                    Parametros["ModoMenu"] = "pareamento"
                    Parametros["TelaAtiva"] = TelaPareamento

            elif Parametros["ModoMenu"] == "pareamento":
                if Parametros["Pareamento"]["BotaoCancelar"].atualizar_evento(evento):
                    for set_nome in Parametros["SetsSelecionados"]:
                        servico_pareamento.cancelar_fila(set_nome, player_id="local-1")
                    Parametros["ModoMenu"] = "escolha_set"
                    Parametros["TelaAtiva"] = TelaEscolhaSet
                    Parametros["ResultadoPareamento"] = {}
                    Parametros["SetsSelecionados"] = []
                    for botao in Parametros["EscolhaSet"]["BotoesSets"]:
                        botao.definir_valor(False)

        if Parametros["ModoMenu"] == "pareamento" and Parametros["SetsSelecionados"]:
            melhor_retorno = None
            for set_nome in Parametros["SetsSelecionados"]:
                retorno = servico_pareamento.atualizar(set_nome)
                if melhor_retorno is None:
                    melhor_retorno = retorno
                if retorno["api"].get("status") == "partida_encontrada":
                    melhor_retorno = retorno
                    break

            Parametros["ResultadoPareamento"] = melhor_retorno["api"] if melhor_retorno else {}

            if melhor_retorno and melhor_retorno["api"]["status"] == "partida_encontrada":
                INFO["PartidaAtual"] = melhor_retorno["api"].get("partida_objeto")
                INFO["TrilhaBatalhas"] = [
                    {"tipo": "normal", "resultado": None},
                    {"tipo": "augment", "resultado": None},
                    {"tipo": "normal", "resultado": None},
                    {"tipo": "normal", "resultado": None},
                    {"tipo": "augment", "resultado": None},
                    {"tipo": "normal", "resultado": None},
                    {"tipo": "normal", "resultado": None},
                    {"tipo": "augment", "resultado": None},
                    {"tipo": "normal", "resultado": None},
                ]
                INFO["IndiceBatalhaAtual"] = 0
                INFO["TempoRestanteBatalhaMs"] = 40000
                Escurecer(TELA, INFO, fps=CONFIG["FPS"])
                parar_musica()
                ESTADOS["Menu"] = False
                ESTADOS["Estrategista"] = True
                return

        Parametros["TelaBase"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)

        Clarear(TELA, INFO, velocidade=4)
        AplicarClaridade(TELA, CONFIG["Claridade"])
        DesenharFPS(TELA, RELOGIO, CONFIG)
        atualizar_musica()

        pygame.display.update()
        RELOGIO.tick(CONFIG["FPS"])
