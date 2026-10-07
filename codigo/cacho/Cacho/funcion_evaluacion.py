"""
Funciones de evaluación para el Cacho (Parte III de la práctica EC02).

Contiene:
  * Tablas probabilísticas exactas del juego (252 manos posibles, reservas,
    matriz de transición de una tirada y programación dinámica por categoría).
  * FuncionEvaluacionBase: réplica de la ecuación (1) del enunciado
        E(s) = (p_MAX + a*V_MAX) - (p_MIN + a*V_MIN),  a = 0.6
    con los valores esperados ESTÁTICOS del programa base.
  * FuncionEvaluacionMejorada: E_nueva(s) = sum_i w_i * f_i(s) con
        f1  diferencia de puntaje
        f2  diferencia de valor futuro con valores esperados DINÁMICOS
            y peso adaptativo por etapa (flexibilidad)
        f3  oportunidad de la mano en curso (dados actuales + tiradas restantes)
        f4  término de riesgo (penalización por varianza dependiente de quién va
            ganando)

Convención de perspectiva: toda evaluación se calcula desde el punto de vista
de `jugador` (valores altos = bueno para `jugador`), sin importar a quién le
toca mover. Esto corrige el error de perspectiva del agente base.

Librerías: numpy (tablas vectorizadas) + biblioteca estándar.
"""
from collections import Counter
from dataclasses import dataclass, asdict
from functools import lru_cache
from itertools import combinations_with_replacement
from math import factorial, tanh, sqrt

import numpy as np

from AgenteCacho import CATEGORIAS, puntuar, normalizar

# ============================================================
# CONSTANTES DE LAS REGLAS (según el programa base)
# ============================================================

N_DADOS = 5
TIRADAS_POR_TURNO = 3            # re-tiradas disponibles tras la tirada inicial
N_CATEGORIAS = len(CATEGORIAS)   # 10 -> 10 rondas por jugador
PUNTAJE_MAXIMO = {c: (5 * int(c) if c in '123456' else
                      {'escalera': 25, 'full': 30, 'poker': 40, 'grande': 50}[c])
                  for c in CATEGORIAS}

# ============================================================
# TABLAS PROBABILÍSTICAS EXACTAS
# ============================================================

ESTADOS = list(combinations_with_replacement(range(1, 7), N_DADOS))   # 252 manos
IDX_ESTADO = {e: i for i, e in enumerate(ESTADOS)}
N_ESTADOS = len(ESTADOS)


@lru_cache(maxsize=None)
def distribucion_tirada(n):
    """Distribución exacta de lanzar n dados: tupla de (multiconjunto, prob)."""
    if n == 0:
        return (((), 1.0),)
    total = 6 ** n
    salida = []
    for combo in combinations_with_replacement(range(1, 7), n):
        formas = factorial(n)
        for v in Counter(combo).values():
            formas //= factorial(v)
        salida.append((combo, formas / total))
    return tuple(salida)


# Reservas: multiconjuntos de 0..4 dados que se conservan (se re-tira >= 1 dado)
RESERVAS = [r for k in range(N_DADOS)
            for r in combinations_with_replacement(range(1, 7), k)]       # 210
IDX_RESERVA = {r: i for i, r in enumerate(RESERVAS)}


@lru_cache(maxsize=None)
def resultados_reserva(reserva):
    """Para una reserva (tupla ordenada) devuelve tupla de (idx_estado, prob)."""
    acumulado = {}
    for combo, p in distribucion_tirada(N_DADOS - len(reserva)):
        i = IDX_ESTADO[normalizar(reserva + combo)]
        acumulado[i] = acumulado.get(i, 0.0) + p
    return tuple(acumulado.items())


def _matriz_transicion():
    m = np.zeros((len(RESERVAS), N_ESTADOS))
    for k, r in enumerate(RESERVAS):
        for i, p in resultados_reserva(r):
            m[k, i] = p
    return m


MATRIZ_T = _matriz_transicion()                      # (210 x 252), filas suman 1


def sub_reservas(dados):
    """Reservas DISTINTAS alcanzables desde una mano (poda de ramas equivalentes)."""
    dados = tuple(dados)
    vistas = set()
    for mascara in range(2 ** N_DADOS - 1):          # excluye 'conservar los 5'
        vistas.add(normalizar([dados[i] for i in range(N_DADOS) if mascara & (1 << i)]))
    return sorted(vistas, key=lambda r: (-len(r), r))


RESERVAS_DE = [[IDX_RESERVA[r] for r in sub_reservas(e)] for e in ESTADOS]
_ANCHO = max(len(x) for x in RESERVAS_DE)
_RESERVAS_PAD = np.array([x + [len(RESERVAS)] * (_ANCHO - len(x)) for x in RESERVAS_DE])

P_INICIAL = np.zeros(N_ESTADOS)                      # distribución de la tirada inicial
for _combo, _p in distribucion_tirada(N_DADOS):
    P_INICIAL[IDX_ESTADO[normalizar(_combo)]] += _p

