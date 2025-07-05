# ZeroWaste Recipes

![Logo](static/img/logo32.png)

**Convierte sobras en comidas y cenas deliciosas** / **Turn leftovers into delicious dinners**

ZeroWaste Recipes es una aplicación web full-stack (Django + HTMX + PWA) que utiliza IA para generar recetas creativas a partir de los ingredientes que ya tienes en tu nevera, calcula la huella de CO₂ evitada y premia tu compromiso con insignias gamificadas.

---

## 📖 Contenido

1. [Demo & Despliegue](#demo--despliegue)  
2. [Características Principales](#caracter%C3%ADsticas-principales)  
3. [Tecnologías](#tecnolog%C3%ADas)  
4. [Instalación & Desarrollo Local](#instalaci%C3%B3n--desarrollo-local)  
5. [Variables de Entorno](#variables-de-entorno)  
6. [Estructura de Carpetas](#estructura-de-carpetas)  
7. [Uso](#uso)  
8. [Insignias & Gamificación](#insignias--gamificaci%C3%B3n)  
9. [PWA & Offline](#pwa--offline)  
10. [Escalado & Producción](#escalado--producci%C3%B3n)  
11. [Roadmap & Mejoras Futuras](#roadmap--mejoras-futuras)  
12. [Licencia](#licencia)  

---

## 🚀 Demo & Despliegue

- **URL producción (Render):** `https://zerowaste-recipes.onrender.com`
- Dominio propio:  
  > 🌐 Ya tienes tu dominio configurado apuntando a Render.  

---

## ✨ Características Principales

- **Recetas generadas por IA**  
  Groq Llama-3 crea platos únicos usando solo tus ingredientes sobrantes.

- **Bilingüe ES / EN**  
  Selector de idioma global + traducción instantánea de cada receta.

- **PWA sin conexión**  
  Instala la app en tu móvil y consulta recetas aun sin internet.

- **Cálculo de huella de CO₂**  
  Suma las emisiones evitadas al aprovechar sobras:  
  ```txt
  3.45 kg CO₂eq
````

* mensaje “Al aprovechar estas sobras, evitas emitir …”.

- **Gamificación & Badges**

  * 🚀 **Starter**: 1ª receta IA
  * 🔗 **Ambassador**: compartir la app 5 veces
  * 🌱 **CO₂ Helper**: 25 recetas IA

  > Se asignan automáticamente y se notifican con un modal.

---

## 🛠 Tecnologías

* **Backend**: Python 3.11 + Django 5.0
* **Frontend**: HTMX, Tailwind CSS (CDN MVP)
* **IA**: Groq API (Llama-3)
* **Base de datos**: PostgreSQL (Render)
* **Despliegue**: Render.com (autoscaling gratuito / startup plan)
* **PWA**: Service Worker + manifest.json

---

## 📥 Instalación & Desarrollo Local

```bash
git clone https://github.com/tu-usuario/zerowaste-recipes.git
cd zerowaste-recipes
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows PowerShell

pip install -r requirements.txt
```

1. **Crear `.env` en raíz**

   ```
   GROQ_API_KEY=tu_api_key_groq
   DJANGO_SECRET_KEY=tu_secret_key
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

2. **Migraciones y datos iniciales**

   ```bash
   python manage.py migrate
   python manage.py loaddata badges_initial.json   # Insignias base
   ```

3. **Correr en local**

   ```bash
   python manage.py runserver
   ```

---

## 🔧 Variables de Entorno

| Variable            | Descripción                   |
| ------------------- | ----------------------------- |
| `GROQ_API_KEY`      | Clave API para Groq Llama-3   |
| `DJANGO_SECRET_KEY` | Clave secreta de Django       |
| `DATABASE_URL`      | Cadena de conexión PostgreSQL |

---

## 📁 Estructura de Carpetas

```
zerowaste-recipes/
├── recipes/
│   ├── models.py
│   ├── views.py
│   ├── templates/recipes/
│   └── static/
├── templates/
│   ├── base.html
│   ├── home.html
│   └── registration/
├── manifest.json
├── service-worker.js
├── render.yaml
├── requirements.txt
└── README.md
```

---

## ▶️ Uso

1. **Landing / Home**

   * Ver insignias, beneficios y “Probar ahora”.
2. **Mis ingredientes**

   * Añade sobras en textarea y pulsa “Sugerir receta”.
3. **Tarjeta de receta**

   * Título, ingredientes, pasos, huella CO₂ y botón “Traducir”.
4. **Insignias**

   * `/badges/` muestra tus insignias ganadas, disponibles y “Próximamente”.

---

## 🏅 Insignias & Gamificación

* **Starter** (1 receta IA)
* **Ambassador** (5 comparticiones distintas)
* **CO₂ Helper** (25 recetas IA)

Al cumplirse, se dispara un **modal**:

> 🎉 **¡Has desbloqueado una insignia!**
> ➜ Ver mis insignias

---

## 📱 PWA & Offline

* **`manifest.json`**: iconos 192×192, 512×512
* **`service-worker.js`**: precache de rutas críticas
* Offline: navegar “Mis ingredientes” y sugerir recetas sin conexión.

---

## ⚙️ Escalado & Producción

* **Render**: `render.yaml` define web service, build commands, health checks.
* **Autoscaling**: ajustes según CPU > 70% o concurrencia.
* **Logs & Alertas**: integración con Sentry (recomendado).

---

## 🛣️ Roadmap & Mejoras Futuras

* **Día 4**: Cache + push notifications + spinner animado de hojas.
* **Día 5**: UI/UX, accesibilidad, formularios feedback “inline”.
* **Día 6**: CI/CD, tests automatizados, SEO, analytics.
* **Día 7**: Documentación completa, marketing y soft-launch.

---

## 📜 Licencia

MIT License

Copyright (c) 2025 ZeroWaste Recipes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction…  
```



---

¡Gracias por llegar hasta aquí! 🎉
Próximamente llevaremos ZeroWaste Recipes a otro nivel con mejoras offline, tests, escalado y más gamificación.