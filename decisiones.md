# Registro de decisiones metodológicas

Este archivo documenta cada decisión que afecta los datos o los resultados: **qué** se decidió, **por qué** y **qué evidencia** la respalda. Las decisiones se numeran (D1, D2…) y se citan en los scripts de `R/`.

**Formato de cada entrada:** fecha · decisión · alternativas consideradas · justificación · evidencia · impacto en los scripts.

---

## Paso A — Entorno reproducible

### A1. Gestión de paquetes con `renv`
- **Fecha:** 2026-11-05
- **Decisión:** fijar las versiones de R y de los paquetes con `renv.lock`.
- **Alternativas:** instalar paquetes manualmente o usar Docker.
- **Justificación:** `renv` es el estándar en R, es liviano y no requiere instalar software adicional. Docker se descarta por ser excesivo para el alcance del curso.
- **Evidencia:** `renv.lock` registra R 4.3.3 y 89 paquetes (dependencias incluidas) de CRAN.
- **Comandos:**
  ```r
  renv::init()       # una vez, al crear el proyecto
  renv::snapshot()   # cada vez que se agrega o actualiza un paquete
  renv::restore()    # para reproducir en otra computadora
  ```

### A2. Estructura de carpetas y rutas relativas
- **Decisión:** separar `data/raw` (intocable), `data/processed`, `R/` y `outputs/`, y usar solo rutas relativas a la raíz del proyecto (`.Rproj`).
- **Justificación:** evita rutas del tipo `C:/Users/...` que no funcionan en otra computadora y protege los datos originales de modificaciones.

### A3. Semilla aleatoria fija
- **Decisión:** `SEMILLA <- 2026` (en `00_config.R`) para la submuestra de Shapiro-Wilk y el bootstrap.
- **Justificación:** sin semilla, los resultados aleatorios cambian en cada ejecución.

### A4. Microdatos fuera de Git
- **Decisión:** `data/raw/` está en `.gitignore`.
- **Justificación:** la base original es grande, la distribuye el INDECI y podría contener localizaciones finas. Se documenta cómo obtenerla en `data/raw/README.md`.

---

## Paso B — Decisiones de datos y análisis

### D1. Selección del archivo de trabajo
- **Fecha:** 2026-11-05
- **Decisión:** usar `RESULTADOS_FINALES_INDECI.xlsx` y descartar el `RESULTADOS_DANOS_INDECI.xlsx` original.
- **Alternativas:** usar ambos archivos o corregir el de daños.
- **Justificación:** en RESULTADOS_DANOS, la media y la mediana de damnificados repetían el **total** en las 17 filas, había conteos de ganado con decimales y 3 hojas de Dunn estaban vacías. RESULTADOS_FINALES pasó todas las verificaciones.
- **Evidencia:** `outputs/tablas/verificacion_calidad.csv` (8/8 verificaciones en TRUE: RIC = P75 − P25, media = total/n, % que suman 100, n por región = 94 869, gl de Levene, η², 136 pares de Dunn, 0 celdas vacías).
- **Script:** `01_limpieza.R`

### D2. Kruskal-Wallis en lugar de ANOVA
- **Decisión:** comparar los grupos con Kruskal-Wallis.
- **Alternativas:** ANOVA de un factor, ANOVA de Welch o un modelo de conteo.
- **Justificación:** no se cumplen los supuestos del ANOVA. Los datos son conteos asimétricos con entre 25 % y 98 % de ceros.
- **Evidencia:** Shapiro-Wilk p < 0,0001 en 17/17 grupos; Levene F(16, 94 852) = 61,65, p < 0,0001.
- **Script:** `03_inferencia.R`

### D3. Post hoc de Dunn con corrección de Bonferroni
- **Decisión:** comparaciones por pares con la prueba de Dunn y ajuste de Bonferroni.
- **Alternativas:** Holm, Benjamini-Hochberg (FDR) o Conover.
- **Justificación:** Bonferroni es la más conservadora y controla el error de tipo I en 136 comparaciones (α ajustado = 0,05/136 = 0,00037). Con n = 94 869, la potencia es alta incluso con una corrección estricta.
- **Evidencia:** 88/136 pares significativos (64,7 %).

