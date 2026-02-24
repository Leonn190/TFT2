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
        sinergia_principal = random.choice(SINERGIAS_TESTE)
        sinergias_secundarias = [sinergia for sinergia in SINERGIAS_TESTE if sinergia != sinergia_principal]
        cartas.append(
            {
                "id": f"teste-{indice:02d}",
                "nome": cor,
                "sinergia": sinergia_principal,
                "sinergia_secundaria": random.choice(sinergias_secundarias),
                "custo": 3,
            }
        )
    return cartas
