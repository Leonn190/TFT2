import random


CORES_BASE = [
    "Vermelho",
    "Azul",
    "Verde",
    "Amarelo",
    "Roxo",
    "Laranja",
    "Ciano",
    "Rosa",
    "Branco",
    "Preto",
    "Marrom",
    "Dourado",
    "Prata",
    "Turquesa",
    "Magenta",
    "Lima",
    "Anil",
    "Coral",
    "Lavanda",
    "Bege",
]

SINERGIAS_TESTE = ["Bonita", "Feia", "Rápida", "Lenta", "Brilhante", "Sombria"]


def criar_cartas_teste():
    cartas = []
    for indice, cor in enumerate(CORES_BASE, start=1):
        cartas.append(
            {
                "id": f"teste-{indice:02d}",
                "nome": cor,
                "sinergia": random.choice(SINERGIAS_TESTE),
                "custo": 3,
            }
        )
    return cartas
