"""14. Evidencia Formal de Eficiencia, punto 3: mismas posiciones, d=4,5,6,7.
Ejecutar sin otros experimentos simultáneos. No se infiere crecimiento polinomial.
"""
import argparse
import json
import time
import platform
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from torneo import RAIZ, guardar_json, huella_codigo, estado_apertura
from AgenteIA.AgenteJugador import ElEstado
from AgentesEspecificos.AgenteOthello import AgenteOthello
from TableroOthello import TableroOthello

def ejecutar(entrada,salida,plies,versiones,repeticiones):
    datos=json.loads(Path(entrada).read_text(encoding='utf-8'))
    posiciones=[dict(ply=0,jugador=1,tablero=TableroOthello(verbose=False).juegoActual.tablero.tolist())]
    meta=json.loads((Path(entrada).parent/'manifest_othello.json').read_text(encoding='utf-8'))
    motor=AgenteOthello(1);e=estado_apertura(meta['aperturas'][datos['apertura_id']])
    for m in datos['movimientos']:
        e=motor.getResultado(e,tuple(m['accion']))
        if m['ply'] in plies:
            posiciones.append(dict(ply=m['ply'],jugador=e.jugador,tablero=e.tablero.tolist()))
    path=Path(salida)
    if path.exists():raise ValueError('No sobrescribir un benchmark original; usar otro nombre')
    resultado=dict(referencia='14. Evidencia Formal de Eficiencia, punto 3',
        partida_origen=datos['id'],codigo_sha256=huella_codigo(),
        fecha_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
        numpy=np.__version__,plataforma=platform.platform(),posiciones=posiciones,
        repeticiones=repeticiones,profundidades=[4,5,6,7],
        nota='Las mismas matrices se miden a todas las profundidades; turno real conservado desde el registro. No son jugadas del torneo.',
        registros=[])
    for pos in posiciones:
        b=np.array(pos['tablero'],dtype=int)
        for v in versiones:
            for d in (4,5,6,7):
                a=AgenteOthello(d,v)
                # Mantener la misma posición y jugador en cada profundidad.
                e=ElEstado(pos['jugador'],0,b,a._get_valid_moves(b,pos['jugador']))
                if not e.movidas:continue
                for repeticion in range(repeticiones):
                    a.estado=e;a.programa()
                    resultado['registros'].append(dict(ply=pos['ply'],evaluacion=v,profundidad=d,
                        repeticion=repeticion,**a.metricas))
                    guardar_json(path,resultado)
                    print(pos['ply'],v,d,round(a.metricas['tiempo_s'],4),flush=True)
    guardar_json(path,resultado)
    return resultado

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--partida',default=str(RAIZ/'datos/othello/torneo_104/partida_a000_d4_0_1_c1.json'))
    p.add_argument('--salida',default=str(RAIZ/'datos/othello/benchmark_othello.json'))
    p.add_argument('--plies',type=int,nargs='*',default=[20,40,50])
    p.add_argument('--versiones',nargs='+',choices=['fija','etapas'],default=['fija','etapas'])
    p.add_argument('--repeticiones',type=int,default=1)
    args=p.parse_args()
    if args.repeticiones<1:p.error('repeticiones >=1')
    ejecutar(args.partida,args.salida,args.plies,args.versiones,args.repeticiones)
