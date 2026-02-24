from pathlib import Path

from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Prefabs.Botao import Botao


def listar_sets_existentes(caminho_sets="Recursos/Sets"):
    raiz = Path(caminho_sets)
    if not raiz.exists() or not raiz.is_dir():
        return []

    return sorted(
        pasta.name
        for pasta in raiz.iterdir()
        if pasta.is_dir() and not pasta.name.startswith(".")
    )


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
    TELA.fill(obter_cor("fundo_menu"))

    fonte_titulo = obter_fonte(58, negrito=True)
    fonte_subtitulo = obter_fonte(30)

    titulo = fonte_titulo.render("Escolha o Set", True, obter_cor("titulo"))
    subtitulo = fonte_subtitulo.render("Um botão para cada set disponível", True, obter_cor("subtitulo"))

    TELA.blit(titulo, titulo.get_rect(center=(960, 140)))
    TELA.blit(subtitulo, subtitulo.get_rect(center=(960, 200)))

    for botao in Parametros["EscolhaSet"]["BotoesSets"]:
        botao.desenhar(TELA)

    Parametros["EscolhaSet"]["BotaoVoltar"].desenhar(TELA)
