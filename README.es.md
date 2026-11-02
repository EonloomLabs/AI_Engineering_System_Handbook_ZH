# Ingeniería de sistemas de IA: de los fundamentos al funcionamiento interno

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) · **Español** · [Tiếng Việt](README.vi.md)

Libro sin conexión · conceptos básicos, mecanismos internos y práctica de ingeniería

De los fundamentos al funcionamiento interno: comprender cómo los modelos de lenguaje procesan entradas y generan salidas, cómo los agentes usan herramientas y gestionan contexto y memoria, y cómo mejorar la calidad de ingeniería con métodos verificables.

## Cómo abrirlo

Descomprime el paquete y abre [`es/index.html`](es/index.html). Sin servidor, sin red, sin API de modelo ni claves.
El selector de idioma de la cabecera de cada página lleva a la misma página en otra edición.

## Estructura del curso

El recorrido principal son cinco etapas y 68 lecciones: primero observar el sistema, después descender capa por capa hasta el interior del modelo y volver por último a la verificación de toda la pila.

| Etapa | Lecciones | Contenido |
| --- | --- | --- |
| Observar el sistema | 01—06 | Convertir la ejecución de una tarea en evidencia revisable antes de cambiar nada |
| Construir el bucle | 07—28 | Llamadas a herramientas, contexto, recuperación, memoria y recuperación ante fallos |
| Optimizar la caja negra | 29—34 | Sin abrir el modelo: permisos, una tarea fija y un cronometraje completo deciden si la optimización sirvió |
| Asumir el control del modelo | 35—63 | De la interfaz del servicio a los tensores, la pasada hacia delante, el entrenamiento y la inferencia, hasta la GPU y la planificación |
| Verificación de toda la pila | 64—68 | Reconectar multimodalidad, incertidumbre y optimización entre capas al mismo criterio de aceptación |

Las 40 lecciones de fundamentos llevan preguntas de autoevaluación; los 28 capítulos de sistemas se organizan en torno a 112 preguntas principales. Doce temas de lectura permiten entrar por un problema concreto cuando ya hay base.
El texto, los diagramas y las notas de las fórmulas están desplegados; las respuestas de autoevaluación están plegadas por omisión.

## Dónde está cada cosa

| Ruta | Contenido |
| --- | --- |
| [`es/index.html`](es/index.html) | Punto de entrada de lectura |
| [`es/complete.html`](es/complete.html) | El mismo contenido como texto continuo, sin depender de otros archivos |
| [`es/worked-examples.html`](es/worked-examples.html) | Índice de ejemplos resueltos, localizables por número |
| [`es/worked-model.html`](es/worked-model.html) | Las mismas dos frases llevadas hasta el final por todas las matrices intermedias |
| [`labs/model/`](labs/model/) | Código del modelo de ejemplo, parámetros originales, parámetros entrenados y registros numéricos |
| [`worked-examples/`](worked-examples/) | Testigos numéricos y de estado deterministas y ejecutables |
| [`diagrams/`](diagrams/) | Fuentes, datos y comprobaciones de los diagramas |
| [`wiki/`](wiki/) | Texto y tabla de contenidos editables del wiki |
| [`editorial/`](editorial/) | Método de redacción y registro de migración de contenido |
| [`validation/integration/`](validation/integration/) | Comprobaciones de esta ronda |
| [`i18n/`](i18n/) | Tabla de traducción, herramientas y registros de validación |

## Recalcular los números

No hacen falta red, GPU ni clave de API. Con Python 3.10 o superior, ejecuta esto en el directorio descomprimido:

```bash
python3 worked-examples/run_all.py
```

El código ejecutable y los datos del modelo están en la raíz del repositorio y los comparten todas las ediciones; los comentarios y la salida de los scripts están en chino.
Cambiar un ejemplo obliga a volver a ejecutarlo y a sincronizar los diagramas, el texto, el índice de búsqueda y la edición continua; las convenciones están en [`AGENTS.md`](AGENTS.md).

## Ediciones

| Idioma | Punto de entrada |
| --- | --- |
| 简体中文 (texto de referencia) | [`index.html`](index.html) |
| English | [`en/index.html`](en/index.html) |
| 日本語 | [`ja/index.html`](ja/index.html) |
| Español | [`es/index.html`](es/index.html) |
| Tiếng Việt | [`vi/index.html`](vi/index.html) |

Cada edición tiene 262 páginas paginadas más un `complete.html` con el mismo contenido. El chino es el texto de referencia; las dudas de traducción y los posibles defectos del original se anotan en [`i18n/SOURCE-ISSUES.md`](i18n/SOURCE-ISSUES.md) en lugar de corregirse por cuenta propia.

## Límites de la validación

401 ejemplos didácticos no equivalen a 401 experimentos sobre la capacidad de un modelo. Las pruebas verifican fórmulas numéricas, dimensiones, causalidad, gradientes, fragmentación de protocolo y comportamiento de estado simplificado; los demás ejemplos de escenario razonan de forma explícita a partir de premisas declaradas.
No demuestran la eficacia de un agente comercial, la velocidad de una GPU, el interior de código cerrado ni la seguridad en producción.
Las fuentes apuntan a archivos, funciones y números de línea reales; la derivación de ingeniería, la medición y la simulación didáctica se señalan por separado.
El redondeo de las figuras numéricas es solo para mostrar; el cálculo usa la precisión original.

El alcance de la verificación de fuentes está en [`engineering/agent-evidence.html`](engineering/agent-evidence.html), con los registros de máquina en `engineering/agent-practice/verified/`.
