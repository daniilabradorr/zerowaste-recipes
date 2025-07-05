# ZeroWaste Recipes

**Convierte sobras en comidas deliciosas** con nuestra aplicación web PWA multilingüe, impulsada por IA, PARA REDUCIR EL DESPERDICIO ALIMENTICIO.

---

## 📖 Índice

1. [Visión general](#visión-general)  
2. [Funcionalidades](#funcionalidades)  
3. [Demo rápida](#demo-rápida)  
4. [Tecnologías & Stack](#tecnologías--stack)  
5. [Instalación local](#instalación-local)  
6. [Desarrollo & Estructura](#desarrollo--estructura)  
7. [Deploy automático en Render](#deploy-automático-en-render)  
8. [Cómo usar](#cómo-usar)  
9. [Internacionalización](#internacionalización)  
10. [PWA y Offline](#pwa-y-offline)  
11. [Pruebas manuales clave](#pruebas-manuales-clave)  
12. [Próximos pasos (Día 3)](#próximos-pasos-día-3)  
13. [Licencia](#licencia)  

---

## Visión general

ZeroWaste Recipes es un **recetario inteligente** que aprovecha tus sobras y las convierte en platos creativos gracias a Groq Llama-3. Disponible en **español** e **inglés**, y como **Progressive Web App** para consultar offline.

---

## Funcionalidades

- **Autenticación**: registro, inicio de sesión y cierre de sesión con Django  
- **CRUD de modelos**:
  - **Ingredient**  
  - **Recipe** (marcadas si son IA)  
  - **RecipeIngredient**  
  - **Leftover** (sobras del usuario)  
- **“Mis ingredientes”**: formulario HTMX sin recarga  
- **Generación IA**: sugerencia de receta vía Groq Llama-3 (modelo llama3-8b-instruct)  
- **Traducción de receta**: botón “Traducir” HTMX que crea la versión en el otro idioma  
- **Selector de idioma**: ES / EN en el header, ajusta cookie `django_language` + recarga  
- **PWA mínima**: 
  - `manifest.json` con iconos (192×192,512×512)  
  - `sw.js` cacheando recursos estáticos  
  - Instalación del Service Worker  
- **CI/CD**: deploy automático en Render con migrations automáticas  

---

## Demo rápida

1. **Regístrate** o ingresa como invitado.  
2. Ve a **Mis ingredientes**, escribe “zanahoria, arroz” → pulsa **Sugerir receta**.  
3. La tarjeta IA aparece sin recargar.  
4. Pulsa **Traducir a inglés** → la tarjeta se actualiza en inglés.  
5. Cambia idioma en el header → toda la UI pasa a ES / EN.  
6. Instala la PWA en tu móvil y consulta offline.

---

## Tecnologías & Stack

- **Backend**: Django 5, django-htmx  
- **IA**: Groq Cloud REST (modelo llama3-8b-instruct)  
- **Base de datos**: PostgreSQL (Render)  
- **Frontend**: HTMX, Tailwind CSS (CDN), Bulma/Tailwind vía SCSS  
- **PWA**: manifest.json + Service Worker  
- **Testing**: pytest, pytest-django  
- **CI/CD**: GitHub Actions (opcional) + Render deploy automático  

---

## Instalación local

1. Clona el repositorio:
   ```
   git clone https://github.com/tu-usuario/zerowaste-recipes.git
   cd zerowaste-recipes

2. Crea y activa un entorno virtual:
    ```
    python3.12 -m venv .venv
    source .venv/bin/activate   # Unix/macOS
    .\.venv\Scripts\activate    # Windows PowerShell


3. Instala dependencias:
    ```
    pip install -r requirements.txt
    
4. Configura variables de entorno en .env:
    ```
    DJANGO_SECRET_KEY=tu_secret_key
    DATABASE_URL=postgres://usuario:pass@localhost:5432/zerowaste
    GROQ_API_KEY=tu_api_key_groq

5. Aplica migraciones:
    ```
    python manage.py migrate

6. Ejecuta el servidor:
    ```
    python manage.py runserver



## desarrollo--estructura
zerowaste-recipes/
├─ recipes/
│  ├─ migrations/
│  ├─ templates/recipes/
│  │  ├─ ingredient_form.html
│  │  └─ _recipe_card.html
│  ├─ models.py
│  ├─ views.py
│  └─ urls.py
├─ static/
│  ├─ img/
│  │  ├─ logo32.png
│  │  ├─ icon-192.png
│  │  └─ icon-512.png
│  ├─ sw.js
│  └─ manifest.json
├─ templates/
│  ├─ base.html
│  └─ home.html
├─ zerowaste/
│  ├─ settings.py
│  └─ urls.py
├─ .env
├─ manage.py
└─ README.md



## Licencia

Este proyecto se distribuye bajo la **Licencia MIT**.  
Puedes consultar el texto completo a continuación:

MIT License

Copyright (c) 2025 ZeroWaste Recipes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.