import plotly.graph_objects as go

# Configuración del rack (en metros)
ancho, alto, profundo = 5.0, 2.59, 1.0 

fig = go.Figure(data=[go.Mesh3d(
    x=[0, ancho, ancho, 0, 0, ancho, ancho, 0],
    y=[0, 0, profundo, profundo, 0, 0, profundo, profundo],
    z=[0, 0, 0, 0, alto, alto, alto, alto],
    color='gray', opacity=0.5
)])

fig.update_layout(scene=dict(aspectmode='data'))
fig.show()
