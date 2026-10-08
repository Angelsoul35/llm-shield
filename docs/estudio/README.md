# Guía de estudio — llm-shield

Esta carpeta es una guía en español para entender llm-shield a fondo. El código,
los comentarios y la documentación técnica están en inglés (nivel B2) a propósito,
para que el proyecto sea creíble y sirva para practicar. Esta guía explica el "por
qué" de cada decisión en tu idioma, para estudiar con calma.

## Orden sugerido de lectura

1. **[01-modelo-de-amenazas.md](01-modelo-de-amenazas.md)** — qué ataques defiende
   y cuáles no (y por qué eso importa).
2. **[02-defensa-en-profundidad.md](02-defensa-en-profundidad.md)** — reglas +
   clasificador, y cómo se combinan en un veredicto.
3. **[03-modelo-y-overfitting.md](03-modelo-y-overfitting.md)** — el clasificador
   (word + char n-grams) y, muy importante, cómo evaluamos de forma honesta para
   no engañarnos con datos sintéticos (over/underfitting).
4. **[04-salida-y-fugas.md](04-salida-y-fugas.md)** — detección de secretos y la
   fuga del system prompt con canario.
5. **[05-preguntas-de-entrevista.md](05-preguntas-de-entrevista.md)** — preguntas
   típicas y cómo responderlas con seguridad.

## Resumen en una frase

llm-shield inspecciona el texto que cruza las dos fronteras de confianza de una
llamada a un LLM (la entrada del usuario y la salida del modelo) y devuelve un
veredicto permitir/marcar/bloquear con una puntuación de riesgo y las detecciones
que lo justifican, combinando reglas deterministas y un clasificador lineal
(word + char n-grams) evaluado de forma honesta para medir su generalización real.
