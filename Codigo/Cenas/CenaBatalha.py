import pygame

from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Modulos.SimuladorCombate import SimuladorBatalha
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Server.ServerEstrategista import ServidorEstrategista
from Codigo.Telas.Opcoes import InicializaTelaOpcoes, ProcessarEventosTelaOpcoes, TelaOpcoes


servico_pareamento = ServidorPareamento()
servidor_estrategista = ServidorEstrategista()
INFO_INDICE_BATALHA_ATUAL = {"indice": 0}


def _obter_jogador_local(partida):
    if partida is None:
        return None
    for jogador in partida.jogadores:
        if jogador.categoria == "player" or jogador.player_id == "local-1":
            return jogador
    return partida.jogadores[0] if partida.jogadores else None


def _escolher_inimigo(partida, jogador_local):
    candidatos = [j for j in partida.jogadores if j.player_id != jogador_local.player_id]
    if not candidatos:
        return None
    candidatos.sort(key=lambda j: j.player_id)
    indice = INFO_INDICE_BATALHA_ATUAL.get("indice", 0) % len(candidatos)
    return candidatos[indice]


def _registrar_resultado_batalha(INFO, resultado):
    trilha = INFO.get("TrilhaBatalhas", [])
    indice = INFO.get("IndiceBatalhaAtual", 0)
    if 0 <= indice < len(trilha):
        trilha[indice]["resultado"] = resultado
    INFO["IndiceBatalhaAtual"] = min(indice + 1, len(trilha))


def _atualizar_discord_presence_batalha(INFO, simulador, jogador_local):
    discord_presence = INFO.get("DiscordPresence")
    if discord_presence is None:
        return

    inimigo = None
    if simulador is not None:
        inimigo_nome = getattr(getattr(simulador, "inimigo_base", None), "nome", None)
        if inimigo_nome is not None:
            class _TempInimigo:
                nome = inimigo_nome
            inimigo = _TempInimigo()

    discord_presence.atualizar_batalha(jogador_local, inimigo=inimigo)


def _registrar_fim_batalha_para_todos(partida):
    if partida is None:
        return
    for jogador in getattr(partida, "jogadores", []):
        servidor_estrategista.registrar_fim_batalha(partida, jogador.player_id)


def TelaBatalha(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((18, 16, 24))
    simulador = Parametros.get("Simulador")
    if simulador is not None:
        simulador.desenhar(TELA)


def InicializaBatalha(TELA, ESTADOS, CONFIG, INFO):
    INFO["Escuro"] = 100
    partida = INFO.get("PartidaAtual")
    jogador_local = _obter_jogador_local(partida)
    simulador = None
    if partida is not None and jogador_local is not None:
        servidor_estrategista.sincronizar_partida(partida)
        INFO_INDICE_BATALHA_ATUAL["indice"] = int(INFO.get("IndiceBatalhaAtual", 0))
        inimigo = _escolher_inimigo(partida, jogador_local)
        if inimigo is not None:
            seed_base = int(getattr(partida, "seed_combate", 1337))
            seed = seed_base + INFO_INDICE_BATALHA_ATUAL["indice"]
            numero_batalha = INFO_INDICE_BATALHA_ATUAL["indice"] + 1
            simulador = SimuladorBatalha(jogador_local, inimigo, seed=seed, numero_batalha=numero_batalha)

    return {
        "TelaAtiva": TelaBatalha,
        "TelaBase": TelaBatalha,
        "PartidaAtual": partida,
        "Simulador": simulador,
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
        dt = RELOGIO.get_time() / 1000.0
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

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                Parametros["MostrarOpcoes"] = True

            simulador_evento = Parametros.get("Simulador")
            if simulador_evento is not None:
                if evento.type == pygame.MOUSEWHEEL and simulador_evento.arena.collidepoint(pygame.mouse.get_pos()):
                    simulador_evento.ajustar_zoom(evento.y * 0.08)
                elif evento.type == pygame.MOUSEBUTTONDOWN and simulador_evento.arena.collidepoint(evento.pos):
                    if evento.button == 4:
                        simulador_evento.ajustar_zoom(0.08)
                    elif evento.button == 5:
                        simulador_evento.ajustar_zoom(-0.08)

        simulador = Parametros.get("Simulador")
        partida = Parametros.get("PartidaAtual")
        jogador_local = _obter_jogador_local(partida) if partida is not None else None
        _atualizar_discord_presence_batalha(INFO, simulador, jogador_local)

        if simulador is None:
            _registrar_fim_batalha_para_todos(partida)
            INFO["TempoRestanteBatalhaMs"] = 40000
            FecharIris(TELA, INFO, fps=CONFIG["FPS"])
            ESTADOS["Batalha"] = False
            ESTADOS["Estrategista"] = True
            return

        simulador.atualizar(dt)
        if simulador.finalizada:
            if simulador.tempo_fim_ms is None:
                simulador.tempo_fim_ms = pygame.time.get_ticks() + 1000
                dano, lado_perdedor = simulador.dano_ao_perdedor()
                inimigo = getattr(simulador, "inimigo_base", None)
                if lado_perdedor == "aliado" and jogador_local is not None:
                    jogador_local.vida = max(0, jogador_local.vida - dano)
                    _registrar_resultado_batalha(INFO, "derrota")
                elif lado_perdedor == "inimigo" and inimigo is not None:
                    inimigo.vida = max(0, inimigo.vida - dano)
                    if jogador_local is not None:
                        _registrar_resultado_batalha(INFO, "vitoria")

                _registrar_fim_batalha_para_todos(partida)

            if pygame.time.get_ticks() >= simulador.tempo_fim_ms:
                INFO["TempoRestanteBatalhaMs"] = 40000
                FecharIris(TELA, INFO, fps=CONFIG["FPS"])
                ESTADOS["Batalha"] = False
                ESTADOS["Estrategista"] = True
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
