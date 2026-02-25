import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Modulos.ConstrutorVisual import construtor_visual_cartucho
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Paineis.Banco import Banco
from Codigo.Paineis.Loja import Loja
from Codigo.Paineis.Ficha import Ficha
from Codigo.Paineis.Mapa import Mapa
from Codigo.Paineis.Sinergias import Sinergias
from Codigo.Paineis.Trilha import Trilha
from Codigo.Paineis.Visualizador import Visualizador
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Server.ServerEstrategista import ServidorEstrategista
from Codigo.Telas.Opcoes import InicializaTelaOpcoes, ProcessarEventosTelaOpcoes, TelaOpcoes


servico_pareamento = ServidorPareamento()
servidor_estrategista = ServidorEstrategista()

INTERVALO_BATALHA_MS = 40000


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


def _inicializar_progresso_trilha(INFO):
    if "TrilhaBatalhas" not in INFO:
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
    if "IndiceBatalhaAtual" not in INFO:
        INFO["IndiceBatalhaAtual"] = 0


def _tempo_restante_batalha(INFO):
    return max(0, INFO.get("TempoRestanteBatalhaMs", INTERVALO_BATALHA_MS))


def TelaEstrategista(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((24, 26, 30))

    partida = Parametros.get("PartidaAtual")
    if partida is None:
        return

    jogador_ativo = _obter_jogador_por_id(partida, Parametros.get("JogadorVisualizadoId", "local-1"))
    if jogador_ativo is None:
        return

    fonte = obter_fonte(30)
    TELA.blit(fonte.render(f"Vida: {jogador_ativo.vida}", True, (236, 236, 236)), (40, 62))

    if CONFIG.get("MostrarPing", False):
        fonte_ping = obter_fonte(24)
        TELA.blit(fonte_ping.render(f"Ping: {partida.ping_ms}ms", True, (196, 204, 216)), (10, 36))

    hover_sinergia = Parametros["Sinergias"].obter_hover_info(
        pygame.mouse.get_pos(),
        jogador_ativo.sinergias,
        jogador_ativo.mapa,
        set_nome=getattr(jogador_ativo, "set_escolhido", "BrawlStars") or "BrawlStars",
    )

    Parametros["Mapa"].desenhar(
        TELA,
        jogador_ativo.mapa,
        slot_destacado=Parametros.get("SlotDestacado"),
        cartas_piscando_ids=hover_sinergia.get("ids_em_campo", set()) if hover_sinergia else set(),
        carta_oculta_uid=(Parametros["DragMapa"]["carta"].get("uid") if Parametros.get("DragMapa") and Parametros["DragMapa"].get("carta") else None),
    )
    Parametros["Trilha"].desenhar_trilha(TELA, INFO.get("TrilhaBatalhas", []), indice_atual=INFO.get("IndiceBatalhaAtual", 0))
    Parametros["Trilha"].desenhar_temporizador(TELA, _tempo_restante_batalha(INFO), duracao_total_ms=INTERVALO_BATALHA_MS)
    Parametros["Sinergias"].desenhar(
        TELA,
        jogador_ativo.sinergias,
        mapa_slots=jogador_ativo.mapa,
        set_nome=getattr(jogador_ativo, "set_escolhido", "BrawlStars") or "BrawlStars",
        hover_info=hover_sinergia,
    )
    Parametros["Ficha"].desenhar(TELA, Parametros.get("CartaHoverMapa"))
    Parametros["Banco"].desenhar(TELA, jogador_ativo.banco, cartas_drag=[Parametros["DragBanco"]["carta"]] if Parametros["DragBanco"] else None, ouro=jogador_ativo.ouro)
    arrastando_banco = Parametros["DragBanco"] is not None
    Parametros["Loja"].desenhar(TELA, jogador_ativo.loja, modo_venda=arrastando_banco, chances_loja=getattr(jogador_ativo, "chances_loja", None))

    if Parametros["DragMapa"] is not None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        card = pygame.Rect(mouse_x - 90, mouse_y - 58, 180, 116)
        construtor_visual_cartucho.desenhar_cartucho(TELA, Parametros["DragMapa"]["carta"], card, destacada=True, alpha=220)

    if jogador_ativo.player_id != "local-1":
        aviso = obter_fonte(22, negrito=True).render(f"Visualizando: {jogador_ativo.nome}", True, (204, 210, 220))
        TELA.blit(aviso, (600, 62))


def InicializaEstrategista(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100
    partida = INFO.get("PartidaAtual")
    if partida is not None:
        servidor_estrategista.sincronizar_partida(partida)

    _inicializar_progresso_trilha(INFO)
    if INFO.get("TempoRestanteBatalhaMs") is None:
        INFO["TempoRestanteBatalhaMs"] = INTERVALO_BATALHA_MS

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
        "Visualizador": Visualizador(),
        "Ficha": Ficha(),
        "Trilha": Trilha(),
        "JogadorVisualizadoId": "local-1",
        "DragBanco": None,
        "DragMapa": None,
        "SlotDestacado": None,
        "CartaHoverMapa": None,
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
        INFO["TempoRestanteBatalhaMs"] = max(0, INFO.get("TempoRestanteBatalhaMs", INTERVALO_BATALHA_MS) - dt_ms)

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

            slot_hover_loop = Parametros["Mapa"].slot_por_posicao(pygame.mouse.get_pos(), jogador_ativo.mapa)
            Parametros["CartaHoverMapa"] = slot_hover_loop.get("carta") if slot_hover_loop and slot_hover_loop.get("carta") else None

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                carta_banco = Parametros["Banco"].carta_por_posicao(evento.pos, jogador_ativo.banco)
                slot_mapa = Parametros["Mapa"].slot_por_posicao(evento.pos, jogador_ativo.mapa)

                Parametros["DragBanco"] = carta_banco
                Parametros["DragMapa"] = slot_mapa if slot_mapa and slot_mapa.get("carta") else None
                Parametros["SlotDestacado"] = None

                if carta_banco is None and slot_mapa is not None and not slot_mapa.get("desbloqueado"):
                    servidor_estrategista.desbloquear_slot_mapa(partida, jogador_ativo.player_id, slot_mapa.get("slot_id", -1))

            if evento.type == pygame.MOUSEMOTION:
                slot_hover = Parametros["Mapa"].slot_por_posicao(evento.pos, jogador_ativo.mapa)
                Parametros["CartaHoverMapa"] = slot_hover.get("carta") if slot_hover and slot_hover.get("carta") else None

                if Parametros["DragBanco"] is not None:
                    slot_mapa = Parametros["Mapa"].slot_por_posicao(evento.pos, jogador_ativo.mapa)
                    if slot_mapa is not None and slot_mapa.get("desbloqueado"):
                        Parametros["SlotDestacado"] = slot_mapa.get("slot_id")
                    else:
                        Parametros["SlotDestacado"] = None

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if Parametros["DragBanco"] is not None:
                    slot_mapa = Parametros["Mapa"].slot_por_posicao(evento.pos, jogador_ativo.mapa)
                    if slot_mapa is not None:
                        servidor_estrategista.mover_banco_para_mapa(
                            partida,
                            jogador_ativo.player_id,
                            Parametros["DragBanco"]["indice"],
                            slot_mapa.get("slot_id", -1),
                        )
                    elif Parametros["Loja"].rect.collidepoint(evento.pos):
                        servidor_estrategista.vender_do_banco(partida, jogador_ativo.player_id, Parametros["DragBanco"]["indice"])

                if Parametros["DragMapa"] is not None and Parametros["Banco"].rect.collidepoint(evento.pos):
                    servidor_estrategista.mover_mapa_para_banco(
                        partida,
                        jogador_ativo.player_id,
                        Parametros["DragMapa"].get("slot_id", -1),
                    )

                Parametros["DragBanco"] = None
                Parametros["DragMapa"] = None
                Parametros["SlotDestacado"] = None

            acao_loja = Parametros["Loja"].processar_evento(evento, jogador_ativo.loja)
            if acao_loja:
                if acao_loja["acao"] == "roletar":
                    servidor_estrategista.roletar_loja(partida, jogador_ativo.player_id)
                elif acao_loja["acao"] == "comprar":
                    servidor_estrategista.comprar_carta_loja(partida, jogador_ativo.player_id, acao_loja["indice"])


        partida = Parametros.get("PartidaAtual")
        if partida is not None and acumulador_sync_ms >= partida.ping_ms:
            servidor_estrategista.sincronizar_partida(partida)
            acumulador_sync_ms = 0

        if INFO.get("TempoRestanteBatalhaMs", INTERVALO_BATALHA_MS) <= 0:
            INFO["TempoRestanteBatalhaMs"] = INTERVALO_BATALHA_MS
            FecharIris(TELA, INFO, fps=CONFIG["FPS"])
            ESTADOS["Estrategista"] = False
            ESTADOS["Batalha"] = True
            return

        Parametros["TelaBase"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        if Parametros["MostrarOpcoes"]:
            TelaOpcoes(TELA, ESTADOS, CONFIG, INFO, Parametros)

        Clarear(TELA, INFO, velocidade=4)
        AplicarClaridade(TELA, CONFIG["Claridade"])
        DesenharFPS(TELA, RELOGIO, CONFIG)

        pygame.display.update()
        RELOGIO.tick(CONFIG["FPS"])
