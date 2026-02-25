from __future__ import annotations

import math


def calcular_dano_colisao(atacante):
    return atacante.atk * 0.60 + atacante.velocidade_escalar * 0.25 + atacante.massa * 0.15


def aplicar_reducao_armadura_lol(dano_bruto, armadura):
    armadura = float(armadura)
    if armadura >= 0:
        return dano_bruto * (100.0 / (100.0 + armadura))
    return dano_bruto * (2.0 - (100.0 / (100.0 - armadura)))


def atualizar_movimento(personagem, arena_rect, dt):
    personagem.x += personagem.vx * dt
    personagem.y += personagem.vy * dt

    if personagem.x - personagem.raio <= arena_rect.left:
        personagem.x = arena_rect.left + personagem.raio
        personagem.vx *= -1
    elif personagem.x + personagem.raio >= arena_rect.right:
        personagem.x = arena_rect.right - personagem.raio
        personagem.vx *= -1

    if personagem.y - personagem.raio <= arena_rect.top:
        personagem.y = arena_rect.top + personagem.raio
        personagem.vy *= -1
    elif personagem.y + personagem.raio >= arena_rect.bottom:
        personagem.y = arena_rect.bottom - personagem.raio
        personagem.vy *= -1


def resolver_colisao_elastica(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    distancia = math.hypot(dx, dy)
    min_dist = a.raio + b.raio

    if distancia <= 0:
        distancia = 0.01
        dx = 0.01
        dy = 0

    if distancia >= min_dist:
        return False

    nx = dx / distancia
    ny = dy / distancia

    sobreposicao = min_dist - distancia
    total_massa = a.massa + b.massa
    a.x -= nx * sobreposicao * (b.massa / total_massa)
    a.y -= ny * sobreposicao * (b.massa / total_massa)
    b.x += nx * sobreposicao * (a.massa / total_massa)
    b.y += ny * sobreposicao * (a.massa / total_massa)

    rvx = b.vx - a.vx
    rvy = b.vy - a.vy
    vel_normal = rvx * nx + rvy * ny
    if vel_normal > 0:
        return True

    restit = 0.92
    impulso = -(1 + restit) * vel_normal
    impulso /= (1 / a.massa) + (1 / b.massa)

    ix = impulso * nx
    iy = impulso * ny

    a.vx -= ix / a.massa
    a.vy -= iy / a.massa
    b.vx += ix / b.massa
    b.vy += iy / b.massa
    return True


def processar_dano_colisao(a, b):
    if a.equipe == b.equipe:
        return

    dano_a = aplicar_reducao_armadura_lol(calcular_dano_colisao(a), b.defesa)
    dano_b = aplicar_reducao_armadura_lol(calcular_dano_colisao(b), a.defesa)
    b.aplicar_dano(dano_a)
    a.aplicar_dano(dano_b)
