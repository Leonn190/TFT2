import math

import pygame

from Codigo.Modulos.ConstrutorVisual import construtor_visual_cartucho
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Prefabs.Botao import Botao


class Loja:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.71), int(altura_tela * 0.79), int(largura_tela * 0.27), int(altura_tela * 0.20))
        self.fonte_titulo = obter_fonte(30)
        self.fonte_carta = obter_fonte(21)
        self.fonte_chance = obter_fonte(16)
        self.botao_roletar = Botao(self.rect.x + 16, self.rect.y + self.rect.height - 44, self.rect.width - 32, 34, "Roletar (2)")
        self.raridades = [
            ("comum", (160, 166, 176), "circulo"),
            ("incomum", (72, 188, 108), "triangulo"),
            ("raro", (84, 144, 236), "quadrado"),
            ("epico", (172, 112, 224), "pentagono"),
            ("lendario", (238, 206, 84), "hexagono"),
            ("mitico", (224, 72, 72), "octogono"),
        ]

    def _rects_cartas(self):
        margem = 10
        largura = (self.rect.width - margem * 4) // 3
        altura = 116
        y = self.rect.y + 36
        return [pygame.Rect(self.rect.x + margem + i * (largura + margem), y, largura, altura) for i in range(3)]

    def _desenhar_forma(self, tela, forma, cor, centro, raio):
        cx, cy = centro
        if forma == "circulo":
            pygame.draw.circle(tela, cor, centro, raio)
            return

        lados = {"triangulo": 3, "quadrado": 4, "pentagono": 5, "hexagono": 6, "octogono": 8}.get(forma, 4)
        pontos = []
        for i in range(lados):
            angulo = -math.pi / 2 + (2 * math.pi * i / lados)
            pontos.append((int(cx + raio * math.cos(angulo)), int(cy + raio * math.sin(angulo))))
        pygame.draw.polygon(tela, cor, pontos)

    def _desenhar_legenda_chances(self, tela, chances_loja):
        x = self.rect.x + 102
        y = self.rect.y + 14
        passo = 62
        for indice, (nome, cor, forma) in enumerate(self.raridades):
            cx = x + indice * passo
            cy = y + 9
            self._desenhar_forma(tela, forma, cor, (cx, cy), 7)
            percentual = int(chances_loja.get(nome, 0)) if chances_loja else 0
            texto = self.fonte_chance.render(f"{percentual}%", True, (228, 234, 246))
            tela.blit(texto, (cx + 10, y))

    def processar_evento(self, evento, cartas_loja):
        if self.botao_roletar.atualizar_evento(evento):
            return {"acao": "roletar"}

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for indice, rect in enumerate(self._rects_cartas()):
                if indice < len(cartas_loja) and rect.collidepoint(evento.pos):
                    return {"acao": "comprar", "indice": indice}

        return None

    def desenhar(self, tela, cartas_loja, modo_venda=False, chances_loja=None):
        if modo_venda:
            pygame.draw.rect(tela, (96, 38, 38), self.rect, border_radius=14)
            pygame.draw.rect(tela, (198, 112, 112), self.rect, width=2, border_radius=14)
            texto = self.fonte_titulo.render("Vender", True, (252, 236, 236))
            tela.blit(texto, (self.rect.centerx - texto.get_width() // 2, self.rect.centery - texto.get_height() // 2))
            return

        pygame.draw.rect(tela, (40, 54, 78), self.rect, border_radius=14)
        pygame.draw.rect(tela, (122, 146, 186), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Loja", True, (236, 236, 236)), (self.rect.x + 12, self.rect.y + 8))
        self._desenhar_legenda_chances(tela, chances_loja or {})

        for indice, rect in enumerate(self._rects_cartas()):
            pygame.draw.rect(tela, (54, 72, 102), rect, border_radius=10)
            pygame.draw.rect(tela, (150, 176, 214), rect, width=2, border_radius=10)
            if indice < len(cartas_loja):
                carta = cartas_loja[indice]
                construtor_visual_cartucho.desenhar_cartucho(tela, carta, rect)

        self.botao_roletar.desenhar(tela)
