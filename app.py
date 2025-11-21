import streamlit as st
import pandas as pd
import sys
import os
import importlib.util
import importlib
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- TRUCO PARA EVITAR ERROR PYCURL ---
from unittest.mock import MagicMock
sys.modules['pycurl'] = MagicMock()
# --------------------------------------

# --- LIBRERÍAS DE MACHINE LEARNING ---
from sklearn.cluster import KMeans, DBSCAN
# ... (resto del código igual)
