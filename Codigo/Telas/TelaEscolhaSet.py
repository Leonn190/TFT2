from pathlib import Path

import pygame

from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Prefabs.Botao import Botao


def listar_sets_existentes(caminho_sets="Sets"):
    raiz = Path(caminho_sets)
    if not raiz.exists() or not raiz.is_dir():
        return []
    if (raiz / "BrawlStars").is_dir():
        return ["BrawlStars"]
    return []


def _carregar_icone_brawl():
    caminho = Path("Sets/BrawlStars/Imagens/Brawl_Stars_iOS_ícone.jpg")
    if not caminho.exists():
        return None
    return pygame.image.load(str(caminho)).convert_alpha()


def InicializaTelaEscolhaSet(CONFIG):
    botoes_sets = []
    largura = 360
    altura = 80
    espaco = 20
    total_sets = len(CONFIG.get("SetsDisponiveis", []))
    largura_total = total_sets * largura + max(0, total_sets - 1) * espaco
    x_inicial = (1920 - largura_total) // 2
    y = 330

    for indice, set_nome in enumerate(CONFIG.get("SetsDisponiveis", [])):
        x = x_inicial + indice * (largura + espaco)
        botoes_sets.append(Botao(x, y, largura, altura, set_nome, estilo="selecao"))

    botao_voltar = Botao(60, 920, 220, 70, "Voltar")
    botao_buscar = Botao(1640, 920, 220, 70, "Buscar")

    return {
        "BotoesSets": botoes_sets,
        "BotaoVoltar": botao_voltar,
        "BotaoBuscar": botao_buscar,
        "IconeBrawl": _carregar_icone_brawl(),
    }


def TelaEscolhaSet(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill(obter_cor("fundo_menu"))

    fonte_titulo = obter_fonte(52, negrito=False)
    fonte_subtitulo = obter_fonte(30)

    titulo = fonte_titulo.render("Escolha os Sets", True, obter_cor("titulo"))
    subtitulo = fonte_subtitulo.render("Selecione um ou mais sets e clique em Buscar", True, obter_cor("subtitulo"))

    TELA.blit(titulo, titulo.get_rect(center=(960, 140)))
    TELA.blit(subtitulo, subtitulo.get_rect(center=(960, 200)))

    for botao in Parametros["EscolhaSet"]["BotoesSets"]:
        botao.desenhar(TELA)
        if botao.texto == "BrawlStars" and Parametros["EscolhaSet"].get("IconeBrawl") is not None:
            icone = pygame.transform.smoothscale(Parametros["EscolhaSet"]["IconeBrawl"], (52, 52))
            TELA.blit(icone, (botao.rect.x + 12, botao.rect.centery - 26))

    Parametros["EscolhaSet"]["BotaoVoltar"].desenhar(TELA)
    Parametros["EscolhaSet"]["BotaoBuscar"].desenhar(TELA)
