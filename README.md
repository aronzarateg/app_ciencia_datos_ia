# Heterogeneidad del impacto humano de los desastres en el Perú

Comparación no paramétrica del número de damnificados por tipo de peligro a partir del registro SINPAD-INDECI (n = 94 869 emergencias).

| | |
|---|---|
| **Autor(a)** | [Nombre del estudiante] — [correo institucional] |
| **Curso** | [Nombre del curso] |
| **Versión** | 0.1.0 (noviembre 2026) |
| **Licencia** | Código: MIT · Datos derivados y resultados: CC BY 4.0 |
| **DOI** | *(pendiente: se asigna al publicar el release en Zenodo)* |

---

## 1. Pregunta de investigación

> ¿Difiere significativamente la distribución del número de damnificados por emergencia según el tipo de peligro registrado por el INDECI y qué proporción de su variabilidad explica el tipo de peligro?

- **H0:** las distribuciones de damnificados por evento son iguales en los 17 tipos de peligro.
- **H1:** al menos un tipo de peligro tiene una distribución distinta.
- **Alcance:** descriptivo y explicativo (asociativo, no causal). α = 0,05, con corrección de Bonferroni.

## 2. Datos

| Elemento | Descripción |
|---|---|
| **Fuente** | Instituto Nacional de Defensa Civil (INDECI), Sistema de Información Nacional para la Respuesta y Rehabilitación (SINPAD), registros de Evaluación de Daños y Análisis de Necesidades (EDAN) |
| **Archivo de trabajo** | `data/processed/RESULTADOS_FINALES_INDECI.xlsx` (8 hojas de resultados agregados) |
| **Unidad de análisis** | Emergencia registrada |
| **Variable dependiente** | Número de damnificados por evento (discreta, ≥ 0) |
| **Variable independiente** | Tipo de peligro (nominal, 17 categorías) |
| **Estratificación** | Región natural (costa, sierra, selva alta, selva baja) |
| **Período** | *Confirmar en la base original* (incluye el sismo de Pisco de 2007) |
| **Datos personales** | No contiene. Solo resultados agregados (Ley N.° 29733) |

El diccionario de datos está en [`docs/diccionario_datos.csv`](docs/diccionario_datos.csv). Para obtener los microdatos originales y reproducir las pruebas desde cero, ver [`data/raw/README.md`](data/raw/README.md).

## 3. Estructura del repositorio

```
indeci-damnificados/
├── README.md                  # este archivo
├── decisiones.md              # registro de decisiones metodológicas (Paso B)
├── renv.lock                  # versiones exactas de R y paquetes (Paso A)
├── run_all.R                  # ejecuta todo el análisis en orden
├── indeci-damnificados.Rproj
├── CITATION.cff               # metadatos para citar (FAIR: Findable)
├── LICENSE
├── R/
│   ├── 00_config.R            # rutas, parámetros y funciones comunes
│   ├── 01_limpieza.R          # verificación de calidad y exportación a CSV
│   ├── 02_descriptivos.R      # tablas y figuras descriptivas
│   ├── 03_inferencia.R        # Shapiro, Levene, Kruskal-Wallis, Dunn, η²
│   └── 04_clustering.R        # etapa de IA: clustering Ward + PAM
├── data/
│   ├── raw/                   # microdatos SINPAD (no se versionan)
│   └── processed/             # RESULTADOS_FINALES_INDECI.xlsx (+ CSV generados)
├── docs/
│   └── diccionario_datos.csv
└── outputs/
    ├── tablas/                # 15 tablas CSV
    └── figuras/               # 6 figuras PNG (300 dpi)
```

## 4. Cómo reproducir el análisis

**Requisitos:** R ≥ 4.3 y RStudio (recomendado). Si usa Windows, se recomienda R ≥ 4.2 por el soporte nativo de UTF-8 (tildes en los nombres de peligros).

