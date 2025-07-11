from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
import os

# Ruta absoluta del script que deseas analizar
#script_path = r'C:\Users\silva\Documents\repo\bolirana\game\game.py'

# Obtener el directorio del script actual
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta hacia 'game.py' de forma portable
script_path = os.path.join(base_dir, 'game.py')

# Configuración de salida del gráfico
graphviz = GraphvizOutput()
graphviz.output_file = 'game_call_graph.png'

# Ejecutar el script y capturar el gráfico de llamadas
with PyCallGraph(output=graphviz):
    # Usamos exec para ejecutar el script externo
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code)
