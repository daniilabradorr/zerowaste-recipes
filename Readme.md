# ZeroWaste Recipes 🌱🍲

Convierte sobras de comida en recetas deliciosas con IA y reduce el desperdicio alimentario.

## Tech stack
- Django 5 · HTMX 1.9 · Tailwind CDN
- IA: Groq Cloud (llama-3-8B)
- Hosting: Render (Web Service + PostgreSQL Free)
- PWA mínima (manifest + SW)
- Tests: pytest-django · GitHub Actions CI

## Live URL
https://zerowaste-recipes.onrender.com   ← plan Free (dormita tras 15 min.)

## Day-by-day roadmap
| Día | Entregables |
|-----|-------------|
| **1** | modelos, admin, plantilla base, primer deploy Render |
| **2** | form HTMX “Mis ingredientes”, generación IA, traducción ES/EN |
| **3** | huella CO₂, badges, README final, demo GIF |

## Local setup
```bash
git clone …
cd zerowaste-recipes
python -m venv .venv && .\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # añade tus claves
python manage.py migrate
python manage.py runserver


