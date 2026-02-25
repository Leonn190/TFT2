import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Banco:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(30, int(altura_tela * 0.81), int(largura_tela * 0.67), int(altura_tela * 0.18))
        self.fonte_titulo = obter_fonte(30)
        self.fonte_carta = obter_fonte(22)

    def _rects_slots(self, quantidade):
        quantidade = max(1, quantidade)
        margem = 12
        largura_slot = (self.rect.width - margem * (quantidade + 1)) // quantidade
        altura_slot = self.rect.height - 54
        y = self.rect.y + 40
        return [
            pygame.Rect(self.rect.x + margem + i * (largura_slot + margem), y, largura_slot, altura_slot)
            for i in range(quantidade)
        ]

    def carta_por_posicao(self, pos, cartas_banco):
        for indice, slot in enumerate(self._rects_slots(max(6, len(cartas_banco)))):
            if indice < len(cartas_banco) and slot.collidepoint(pos):
                return {"indice": indice, "carta": cartas_banco[indice], "rect": slot}
        return None

    def desenhar(self, tela, cartas_banco, cartas_selecionadas=None, cartas_drag=None):
        cartas_selecionadas = cartas_selecionadas or set()
        pygame.draw.rect(tela, (46, 50, 56), self.rect, border_radius=14)
        pygame.draw.rect(tela, (122, 130, 142), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Banco", True, (236, 236, 236)), (self.rect.x + 12, self.rect.y + 8))

        slots = self._rects_slots(max(6, len(cartas_banco)))
        for indice, slot in enumerate(slots):
            pygame.draw.rect(tela, (64, 70, 78), slot, border_radius=10)
            pygame.draw.rect(tela, (132, 140, 152), slot, width=2, border_radius=10)
            if indice < len(cartas_banco):
                carta = cartas_banco[indice]
                selecionada = carta.get("uid") in cartas_selecionadas
                card_rect = slot.move(0, -8) if selecionada else slot
                borda = (240, 214, 76) if selecionada else (132, 140, 152)
                pygame.draw.rect(tela, (72, 78, 86), card_rect, border_radius=10)
                pygame.draw.rect(tela, borda, card_rect, width=2, border_radius=10)
                nome = carta.get("nome", "Carta")
                sinergia = carta.get("sinergia", "-")
                if carta.get("sinergia_secundaria"):
                    sinergia = f"{sinergia}/{carta.get('sinergia_secundaria')}"
                tela.blit(self.fonte_carta.render(nome, True, (240, 240, 240)), (card_rect.x + 8, card_rect.y + 8))
                tela.blit(self.fonte_carta.render(sinergia, True, (206, 212, 220)), (card_rect.x + 8, card_rect.y + 34))

        if cartas_drag:
            mouse = pygame.mouse.get_pos()
            largura = 170
            altura = 78
            espacamento = 18
            for i, carta in enumerate(cartas_drag):
                ghost = pygame.Rect(mouse[0] - largura // 2 + i * espacamento, mouse[1] - altura // 2 + i * 6, largura, altura)
                pygame.draw.rect(tela, (74, 80, 88), ghost, border_radius=10)
                pygame.draw.rect(tela, (250, 216, 90), ghost, width=2, border_radius=10)
                tela.blit(self.fonte_carta.render(carta.get("nome", "Carta"), True, (242, 242, 242)), (ghost.x + 8, ghost.y + 8))
