import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Mapa:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.20), 120, int(largura_tela * 0.58), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(30, negrito=True)
        self.fonte_carta = obter_fonte(20)
        self._layout = []

    @staticmethod
    def _sinergias_da_carta(carta):
        sinergias = {carta.get("sinergia", "-")}
        secundaria = carta.get("sinergia_secundaria")
        if secundaria:
            sinergias.add(secundaria)
        return sinergias

    def _calcular_layout(self, cartas_mapa):
        self._layout = []
        x = self.rect.x + 18
        y = self.rect.y + 52
        largura_carta, altura_carta = 164, 74
        gap_carta, gap_grupo, linha_h = 12, 34, 118

        for grupo in cartas_mapa:
            cartas = grupo.get("cartas", [])
            largura_grupo = max(largura_carta, len(cartas) * largura_carta + max(0, len(cartas) - 1) * gap_carta)
            if x + largura_grupo > self.rect.right - 16:
                x = self.rect.x + 18
                y += linha_h

            grupo_rect = pygame.Rect(x - 6, y - 6, largura_grupo + 12, altura_carta + 30)
            cards = []
            for indice, carta in enumerate(cartas):
                card_rect = pygame.Rect(x + indice * (largura_carta + gap_carta), y + 18, largura_carta, altura_carta)
                cards.append({"carta": carta, "rect": card_rect})
            self._layout.append({"grupo": grupo, "rect": grupo_rect, "cards": cards})
            x += largura_grupo + gap_grupo

    def carta_por_posicao(self, pos, cartas_mapa):
        self._calcular_layout(cartas_mapa)
        for item in self._layout:
            for card in item["cards"]:
                if card["rect"].collidepoint(pos):
                    return {"grupo": item["grupo"], "carta": card["carta"], "rect": card["rect"]}
        return None

    def grupo_por_posicao(self, pos, cartas_mapa):
        self._calcular_layout(cartas_mapa)
        for item in self._layout:
            if item["rect"].collidepoint(pos):
                return item["grupo"]
        return None

    def grupo_compativel_para_arraste(self, pos, cartas_mapa, cartas_drag):
        if not cartas_drag:
            return None
        grupo = self.grupo_por_posicao(pos, cartas_mapa)
        if grupo is None:
            return None
        sinergia = grupo.get("sinergia", "-")
        if all(sinergia in self._sinergias_da_carta(carta) for carta in cartas_drag):
            return grupo.get("grupo_id")
        return None

    def desenhar(self, tela, cartas_mapa, cartas_selecionadas=None, cartas_drag=None, grupo_destacado=None, tick_ms=0):
        cartas_selecionadas = cartas_selecionadas or set()
        pygame.draw.rect(tela, (52, 56, 62), self.rect, border_radius=14)
        pygame.draw.rect(tela, (124, 132, 143), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Mapa", True, (236, 236, 236)), (self.rect.x + 14, self.rect.y + 8))

        self._calcular_layout(cartas_mapa)
        if not self._layout:
            vazio = self.fonte_carta.render("Arraste cartas para montar sinergias", True, (184, 190, 198))
            tela.blit(vazio, (self.rect.x + 18, self.rect.y + 66))

        pisca = (tick_ms // 180) % 2 == 0
        for item in self._layout:
            grupo = item["grupo"]
            grupo_rect = item["rect"]
            brilho = grupo_destacado == grupo.get("grupo_id") and pisca
            cor_box = (82, 92, 66) if brilho else (64, 70, 78)
            borda = (248, 220, 88) if brilho else (132, 140, 152)
            pygame.draw.rect(tela, cor_box, grupo_rect, border_radius=10)
            pygame.draw.rect(tela, borda, grupo_rect, width=2, border_radius=10)
            titulo = self.fonte_carta.render(f"{grupo.get('sinergia', '-')} ({len(grupo.get('cartas', []))})", True, (226, 232, 238))
            tela.blit(titulo, (grupo_rect.x + 8, grupo_rect.y + 2))

            for card in item["cards"]:
                carta = card["carta"]
                card_rect = card["rect"]
                selecionada = carta.get("uid") in cartas_selecionadas
                cor = (88, 96, 106)
                cor_borda = (242, 214, 76) if selecionada else (178, 186, 196)
                pygame.draw.rect(tela, cor, card_rect, border_radius=10)
                pygame.draw.rect(tela, cor_borda, card_rect, width=2, border_radius=10)
                texto_nome = self.fonte_carta.render(carta.get("nome", "Carta"), True, (245, 245, 245))
                sinergia = carta.get("sinergia", "-")
                if carta.get("sinergia_secundaria"):
                    sinergia = f"{sinergia}/{carta.get('sinergia_secundaria')}"
                texto_sin = self.fonte_carta.render(sinergia, True, (216, 220, 226))
                tela.blit(texto_nome, (card_rect.x + 8, card_rect.y + 8))
                tela.blit(texto_sin, (card_rect.x + 8, card_rect.y + 36))

        if cartas_drag:
            mouse = pygame.mouse.get_pos()
            for i, carta in enumerate(cartas_drag):
                ghost = pygame.Rect(mouse[0] - 84 + i * 20, mouse[1] - 36 + i * 8, 164, 74)
                pygame.draw.rect(tela, (74, 80, 88), ghost, border_radius=10)
                pygame.draw.rect(tela, (250, 216, 90), ghost, width=2, border_radius=10)
                tela.blit(self.fonte_carta.render(carta.get("nome", "Carta"), True, (242, 242, 242)), (ghost.x + 8, ghost.y + 8))
