# 03 — El modelo y el over/underfitting

Este es el capítulo más importante para entender *de verdad* un modelo de ML, y el
que más errores de principiante evita.

## La trampa de los datos sintéticos

Si entrenas y evalúas con el **mismo puñado de plantillas**, el modelo **memoriza
las plantillas** y reporta una exactitud de ~1.0. Ese número es **mentira**:
train y test son casi duplicados, así que estás midiendo memoria, no
generalización. Un guardarraíl que presuma de ese 1.0 da falsa confianza y
esconde sus debilidades reales (falsos positivos en texto benigno, ataques nuevos
no detectados).

El síntoma es inconfundible: una validación cruzada de 1.000 ± 0.000 sobre datos
de plantilla que se desploma en cuanto evalúas frases con una estructura que el
modelo no vio en entrenamiento. La exactitud "perfecta" solo medía que train y
test salían del mismo molde; el modelo había memorizado el vocabulario de las
plantillas, no aprendido a reconocer un ataque. Por eso este proyecto se mide con
un split por **familias disjuntas** (más abajo), que no deja que eso pase
desapercibido.

## Overfitting vs underfitting (recordatorio)

- **Overfitting (sobreajuste):** el modelo aprende el ruido/los detalles del
  entrenamiento y no generaliza. Señal: exactitud de train alta, de test baja (una
  **brecha** grande).
- **Underfitting (subajuste):** el modelo es demasiado simple y no captura ni la
  señal. Señal: exactitud baja en train **y** en test.

Queremos el punto medio: buena en test, con brecha pequeña.

## Cómo lo arreglamos aquí

Dos cambios, uno en los datos y uno en el modelo:

### 1) Datos variados con vocabulario solapado

El generador arma prompts de **muchas familias** con **vocabulario que se solapa
entre clases**. A propósito, hay prompts benignos que contienen palabras típicas
de ataque: "What are the **instructions** for resetting my router?", "Can you
**ignore** the typos in my draft?", "What does the **system** prompt box do?". Así
el modelo **no puede** ganar con una sola palabra clave: tiene que aprender
combinaciones.

### 2) Word + char n-grams

El clasificador combina (con `FeatureUnion`) dos vistas TF-IDF:

- **Palabras** (unigramas y bigramas): capturan el fraseo.
- **Caracteres** (`char_wb`, 3-5): capturan señales por debajo de la palabra y
  sobreviven a ofuscación ligera, espacios raros y erratas.

Encima, una regresión logística regularizada (`C=1.0`, `class_weight="balanced"`).

## La evaluación honesta: split por familias

`evaluation.py` **retira familias enteras** del entrenamiento (p. ej. toda la
familia "extraction" de ataques), así el test contiene **estructuras nunca vistas**
al entrenar. Reporta:

```
grouped accuracy : 0.79    # con 40% de familias fuera del entrenamiento
train accuracy   : 1.00
train-test gap   : 0.21    # acotada -> regularizado, no sobreajuste patológico
```

Ese **0.79** es el suelo honesto frente a un **estilo** de ataque nunca visto —el
caso difícil—. Sobre estilos de ataque ya conocidos (en distribución) el
clasificador separa bien lo malicioso de lo benigno, como comprueban las pruebas
de `test_classifier.py`. La cifra que reportamos es la conservadora, la de
familias disjuntas: es la que de verdad dice cuánto generaliza. Y justo porque un
solo modelo nunca basta contra ataques nuevos, el diseño lo combina con reglas
deterministas y umbrales — defensa en profundidad, no confianza en un único
número.

## La lección

- Nunca creas una exactitud perfecta en datos sintéticos: casi siempre es
  memorización.
- Evalúa con un split que fuerce **generalización** (aquí, familias disjuntas) y
  reporta la **brecha** train-test.
- Haz el dato más difícil (vocabulario solapado) para que el modelo aprenda señal,
  no atajos.
- Sé honesto en el README: reporta el número conservador, no el bonito.

## Para fijar la idea

- Datos sintéticos + split aleatorio = 1.0 falso (memorización).
- Overfitting = brecha grande; underfitting = malo en ambos.
- Arreglo: vocabulario solapado + word/char n-grams + regularización + evaluación
  por familias disjuntas, reportando la brecha.
