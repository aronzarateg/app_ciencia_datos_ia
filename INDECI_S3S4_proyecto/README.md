# Análisis de desastres naturales e impacto humano — INDECI

**Curso:** Ciencia de Datos e IA Aplicada · Sesiones 3 y 4  
**Herramientas:** RStudio, Quarto, R.  
**Origen:** Archivo `RESULTADOS_FINALES_INDECI.xlsx` proporcionado para este proyecto.

## Pregunta de investigación
¿Existen diferencias en el número de damnificados entre tipos de eventos naturales y cómo se distribuye el impacto por región natural?

## Hipótesis
- H0: Las distribuciones del número de damnificados son iguales entre los tipos de evento.
- H1: Al menos un tipo de evento presenta una distribución diferente.

## Advertencia metodológica
La fuente disponible es un **libro de resultados agregados**, no una base de registros individuales. Las cifras de pruebas estadísticas se presentan como resultados aportados por la fuente; no se vuelven a calcular con observaciones ficticias. No es posible ejecutar correctamente un split train/test, SMOTE, PCA a nivel individual o modelos de ensamble con este archivo. Para ello se requiere la base original con una fila por evento.

## Estructura
- `analisis/S3S4_parte1.qmd`: análisis descriptivo, pruebas reportadas, visualización e interpretación.
- `analisis/eda_automatico.qmd`: resumen parametrizable de hojas de resultados.
- `data/raw/`: libro Excel original sin modificar.
- `data/processed/`: ocho CSV exportados directamente de cada hoja.
- `notebooks/`: reservado para modelos de ensamble cuando se disponga de datos individuales.

## Ejecución
1. Abrir `INDECI_S3S4.Rproj` en RStudio.
2. Instalar paquetes: `install.packages(c("readr", "dplyr", "ggplot2", "knitr", "tidyr", "here", "scales"))`.
3. Abrir `analisis/S3S4_parte1.qmd` y pulsar **Render**.
4. Opcional: renderizar `analisis/eda_automatico.qmd`.

**Estado:** adaptación de código preparada; renderización y ejecución en RStudio pendientes de validación local.