PUNTOS = np.array([[puntuar(c, e) for e in ESTADOS] for c in CATEGORIAS], float)


def _dp_categoria(fila_puntos):
    """
    Programación dinámica exacta "apuntando" a una sola categoría.
    V[r][d] = valor esperado con mano d y r re-tiradas, jugando óptimamente
    para esa categoría (puede plantarse en cualquier momento).
    S[r][d] = segundo momento bajo la misma política (para la varianza).
    """
    V = [fila_puntos.copy()]
    S = [fila_puntos ** 2]
    for _ in range(TIRADAS_POR_TURNO):
        ev = np.append(MATRIZ_T @ V[-1], -np.inf)
        es = np.append(MATRIZ_T @ S[-1], 0.0)
        candidatos = ev[_RESERVAS_PAD]                   # (252 x ancho)
        mejor = candidatos.argmax(axis=1)
        mejor_k = _RESERVAS_PAD[np.arange(N_ESTADOS), mejor]
        mejor_v = ev[mejor_k]
        plantarse = fila_puntos >= mejor_v
        V.append(np.where(plantarse, fila_puntos, mejor_v))
        S.append(np.where(plantarse, fila_puntos ** 2, es[mejor_k]))
    return np.array(V), np.array(S)


_DP = {c: _dp_categoria(PUNTOS[i]) for i, c in enumerate(CATEGORIAS)}

# Valor esperado dinámico V_r^c(d) para cualquier mano y tiradas restantes
TABLA_VE = {c: _DP[c][0] for c in CATEGORIAS}                  # (4 x 252)
# Media y varianza de una categoría al inicio de un turno (mano recién tirada)
MU = {c: float(P_INICIAL @ _DP[c][0][TIRADAS_POR_TURNO]) for c in CATEGORIAS}
VAR = {c: max(0.0, float(P_INICIAL @ _DP[c][1][TIRADAS_POR_TURNO]) - MU[c] ** 2)
       for c in CATEGORIAS}


def valor_esperado_dinamico(categoria, dados, tiradas_restantes):
    """E[puntos en `categoria` | dados actuales, tiradas restantes]."""
    return float(TABLA_VE[categoria][tiradas_restantes][IDX_ESTADO[normalizar(dados)]])


# ============================================================
# FUNCIÓN DE EVALUACIÓN BASE (ecuación (1) del enunciado)
# ============================================================

_VE_ESTATICO = {c: sum(puntuar(c, e) for e in ESTADOS) / len(ESTADOS) for c in CATEGORIAS}


class FuncionEvaluacionBase:
    """
    E(s) = (p_j + a*Vfut_j) - (p_o + a*Vfut_o)

    Mismos valores esperados estáticos que AgenteCacho._valor_esperado_cat
    (promedio uniforme sobre los 252 multiconjuntos, NO ponderado por su
    probabilidad real). Se agrega el término futuro del oponente que la
    ecuación (1) incluye pero el código base omitía.
    """

    nombre = "base"

    def __init__(self, alfa=0.6):
        self.alfa = alfa
        self.llamadas = 0

    def __call__(self, estado, jugador):
        self.llamadas += 1
        t = estado.tablero
        o = 1 - jugador
        fut = [sum(_VE_ESTATICO[c] for c in CATEGORIAS if c not in t['usadas'][k])
               for k in (0, 1)]
        return ((t['puntajes'][jugador] + self.alfa * fut[jugador])
                - (t['puntajes'][o] + self.alfa * fut[o]))

    # Misma interfaz que FuncionEvaluacionMejorada para poder combinar
    # "búsqueda mejorada + función base" y aislar el aporte de cada parte.
    def evaluar(self, p_j, p_o, libres_j, libres_o, mueve_j, dados=None, tiradas=None):
        self.llamadas += 1
        return ((p_j + self.alfa * sum(_VE_ESTATICO[c] for c in libres_j))
                - (p_o + self.alfa * sum(_VE_ESTATICO[c] for c in libres_o)))

    def cota_superior_anotar(self, p_j, p_o, libres_j, libres_o):
        fut_o = self.alfa * sum(_VE_ESTATICO[c] for c in libres_o)
        return max(p_j + PUNTAJE_MAXIMO[c]
                   + self.alfa * sum(_VE_ESTATICO[x] for x in libres_j if x != c)
                   for c in libres_j) - p_o - fut_o


# ============================================================
# FUNCIÓN DE EVALUACIÓN MEJORADA
# ============================================================

@dataclass(frozen=True)
class Pesos:
    """
    Pesos de E_nueva. Rangos sugeridos para el ajuste (ver README):
      w_puntaje      1.0 fijo (escala de referencia: 1 unidad = 1 punto)
      w_futuro       [0.5, 1.5]  1.0 => los mu(c) son valores esperados exactos
      beta_etapa     [0.0, 0.5]  bonificación por flexibilidad al inicio
      w_oportunidad  [0.0, 1.5]  peso de la mano en curso
      w_riesgo       [0.0, 0.5]  aversión/búsqueda de riesgo según el marcador
      escala_riesgo  [10, 60]    puntos para saturar tanh
    """
    w_puntaje: float = 1.0
    w_futuro: float = 1.0
    beta_etapa: float = 0.10
    w_oportunidad: float = 1.0
    w_riesgo: float = 0.10
    escala_riesgo: float = 25.0

    def como_dict(self):
        return asdict(self)


