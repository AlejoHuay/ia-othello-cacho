"""Gu?a: 4. Formulaci?n de la Funci?n de Evaluaci?n; 7. Descripci?n de Funciones en el Art?culo.
Propuestas del grupo asistidas por IA; reglas delegadas al agente del docente.
Componentes [-1,1], pesos [0,55], suma 100: decisi?n de dise?o, no l?mite de la gu?a.
"""
import numpy as np

VERSIONES = ("fija", "etapas")
PESOS = {
    "fija": (10, 40, 35, 15),
    "apertura": (0, 35, 45, 20),
    "medio": (10, 40, 35, 15),
    "final": (55, 30, 10, 5),
}
DIRECCIONES = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))

def razon(a, b):
    return (a - b) / (a + b) if a + b else 0.0

def componentes(tablero, jugador, movimientos):
    """Diferencia normalizada de fichas, esquinas, movilidad y frontera inversa."""
    oponente = 3 - jugador
    n = tablero.shape[0]
    propias = int(np.count_nonzero(tablero == jugador))
    ajenas = int(np.count_nonzero(tablero == oponente))
    esquinas = (tablero[0,0], tablero[0,n-1], tablero[n-1,0], tablero[n-1,n-1])
    c = (esquinas.count(jugador) - esquinas.count(oponente)) / 4
    m = razon(len(movimientos(tablero, jugador)), len(movimientos(tablero, oponente)))
    frontera = [0, 0, 0]
    for r in range(n):
        for col in range(n):
            ficha = int(tablero[r, col])
            if ficha and any(0 <= r+dr < n and 0 <= col+dc < n and tablero[r+dr,col+dc] == 0
                             for dr, dc in DIRECCIONES):
                frontera[ficha] += 1
    return {"fichas": (propias-ajenas)/(n*n), "esquinas": c,
            "movilidad": m, "frontera": razon(frontera[oponente], frontera[jugador])}

def pesos(tablero, version):
    if version == "fija":
        return PESOS["fija"]
    if version != "etapas":
        raise ValueError("Evaluaci?n desconocida")
    ocupadas = np.count_nonzero(tablero)
    return PESOS["apertura" if ocupadas < 20 else "medio" if ocupadas < 45 else "final"]

def evaluar(tablero, jugador, version, movimientos):
    valores = componentes(tablero, jugador, movimientos)
    return sum(w * v for w, v in zip(pesos(tablero, version), valores.values()))
