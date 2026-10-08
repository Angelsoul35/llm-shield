# 05 — Preguntas de entrevista

Preguntas típicas sobre este proyecto y cómo responderlas con seguridad.
Practica diciéndolas en voz alta en inglés también.

## Sobre el enfoque

**¿Por qué reglas y clasificador, y no solo uno?**
Porque fallan distinto. Las reglas son precisas pero frágiles (un reformuleo las
esquiva); el clasificador generaliza pero es probabilístico. Juntos cubren la
debilidad mutua. Además los combino de forma monótona: la severidad de las reglas
pone un suelo al riesgo, así lo conocido-malo nunca queda perdonado por una
puntuación baja.

**¿Por qué tres veredictos y no block/allow?**
Porque el tráfico real tiene zona gris. `flag` permite una acción intermedia
(fricción, revisión, pedir reformular). Los umbrales son configurables para que el
operador fije el balance precisión/recall.

## Sobre el modelo (la pregunta clave)

**Tu validación da ~1.0. ¿No es sospechoso?**
Sí, y por eso **no** reporto ese número. Con datos sintéticos de plantillas, un
split aleatorio mide memorización, no generalización. Evalúo con un **split por
familias disjuntas** (retiro familias enteras del entrenamiento) y reporto ~0.79,
más la brecha train-test (0.21, acotada). También pruebo con frases escritas a
mano fuera de plantilla.

**¿Cómo sabes si hay overfitting o underfitting?**
Overfitting: train alto, test bajo (brecha grande). Underfitting: malo en ambos.
Mido las dos y acoto la brecha con un test. Para reducir el sobreajuste: datos con
vocabulario solapado entre clases (para que no gane con una palabra), word + char
n-grams, y regularización (`C=1.0`, `class_weight="balanced"`).

**¿Por qué char n-grams además de palabras?**
Porque capturan señales por debajo de la palabra y sobreviven a ofuscación,
espacios y erratas (p. ej. "i g n o r e" o "ignoree"). Ayudan a generalizar a
frases fuera de plantilla, que es justo lo que mide la evaluación por familias
disjuntas (~0.79).

## Sobre la salida

**¿Cómo detectas la fuga del system prompt sin falsos positivos?**
Con un canario: un token único incrustado en el prompt. Una coincidencia exacta de
subcadena. Si aparece en la salida, se filtró. Fiable, barato y sin guardar el
prompt en el detector. Límite: atrapa la fuga literal, no la parafraseada.

## Sobre el alcance (madurez de seguridad)

**¿Esto hace segura mi app con LLM?**
No por sí solo. Es la capa de texto. No sustituye la alineación del modelo, la
autorización de herramientas ni la codificación de salida. Y la inyección
indirecta solo se atrapa si paso por el escudo también el texto recuperado y la
salida de herramientas, no solo el turno del usuario. Decir esto es parte del
trabajo: una falsa sensación de seguridad es peor que ninguna.

## Pregunta trampa

**Si subes el `block_threshold` a 0.95, ¿qué pasa?**
Bajan los falsos positivos (menos texto benigno bloqueado) pero suben los falsos
negativos (más ataques nuevos pasan), porque solo bloqueas cuando el modelo está
muy seguro. Las reglas de severidad alta siguen bloqueando igual (su suelo es
0.95), así que los ataques conocidos no se ven afectados; el umbral solo mueve la
sensibilidad del clasificador para lo novedoso. Es la palanca precisión/recall del
operador.
