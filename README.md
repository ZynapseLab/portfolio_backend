Para levantar el proyecto necesitás:

  1. MongoDB con Docker:

  docker-compose up -d


  2. Crear tu archivo .env:

  cp .env.example .env


  Luego editá .env con tus API keys reales (OPENROUTER_API_KEY, OPENAI_API_KEY, JWT_SECRET).

  3. Seed de datos en MongoDB:

  .venv/bin/python -m scripts.seed_prompts


  4. Levantar el servidor:

  .venv/bin/uvicorn main:app --reload


  El server arranca en http://localhost:8000. Podés verificar con GET /health.