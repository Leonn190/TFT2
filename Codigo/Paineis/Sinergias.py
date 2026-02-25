import csv
from pathlib import Path

import pygame

from Codigo.Modulos.ConstrutorVisual import CORES_RARIDADE
from Codigo.Modulos.GeradoresVisuais import obter_fonte
from Codigo.Prefabs.Tooltip import tooltip_padrao


ORDEM_RARIDADE = {"comum": 0, "incomum": 1, "raro": 2, "epico": 3, "lendario": 4, "mitico": 5}


class Sinergias:
    def __init__(self, largura_tela=1920, altura_tela=1080):
        self.rect = pygame.Rect(30, 120, int(largura_tela * 0.16), int(altura_tela * 0.56))
        self.fonte_titulo = obter_fonte(30)
        self.fonte_item = obter_fonte(22)
        self._cache_set = {}
        self._cache_imagens = {}

    @staticmethod
    def _listar_sinergias_carta(carta):
        sinergias = []
        for campo in ("sinergia", "sinergia_secundaria", "sinergia_terciaria", "sinergia_quaternaria"):
            valor = carta.get(campo)
            if valor and valor != "-":
                sinergias.append(str(valor))
        extras = carta.get("sinergias", [])
        if isinstance(extras, (list, tuple)):
            for item in extras:
                if item and item != "-":
                    sinergias.append(str(item))
        return set(sinergias)

    def _carregar_dados_set(self, set_nome="BrawlStars"):
        if set_nome in self._cache_set:
            return self._cache_set[set_nome]

        base = Path("Sets") / str(set_nome) / "Dados"
        arquivo_personagens = base / "Personagens.csv"
        arquivo_sinergias = base / "Sinergias.csv"

        metadados = {}
        personagens_por_sinergia = {}

        if arquivo_sinergias.exists():
            with arquivo_sinergias.open(encoding="utf-8-sig", newline="") as arquivo:
                leitor = csv.reader(arquivo)
                niveis_atuais = []
                for linha in leitor:
                    if not linha:
                        continue
                    chave = str(linha[0] or "").strip()
                    if not chave:
                        continue

                    if chave.lower().replace(" ", "") == "nivel":
                        niveis_atuais = []
                        for valor in linha[1:-1]:
                            try:
                                niveis_atuais.append(int(str(valor).strip()))
                            except ValueError:
                                pass
                        continue

                    descricao = ""
                    if linha:
                        descricao = str(linha[-1] or "").strip()
                    metadados[chave] = {
                        "breakpoints": list(niveis_atuais),
                        "descricao": descricao,
                    }

        if arquivo_personagens.exists():
            with arquivo_personagens.open(encoding="utf-8-sig", newline="") as arquivo:
                leitor = csv.DictReader(arquivo)
                for linha in leitor:
                    nome = str(linha.get("Nome") or "").strip()
                    raridade = str(linha.get("Raridade") or "comum").strip().lower()
                    sinergias = [
                        str(linha.get("Sinergia 1") or "").strip(),
                        str(linha.get("Sinergia 2") or "").strip(),
                        str(linha.get("Sinergia 3") or "").strip(),
                        str(linha.get("Sinergia 4") or "").strip(),
                    ]
                    nome_arquivo = nome.replace("/", "-").replace("\\", "-")
                    imagem = Path("Sets") / str(set_nome) / "Imagens" / "Personagens" / f"{nome_arquivo}_portrait.png"

                    carta = {
                        "nome": nome,
                        "raridade": raridade if raridade in ORDEM_RARIDADE else "comum",
                        "imagem": str(imagem),
                        "sinergias": [item for item in sinergias if item and item != "-"],
                    }
                    for sinergia in carta["sinergias"]:
                        personagens_por_sinergia.setdefault(sinergia, []).append(carta)

        for sinergia, cartas in personagens_por_sinergia.items():
            cartas.sort(key=lambda item: (ORDEM_RARIDADE.get(item["raridade"], 99), item["nome"]))
            metadados.setdefault(sinergia, {"breakpoints": [], "descricao": ""})

        dados = {"metadados": metadados, "personagens": personagens_por_sinergia}
        self._cache_set[set_nome] = dados
        return dados

    def _linhas(self, sinergias, mapa_slots, set_nome):
        dados = self._carregar_dados_set(set_nome)
        contagem_por_sinergia = {str(item.get("sinergia")): int(item.get("quantidade", 0)) for item in sinergias or []}

        ids_em_campo = {}
        nomes_em_campo = {}
        for slot in mapa_slots or []:
            carta = slot.get("carta") if isinstance(slot, dict) else None
            if not carta:
                continue
            carta_id = str(carta.get("id") or "")
            nome = str(carta.get("nome") or "")
            for sinergia in self._listar_sinergias_carta(carta):
                ids_em_campo.setdefault(sinergia, set()).add(carta_id)
                nomes_em_campo.setdefault(sinergia, set()).add(nome)

        linhas = []
        for nome, quantidade in sorted(
            contagem_por_sinergia.items(),
            key=lambda item: (-(item[1] >= (dados["metadados"].get(item[0], {}).get("breakpoints", [1])[0] if dados["metadados"].get(item[0], {}).get("breakpoints") else 1)), -item[1], item[0]),
        ):
            meta = dados["metadados"].get(nome, {"breakpoints": [], "descricao": ""})
            breakpoints = list(meta.get("breakpoints", []))
            proximo = next((nivel for nivel in breakpoints if quantidade < nivel), breakpoints[-1] if breakpoints else quantidade)
            atual = quantidade if quantidade <= proximo else proximo

            linhas.append(
                {
                    "sinergia": nome,
                    "quantidade": quantidade,
                    "breakpoints": breakpoints,
                    "descricao": str(meta.get("descricao") or "").strip() or "ainda não adicionado",
                    "progresso": f"{atual}/{proximo}" if proximo else f"{quantidade}",
                    "ativada": quantidade >= breakpoints[0] if breakpoints else quantidade > 0,
                    "cartas_set": dados["personagens"].get(nome, []),
                    "ids_em_campo": ids_em_campo.get(nome, set()),
                    "nomes_em_campo": nomes_em_campo.get(nome, set()),
                }
            )
        return linhas

    def obter_hover_info(self, mouse_pos, sinergias, mapa_slots, set_nome="BrawlStars"):
        y = self.rect.y + 52
        for linha in self._linhas(sinergias, mapa_slots, set_nome):
            rect_item = pygame.Rect(self.rect.x + 8, y - 2, self.rect.width - 16, 30)
            if rect_item.collidepoint(mouse_pos):
                return linha
            y += 32
        return None

    def _imagem_card_tooltip(self, carta, em_campo=False):
        tamanho = (42, 42)
        chave = (carta.get("imagem"), bool(em_campo))
        if chave in self._cache_imagens:
            return self._cache_imagens[chave]

        superficie = pygame.Surface(tamanho, pygame.SRCALPHA)
        cor_raridade = CORES_RARIDADE.get(str(carta.get("raridade", "comum")).lower(), CORES_RARIDADE["comum"])
        pygame.draw.rect(superficie, cor_raridade, superficie.get_rect(), border_radius=4)
        pygame.draw.rect(superficie, (0, 0, 0), superficie.get_rect(), width=1, border_radius=4)

        imagem_path = Path(str(carta.get("imagem") or ""))
        if imagem_path.exists():
            imagem = pygame.image.load(str(imagem_path)).convert_alpha()
            imagem = pygame.transform.smoothscale(imagem, (36, 36))
            if not em_campo:
                imagem.set_alpha(90)
            superficie.blit(imagem, (3, 3))
        else:
            cor = (48, 54, 64, 200 if em_campo else 120)
            pygame.draw.rect(superficie, cor, pygame.Rect(3, 3, 36, 36))

        if not em_campo:
            sombra = pygame.Surface((36, 36), pygame.SRCALPHA)
            sombra.fill((24, 26, 30, 100))
            superficie.blit(sombra, (3, 3))

        self._cache_imagens[chave] = superficie
        return superficie

    def desenhar(self, tela, sinergias, mapa_slots=None, set_nome="BrawlStars", hover_info=None):
        tela.blit(self.fonte_titulo.render("Sinergias", True, (236, 236, 236)), (self.rect.x + 10, self.rect.y + 8))

        linhas = self._linhas(sinergias, mapa_slots, set_nome)
        y = self.rect.y + 52
        if not linhas:
            vazio = self.fonte_item.render("Sem tropas", True, (184, 190, 198))
            tela.blit(vazio, (self.rect.x + 12, y))
            return

        mouse_pos = pygame.mouse.get_pos()
        for linha in linhas:
            nome = linha["sinergia"]
            quantidade = linha["quantidade"]
            texto_linha = f"{nome} {linha['progresso']}"
            cor = (226, 230, 236) if linha["ativada"] else (130, 136, 146)
            rect_item = pygame.Rect(self.rect.x + 8, y - 2, self.rect.width - 16, 30)

            if rect_item.collidepoint(mouse_pos):
                pygame.draw.rect(tela, (66, 74, 92), rect_item, border_radius=6)
            txt = self.fonte_item.render(texto_linha, True, cor)
            tela.blit(txt, (self.rect.x + 12, y))

            y += 32

        if hover_info:
            cards = []
            for carta in hover_info.get("cartas_set", []):
                em_campo = str(carta.get("nome") or "") in hover_info.get("nomes_em_campo", set())
                cards.append(self._imagem_card_tooltip(carta, em_campo=em_campo))

            linhas_tooltip = [
                f"Próximo marco: {hover_info.get('progresso', '-')}",
                f"Descrição: {hover_info.get('descricao', 'ainda não adicionado')}",
                "Composição:",
            ]
            tooltip_padrao.desenhar(
                tela,
                titulo=hover_info.get("sinergia", "Sinergia"),
                linhas_texto=linhas_tooltip,
                cards=cards,
                posicao=(mouse_pos[0] + 18, mouse_pos[1] + 18),
                largura=390,
            )
