import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Paineis.Banco import Banco
from Codigo.Paineis.Loja import Loja
from Codigo.Paineis.Mapa import Mapa
from Codigo.Paineis.Selecao import Selecao
from Codigo.Paineis.Sinergias import Sinergias
from Codigo.Paineis.Visualizador import Visualizador
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


def _obter_jogador_por_id(partida, player_id):
    for jogador in partida.jogadores:
        if jogador.player_id == player_id:
            return jogador
    return _obter_jogador_local(partida)


def TelaEstrategista(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((26, 52, 34))

    partida = Parametros.get("PartidaAtual")
    if partida is None:
        return

    jogador_ativo = _obter_jogador_por_id(partida, Parametros.get("JogadorVisualizadoId", "local-1"))
    if jogador_ativo is None:
        return

    fonte = obter_fonte(30)
    TELA.blit(fonte.render(f"Vida: {jogador_ativo.vida}", True, (236, 236, 236)), (40, 62))
    TELA.blit(fonte.render(f"Ouro: {jogador_ativo.ouro}", True, (236, 218, 126)), (230, 62))

    if CONFIG.get("MostrarPing", False):
        fonte_ping = obter_fonte(24)
        TELA.blit(fonte_ping.render(f"Ping: {partida.ping_ms}ms", True, (184, 214, 242)), (10, 36))

    Parametros["Mapa"].desenhar(TELA, jogador_ativo.mapa, mostrar_grade=Parametros["Banco"].drag is not None, carta_drag=Parametros["Banco"].drag["carta"] if Parametros["Banco"].drag else None)
    Parametros["Sinergias"].desenhar(TELA, jogador_ativo.sinergias)
    Parametros["Selecao"].desenhar(TELA, jogador_ativo.selecao)
    Parametros["Visualizador"].desenhar(TELA, partida.jogadores, Parametros.get("JogadorVisualizadoId", "local-1"))
    Parametros["Banco"].desenhar(TELA, jogador_ativo.banco)
    Parametros["Loja"].desenhar(TELA, jogador_ativo.loja)

    if jogador_ativo.player_id != "local-1":
        aviso = obter_fonte(22, negrito=True).render(f"Visualizando: {jogador_ativo.nome}", True, (190, 212, 232))
        TELA.blit(aviso, (600, 62))


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
        "Mapa": Mapa(),
        "Sinergias": Sinergias(),
        "Selecao": Selecao(),
        "Visualizador": Visualizador(),
        "JogadorVisualizadoId": "local-1",
        "DragMapa": None,
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

            jogador_ativo = _obter_jogador_por_id(partida, Parametros.get("JogadorVisualizadoId", "local-1"))
            if jogador_ativo is None:
                continue

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                player_id = Parametros["Visualizador"].jogador_clicado(evento.pos, partida.jogadores)
                if player_id is not None:
                    Parametros["JogadorVisualizadoId"] = player_id
                    continue

                entry = Parametros["Mapa"].tropa_por_posicao(evento.pos, jogador_ativo.mapa)
                if entry is not None:
                    Parametros["DragMapa"] = entry
                    continue

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1 and Parametros["DragMapa"] is not None:
                indice_selecao = Parametros["Selecao"].slot_por_posicao(evento.pos)
                if indice_selecao is not None:
                    servidor_estrategista.mover_mapa_para_selecao(
                        partida,
                        jogador_ativo.player_id,
                        Parametros["DragMapa"]["q"],
                        Parametros["DragMapa"]["r"],
                        indice_selecao,
                    )
                Parametros["DragMapa"] = None
                continue

            acao_loja = Parametros["Loja"].processar_evento(evento, jogador_ativo.loja)
            if acao_loja:
                if acao_loja["acao"] == "roletar":
                    servidor_estrategista.roletar_loja(partida, jogador_ativo.player_id)
                elif acao_loja["acao"] == "comprar":
                    servidor_estrategista.comprar_carta_loja(partida, jogador_ativo.player_id, acao_loja["indice"])

            acao_banco = Parametros["Banco"].processar_evento(evento, jogador_ativo.banco, Parametros["Loja"].rect)
            if acao_banco:
                if acao_banco["acao"] == "vender":
                    servidor_estrategista.vender_do_banco(partida, jogador_ativo.player_id, acao_banco["indice"])
                elif acao_banco["acao"] == "soltar":
                    pos_hex = Parametros["Mapa"].slot_para_posicao(acao_banco["pos"])
                    if pos_hex is not None:
                        servidor_estrategista.posicionar_do_banco(partida, jogador_ativo.player_id, acao_banco["indice"], pos_hex[0], pos_hex[1])

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