### D4. Análisis de sensibilidad sin el sismo de Pisco 2007
- **Decisión:** repetir Kruskal-Wallis excluyendo el sismo de Pisco (15/08/2007).
- **Justificación:** es un evento extremo que podría dominar la categoría SISMO.
- **Evidencia:** H pasa de 19 413,49 a 19 407,05 (−0,03 %). La conclusión es **robusta**.

### D5. Tamaño del efecto: η² de Kruskal-Wallis
- **Decisión:** reportar η²_H = (H − k + 1)/(n − k).
- **Justificación:** con n ≈ 95 000 casi cualquier diferencia es significativa; el tamaño del efecto indica la relevancia práctica.
- **Evidencia:** η² = 0,2045, un efecto **grande** (umbral > 0,14). El script lo recalcula y coincide con el archivo (tolerancia de 0,0005).

### D6. Shapiro-Wilk sobre una submuestra de 200 por grupo
- **Decisión:** aplicar la prueba a una submuestra aleatoria de hasta 200 eventos por peligro (semilla A3).
- **Justificación:** con n muy grande, Shapiro-Wilk rechaza ante desviaciones mínimas, y la función de R admite como máximo 5000 casos. La submuestra da una prueba informativa.

### D7. Reporte de p-valores iguales a 0
- **Decisión:** reportar p < 1×10⁻⁴ como "< 0.0001" y guardar el valor numérico en una columna aparte.
- **Justificación:** un p-valor nunca es exactamente 0. El 0 aparece por el límite de precisión numérica de la computadora. Además, el archivo original mezclaba p-valores como texto y como número (problema de interoperabilidad, FAIR-I).
- **Script:** funciones `formatear_p()` y `p_a_numero()` en `00_config.R`.

### D8. Variables del perfil para clustering (etapa de IA)
- **Decisión:** perfilar cada peligro con log(1+media), log(1+P75), log(1+P95), % de ceros y log(1+% del total), estandarizadas (z).
- **Alternativas:** usar solo la media o incluir la desviación estándar.
- **Justificación:** se describe la **forma completa** de la distribución (centro, cola, ceros, peso). La transformación logarítmica evita que el sismo domine las distancias. La desviación estándar se excluye por ser redundante con P95 y muy sensible a extremos.
- **k = 4:** se fija para contrastar con la clasificación actual de 4 niveles. La silueta es máxima para Ward en k = 4 (0,318).

### D9. Estabilidad por bootstrap
- **Decisión:** 500 réplicas bootstrap; un clúster se considera estable si su índice de Jaccard medio es ≥ 0,75 (Hennig, 2007).
- **Justificación:** con solo 17 observaciones, los clústeres pueden ser artefactos de la muestra.

### D10. Interpretación del clustering *(resultado)*
- **Resultado:** el clúster {SISMO, INUNDACIÓN, LLUVIA INTENSA} es estable (Jaccard = 0,85) y el de peligros de bajo impacto y muchos ceros también lo es (0,77). Los otros dos no alcanzan el umbral (0,73).
- **Concordancia:** ARI ≈ 0,16 entre clústeres y clasificación actual; ARI = 0,79 entre Ward y PAM.
- **Decisión:** **mantener la clasificación de 4 niveles como resultado principal** (se basa en la media y es interpretable) y reportar el clustering como **validación complementaria**. El clustering muestra que la lluvia intensa se parece en su perfil a los peligros de alto impacto por su peso en el total, aunque su media por evento sea moderada.
- **Implicancia:** priorizar por media y priorizar por impacto acumulado dan órdenes distintos. Ambos deben reportarse.

### D11. Uso de IA generativa
- **Decisión:** se usó un asistente de IA generativa para redactar la documentación y el borrador de los scripts.
- **Control:** todo el código se ejecutó de principio a fin (`run_all.R`), sin errores ni advertencias. Las cifras del README y de la propuesta se contrastaron con `outputs/tablas/`.

---

## Pendientes

- [ ] Confirmar el período de la base SINPAD y la licencia exacta del conjunto de datos de origen.
- [ ] Obtener los microdatos y ejecutar el **Modo B** de `03_inferencia.R` para reproducir H, Levene y Dunn de forma independiente.
- [ ] Publicar un release en GitHub y enlazarlo a Zenodo para obtener el DOI.
- [ ] Extensión futura: modelo hurdle o binomial negativa inflada en ceros con covariables (población expuesta, año, región).
