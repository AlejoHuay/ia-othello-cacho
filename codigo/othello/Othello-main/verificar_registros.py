"""3.1. Reglas Fundamentales; 22. Formato de Datos; 23. Política de Integridad Académica.
Reproduce todas las partidas desde sus aperturas sin volver a ejecutar búsquedas.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from torneo import RAIZ, leer_partidas, estado_apertura, huella_codigo
from AgentesEspecificos.AgenteOthello import AgenteOthello
from evaluador import evaluar

def verificar(carpeta):
    carpeta=Path(carpeta)
    meta=json.loads((carpeta/'manifest_othello.json').read_text(encoding='utf-8'))
    if meta['codigo_sha256']!=huella_codigo():raise ValueError('El código relevante difiere del manifiesto')
    motor=AgenteOthello(1);n=0;ids=set()
    for p in leer_partidas(carpeta):
        if p['id'] in ids:raise ValueError('ID repetido')
        ids.add(p['id'])
        e=estado_apertura(meta['aperturas'][p['apertura_id']]);f=p['fila']
        assert p['estado']=='completa'
        assert f['profundidad_a']==f['profundidad_b'] and f['profundidad_a'] in meta['plan']['profundidades']
        nombres={p['color_a']:f['agente_a'],3-p['color_a']:f['agente_b']}
        snapshots={x['ply']:x for x in p['posiciones']}
        for m in p['movimientos']:
            assert m['jugador']==e.jugador and m['agente']==nombres[e.jugador]
            assert tuple(m['accion']) in e.movidas
            assert m['tiempo_s']>=0
            if m['nodos_evaluados'] is not None:
                assert m['nodos_evaluados']>=1
                assert np.isclose(m['nodos_por_segundo'],m['nodos_evaluados']/m['tiempo_s'])
            anterior=e.jugador;e=motor.getResultado(e,tuple(m['accion']))
            ply=int(np.count_nonzero(e.tablero))-4
            assert ply==m['ply']
            assert m['pase_oponente']==bool(e.movidas and e.jugador==anterior)
            if ply in snapshots:
                s=snapshots[ply]
                assert s['perspectiva']==1 and s['tablero']==e.tablero.tolist()
                for v,x in s['evaluaciones'].items():
                    assert np.isclose(x,evaluar(e.tablero,1,v,motor._get_valid_moves))
        assert motor.testTerminal(e)
        assert e.tablero.tolist()==p['tablero_final']
        negro=int(np.count_nonzero(e.tablero==1));blanco=int(np.count_nonzero(e.tablero==2))
        assert (negro,blanco)==(p['negras'],p['blancas'])
        dif=(negro-blanco)*(1 if p['color_a']==1 else -1)
        assert f['diferencia_fichas']==dif
        ganador=f['agente_a'] if dif>0 else f['agente_b'] if dif<0 else 'empate'
        assert f['ganador']==ganador
        for sufijo in ('a','b'):
            tiempos=[m['tiempo_s'] for m in p['movimientos'] if m['agente']==f['agente_'+sufijo]]
            assert np.isclose(f['tiempo_'+sufijo],sum(tiempos)/len(tiempos) if tiempos else 0.)
        n+=1
    return n

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entrada',default=str(RAIZ/'datos/othello/torneo_104'))
    args=p.parse_args();print('Partidas reproducidas y verificadas:',verificar(args.entrada))
