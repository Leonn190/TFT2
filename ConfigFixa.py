CONFIG_FIXA = {
    "FPS": 120,
    "Volume": 0.5,
    "Claridade": 75,
    "Mudo": False,
    "MostrarFPS": False,
    "MostrarPing": False,
}


def carregar_configuracoes_fixas():
    return CONFIG_FIXA.copy()


def salvar_configuracoes_fixas(configuracoes):
    for chave in CONFIG_FIXA.keys():
        if chave in configuracoes:
            CONFIG_FIXA[chave] = configuracoes[chave]
