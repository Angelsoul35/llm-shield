# 04 — Salida y fugas

## La salida se escanea distinto que la entrada

En la entrada, la amenaza (inyección) es difusa: hay que juzgar intención, por eso
usamos reglas **y** un clasificador. En la salida, las amenazas son de
**coincidencia exacta**: ¿aparece un secreto?, ¿aparece el system prompt? No hace
falta un modelo probabilístico para eso; las reglas exactas son mejores (sin
falsos positivos). Por eso la salida usa **solo reglas**, y cualquier detección es
un **bloqueo duro**.

## Detección de secretos

Expresiones regulares para formatos de credenciales conocidos:

- OpenAI: `sk-...`
- AWS: `AKIA...`
- GitHub: `ghp_...`
- Bearer tokens
- Claves privadas PEM (`-----BEGIN ... PRIVATE KEY-----`)

Si el modelo emite algo con ese formato hacia el usuario, se bloquea.

## Fuga del system prompt: el canario

Detectar "¿la salida contiene el system prompt?" por coincidencia difusa es poco
fiable: falsos positivos cuando la salida cita una frase normal, falsos negativos
cuando la fuga es parcial o parafraseada, y obliga al detector a guardar el prompt
completo.

La solución es un **canario**: un token corto, único y sin sentido, incrustado en
el system prompt de la aplicación (`LS_SYSTEM_PROMPT_CANARY`). El detector hace una
sola comprobación de subcadena exacta. Si el canario aparece en la salida, el
system prompt se filtró, porque el canario no existe en ningún otro sitio.

### Ventajas y límite

- **Fiable y barato:** coincidencia exacta de un token único → prácticamente sin
  falsos positivos ni negativos para una fuga literal, en O(n).
- **Sin el prompt en el detector:** solo necesita el canario, no el texto
  sensible.
- **Límite riguroso:** atrapa la fuga del prompt **tal como está escrito**; un
  modelo que parafrasee sus instrucciones sin emitir el canario lo evadiría. Por
  eso el canario se coloca donde una fuga lo arrastraría (cerca del inicio del
  prompt) y se complementa con los detectores de secretos y con no poner datos
  realmente sensibles en el prompt.

## Para fijar la idea

- Entrada = amenaza difusa (reglas + modelo); salida = amenaza exacta (solo
  reglas).
- Secretos: regex por formato de credencial.
- Fuga del prompt: un canario único → coincidencia exacta, fiable y barata, con su
  límite claro (fuga literal, no parafraseada).