```r
# 1. Clonar el repositorio y abrir indeci-damnificados.Rproj en RStudio

# 2. Paso A: restaurar el entorno exacto de paquetes
install.packages("renv")
renv::restore()        # instala las versiones registradas en renv.lock

# 3. Ejecutar todo el análisis (≈ 5 segundos)
source("run_all.R")
```

Desde la terminal: `Rscript run_all.R`

Los scripts deben ejecutarse **desde la raíz del proyecto**. `run_all.R` los corre en orden y guarda `outputs/sessionInfo.txt` con el detalle del entorno usado.

## 5. Flujo de análisis

| Script | Qué hace | Salidas principales |
|---|---|---|
| `01_limpieza.R` | Revisa celdas vacías y duplicados, hace 8 verificaciones de consistencia interna, estandariza los p-valores y códigos de peligro, y exporta a CSV UTF-8 | `verificacion_calidad.csv`, `data/processed/csv/` |
| `02_descriptivos.R` | Descriptivos por peligro y por grupo de impacto, y concentración del total | `descriptivos_*.csv`, figuras 1 a 3 |
| `03_inferencia.R` | **Modo A:** consolida y verifica la inferencia del archivo. **Modo B:** si hay microdatos, re-ejecuta las pruebas | `inferencia_*.csv`, figura 4 |
| `04_clustering.R` | Clustering jerárquico (Ward.D2) y PAM, selección de k por silueta, estabilidad bootstrap (Jaccard) e índice de Rand ajustado frente a la clasificación actual | `clustering_*.csv`, figuras 5 y 6 |

## 6. Resultados principales

- **Concentración:** sismo, inundación y lluvia intensa suman el **73,3 %** de los 2 020 540 damnificados.
- **Supuestos:** no hay normalidad (Shapiro-Wilk p < 0,0001 en 17/17 grupos) y las varianzas son heterogéneas (Levene F(16, 94 852) = 61,65; p < 0,0001). Por eso se usa Kruskal-Wallis.
- **Kruskal-Wallis:** H(16) = 19 413,49; p < 0,0001. **η² = 0,204 (efecto grande):** el tipo de peligro explica alrededor del 20 % de la variabilidad en rangos.
- **Robustez:** sin Pisco 2007, H(16) = 19 407,05; p < 0,0001. La conclusión no cambia.
- **Dunn-Bonferroni:** 88 de 136 pares (64,7 %) difieren significativamente (α ajustado = 0,00037).
- **IA (clustering):** los datos forman un grupo estable de alto impacto (**sismo, inundación y lluvia intensa**; Jaccard = 0,85). La concordancia con la clasificación actual de 4 niveles es baja (ARI ≈ 0,16): los clústeres agrupan por la *forma* de la distribución (inflación de ceros, cola) y no solo por la media. Ver D10 en `decisiones.md`.

## 7. Limitaciones

1. Los resultados son agregados: sin microdatos no se pueden recalcular las pruebas ni controlar por exposición o vulnerabilidad.
2. Puede haber subregistro en el EDAN en zonas rurales y remotas.
3. El clustering se hace sobre solo 17 peligros, así que dos clústeres no alcanzan la estabilidad mínima (Jaccard < 0,75). Se usa como validación, no como resultado principal.
4. Es un diseño observacional: las asociaciones no implican causalidad.

## 8. Cómo citar

> [Apellido, Nombre]. (2026). *Heterogeneidad del impacto humano de los desastres en el Perú* (v0.1.0) [Código y datos]. GitHub. https://github.com/[usuario]/indeci-damnificados

Fuente de los datos: Instituto Nacional de Defensa Civil (INDECI). Sistema de Información Nacional para la Respuesta y Rehabilitación (SINPAD).

## 9. Uso de IA

Se usó un asistente de IA generativa para apoyar la redacción de la documentación y el código. Todo el código se ejecutó y sus resultados se contrastaron con el archivo de origen (ver `outputs/tablas/verificacion_calidad.csv` y D11 en `decisiones.md`).
