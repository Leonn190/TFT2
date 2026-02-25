import pygame

from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Selecao:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(int(largura_tela * 0.24), int(altura_tela * 0.69), int(largura_tela * 0.50), int(altura_tela * 0.11))
        self.fonte_item = obter_fonte(18)
        self.drag_ativo = False

    def _slots(self):
        margem = 8
        largura_slot = (self.rect.width - margem * 4) // 3
        altura_slot = self.rect.height - 18
        y = self.rect.y + 8
        return [
            pygame.Rect(self.rect.x + i * (largura_slot + margem), y, largura_slot, altura_slot)
            for i in range(3)
        ]

    def processar_evento(self, evento, selecao):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and len(selecao) == 3 and self.rect.collidepoint(evento.pos):
            self.drag_ativo = True
            return {"acao": "drag_inicio"}

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1 and self.drag_ativo:
            self.drag_ativo = False
            return {"acao": "soltar", "pos": evento.pos}

        return None

    def desenhar(self, tela, selecao, carta_drag=None):
        dados = list(selecao[:3]) + [None] * (3 - len(selecao))
        for slot, item in zip(self._slots(), dados):
            pygame.draw.rect(tela, (56, 60, 68), slot, border_radius=8)
            pygame.draw.rect(tela, (126, 134, 146), slot, width=2, border_radius=8)

            if item is None:
                texto = self.fonte_item.render("Selecione", True, (180, 186, 194))
                tela.blit(texto, (slot.centerx - texto.get_width() // 2, slot.centery - texto.get_height() // 2))
                continue

            carta = item.get("carta", {})
            nome = self.fonte_item.render(carta.get("nome", "Carta"), True, (236, 236, 236))
            origem = self.fonte_item.render(item.get("origem", "?").upper(), True, (206, 212, 220))
            tela.blit(nome, (slot.x + 8, slot.y + 8))
            tela.blit(origem, (slot.x + 8, slot.y + 28))

        dica = "Arraste as 3 selecionadas para o mapa" if len(selecao) == 3 else "Clique no banco/mapa para montar trio"
        cor = (216, 222, 230) if len(selecao) == 3 else (162, 170, 182)
        txt_dica = self.fonte_item.render(dica, True, cor)
        tela.blit(txt_dica, (self.rect.x, self.rect.y - 24))

        if carta_drag is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            largura_drag, altura_drag = 180, 58
            card = pygame.Rect(mouse_x - largura_drag // 2, mouse_y - altura_drag // 2, largura_drag, altura_drag)
            pygame.draw.rect(tela, (76, 84, 94), card, border_radius=8)
            pygame.draw.rect(tela, (186, 196, 208), card, width=2, border_radius=8)
            nome = self.fonte_item.render(carta_drag.get("nome", "Trio"), True, (244, 244, 244))
            sinergia = self.fonte_item.render(carta_drag.get("sinergia", "-"), True, (220, 226, 234))
            tela.blit(nome, (card.x + 8, card.y + 6))
            tela.blit(sinergia, (card.x + 8, card.y + 30))
