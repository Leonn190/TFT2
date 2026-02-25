from pathlib import Path


RARIDADES = ["comum", "incomum", "raro", "epico", "lendario", "mitico"]
CUSTO_POR_RARIDADE = {
    "comum": 1,
    "incomum": 2,
    "raro": 3,
    "epico": 4,
    "lendario": 5,
    "mitico": 6,
}

BRAWLERS_BASE = [
    ("Shelly", "Atirador", "Controle", "comum"),
    ("Colt", "Atirador", "Dano", "comum"),
    ("Poco", "Suporte", "Místico", "comum"),
    ("Nita", "Invocador", "Lutador", "comum"),
    ("Bull", "Tanque", "Lutador", "incomum"),
    ("Jessie", "Invocador", "Controle", "incomum"),
    ("Rosa", "Tanque", "Lutador", "incomum"),
    ("El Primo", "Tanque", "Mergulho", "incomum"),
    ("Barley", "Arremessador", "Controle", "raro"),
    ("Penny", "Invocador", "Arremessador", "raro"),
    ("Dynamike", "Arremessador", "Dano", "raro"),
    ("Bo", "Controle", "Atirador", "raro"),
    ("Bibi", "Lutador", "Mergulho", "epico"),
    ("Pam", "Suporte", "Tanque", "epico"),
    ("Frank", "Tanque", "Controle", "epico"),
    ("Piper", "Atirador", "Crítico", "epico"),
    ("Spike", "Mítico", "Controle", "lendario"),
    ("Sandy", "Místico", "Suporte", "lendario"),
    ("Leon", "Mergulho", "Assassino", "lendario"),
    ("Meg", "Tanque", "Tecnologia", "mitico"),
    ("Chester", "Caótico", "Místico", "mitico"),
    ("Cordelius", "Místico", "Assassino", "mitico"),
]


def _slug(nome):
    nome = nome.lower().replace(" ", "")
    mapeamentos = {
        "elprimo": "elprimo",
    }
    return mapeamentos.get(nome, nome)


def criar_cartas_teste():
    raiz_imagens = Path("Sets/BrawlStars/Imagens/Personagens")
    cartas = []

    for indice, (nome, sinergia, sinergia_secundaria, raridade) in enumerate(BRAWLERS_BASE, start=1):
        slug = _slug(nome)
        caminho_imagem = raiz_imagens / f"{slug}_portrait.png"
        if not caminho_imagem.exists():
            caminho_imagem = raiz_imagens / f"{nome.lower()}_portrait.png"

        cartas.append(
            {
                "id": f"brawl-{indice:03d}",
                "nome": nome,
                "sinergia": sinergia,
                "sinergia_secundaria": sinergia_secundaria,
                "raridade": raridade,
                "custo": CUSTO_POR_RARIDADE[raridade],
                "imagem": str(caminho_imagem),
                "set": "BrawlStars",
            }
        )

    return cartas
