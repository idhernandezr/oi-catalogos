# oi-catalogos

Archivos que lee el **Generador de OI** (`oi_generador.html`) cada vez que se abre.
Si cambias algo aquí, todos los vendedores lo ven la próxima vez que abran el HTML. No hay que redistribuir nada.

| Archivo | Qué es | Cuándo editarlo |
|---|---|---|
| `catalogo.json` | Productos (Categoría → Vertical → Tipo → Producto → Medidas, CTR, Completion), frecuencias, plataformas | Al agregar o cambiar productos |
| `config.json` | URL del form de Monday, nombres de parámetros y listas (Dirección Comercial, Propuesta, Prioridad, Tipo de solicitud) | Al cambiar el form o sus opciones |
| `plantilla_oi.xlsx` | Plantilla de la OI con formato | Al cambiar el diseño de la OI (ver reglas abajo) |
| `version.json` | Versiones y un mensaje opcional que se muestra arriba | Cada vez que publiques un cambio |
| `oi_generador.html` | La herramienta | Solo cuando haya una versión nueva |

## Cómo publicar un cambio

1. Edita el archivo en GitHub (lápiz ✏️) y guarda con **Commit changes**.
2. En `version.json`, actualiza la fecha del archivo que cambiaste (`catalogo`, `config` o `plantilla`).
3. Si subes un `oi_generador.html` nuevo, sube también `"app"` (por ejemplo `1.0.1`): los vendedores verán un aviso para descargarlo.

GitHub tarda hasta 5 minutos en servir la versión nueva.

## Agregar un producto a `catalogo.json`

Copia un bloque dentro de `"productos"` y cambia los valores. `ctr` y `completion` van como decimal (`0.015` = 1.5%) o `null` si no aplica:

```json
{ "categoria": "O&O", "vertical": "TELEVISA ADS RON", "tipo": "DISPLAY", "producto": "NUEVO FORMATO",
  "medidas": "300x250 | 728x90", "ctr": 0.0013, "completion": null }
```

## Parámetros del form de Monday (`config.json` → `params`)

En cada pregunta del form, en **Settings → Parameter**, escribe exactamente el nombre de la derecha:

| Pregunta del form | Parameter |
|---|---|
| Quién Solicita | `solicita` |
| Correo electrónico | `correo` |
| Account Manager | `account_manager` |
| Cuenta | `cuenta` |
| Nombre de Campaña | `campana` |
| Geolocalización de campaña | `geo` |
| Presupuesto | `presupuesto` |
| CPM Especial (lista) | `cpm_especial` |
| ¿Cuál? (texto de CPM especial) | `cpm` |
| Calendario (rango de fechas) | `calendario` → se envía como `AAAA-MM-DD,AAAA-MM-DD` (`calendario_formato`) |
| Especificaciones Calendario | `esp_calendario` |
| Dirección Comercial | `direccion` |
| Tu propuesta es | `propuesta` |
| Prioridad | `prioridad` |
| Tipo de Solicitud | `tipo_solicitud` (opciones separadas por coma) |
| Estrategia | `Source` (ya existía en el form) |
| Notificación al Planner | `comentarios` (ya existía en el form) |

El script `configurar_parametros_monday.py` los configura vía API (no sobrescribe los que ya existen salvo con `--forzar`) y avisa si las opciones de las listas no coinciden con el form.

Si Monday te obliga a usar otro nombre, cambia solo el valor en `config.json` (no la clave).
Hoy `form_url` apunta al form de **pruebas**. Para pasar a producción, copia el valor de `form_url_produccion` en `form_url`.

## Reglas de la plantilla

El HTML escribe en celdas fijas de la hoja **OI - Pauta**. Si editas la plantilla, no muevas:
encabezado D8–D22 y H8–H19, pauta en filas 26–40 (columnas B–U), total en fila 41, resumen en T43–T45 y términos en B48.
