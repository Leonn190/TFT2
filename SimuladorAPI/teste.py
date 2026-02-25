import csv
from pathlib import Path


RARIDADE_CUSTO = {
    "comum": 1,
    "incomum": 2,
    "raro": 3,
    "epico": 4,
    "lendario": 5,
    "mitico": 6,
}


def _normalizar_raridade(valor):
    raridade = (valor or "comum").strip().lower()
    if raridade not in RARIDADE_CUSTO:
        return "comum"
    return raridade


def criar_cartas_teste(set_nome="BrawlStars"):
    caminho_csv = Path("Sets") / set_nome / "Dados" / "Personagens.csv"
    if not caminho_csv.exists():
        return []

    cartas = []
    with caminho_csv.open(encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            raridade = _normalizar_raridade(linha.get("raridade"))
            cartas.append(
                {
                    "id": linha.get("id") or f"{set_nome.lower()}-{len(cartas) + 1:02d}",
                    "nome": linha.get("nome", "Sem nome"),
                    "raridade": raridade,
                    "custo": int(linha.get("custo") or RARIDADE_CUSTO[raridade]),
                    "sinergia": linha.get("sinergia", "-"),
                    "sinergia_secundaria": linha.get("sinergia_secundaria") or None,
                    "imagem": linha.get("imagem") or "Brawl_Stars_iOS_ícone.jpg",
                    "set_nome": set_nome,
                }
            )
    return cartas
