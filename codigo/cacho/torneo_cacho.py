"""
Punto de entrada para torneo_cacho.py en codigo/cacho/
"""
import os
import sys

dir_cacho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Cacho")
if dir_cacho not in sys.path:
    sys.path.insert(0, dir_cacho)

from torneo_cacho import main

if __name__ == "__main__":
    main()
