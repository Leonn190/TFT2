import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Paineis.Banco import Banco
from Codigo.Paineis.Loja import Loja
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Server.ServerEstrategista import ServidorEstrategista
from Codigo.Telas.Opcoes import InicializaTelaOpcoes, ProcessarEventosTelaOpcoes, TelaOpcoes


servico_pareamento = ServidorPareamento()
servidor_estrategista = ServidorEstrategista()


def _obter_jogador_local(partida):
    for jogador in partida.jogadores:
        if jogador.categoria == "player" or jogador.player_id == "local-1":
            return jogador
    return partida.jogadores[0] if partida.jogadores else None


def TelaEstrategista(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((26, 52, 34))

    partida = Parametros.get("PartidaAtual")
    if partida is None:
        return

    jogador_local = _obter_jogador_local(partida)
    if jogador_local is None:
        return

    fonte = obter_fonte(30)
    TELA.blit(fonte.render(f"Partida: {partida.partida_id}", True, (236, 236, 236)), (40, 24))
    TELA.blit(fonte.render(f"Vida: {jogador_local.vida}", True, (236, 236, 236)), (40, 62))
    TELA.blit(fonte.render(f"Ouro: {jogador_local.ouro}", True, (236, 218, 126)), (230, 62))
    TELA.blit(fonte.render(f"Ping: {partida.ping_ms}ms", True, (184, 214, 242)), (380, 62))

    Parametros["Banco"].desenhar(TELA, jogador_local.banco)
    Parametros["Loja"].desenhar(TELA, jogador_local.loja)


def InicializaEstrategista(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100
    partida = INFO.get("PartidaAtual")
    if partida is not None:
        servidor_estrategista.sincronizar_partida(partida)

    return {
        "TelaAtiva": TelaEstrategista,
        "TelaBase": TelaEstrategista,
        "PartidaAtual": partida,
        "Opcoes": InicializaTelaOpcoes(CONFIG),
        "MostrarOpcoes": False,
        "Banco": Banco(),
        "Loja": Loja(),
    }


def EstrategistaLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):
    Parametros = InicializaEstrategista(TELA, ESTADOS, CONFIG, INFO)

    def ao_sair_partida():
        partida = Parametros.get("PartidaAtual")
        if partida is not None:
            servico_pareamento.registrar_saida_partida(partida.partida_id, player_id="local-1")
        INFO["PartidaAtual"] = None
        Parametros["PartidaAtual"] = None

    acumulador_sync_ms = 0

    while ESTADOS["Estrategista"] and ESTADOS["Rodando"]:
        dt_ms = RELOGIO.get_time()
        acumulador_sync_ms += dt_ms

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
                if evento.key == pygame.K_1:
                    servidor_estrategista.definir_ping(20)
                if evento.key == pygame.K_2:
                    servidor_estrategista.definir_ping(80)

            partida = Parametros.get("PartidaAtual")
            if partida is None:
                continue

            jogador_local = _obter_jogador_local(partida)
            if jogador_local is None:
                continue

            acao_loja = Parametros["Loja"].processar_evento(evento, jogador_local.loja)
            if acao_loja:
                if acao_loja["acao"] == "roletar":
                    servidor_estrategista.roletar_loja(partida, jogador_local.player_id)
                elif acao_loja["acao"] == "comprar":
                    servidor_estrategista.comprar_carta_loja(partida, jogador_local.player_id, acao_loja["indice"])

            acao_banco = Parametros["Banco"].processar_evento(evento, jogador_local.banco, Parametros["Loja"].rect)
            if acao_banco and acao_banco["acao"] == "vender":
                servidor_estrategista.vender_do_banco(partida, jogador_local.player_id, acao_banco["indice"])

        partida = Parametros.get("PartidaAtual")
        if partida is not None and acumulador_sync_ms >= partida.ping_ms:
            servidor_estrategista.sincronizar_partida(partida)
            acumulador_sync_ms = 0

        Parametros["TelaBase"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        if Parametros["MostrarOpcoes"]:
            TelaOpcoes(TELA, ESTADOS, CONFIG, INFO, Parametros)

        Clarear(TELA, INFO, velocidade=4)
        AplicarClaridade(TELA, CONFIG["Claridade"])
        DesenharFPS(TELA, RELOGIO, CONFIG)

        pygame.display.update()
        RELOGIO.tick(CONFIG["FPS"])
