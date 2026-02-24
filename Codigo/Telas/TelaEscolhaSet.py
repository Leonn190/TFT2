import pygame

from Codigo.Prefabs.Botao import Botao


def InicializaTelaEscolhaSet(CONFIG):
    botoes_sets = []
    largura = 320
    altura = 80
    espaco = 24
    x = (1920 - largura) // 2
    y_inicial = 260

    for indice, set_nome in enumerate(CONFIG.get("SetsDisponiveis", [])):
        y = y_inicial + indice * (altura + espaco)
        botoes_sets.append(Botao(x, y, largura, altura, set_nome))

    botao_voltar = Botao(60, 920, 220, 70, "Voltar")

    return {
        "BotoesSets": botoes_sets,
        "BotaoVoltar": botao_voltar,
    }


def TelaEscolhaSet(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((22, 26, 44))

    fonte_titulo = pygame.font.SysFont("arial", 58, bold=True)
    fonte_subtitulo = pygame.font.SysFont("arial", 30)

    titulo = fonte_titulo.render("Escolha o Set", True, (244, 244, 244))
    subtitulo = fonte_subtitulo.render("Um botão para cada set disponível", True, (180, 190, 212))

    TELA.blit(titulo, titulo.get_rect(center=(960, 140)))
    TELA.blit(subtitulo, subtitulo.get_rect(center=(960, 200)))

    for botao in Parametros["EscolhaSet"]["BotoesSets"]:
        botao.desenhar(TELA)

    Parametros["EscolhaSet"]["BotaoVoltar"].desenhar(TELA)
