import csv
import unicodedata
from pathlib import Path


CUSTO_POR_RARIDADE = {
    "comum": 1,
    "incomum": 2,
    "raro": 3,
    "epico": 4,
    "lendario": 5,
    "mitico": 6,
}

QUANTIDADE_POR_RARIDADE = {
    "comum": 12,
    "incomum": 11,
    "raro": 9,
    "epico": 8,
    "lendario": 5,
    "mitico": 4,
}

ARQUIVO_BRAWLERS = Path("Sets/BrawlStars/Dados/Personagens.csv")
PASTA_IMAGENS = Path("Sets/BrawlStars/Imagens/Personagens")


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return "".join(char.lower() for char in texto if char.isalnum())


def _indice_imagens():
    imagens = {}
    for arquivo in PASTA_IMAGENS.glob("*_portrait.png"):
        chave = _normalizar(arquivo.stem.replace("_portrait", ""))
        imagens[chave] = arquivo
    return imagens


def _imagem_brawler(nome, imagens_por_chave):
    arquivo = imagens_por_chave.get(_normalizar(nome))
    return str(arquivo) if arquivo is not None else ""


def criar_cartas_teste():
    imagens_por_chave = _indice_imagens()
    cartas = []

    with ARQUIVO_BRAWLERS.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for indice, linha in enumerate(leitor, start=1):
            nome = str(linha.get("Nome") or "").strip()
            raridade = str(linha.get("Raridade") or "comum").strip().lower()
            sinergias = [
                str(linha.get("Sinergia 1") or "").strip(),
                str(linha.get("Sinergia 2") or "").strip(),
                str(linha.get("Sinergia 3") or "").strip(),
                str(linha.get("Sinergia 4") or "").strip(),
            ]

            sinergias_validas = [s for s in sinergias if s and s != "-"]
            raridade = raridade if raridade in CUSTO_POR_RARIDADE else "comum"

            cartas.append(
                {
                    "id": f"brawl-{indice:03d}",
                    "nome": nome or f"Brawler {indice}",
                    "sinergia": sinergias_validas[0] if len(sinergias_validas) > 0 else "-",
                    "sinergia_secundaria": sinergias_validas[1] if len(sinergias_validas) > 1 else None,
                    "sinergia_terciaria": sinergias_validas[2] if len(sinergias_validas) > 2 else None,
                    "sinergia_quaternaria": sinergias_validas[3] if len(sinergias_validas) > 3 else None,
                    "sinergias": sinergias_validas,
                    "raridade": raridade,
                    "custo": CUSTO_POR_RARIDADE[raridade],
                    "imagem": _imagem_brawler(nome, imagens_por_chave),
                    "vida": str(linha.get("Vida") or "-").strip() or "-",
                    "atk": str(linha.get("Atk") or "-").strip() or "-",
                    "spd": str(linha.get("SpD") or linha.get("Spd") or "-").strip() or "-",
                    "spa": str(linha.get("SpA") or "-").strip() or "-",
                    "vel": str(linha.get("Vel") or "-").strip() or "-",
                    "def": str(linha.get("Def") or "-").strip() or "-",
                    "descricao": str(linha.get("Descrição") or "").strip(),
                    "set": "BrawlStars",
                }
            )

    return cartas


def criar_estoque_por_raridade(cartas):
    estoque = {}
    for carta in cartas:
        raridade = str(carta.get("raridade", "comum")).lower()
        estoque[carta["id"]] = QUANTIDADE_POR_RARIDADE.get(raridade, QUANTIDADE_POR_RARIDADE["comum"])
    return estoque
