# 01 — El modelo de amenazas

## Qué defiende

llm-shield cubre los riesgos de la capa de **texto** de una aplicación con LLM, en
las dos fronteras de confianza:

**Entrada del usuario (lo que entra al modelo):**

- **Inyección directa de prompt:** el usuario le ordena al modelo ignorar su
  system prompt, cambiar de persona ("DAN", "developer mode") o desactivar la
  seguridad.
- **Extracción del system prompt:** intentos de que el modelo revele sus
  instrucciones ocultas.
- **Cargas ofuscadas:** instrucciones escondidas en un blob base64/opaco para
  evadir filtros de palabras clave.

**Salida del modelo (lo que sale hacia el usuario):**

- **Exfiltración:** el modelo emite secretos (claves de API, tokens, claves
  privadas) o filtra el system prompt literal.

## Qué NO defiende (y por qué decirlo importa)

Un buen proyecto de seguridad es **riguroso sobre su alcance**. llm-shield **no**
es:

- un sustituto de la alineación del propio modelo;
- control de autorización sobre las herramientas que el modelo puede llamar;
- codificación de salida contra XSS en tu frontend.

Es el **filtro de la capa de texto** que complementa esas defensas, no las
reemplaza. Decir esto evita una falsa sensación de seguridad, que en seguridad es
peor que no tener la defensa.

## Inyección indirecta: la trampa

La inyección **indirecta** llega por texto que el modelo lee pero que no escribió
el usuario: un documento recuperado (RAG), la salida de una herramienta, un correo
citado. llm-shield solo la atrapa si **ese** texto también pasa por `scan_input`.
La lección de diseño: hay que envolver el escudo alrededor de **toda** fuente de
texto no confiable, no solo el turno del usuario.

## Para fijar la idea

- Dos fronteras: entrada (inyección, extracción, ofuscación) y salida (fugas de
  secretos y del system prompt).
- Es una capa de defensa, no toda la defensa: se declara explícitamente qué no
  cubre.
- La inyección indirecta exige pasar por el escudo también el texto recuperado y
  la salida de herramientas.
