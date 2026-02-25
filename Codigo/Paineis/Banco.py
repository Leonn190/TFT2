import pygame

from Codigo.Modulos.ConstrutorVisual import construtor_visual_cartucho
from Codigo.Modulos.GeradoresVisuais import obter_fonte


class Banco:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(30, int(altura_tela * 0.79), int(largura_tela * 0.67), int(altura_tela * 0.20))
        self.fonte_titulo = obter_fonte(30)
        self.fonte_carta = obter_fonte(22)
        self.limite_cartas = 10
        self.largura_carta = 194
        self.altura_carta = self.rect.height - 52
        self.escala_hover = {}

    def _rects_slots(self, quantidade):
        quantidade = max(1, min(self.limite_cartas, quantidade))
        y = self.rect.y + 40
        largura_slot = self.largura_carta
        altura_slot = self.altura_carta
        inicio_x = self.rect.x + 12

        if quantidade == 1:
            passo_x = 0
        else:
            largura_disponivel = self.rect.width - 24 - largura_slot
            passo_x = min(largura_slot + 8, max(1, largura_disponivel // (quantidade - 1)))

        return [pygame.Rect(int(inicio_x + i * passo_x), y, largura_slot, altura_slot) for i in range(quantidade)]

    def carta_por_posicao(self, pos, cartas_banco):
        slots = self._rects_slots(max(6, len(cartas_banco)))
        for indice in range(min(len(cartas_banco), len(slots)) - 1, -1, -1):
            slot = slots[indice]
            if slot.collidepoint(pos):
                return {"indice": indice, "carta": cartas_banco[indice], "rect": slot}
        return None

    def desenhar(self, tela, cartas_banco, cartas_selecionadas=None, cartas_drag=None, ouro=None):
        cartas_selecionadas = cartas_selecionadas or set()
        pygame.draw.rect(tela, (68, 52, 38), self.rect, border_radius=14)
        pygame.draw.rect(tela, (158, 132, 102), self.rect, width=2, border_radius=14)
        tela.blit(self.fonte_titulo.render("Banco", True, (236, 236, 236)), (self.rect.x + 12, self.rect.y + 8))

        contador = self.fonte_carta.render(f"{len(cartas_banco)}/{self.limite_cartas}", True, (236, 236, 236))
        tela.blit(contador, (self.rect.x + 140, self.rect.y + 14))

        if ouro is not None:
            txt_ouro = self.fonte_titulo.render(f"Ouro: {ouro}", True, (236, 218, 126))
            tela.blit(txt_ouro, (self.rect.right - txt_ouro.get_width() - 12, self.rect.y + 8))

        cartas_visiveis = cartas_banco[: self.limite_cartas]
        slots = self._rects_slots(max(6, len(cartas_visiveis)))
        mouse = pygame.mouse.get_pos()
        hover_indice = None
        cartas_drag_uids = {str(c.get("uid")) for c in (cartas_drag or []) if isinstance(c, dict) and c.get("uid") is not None}
        for indice in range(min(len(cartas_visiveis), len(slots)) - 1, -1, -1):
            carta = cartas_visiveis[indice]
            uid_hover = str(carta.get("uid")) if isinstance(carta, dict) else str(getattr(carta, "uid", ""))
            if uid_hover in cartas_drag_uids:
                continue
            if slots[indice].collidepoint(mouse):
                hover_indice = indice
                break

        for indice, slot in enumerate(slots):
            if indice < len(cartas_visiveis):
                carta = cartas_visiveis[indice]
                uid_raw = carta.get("uid", f"carta-{indice}") if isinstance(carta, dict) else getattr(carta, "uid", f"carta-{indice}")
                uid_str = str(uid_raw)
                if uid_str in cartas_drag_uids:
                    continue
                uid = uid_raw
                atual = self.escala_hover.get(uid, 1.0)
                alvo = 1.04 if indice == hover_indice else 1.0
                atual += (alvo - atual) * 0.28
                self.escala_hover[uid] = atual

                selecionada = uid in cartas_selecionadas
                base_rect = slot.move(0, -8) if selecionada else slot
                centro = base_rect.center
                largura = int(base_rect.width * atual)
                altura = int(base_rect.height * atual)
                card_rect = pygame.Rect(0, 0, largura, altura)
                card_rect.center = (centro[0], centro[1] - (2 if indice == hover_indice else 0))

                if indice == hover_indice:
                    continue

                construtor_visual_cartucho.desenhar_cartucho(tela, carta, card_rect, selecionada=selecionada)

        if hover_indice is not None and hover_indice < len(cartas_visiveis):
            if str((cartas_visiveis[hover_indice] or {}).get("uid")) in cartas_drag_uids:
                hover_indice = None

        if hover_indice is not None and hover_indice < len(cartas_visiveis):
            carta = cartas_visiveis[hover_indice]
            uid = carta.get("uid", f"carta-{hover_indice}") if isinstance(carta, dict) else getattr(carta, "uid", f"carta-{hover_indice}")
            selecionada = uid in cartas_selecionadas
            slot = slots[hover_indice]
            atual = self.escala_hover.get(uid, 1.0)
            base_rect = slot.move(0, -8) if selecionada else slot
            centro = base_rect.center
            largura = int(base_rect.width * atual)
            altura = int(base_rect.height * atual)
            card_rect = pygame.Rect(0, 0, largura, altura)
            card_rect.center = (centro[0], centro[1] - 2)
            construtor_visual_cartucho.desenhar_cartucho(tela, carta, card_rect, selecionada=selecionada, destacada=True)

        if cartas_drag:
            mouse = pygame.mouse.get_pos()
            largura = 180
            altura = 116
            espacamento = 18
            for i, carta in enumerate(cartas_drag):
                ghost = pygame.Rect(mouse[0] - largura // 2 + i * espacamento, mouse[1] - altura // 2 + i * 6, largura, altura)
                construtor_visual_cartucho.desenhar_cartucho(tela, carta, ghost, destacada=True, alpha=220)
