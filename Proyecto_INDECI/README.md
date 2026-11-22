# Proyecto INDECI - Analisis de Datos e IA Aplicada

Estructura inicial del proyecto para avanzar clase por clase en RStudio y Quarto.

## Estado inicial
- Incluye solamente el CSV original de INDECI, **sin modificaciones**.
- No se han agregado notebooks, analisis, graficos ni articulo.
- No se han entrenado modelos.

## Carpetas
- `datos/00_original/`: CSV oficial descargado. Nunca sobrescribir este archivo.
- `datos/01_procesados/`: versiones derivadas y limpiadas que se generen despues.
- `sesiones/`: un archivo Quarto `.qmd` por sesion, cuando corresponda.
- `scripts/`: codigo reutilizable en R.
- `resultados/tablas/`: tablas exportadas de cada analisis.
- `resultados/figuras/`: figuras exportadas de cada analisis.
- `articulo/`: manuscrito cientifico final, por construir.
- `documentacion/`: diccionario de variables, bitacora y decisiones metodologicas.

## Como empezar
1. Extrae el ZIP completo en una carpeta de tu PC.
2. Abre `Proyecto_INDECI.Rproj` en RStudio.
3. En cada clase crea el nuevo archivo `.qmd` dentro de `sesiones/`.
4. Guarda tablas y figuras en `resultados/`, y documenta cada paso.
5. No reemplaces el CSV original por una version limpiada.

## GitHub
El archivo CSV original se incluye en el ZIP para tu trabajo local, pero el `.gitignore` lo excluye de GitHub por defecto. Para que otras personas lo obtengan, publica un enlace a la fuente oficial y sus instrucciones de descarga.
