import streamlit as st
import streamlit.components.v1 as components

# Configuración de la página para que use todo el ancho
st.set_page_config(layout="wide", page_title="Giormely Web")

# Tu código HTML guardado en una variable
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giormely | Descanso Premium</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Pegar aquí TODO tu bloque de <style> que ya tienes */
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Montserrat', sans-serif; }
        header { background-color: #001d3d; width: 100%; position: fixed; top: 0; left: 0; z-index: 1000; padding: 15px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .header-container { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }
        .logo-area { text-align: center; margin-bottom: 15px; color: white; }
        .brand-name { font-size: 32px; font-weight: 700; letter-spacing: 5px; text-transform: uppercase; }
        .nav-links { display: flex; justify-content: center; list-style: none; gap: 40px; padding-top: 15px; }
        .nav-links li a { color: #ffffff; text-decoration: none; font-size: 13px; text-transform: uppercase; }
        .hero { height: 100vh; background: #001d3d; display: flex; justify-content: center; align-items: center; color: white; text-align: center; }
        .hero h1 { font-size: 50px; }
    </style>
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo-area">
                <div class="brand-name">Giormely</div>
            </div>
            <nav>
                <ul class="nav-links">
                    <li><a href="#">Colchones</a></li>
                    <li><a href="#">Almohadas</a></li>
                    <li><a href="#">Contacto</a></li>
                </ul>
            </nav>
        </div>
    </header>
    <section class="hero">
        <div>
            <h1>Tu descanso ideal te espera</h1>
        </div>
    </section>
</body>
</html>
"""

# Renderizar el HTML en Streamlit
components.html(html_code, height=800, scrolling=True)
