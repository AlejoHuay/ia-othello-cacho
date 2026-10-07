"""
Simulador sin interfaz gráfica de UNA partida de Cacho IA vs IA.

Aplica exactamente las reglas de EntornoCacho (5 dados, tirada inicial +
3 re-tiradas, 10 categorías por jugador) y usa su propio generador
aleatorio con semilla para que cada partida sea reproducible.

Cada agente recibe una VISTA en la que él es siempre el jugador 0. Así el
agente base (que asume ser el jugador 0 / MAX) se comporta igual sin
importar si empieza o no, y la comparación es justa.

Uso mínimo:
    from simulador import jugar_partida
    r = jugar_partida(agente_a, agente_b, semilla=7, empieza=0)
    r['puntajes'], r['ganador'], r['decisiones']
"""
import random
from time import perf_counter

from AgenteCacho import CATEGORIAS, puntuar, normalizar
from AgenteIA.AgenteJugador import ElEstado
from funcion_evaluacion import TIRADAS_POR_TURNO, N_DADOS


def vista_para(tablero, jugador):
    """ElEstado espejado: el agente que decide aparece como jugador 0."""
    o = 1 - jugador
    t = {
        'dados': tuple(tablero['dados']),
        'tiradas_restantes': tablero['tiradas_restantes'],
        'puntajes': [tablero['puntajes'][jugador], tablero['puntajes'][o]],
        'usadas': [set(tablero['usadas'][jugador]), set(tablero['usadas'][o])],
        'ronda': tablero['ronda'],
    }
    return ElEstado(jugador=0, get_utilidad=0, tablero=t, movidas=None)


def accion_valida(accion, tablero, jugador):
    if not (isinstance(accion, tuple) and len(accion) == 2):
        return False
    tipo, param = accion
    if tipo == 'anotar':
        return param in CATEGORIAS and param not in tablero['usadas'][jugador]
    if tipo == 'tirar':
        return (tablero['tiradas_restantes'] > 0 and bool(param)
                and all(0 <= i < N_DADOS for i in param))
    return False


def jugar_partida(agente_a, agente_b, semilla=None, empieza=0, verbose=False):
    """
    Juega una partida completa. agente_a es el jugador 0 y agente_b el 1.
    Devuelve dict con puntajes, ganador (0, 1 o None si empate), semilla,
    empieza, errores (acciones inválidas corregidas) y la lista de decisiones
    [{'jugador', 'tipo', 'detalle', 'tiempo', 'dados', 'tiradas_restantes'}].
    """
    rng = random.Random(semilla)
    agentes = (agente_a, agente_b)
    tablero = {'dados': None, 'tiradas_restantes': TIRADAS_POR_TURNO,
               'puntajes': [0, 0], 'usadas': [set(), set()], 'ronda': 0}
    decisiones, errores = [], [0, 0]
    turno = empieza
    total_anotaciones = 2 * len(CATEGORIAS)

    def tirar_5():
        return normalizar([rng.randint(1, 6) for _ in range(N_DADOS)])

    tablero['dados'] = tirar_5()
    while tablero['ronda'] < total_anotaciones:
        estado = vista_para(tablero, turno)
        inicio = perf_counter()
        accion = agentes[turno].elegir_accion(estado)
        tiempo = perf_counter() - inicio

        if not accion_valida(accion, tablero, turno):
            # Corrección mínima: anotar en la categoría libre que más puntúa
            errores[turno] += 1
            libres = [c for c in CATEGORIAS if c not in tablero['usadas'][turno]]
            accion = ('anotar', max(libres, key=lambda c: puntuar(c, tablero['dados'])))

        tipo, param = accion
        decisiones.append({'jugador': turno, 'tipo': tipo,
                           'detalle': sorted(param) if tipo == 'tirar' else param,
                           'tiempo': tiempo, 'dados': tablero['dados'],
                           'tiradas_restantes': tablero['tiradas_restantes']})
        if tipo == 'tirar':
            dados = list(tablero['dados'])
            for i in param:
                dados[i] = rng.randint(1, 6)
            tablero['dados'] = normalizar(dados)
            tablero['tiradas_restantes'] -= 1
        else:
            pts = puntuar(param, tablero['dados'])
            tablero['puntajes'][turno] += pts
            tablero['usadas'][turno].add(param)
            tablero['ronda'] += 1
            if verbose:
                print(f"[{agentes[turno].nombre}] anota {param} con {tablero['dados']} "
                      f"-> +{pts} (total {tablero['puntajes'][turno]})")
            # Pasa el turno (si el rival ya llenó todo, sigue el mismo jugador)
            if len(tablero['usadas'][1 - turno]) < len(CATEGORIAS):
                turno = 1 - turno
            tablero['dados'] = tirar_5()
            tablero['tiradas_restantes'] = TIRADAS_POR_TURNO

    p = tablero['puntajes']
    ganador = None if p[0] == p[1] else (0 if p[0] > p[1] else 1)
    return {'puntajes': list(p), 'ganador': ganador, 'semilla': semilla,
            'empieza': empieza, 'errores': errores, 'decisiones': decisiones}
