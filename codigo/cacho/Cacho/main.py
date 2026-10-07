"""
Juego Cacho: IA vs Humano con interfaz pygame.

    python main.py          -> IA mejorada (agente_ia.AgenteCachoMejorado)
    python main.py --base   -> IA del programa base (AgenteCachoIA)
"""
import sys

from EntornoCacho import EntornoCacho
from AgenteCachoIA import AgenteCachoIA
from AgenteCachoHumano import AgenteCachoHumano
from agente_ia import AgenteCachoMejorado
from VistaCacho import VistaCacho


if __name__ == "__main__":
    entorno = EntornoCacho()

    if "--base" in sys.argv:
        ia = AgenteCachoIA(nombre="IA", altura=1)
    else:
        ia = AgenteCachoMejorado(nombre="IA")
    humano = AgenteCachoHumano(nombre="Tú")

    entorno.insertar(ia)
    entorno.insertar(humano)

    vista = VistaCacho(entorno)
    vista.loop()