class FuncionEvaluacionMejorada:
    nombre = "mejorada"

    def __init__(self, pesos=None):
        self.pesos = pesos or Pesos()
        self.llamadas = 0
        self._cache_opp = {}

    # ---------------- características individuales ----------------

    def suma_mu(self, libres):
        return sum(MU[c] for c in libres)

    def var_total(self, libres):
        return sum(VAR[c] for c in libres)

    def futuro_etapa(self, libres):
        """Phi(L) = (1 + beta*(|L|-1)/(N-1)) * sum mu(c): peso adaptativo por etapa."""
        n = len(libres)
        if n == 0:
            return 0.0
        factor = 1.0 + self.pesos.beta_etapa * (n - 1) / (N_CATEGORIAS - 1)
        return factor * self.suma_mu(libres)

    def oportunidad(self, libres, dados, tiradas):
        """G = max_c [V_r^c(dados) - mu(c)]: cuánto mejor es esta mano que una nueva."""
        if not libres:
            return 0.0
        i = IDX_ESTADO[normalizar(dados)]
        return max(TABLA_VE[c][tiradas][i] - MU[c] for c in libres)

    def oportunidad_esperada(self, libres):
        """E_d[G] para una mano recién tirada (cuando aún no se conocen los dados)."""
        clave = frozenset(libres)
        if clave not in self._cache_opp:
            if not libres:
                self._cache_opp[clave] = 0.0
            else:
                filas = np.array([TABLA_VE[c][TIRADAS_POR_TURNO] - MU[c] for c in libres])
                self._cache_opp[clave] = float(P_INICIAL @ filas.max(axis=0))
        return self._cache_opp[clave]

    def caracteristicas(self, p_j, p_o, libres_j, libres_o, mueve_j,
                        dados=None, tiradas=None):
        """
        Devuelve (f1, f2, f3, f4) desde la perspectiva de j.
        mueve_j: True si el siguiente en actuar es j.
        dados=None => la mano del que mueve aún no se ha tirado (usa E[G]).
        """
        f1 = p_j - p_o
        f2 = self.futuro_etapa(libres_j) - self.futuro_etapa(libres_o)
        libres_mueve = libres_j if mueve_j else libres_o
        if dados is None:
            g = self.oportunidad_esperada(libres_mueve)
        else:
            g = float(self.oportunidad(libres_mueve, dados, tiradas))
        f3 = g if mueve_j else -g
        delta_esp = f1 + self.suma_mu(libres_j) - self.suma_mu(libres_o)
        sigma = sqrt(self.var_total(libres_j) + self.var_total(libres_o))
        f4 = -tanh(delta_esp / self.pesos.escala_riesgo) * sigma
        return f1, f2, f3, f4

    def combinar(self, f):
        w = self.pesos
        return (w.w_puntaje * f[0] + w.w_futuro * f[1]
                + w.w_oportunidad * f[2] + w.w_riesgo * f[3])

    def evaluar(self, p_j, p_o, libres_j, libres_o, mueve_j, dados=None, tiradas=None):
        self.llamadas += 1
        return self.combinar(self.caracteristicas(p_j, p_o, libres_j, libres_o,
                                                  mueve_j, dados, tiradas))

    def cota_superior_anotar(self, p_j, p_o, libres_j, libres_o):
        """
        Cota superior de cualquier hoja 'anotar' del turno (para la poda Star1).
        Usa el puntaje máximo de cada categoría y |tanh| <= 1 (válida si w_riesgo >= 0).
        """
        w = self.pesos
        mejor = -float('inf')
        g_o = self.oportunidad_esperada(libres_o)
        for c in libres_j:
            resto = [x for x in libres_j if x != c]
            sigma = sqrt(self.var_total(resto) + self.var_total(libres_o))
            v = (w.w_puntaje * (p_j + PUNTAJE_MAXIMO[c] - p_o)
                 + w.w_futuro * (self.futuro_etapa(resto) - self.futuro_etapa(libres_o))
                 - w.w_oportunidad * g_o + abs(w.w_riesgo) * sigma)
            mejor = max(mejor, v)
        return mejor

    # ---------------- interfaz con ElEstado ----------------

    def __call__(self, estado, jugador):
        """Evalúa un ElEstado del programa base desde la perspectiva de `jugador`."""
        t = estado.tablero
        o = 1 - jugador
        libres = [[c for c in CATEGORIAS if c not in t['usadas'][k]] for k in (0, 1)]
        return self.evaluar(t['puntajes'][jugador], t['puntajes'][o],
                            libres[jugador], libres[o], estado.jugador == jugador,
                            t['dados'], t['tiradas_restantes'])
