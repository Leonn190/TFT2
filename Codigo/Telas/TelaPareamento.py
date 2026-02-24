from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Prefabs.Botao import Botao


def InicializaTelaPareamento():
    return {
        "BotaoCancelar": Botao(60, 920, 260, 70, "Cancelar"),
    }


def TelaPareamento(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill(obter_cor("fundo_pareamento"))

    fonte_titulo = obter_fonte(56, negrito=True)
    fonte_texto = obter_fonte(34)

    titulo = fonte_titulo.render("Pareamento", True, obter_cor("titulo"))
    TELA.blit(titulo, titulo.get_rect(center=(960, 150)))

    dados = Parametros.get("ResultadoPareamento", {})
    tempo = dados.get("tempo_espera", 0)
    jogadores = dados.get("jogadores_na_fila", 0)
    tamanho = dados.get("tamanho_partida", 10)
    sets_escolhidos = Parametros.get("SetsSelecionados", [])
    texto_sets = ", ".join(sets_escolhidos) if sets_escolhidos else "-"

    linhas = [
        f"Sets: {texto_sets}",
        f"Tempo de espera: {tempo:.1f}s",
        f"Jogadores: {jogadores}/{tamanho}",
        "Se não completar em 20s, bots entram automaticamente.",
    ]

    y = 290
    for linha in linhas:
        texto = fonte_texto.render(linha, True, obter_cor("texto"))
        TELA.blit(texto, texto.get_rect(center=(960, y)))
        y += 70

    Parametros["Pareamento"]["BotaoCancelar"].desenhar(TELA)
