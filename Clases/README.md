## Principios FAIR

Los principios **FAIR** son un conjunto de buenas prácticas que buscan mejorar la gestión, disponibilidad y reutilización de los datos científicos. Su nombre corresponde a cuatro principios fundamentales:

- **F – Findable (Localizable):** Los datos deben ser fáciles de encontrar mediante identificadores y metadatos descriptivos.
- **A – Accessible (Accesible):** Los datos deben poder recuperarse mediante mecanismos de acceso claros y definidos.
- **I – Interoperable (Interoperable):** Los datos deben utilizar formatos y estándares que faciliten su integración con diferentes herramientas y sistemas.
- **R – Reusable (Reutilizable):** Los datos deben contar con documentación, procedencia y condiciones de uso que permitan su aprovechamiento en futuras investigaciones.

### Aplicación al dataset del INDECI

En este proyecto se realiza una evaluación preliminar de los principios FAIR aplicada a la **Base de Datos de Emergencia y Daños con Poblaciones Vulnerables y Grupos Etáreos 2019–2020**, publicada por el Instituto Nacional de Defensa Civil (INDECI) del Perú.

La base de datos es localizable mediante el portal institucional y permite descargar información en formato Excel (`.xls`). Sin embargo, se identificaron oportunidades de mejora relacionadas con la presentación del archivo, la interoperabilidad y la documentación necesaria para su reutilización.

### Importancia en Ciencia de Datos e IA

Los principios FAIR facilitan la organización, integración y reutilización de conjuntos de datos, contribuyendo a la transparencia y reproducibilidad de los análisis estadísticos y modelos de inteligencia artificial.

**Fuente:** [Portal oficial del INDECI](https://portal.indeci.gob.pe/direccion-politicas-y-planes/base-de-datos-de-emergencia-y-danos/base-de-datos-de-emergencia-y-danos-con-poblaciones-vulnerables-y-grupos-etareos-2019-2020/)

Análisis de emergencias y daños en el Perú – INDECI

Descripción del proyecto

El proyecto tiene como finalidad analizar los registros históricos de emergencias y daños en el Perú, utilizando información oficial del Instituto Nacional de Defensa Civil (INDECI), disponible en el Portal Nacional de Datos Abiertos.

Se trabajó con una base de datos previamente depurada, cuyos resultados fueron organizados en un archivo Excel y presentados mediante un reporte desarrollado en RStudio con Quarto, utilizando HTML como formato de visualización.

Actividades realizadas

Preparación de datos: Se utilizó una base de datos previamente procesada. Los procedimientos específicos de limpieza requieren documentarse con el archivo original y el código empleado.

Análisis descriptivo: Se resumió la distribución de personas damnificadas según el tipo de emergencia, considerando medidas estadísticas y valores acumulados.

Evaluación de normalidad: Se presentaron los resultados de la prueba de Shapiro–Wilk para evaluar el supuesto de normalidad.

Homogeneidad de varianzas: Se incorporaron los resultados de la prueba de Levene.

Comparación entre emergencias: Se utilizó la prueba no paramétrica de Kruskal–Wallis para evaluar diferencias entre los tipos de eventos.

Comparaciones múltiples: Se presentaron los resultados de Dunn con ajuste Bonferroni para identificar diferencias estadísticamente significativas entre grupos.

Análisis geográfico: Se resumieron los resultados según las regiones naturales del Perú.

Evaluación del impacto: Se presentó la clasificación de eventos y el tamaño del efecto reportado.

Herramientas utilizadas

RStudio: Entorno de trabajo.

R: Procesamiento y visualización de resultados.

Quarto: Generación del informe reproducible.

HTML: Presentación del reporte.

Excel: Almacenamiento de resultados estadísticos.

ggplot2: Elaboración de gráficos.

readxl y knitr: Lectura de datos y presentación de tablas.

Resultados y conclusiones

Los resultados reportados evidencian diferencias estadísticas entre algunos tipos de emergencias respecto al número de personas damnificadas. Asimismo, se identificó la importancia de considerar valores extremos y distribuciones asimétricas durante la interpretación.

El reporte HTML integra tablas, gráficos y resultados inferenciales para facilitar la presentación académica de los hallazgos.

Nota metodológica: El documento presenta análisis previamente calculados. No ejecuta nuevamente la limpieza de datos ni permite verificar por sí solo las transformaciones realizadas.

Fuente de información

Instituto Nacional de Defensa Civil (INDECI). Emergencias y daños a nivel nacional. Portal Nacional de Datos Abiertos del Perú.