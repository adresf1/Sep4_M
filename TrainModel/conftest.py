
import sys, os

# Tilføj projektroden (den mappe, conftest.py ligger i) til import-stien
root = os.path.abspath(os.path.dirname(__file__))
if root not in sys.path:
    sys.path.insert(0, root)