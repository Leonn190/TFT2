import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Banco:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(30, int(altura_tela * 0.73), int(largura_tela * 0.67), int(altura_tela * 0.24))
        self.fonte_titulo = obter_fonte(30, negrito=True)
        self.fonte_carta = obter_fonte(22)
        self.drag = None

    def _rects_slots(self, quantidade):
        quantidade = max(1, quantidade)
        margem = 16
        largura_slot = (self.rect.width - margem * (quantidade + 1)) // quantidade
        altura_slot = self.rect.height - 56
        y = self.rect.y + 42
        return [
            pygame.Rect(self.rect.x + margem + i * (largura_slot + margem), y, largura_slot, altura_slot)
            for i in range(quantidade)
        ]

    def processar_evento(self, evento, cartas_banco, area_loja_rect):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for indice, slot in enumerate(self._rects_slots(max(6, len(cartas_banco)))):
                if indice < len(cartas_banco) and slot.collidepoint(evento.pos):
                    self.drag = {"indice": indice, "carta": cartas_banco[indice], "offset": (evento.pos[0] - slot.x, evento.pos[1] - slot.y)}
                    return {"acao": "drag_inicio", "indice": indice}

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1 and self.drag is not None:
            indice = self.drag["indice"]
            drop_pos = evento.pos
            self.drag = None
            if area_loja_rect.collidepoint(drop_pos):
                return {"acao": "vender", "indice": indice}
            return {"acao": "soltar", "indice": indice, "pos": drop_pos}

        return None

    def desenhar(self, tela, cartas_banco):
        pygame.draw.rect(tela, (28, 35, 25), self.rect, border_radius=14)
        pygame.draw.rect(tela, (98, 122, 92), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Banco", True, (236, 236, 236)), (self.rect.x + 12, self.rect.y + 8))

        slots = self._rects_slots(max(6, len(cartas_banco)))
        for indice, slot in enumerate(slots):
            pygame.draw.rect(tela, (53, 72, 47), slot, border_radius=10)
            pygame.draw.rect(tela, (95, 122, 90), slot, width=2, border_radius=10)
            if indice < len(cartas_banco):
                carta = cartas_banco[indice]
                nome = carta.get("nome", "Carta")
                sinergia = carta.get("sinergia", "-")
                tela.blit(self.fonte_carta.render(nome, True, (240, 240, 240)), (slot.x + 10, slot.y + 10))
                tela.blit(self.fonte_carta.render(sinergia, True, (204, 214, 191)), (slot.x + 10, slot.y + 42))

        if self.drag is not None:
            mouse = pygame.mouse.get_pos()
            carta = self.drag["carta"]
            w, h = 170, 95
            ghost = pygame.Rect(mouse[0] - self.drag["offset"][0], mouse[1] - self.drag["offset"][1], w, h)
            pygame.draw.rect(tela, (74, 94, 66), ghost, border_radius=10)
            pygame.draw.rect(tela, (135, 162, 130), ghost, width=2, border_radius=10)
            tela.blit(self.fonte_carta.render(carta.get("nome", "Carta"), True, (242, 242, 242)), (ghost.x + 8, ghost.y + 8))
