"""
recipes/utils.py
Ayudo a Groq Llama-3 a generar una receta en formato JSON
a partir de una lista de ingredientes.
"""
from __future__ import annotations

import json
import os
import textwrap
from typing import Dict, List

import requests
from requests.exceptions import HTTPError, JSONDecodeError, Timeout

#  Configuracion de Groq 
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama3-8b-8192"
TIMEOUT  = 60  # segundos

def suggest_recipe(ingredients: str, lang: str = "es") -> Dict[str, List[str] | str]:
    """
    Devuelvo un diccionario con 'title', 'ingredients' (list) y 'steps' (list).
    
    :param ingredients: Cadena con la lista “zanahoria, garbanzos…”
    :param lang: 'es' o 'en' – idioma de respuesta
    :raises RuntimeError: si la API falla o el JSON es inválido
    """
    # Guardo el prompt. Uso un bloque delimitado para forzar JSON puro.
    prompt = textwrap.dedent(f"""
        Eres un chef creativo experto en cocina de aprovechamiento. 
        Crea UNA receta que use exclusivamente esta lista:
        {ingredients}

        Devuelve SOLO JSON válido (sin ``` ni texto adicional) 
        en {lang.upper()} con esta forma:
        {{
          "title": "…",
          "ingredients": ["…", "…"],
          "steps": ["…", "…"]
        }}
        ###
    """)

    try:
        # Hago la llamada a Groq
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system",
                     "content": "You are ZeroWaste Recipes, an assistant that outputs JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()

        # Extraigo el mensaje del modelo
        raw_content: str = resp.json()["choices"][0]["message"]["content"].strip()

        # Intento parsear el JSON
        return json.loads(raw_content)

    except Timeout:
        raise RuntimeError("Groq API tardó demasiado en responder.")
    except HTTPError as exc:
        raise RuntimeError(f"Groq API devolvió un error: {exc.response.status_code}") from exc
    except (KeyError, JSONDecodeError) as exc:
        raise RuntimeError(f"Respuesta de IA no es JSON válido: {raw_content[:120]}…") from exc
