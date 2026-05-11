<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giormely | Descanso Premium</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">

    <style>
        /* Reset general */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Montserrat', sans-serif;
        }

        /* --- ENCABEZADO PREMIUM --- */
        header {
            background-color: #001d3d; /* Azul profundo de la marca */
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
            padding: 15px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border-bottom: 1px solid rgba(77, 166, 255, 0.2);
        }

        .header-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            flex-direction: column; /* Logo arriba, menú abajo */
            align-items: center;
        }

        /* Área del Logo */
        .logo-area {
            text-align: center;
            margin-bottom: 15px;
        }

        .logo-area img {
            height: 100px; /* Tamaño grande para que el fénix resalte */
            width: auto;
            filter: drop-shadow(0 0 10px rgba(77, 166, 255, 0.4));
        }

        .brand-name {
            color: #ffffff;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: 5px;
            text-transform: uppercase;
            margin-top: 5px;
        }

        .brand-slogan {
            color: #4da6ff; /* Celeste del logo */
            font-size: 11px;
            font-weight: 400;
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        /* Navegación */
        nav {
            width: 100%;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 15px;
        }

        .nav-links {
            display: flex;
            justify-content: center;
            list-style: none;
            gap: 40px;
        }

        .nav-links li a {
            color: #ffffff;
            text-decoration: none;
            font-size: 13px;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s ease;
            opacity: 0.8;
        }

        .nav-links li a:hover {
            opacity: 1;
            color: #4da6ff;
            text-shadow: 0 0 8px rgba(77, 166, 255, 0.6);
        }

        /* --- SECCIÓN PRINCIPAL (HERO) --- */
        .hero {
            height: 100vh;
            background: linear-gradient(rgba(0, 29, 61, 0.6), rgba(0, 29, 61, 0.3)), 
                        url('FT/Cama.jpeg');
            background-size: cover;
            background-position: center;
            display: flex;
            justify-content: center;
            align-items: center;
            padding-top: 200px; /* Para no chocar con el header grande */
        }

        .hero-content {
            text-align: center;
            color: white;
        }

        .hero-content h1 {
            font-size: 60px;
            font-weight: 300;
            margin-bottom: 20px;
            text-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }

        .btn-premium {
            display: inline-block;
            padding: 18px 50px;
            background-color: #4da6ff;
            color: white;
            text-decoration: none;
            font-weight: 700;
            border-radius: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: 0.4s;
            box-shadow: 0 5px 15px rgba(77, 166, 255, 0.4);
        }

        .btn-premium:hover {
            background-color: white;
            color: #001d3d;
            transform: translateY(-5px);
        }
    </style>
</head>
<body>

    <header>
        <div class="header-container">
            <div class="logo-area">
                <img src="FT/LOGO11.png" alt="Giormely Logo">
                <div class="brand-name">Giormely</div>
                <div class="brand-slogan">Duerme, Sueña, Vive Mejor</div>
            </div>

            <nav>
                <ul class="nav-links">
                    <li><a href="#">Colchones</a></li>
                    <li><a href="#">Almohadas</a></li>
                    <li><a href="#">Packs de Descanso</a></li>
                    <li><a href="#">Garantía</a></li>
                    <li><a href="#">Nosotros</a></li>
                    <li><a href="#">Contacto</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <section class="hero">
        <div class="hero-content">
            <h1>Tu descanso ideal te espera</h1>
            <a href="#" class="btn-premium">Ver Colección 2026</a>
        </div>
    </section>

</body>
</html>
