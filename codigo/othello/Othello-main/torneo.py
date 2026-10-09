"""6. Descripción de la Competencia; 6.1. Estructura del Torneo;
12.1. Para Othello; 22. Formato de Datos. Round-robin local reproducible.
"""
import argparse
import csv
import hashlib
import importlib
import itertools
import json
import os
from pathlib import Path
import platform
import random
import time
from datetime import datetime, timezone
import numpy as np
from AgenteIA.AgenteJugador import ElEstado
from AgentesEspecificos.AgenteOthello import AgenteOthello
from TableroOthello import TableroOthello
from evaluador import evaluar, componentes, VERSIONES

RAIZ = Path(__file__).resolve().parents[3]
COLUMNAS = ['agente_a','agente_b','ganador','diferencia_fichas',
            'profundidad_a','profundidad_b','tiempo_a','tiempo_b']

def guardar_json(path, valor):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = path.with_suffix(path.suffix + '.tmp')
    temporal.write_text(json.dumps(valor, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    temporal.replace(path)

def huella_codigo():
    base = Path(__file__).resolve().parent
    return {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted([base/'torneo.py', base/'evaluador.py', base/'TableroOthello.py',
                             base/'AgenteIA/Agente.py', base/'AgenteIA/AgenteJugador.py',
                             base/'AgentesEspecificos/AgenteOthello.py'])}

def configuraciones(path=None):
    if path:
        datos = json.loads(Path(path).read_text(encoding='utf-8'))
    else:
        datos = [{"nombre": v, "evaluacion": v} for v in VERSIONES]
    nombres = [x['nombre'] for x in datos]
    if len(nombres) < 2 or len(set(nombres)) != len(nombres) or 'empate' in nombres:
        raise ValueError('Se requieren al menos dos nombres únicos, distintos de empate')
    return datos

def crear_agente(config, profundidad):
    if 'factory' in config:
        modulo, nombre = config['factory'].split(':')
        return getattr(importlib.import_module(modulo), nombre)(altura=profundidad, **config.get('opciones', {}))
    return AgenteOthello(profundidad, config['evaluacion'], config.get('tecnica', 'podaalfabeta'))

def aperturas(cantidad, semilla, plies=8):
    if cantidad < 1 or not 0 <= plies <= 20 or (plies == 0 and cantidad > 1):
        raise ValueError('Cantidad positiva; apertura de 0 a 20 colocaciones; inicio único si plies=0')
    motor = AgenteOthello(1)
    rng = random.Random(semilla)
    resultado, vistos = [], set()
    for intento in range(max(1000, cantidad * 1000)):
        if len(resultado) == cantidad:
            return resultado
        estado = TableroOthello(verbose=False).juegoActual
        secuencia = []
        for _ in range(plies):
            if not estado.movidas:
                break
            m = rng.choice(estado.movidas)
            secuencia.append(list(m))
            estado = motor.getResultado(estado, m)
        if len(secuencia) != plies or motor.testTerminal(estado):
            continue
        # No repetir posiciones equivalentes por rotación/reflexión.
        firma = min(np.rot90(t, k).tobytes() for t in (estado.tablero, np.fliplr(estado.tablero)) for k in range(4))
        firma = (estado.jugador, firma)
        if firma in vistos:
            continue
        vistos.add(firma)
        resultado.append(dict(id=len(resultado), secuencia=secuencia,
                              tablero=estado.tablero.tolist(), jugador=estado.jugador))
    raise ValueError('No se consiguieron suficientes aperturas únicas')

def estado_apertura(apertura):
    motor = AgenteOthello(1)
    e = TableroOthello(verbose=False).juegoActual
    for m in apertura['secuencia']:
        m = tuple(m)
        if m not in e.movidas:
            raise ValueError('Apertura ilegal')
        e = motor.getResultado(e, m)
    if e.tablero.tolist() != apertura['tablero'] or e.jugador != apertura['jugador']:
        raise ValueError('Apertura inconsistente')
    return e

def jugar(config_a, config_b, profundidad, apertura, color_a, destino, identidad):
    agentes = {color_a: crear_agente(config_a, profundidad),
               3-color_a: crear_agente(config_b, profundidad)}
    nombres = {color_a: config_a['nombre'], 3-color_a: config_b['nombre']}
    motor = AgenteOthello(1)
    e = estado_apertura(apertura)
    movimientos, posiciones = [], []
    inicio = time.perf_counter()
    progreso = Path(destino).with_suffix('.progreso.json')
    while not motor.testTerminal(e):
        if not e.movidas:
            e = motor.getResultado(e, None)
            continue
        jugador = e.jugador
        agente = agentes[jugador]
        # Entregar una copia para aislar incluso agentes externos mutables.
        agente.estado = ElEstado(jugador, 0, e.tablero.copy(), list(e.movidas))
        t = time.perf_counter()
        agente.programa()
        segundos = time.perf_counter()-t
        accion = agente.get_acciones()
        if accion is None or tuple(accion) not in e.movidas:
            raise ValueError('Acción ilegal de ' + nombres[jugador])
        accion = tuple(int(x) for x in accion)
        metricas = getattr(agente, 'metricas', {})
        nodos = metricas.get('nodos_evaluados')  # desconocido si el adaptador no informa
        nueva = motor.getResultado(e, accion)
        ply = int(np.count_nonzero(nueva.tablero))-4
        movimientos.append(dict(ply=ply, jugador=jugador, agente=nombres[jugador],
            accion=list(accion), tiempo_s=segundos, nodos_evaluados=nodos,
            nodos_por_segundo=nodos/segundos if nodos is not None and segundos else None,
            nodos_visitados=metricas.get('nodos_visitados'), cortes=metricas.get('cortes'),
            pase_oponente=bool(nueva.movidas and nueva.jugador == jugador)))
        e = nueva
        if ply in (20,30,40,50):
            posiciones.append(dict(ply=ply, perspectiva=1, tablero=e.tablero.tolist(),
                componentes=componentes(e.tablero,1,motor._get_valid_moves),
                evaluaciones={v:evaluar(e.tablero,1,v,motor._get_valid_moves) for v in VERSIONES}))
        guardar_json(progreso, dict(id=identidad, estado='en_curso', movimientos=movimientos,
                                   segundos=time.perf_counter()-inicio))
    negras = int(np.count_nonzero(e.tablero==1))
    blancas = int(np.count_nonzero(e.tablero==2))
    diferencia = (negras-blancas) * (1 if color_a==1 else -1)
    ganador = config_a['nombre'] if diferencia>0 else config_b['nombre'] if diferencia<0 else 'empate'
    def promedio(nombre):
        valores = [m['tiempo_s'] for m in movimientos if m['agente']==nombre]
        return sum(valores)/len(valores) if valores else 0.0
    fila = dict(agente_a=config_a['nombre'], agente_b=config_b['nombre'], ganador=ganador,
                diferencia_fichas=diferencia, profundidad_a=profundidad, profundidad_b=profundidad,
                tiempo_a=promedio(config_a['nombre']), tiempo_b=promedio(config_b['nombre']))
    resultado = dict(id=identidad, apertura_id=apertura['id'], color_a=color_a,
        fila=fila, negras=negras, blancas=blancas, tablero_final=e.tablero.tolist(),
        movimientos=movimientos, posiciones=posiciones, estado='completa',
        duracion_s=time.perf_counter()-inicio)
    guardar_json(destino, resultado)
    progreso.unlink(missing_ok=True)
    return resultado

def leer_partidas(carpeta):
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted(Path(carpeta).glob('partida_*.json'))
            if '.progreso.' not in p.name]

def exportar(carpeta, destino):
    partidas = leer_partidas(carpeta)
    with Path(destino).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=COLUMNAS); w.writeheader()
        w.writerows(p['fila'] for p in partidas)
    return len(partidas)

