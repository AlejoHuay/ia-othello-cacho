"""6.1. Estructura del Torneo; 12.1. Para Othello; 22. Formato de Datos.
Resumen descriptivo de resultados externos reportados, separado del torneo interno.
Ejecutar desde cualquier directorio: python analizar_externa_othello.py
"""
import csv
import json
from pathlib import Path

RAIZ=Path(__file__).resolve().parents[3]
CARPETA=RAIZ/'datos/othello/competencia_externa'

def analizar():
    datos=json.loads((CARPETA/'registros_externos_othello.json').read_text(encoding='utf-8'))
    partidas=datos['partidas']
    assert len({p['partida'] for p in partidas})==len(partidas)
    filas=[]
    for rival in sorted({p['rival'] for p in partidas}):
        ps=[p for p in partidas if p['rival']==rival]
        victorias=sum(p['ganador']=='Ispis' for p in ps)
        empates=sum(p['ganador']=='empate' for p in ps)
        filas.append(dict(rival=rival,partidas=len(ps),victorias_ispis=victorias,
            derrotas_ispis=len(ps)-victorias-empates,empates=empates,
            diferencia_media_ispis=sum(p['diferencia_fichas'] for p in ps)/len(ps),
            puntos_ispis=victorias+0.5*empates))
    with (CARPETA/'resumen_externo_othello.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(filas[0]));w.writeheader();w.writerows(filas)
    linea=chr(92)*2
    tex=[r'% 6.1. Estructura del Torneo; 12.1. Para Othello; 16. Formato de Tablas y Figuras.',
         r'\begin{table}[htbp]',r'\centering\small',
         r'\caption{Competencia externa reportada. I: Ispis; JP: equipo Juan Pablo; D: equipo Daniela; N/B: negras/blancas. Inició según colores reportados (negras). P5: terminalidad no confirmada.}',
         r'\label{tab:othello_externa}',r'\begin{tabular}{rlcccrrl}',r'\toprule',
         'Partida & Rival & Color I & Color rival & Inició & Fichas I & Rival & Ganador '+linea,r'\midrule']
    for p in partidas:
        assert p['fichas_ispis']+p['fichas_rival']<=64
        assert p['diferencia_fichas']==p['fichas_ispis']-p['fichas_rival']
        assert p['ganador']==('Ispis' if p['diferencia_fichas']>0 else p['rival'] if p['diferencia_fichas']<0 else 'empate')
        alias='JP' if p['rival']=='Equipo Juan Pablo' else 'D'
        color='N' if p['color_ispis']=='Negras' else 'B'
        otro='B' if color=='N' else 'N';inicio='I' if color=='N' else alias
        ganador='I' if p['ganador']=='Ispis' else alias
        tex.append(f"{p['partida']} & {alias} & {color} & {otro} & {inicio} & {p['fichas_ispis']} & {p['fichas_rival']} & {ganador} "+linea)
    tex += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (CARPETA/'tabla_externa_othello.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')
    print('Resumen externo regenerado:',len(partidas),'resultados reportados; sin inferencia estadística.')
    return filas

if __name__=='__main__':
    analizar()
