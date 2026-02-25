import csv
import unicodedata
from pathlib import Path


CUSTO_POR_RARIDADE_PADRAO = {
    "comum": 1,
    "incomum": 2,
    "raro": 3,
    "epico": 4,
    "lendario": 5,
    "mitico": 6,
}

QUANTIDADE_POR_RARIDADE_PADRAO = {
    "comum": 12,
    "incomum": 11,
    "raro": 9,
    "epico": 8,
    "lendario": 5,
    "mitico": 4,
}


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return "".join(char.lower() for char in texto if char.isalnum())


def _arquivo_brawlers(set_escolhido):
    return Path("Sets") / str(set_escolhido or "BrawlStars") / "Dados" / "Personagens.csv"


def _pasta_imagens(set_escolhido):
    return Path("Sets") / str(set_escolhido or "BrawlStars") / "Imagens" / "Personagens"


def _indice_imagens(set_escolhido):
    imagens = {}
    pasta_imagens = _pasta_imagens(set_escolhido)
    for arquivo in pasta_imagens.glob("*_portrait.png"):
        chave = _normalizar(arquivo.stem.replace("_portrait", ""))
        imagens[chave] = arquivo
    return imagens


def _imagem_brawler(nome, imagens_por_chave):
    arquivo = imagens_por_chave.get(_normalizar(nome))
    return str(arquivo) if arquivo is not None else ""


def criar_cartas_teste(set_escolhido="BrawlStars", regras=None):
    regras = regras or {}
    custo_por_raridade = regras.get("custo_por_raridade") or CUSTO_POR_RARIDADE_PADRAO

    imagens_por_chave = _indice_imagens(set_escolhido)
    cartas = []

    with _arquivo_brawlers(set_escolhido).open(encoding="utf-8-sig", newline="") as arquivo:
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
            raridade = raridade if raridade in custo_por_raridade else "comum"

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
                    "custo": custo_por_raridade[raridade],
                    "imagem": _imagem_brawler(nome, imagens_por_chave),
                    "vida": str(linha.get("Vida") or "-").strip() or "-",
                    "atk": str(linha.get("Atk") or "-").strip() or "-",
                    "spd": str(linha.get("SpD") or linha.get("Spd") or "-").strip() or "-",
                    "spa": str(linha.get("SpA") or "-").strip() or "-",
                    "vel": str(linha.get("Vel") or "-").strip() or "-",
                    "def": str(linha.get("Def") or "-").strip() or "-",
                    "descricao": str(linha.get("Descrição") or "").strip(),
                    "set": set_escolhido,
                }
            )

    return cartas


def criar_estoque_por_raridade(cartas, regras=None):
    regras = regras or {}
    quantidade_por_raridade = regras.get("quantidade_estoque_por_raridade") or QUANTIDADE_POR_RARIDADE_PADRAO

    estoque = {}
    for carta in cartas:
        raridade = str(carta.get("raridade", "comum")).lower()
        estoque[carta["id"]] = quantidade_por_raridade.get(raridade, quantidade_por_raridade["comum"])
    return estoque
