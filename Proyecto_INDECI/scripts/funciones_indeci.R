# Funciones del proyecto INDECI: sesiones 3 y 4.
# Fuente: archivo ORIGINAL INDECI (CSV ; en Latin-1), no alterarlo.
# Rutas relativas a la raiz de Proyecto_INDECI.Rproj.

cargar_indeci_natural <- function(ruta = "datos/00_original/BD_2003-2025_EMERGENCIAS.csv") {
  if (!file.exists(ruta)) stop("No existe el CSV original en: ", ruta)
  raw <- readr::read_delim(
    ruta, delim = ";", locale = readr::locale(encoding = "Latin1"),
    col_types = readr::cols(.default = readr::col_character()),
    trim_ws = TRUE, show_col_types = FALSE, progress = FALSE
  )
  stopifnot(ncol(raw) == 49)
  anio <- suppressWarnings(as.integer(raw[["AÑO"]]))
  fecha <- as.Date(rep(NA_character_, nrow(raw)))
  i25 <- !is.na(anio) & anio == 2025
  fecha[!i25] <- as.Date(raw[["FECHA  DE LA EMER"]][!i25], format = "%d/%m/%Y")
  fecha[i25] <- as.Date(raw[["FECHA  DE LA EMER"]][i25], format = "%m/%d/%y")
  dn <- suppressWarnings(as.numeric(raw[["DAMNIFICADOS"]]))
  # Se filtra por una clasificacion publicada, sin borrar la base fuente.
  naturales <- raw[["TIPO DE PELIGRO"]] == "ORIGEN NATURAL"
  naturales[is.na(naturales)] <- FALSE
  out <- tibble::tibble(
    FILA_ORIGEN_CSV = seq_len(nrow(raw)) + 1L,
    SINPAD = raw[["CODIGO DE EMERGENCIA-SINPAD"]],
    COD_DISTRITO = raw[["COD. DISTRITO"]],
    FECHA_NORMALIZADA = fecha,
    ANIO = anio,
    MES_NOMBRE = raw[["MES"]],
    DEPARTAMENTO = raw[["DPTO."]],
    REGION_NATURAL = raw[["REGIÓN NATURAL"]],
    PELIGRO = raw[["PELIGRO"]],
    DAMNIFICADOS_NUM = dn,
    TIENE_DAMNIFICADOS = dplyr::case_when(
      is.na(dn) ~ NA_character_, dn > 0 ~ "Si", dn == 0 ~ "No", TRUE ~ NA_character_
    )
  )[naturales, ]
  out$TIENE_DAMNIFICADOS <- factor(out$TIENE_DAMNIFICADOS, levels = c("No", "Si"))
  attr(out, "n_original") <- nrow(raw)
  attr(out, "duplicadas_original") <- sum(duplicated(raw))
  out
}

cramer_v <- function(tabla) {
  test <- suppressWarnings(chisq.test(tabla, correct = FALSE))
  n <- sum(tabla)
  v <- sqrt(unname(test$statistic) / (n * min(nrow(tabla) - 1, ncol(tabla) - 1)))
  tibble::tibble(chi2 = unname(test$statistic), gl = unname(test$parameter),
                 valor_p = test$p.value, v_cramer = v,
                 minimo_esperado = min(test$expected))
}

comprobar_indeci <- function(x) {
  stopifnot(nrow(x) == 106301L)
  stopifnot(sum(x$TIENE_DAMNIFICADOS == "Si", na.rm = TRUE) == 29653L)
  stopifnot(sum(x$TIENE_DAMNIFICADOS == "No", na.rm = TRUE) == 76648L)
  stopifnot(!anyNA(x$FECHA_NORMALIZADA))
  invisible(TRUE)
}
