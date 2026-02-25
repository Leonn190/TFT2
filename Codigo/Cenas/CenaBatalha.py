import random

import pygame

from Codigo.Classes.PlayerCombate import PlayerCombate
from Codigo.Modulos.EfeitosTela import AplicarClaridade, Clarear, DesenharFPS, FecharIris
from Codigo.Modulos.FisicaCombate import atualizar_movimento, processar_dano_colisao, resolver_colisao_elastica
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Paineis.FichaCombate import FichaCombate
from Codigo.Server.Pareamento import ServidorPareamento
from Codigo.Server.ServerEstrategista import ServidorEstrategista
from Codigo.Telas.Opcoes import InicializaTelaOpcoes, ProcessarEventosTelaOpcoes, TelaOpcoes


servico_pareamento = ServidorPareamento()
servidor_estrategista = ServidorEstrategista()


def _obter_jogador_local(partida):
    if partida is None:
        return None
    for jogador in partida.jogadores:
        if jogador.categoria == "player" or jogador.player_id == "local-1":
            return jogador
    return partida.jogadores[0] if partida.jogadores else None


def _escolher_inimigo(partida, jogador_local):
    candidatos = [j for j in partida.jogadores if j.player_id != jogador_local.player_id]
    return random.choice(candidatos) if candidatos else None


def _registrar_resultado_batalha(INFO, resultado):
    trilha = INFO.get("TrilhaBatalhas", [])
    indice = INFO.get("IndiceBatalhaAtual", 0)
    if 0 <= indice < len(trilha):
        trilha[indice]["resultado"] = resultado
    INFO["IndiceBatalhaAtual"] = min(indice + 1, len(trilha))


class SimuladorBatalha:
    def __init__(self, aliado, inimigo):
        self.aliado_base = PlayerCombate(aliado)
        self.inimigo_base = PlayerCombate(inimigo)

        self.arena = pygame.Rect(430, 160, 1060, 700)
        self.ficha_esquerda = pygame.Rect(20, 160, 380, 700)
        self.ficha_direita = pygame.Rect(1520, 160, 380, 700)

        self.painel_aliado = FichaCombate("esquerda")
        self.painel_inimigo = FichaCombate("direita")

        self.round_atual = 0
        self.placar = {"aliado": 0, "inimigo": 0}
        self.sobreviventes = {"aliado": 0, "inimigo": 0}
        self.finalizada = False
        self.vencedor = None
        self.texto_resultado = ""
        self.tempo_fim_ms = None

        self.time_aliado = []
        self.time_inimigo = []
        self._iniciar_round(0)

    def _iniciar_round(self, indice):
        self.round_atual = indice
        self.time_aliado = self.aliado_base.montar_time_linha(indice, "aliado", self.arena)
        self.time_inimigo = self.inimigo_base.montar_time_linha(indice, "inimigo", self.arena)

    def _avaliar_fim_round(self):
        vivos_aliados = [p for p in self.time_aliado if p.viva]
        vivos_inimigos = [p for p in self.time_inimigo if p.viva]

        if vivos_aliados and vivos_inimigos:
            return

        if len(vivos_aliados) > len(vivos_inimigos):
            self.placar["aliado"] += 1
            self.sobreviventes["aliado"] += len(vivos_aliados)
        elif len(vivos_inimigos) > len(vivos_aliados):
            self.placar["inimigo"] += 1
            self.sobreviventes["inimigo"] += len(vivos_inimigos)

        if self.placar["aliado"] >= 2 or self.placar["inimigo"] >= 2 or self.round_atual >= 2:
            self.finalizada = True
            if self.placar["aliado"] > self.placar["inimigo"]:
                self.vencedor = "aliado"
            elif self.placar["inimigo"] > self.placar["aliado"]:
                self.vencedor = "inimigo"
            else:
                self.vencedor = "aliado" if self.sobreviventes["aliado"] >= self.sobreviventes["inimigo"] else "inimigo"
            self.texto_resultado = f"Vencedor: {self.vencedor.upper()}"
            return

        self._iniciar_round(self.round_atual + 1)

    def atualizar(self, dt):
        if self.finalizada:
            return

        personagens = [p for p in (self.time_aliado + self.time_inimigo) if p.viva]
        for p in personagens:
            atualizar_movimento(p, self.arena, dt)

        for i in range(len(personagens)):
            for j in range(i + 1, len(personagens)):
                a = personagens[i]
                b = personagens[j]
                if resolver_colisao_elastica(a, b):
                    processar_dano_colisao(a, b)

        self._avaliar_fim_round()

    def desenhar(self, tela):
        pygame.draw.rect(tela, (22, 24, 32), self.arena, border_radius=18)
        pygame.draw.rect(tela, (110, 126, 158), self.arena, width=3, border_radius=18)

        fonte = obter_fonte(32, negrito=True)
        texto_round = fonte.render(f"Rodada {self.round_atual + 1}/3", True, (232, 232, 238))
        tela.blit(texto_round, (self.arena.centerx - texto_round.get_width() // 2, 110))

        placar_txt = obter_fonte(28).render(
            f"{self.aliado_base.nome} {self.placar['aliado']}  x  {self.placar['inimigo']} {self.inimigo_base.nome}",
            True,
            (220, 220, 228),
        )
        tela.blit(placar_txt, (self.arena.centerx - placar_txt.get_width() // 2, 840))

        for p in self.time_aliado + self.time_inimigo:
            p.desenhar(tela)

        hover_aliado = self.painel_aliado.desenhar_lista(tela, self.time_aliado, self.ficha_esquerda, self.aliado_base.nome)
        hover_inimigo = self.painel_inimigo.desenhar_lista(tela, self.time_inimigo, self.ficha_direita, self.inimigo_base.nome)
        self.painel_aliado.desenhar_ficha_hover(tela, hover_aliado or hover_inimigo)

        if self.finalizada:
            fonte_fim = obter_fonte(44, negrito=True)
            txt = fonte_fim.render(self.texto_resultado, True, (236, 236, 236))
            tela.blit(txt, txt.get_rect(center=(self.arena.centerx, self.arena.centery)))

    def dano_ao_perdedor(self):
        perdedor = "inimigo" if self.vencedor == "aliado" else "aliado"
        return 10 + self.sobreviventes[self.vencedor], perdedor


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
        inimigo = _escolher_inimigo(partida, jogador_local)
        if inimigo is not None:
            simulador = SimuladorBatalha(jogador_local, inimigo)

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

        simulador = Parametros.get("Simulador")
        partida = Parametros.get("PartidaAtual")
        jogador_local = _obter_jogador_local(partida) if partida is not None else None

        if simulador is None:
            if jogador_local is not None:
                servidor_estrategista.registrar_fim_batalha(partida, jogador_local.player_id)
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
                if lado_perdedor == "aliado" and jogador_local is not None:
                    jogador_local.vida = max(0, jogador_local.vida - dano)
                    _registrar_resultado_batalha(INFO, "derrota")
                elif lado_perdedor == "inimigo" and jogador_local is not None:
                    _registrar_resultado_batalha(INFO, "vitoria")

                if partida is not None and jogador_local is not None:
                    servidor_estrategista.registrar_fim_batalha(partida, jogador_local.player_id)

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
