from __future__ import annotations

import math
import random
import pygame

from Codigo.Modulos.ConstrutorVisual import construir_avatar_circular


class PersonagemCombate:
    def __init__(self, carta, equipe, arena_rect, indice=0):
        self.carta = carta or {}
        self.equipe = equipe
        self.nome = str(self.carta.get("nome") or "Brawler")

        self.vida_max = self._int_campo("vida", "Vida", padrao=100)
        self.vida = float(self.vida_max)
        self.atk = self._int_campo("atk", "Atk", padrao=10)
        self.defesa = self._int_campo("def", "Def", padrao=10)
        self.spd = self._int_campo("spd", "SpD", padrao=10)
        self.vel = self._int_campo("vel", "Vel", padrao=30)
        self.velocidade_base = max(90.0, float(self.vel) * 2.2)
        self.massa = max(8.0, self.vida_max / 40.0)
        self.raio = max(18, min(42, int(14 + self.massa * 1.5)))

        self.x, self.y = self._posicao_inicial(arena_rect, indice)
        self.vx, self.vy = self._velocidade_inicial()

        self.imagem = self._carregar_imagem()

    def _int_campo(self, *campos, padrao=0):
        for campo in campos:
            valor = self.carta.get(campo)
            if valor in (None, "", "-"):
                continue
            try:
                return int(float(valor))
            except (ValueError, TypeError):
                continue
        return padrao

    def _posicao_inicial(self, arena_rect, indice):
        margem_x = arena_rect.width * 0.18
        faixa_esquerda = (arena_rect.left + 24, arena_rect.left + margem_x)
        faixa_direita = (arena_rect.right - margem_x, arena_rect.right - 24)

        if self.equipe == "aliado":
            x = random.uniform(*faixa_esquerda)
        else:
            x = random.uniform(*faixa_direita)

        altura_util = arena_rect.height - 2 * (self.raio + 8)
        y_base = arena_rect.top + self.raio + 8
        y = y_base + ((indice + 1) / 6.0) * max(40, altura_util)
        y += random.uniform(-20, 20)
        return x, y

    def _velocidade_inicial(self):
        angulo = random.uniform(0, math.tau)
        modulo = self.velocidade_base
        return math.cos(angulo) * modulo, math.sin(angulo) * modulo

    def _carregar_imagem(self):
        diametro = self.raio * 2 - 4
        return construir_avatar_circular(str(self.carta.get("imagem") or ""), diametro)


    @property
    def viva(self):
        return self.vida > 0

    @property
    def velocidade_escalar(self):
        return math.hypot(self.vx, self.vy)

    def aplicar_dano(self, dano):
        self.vida = max(0.0, self.vida - max(0.0, float(dano)))

    def desenhar(self, tela):
        if not self.viva:
            return

        centro = (int(self.x), int(self.y))
        cor_borda = (84, 206, 132) if self.equipe == "aliado" else (226, 104, 104)
        pygame.draw.circle(tela, cor_borda, centro, self.raio)
        pygame.draw.circle(tela, (24, 24, 32), centro, self.raio - 2)

        if self.imagem is not None:
            rect = self.imagem.get_rect(center=centro)
            tela.blit(self.imagem, rect)

        largura_barra = self.raio * 2
        x = int(self.x - self.raio)
        y = int(self.y - self.raio - 12)
        pygame.draw.rect(tela, (42, 42, 52), (x, y, largura_barra, 6), border_radius=3)
        proporcao = 0 if self.vida_max <= 0 else self.vida / self.vida_max
        pygame.draw.rect(tela, (92, 214, 122), (x, y, int(largura_barra * proporcao), 6), border_radius=3)
