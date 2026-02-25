from copy import deepcopy
from importlib import import_module


REGRAS_PARTIDA_PADRAO = {
    "tempo_entre_combates_ms": 40000,
    "trilha_batalhas": [
        {"tipo": "normal", "resultado": None},
        {"tipo": "augment", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "augment", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "augment", "resultado": None},
        {"tipo": "normal", "resultado": None},
    ],
    "custo_por_raridade": {
        "comum": 1,
        "incomum": 2,
        "raro": 3,
        "epico": 4,
        "lendario": 5,
        "mitico": 6,
    },
    "quantidade_estoque_por_raridade": {
        "comum": 12,
        "incomum": 11,
        "raro": 9,
        "epico": 8,
        "lendario": 5,
        "mitico": 4,
    },
    "raridades_bloqueadas_banco_inicial": ["epico", "lendario", "mitico"],
    "chances_loja_por_slots": {
        1: {"comum": 80, "incomum": 15, "raro": 5, "epico": 0, "lendario": 0, "mitico": 0},
        3: {"comum": 62, "incomum": 30, "raro": 8, "epico": 0, "lendario": 0, "mitico": 0},
        4: {"comum": 50, "incomum": 38, "raro": 10, "epico": 2, "lendario": 0, "mitico": 0},
        5: {"comum": 40, "incomum": 42, "raro": 15, "epico": 3, "lendario": 0, "mitico": 0},
        6: {"comum": 29, "incomum": 45, "raro": 20, "epico": 5, "lendario": 1, "mitico": 0},
        7: {"comum": 22, "incomum": 38, "raro": 30, "epico": 8, "lendario": 2, "mitico": 0},
        8: {"comum": 20, "incomum": 28, "raro": 38, "epico": 10, "lendario": 3, "mitico": 1},
        9: {"comum": 18, "incomum": 22, "raro": 31, "epico": 20, "lendario": 6, "mitico": 3},
        10: {"comum": 16, "incomum": 20, "raro": 25, "epico": 25, "lendario": 10, "mitico": 4},
        11: {"comum": 15, "incomum": 18, "raro": 21, "epico": 26, "lendario": 15, "mitico": 5},
        12: {"comum": 13, "incomum": 15, "raro": 18, "epico": 24, "lendario": 20, "mitico": 10},
        13: {"comum": 12, "incomum": 13, "raro": 15, "epico": 20, "lendario": 25, "mitico": 15},
        14: {"comum": 10, "incomum": 10, "raro": 12, "epico": 18, "lendario": 30, "mitico": 20},
        15: {"comum": 8, "incomum": 9, "raro": 10, "epico": 16, "lendario": 32, "mitico": 25},
    },
}


def _mesclar_dicts(base, sobrescrita):
    for chave, valor in sobrescrita.items():
        if isinstance(valor, dict) and isinstance(base.get(chave), dict):
            _mesclar_dicts(base[chave], valor)
        else:
            base[chave] = deepcopy(valor)


def carregar_regras_partida(set_escolhido):
    regras = deepcopy(REGRAS_PARTIDA_PADRAO)
    nome_set = str(set_escolhido or "BrawlStars")

    try:
        modulo_mecanicas = import_module(f"Sets.{nome_set}.Codigo.Mecanicas")
    except ModuleNotFoundError:
        return regras

    if hasattr(modulo_mecanicas, "REGRAS_PARTIDA"):
        _mesclar_dicts(regras, getattr(modulo_mecanicas, "REGRAS_PARTIDA"))

    if hasattr(modulo_mecanicas, "configurar_regras"):
        regras_customizadas = modulo_mecanicas.configurar_regras(deepcopy(regras))
        if isinstance(regras_customizadas, dict):
            _mesclar_dicts(regras, regras_customizadas)

    return regras
