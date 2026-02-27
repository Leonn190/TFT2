from __future__ import annotations

import random

import pygame

from Codigo.Classes.PlayerCombate import PlayerCombate
from Codigo.Modulos.FisicaCombate import atualizar_movimento, processar_dano_colisao, resolver_colisao_elastica
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Paineis.Arena import ArenaBatalha
from Codigo.Paineis.FichaCombate import FichaCombate


class SimuladorBatalha:
    def __init__(self, aliado, inimigo, seed=1337, numero_batalha=1, zoom=1.0):
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.aliado_base = PlayerCombate(aliado, rng=self.rng)
        self.inimigo_base = PlayerCombate(inimigo, rng=self.rng)

        self.arena_config = ArenaBatalha(430, 160, 1060, 700, numero_batalha=numero_batalha, zoom=zoom)
        self.arena = self.arena_config.rect
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

    def ajustar_zoom(self, delta_zoom):
        novo_zoom = max(0.45, min(2.2, self.arena_config.zoom + float(delta_zoom)))
        if abs(novo_zoom - self.arena_config.zoom) < 0.0001:
            return

        arena_antiga = self.arena.copy()
        self.arena_config.zoom = novo_zoom
        self.arena = self.arena_config.rect
        self._reposicionar_personagens_por_zoom(arena_antiga, self.arena)

    def _reposicionar_personagens_por_zoom(self, arena_antiga, arena_nova):
        largura_antiga = max(1, arena_antiga.width)
        altura_antiga = max(1, arena_antiga.height)

        for personagem in self.time_aliado + self.time_inimigo:
            x_rel = (personagem.x - arena_antiga.left) / largura_antiga
            y_rel = (personagem.y - arena_antiga.top) / altura_antiga
            personagem.x = arena_nova.left + x_rel * arena_nova.width
            personagem.y = arena_nova.top + y_rel * arena_nova.height
            personagem.raio = max(8, int(round(self.arena_config.raio_personagem_px * 0.9)))

    def _iniciar_round(self, indice):
        self.round_atual = indice
        self.time_aliado = self.aliado_base.montar_time_linha(indice, "aliado", self.arena_config)
        self.time_inimigo = self.inimigo_base.montar_time_linha(indice, "inimigo", self.arena_config)

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