def ejecutar(args):
    configs = configuraciones(args.agentes)
    if any(d<1 for d in args.profundidades):
        raise ValueError('Profundidades positivas')
    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True,exist_ok=True)
    plan = dict(semilla=args.semilla, aperturas=args.aperturas, plies=args.plies,
                profundidades=args.profundidades, agentes=configs)
    manifest = carpeta/'manifest_othello.json'
    hashes = huella_codigo()
    if manifest.exists():
        meta=json.loads(manifest.read_text(encoding='utf-8'))
        if meta['plan'] != plan or meta['codigo_sha256'] != hashes:
            raise ValueError('Plan/código diferente: usar otra carpeta; no mezclar experimentos')
    else:
        meta=dict(plan=plan, codigo_sha256=hashes, aperturas=aperturas(args.aperturas,args.semilla,args.plies),
            hardware=dict(sistema=platform.platform(),cpu=platform.processor(), nucleos=os.cpu_count()),
            python=platform.python_version(),numpy=np.__version__,fecha_utc=datetime.now(timezone.utc).isoformat(),
            referencia='6.1. Estructura del Torneo; 12.1. Para Othello; 22. Formato de Datos',
            profundidad='colocaciones; pases sin consumir nivel',
            nodo_evaluado='hoja terminal o corte de profundidad; una llamada de valoración',
            tiempo='segundos de pared en programa por movimiento; CSV contiene media por agente',
            puntuacion='victoria 1; empate 0.5; derrota 0',
            externa='pendiente: sin agentes externos' if not args.agentes else 'configuración proporcionada')
        guardar_json(manifest,meta)
    inicio=time.perf_counter(); nuevas=0
    # Abrir primero todos los niveles del primer bloque: el piloto cubre 4,5,6,7.
    for apertura in meta['aperturas']:
        for profundidad in args.profundidades:
            for ia, ib in itertools.combinations(range(len(configs)),2):
                for color in (1,2):
                    identidad=f"a{apertura['id']:03d}_d{profundidad}_{ia}_{ib}_c{color}"
                    destino=carpeta/f'partida_{identidad}.json'
                    if destino.exists():
                        continue
                    if (args.max_partidas and nuevas>=args.max_partidas) or (args.max_segundos and time.perf_counter()-inicio>=args.max_segundos):
                        exportar(carpeta,carpeta/'resultados_othello.csv')
                        print('Pausa entre partidas; ejecución reanudable',flush=True)
                        return
                    print('INICIO',identidad,flush=True)
                    resultado=jugar(configs[ia],configs[ib],profundidad,apertura,color,destino,identidad)
                    nuevas+=1
                    exportar(carpeta,carpeta/'resultados_othello.csv')
                    print('FIN',identidad,resultado['fila']['ganador'],round(resultado['duracion_s'],2),'s',flush=True)
    exportar(carpeta,carpeta/'resultados_othello.csv')
    print('Plan completo',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida',default=str(RAIZ/'datos/othello/torneo_104'))
    p.add_argument('--profundidades',nargs='+',type=int,default=[4,5,6,7])
    p.add_argument('--aperturas',type=int,default=13)
    p.add_argument('--plies',type=int,default=8)
    p.add_argument('--semilla',type=int,default=20261008)
    p.add_argument('--agentes',help='JSON con nombres y evaluacion o factory modulo:funcion')
    p.add_argument('--max-partidas',type=int,default=0)
    p.add_argument('--max-segundos',type=float,default=0,help='Presupuesto entre partidas, no interrumpe decisiones')
    ejecutar(p.parse_args())

if __name__=='__main__':
    main()
