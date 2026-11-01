# EventHive — Servicio predictivo de recomendaciones

Microservicio Python con FastAPI que calcula la afinidad entre usuarios y un evento recién publicado. Forma parte del MVP de recomendaciones de EventHive.

## 1. Qué hace

1. Spring Boot detecta que un evento pasó a `PUBLICADO`, después de confirmar la transacción.
2. Java consulta PostgreSQL y obtiene un conjunto pequeño de usuarios activos con favoritos o compras confirmadas en la categoría del evento.
3. Java excluye desde la consulta a los usuarios que ya compraron el evento.
4. Java envía a este servicio únicamente el identificador del evento, su categoría y los contadores de comportamiento de cada candidato.
5. Python calcula una puntuación heurística, clasifica cada usuario como `BAJA`, `MEDIA` o `ALTA` y devuelve los resultados ordenados.
6. Python también devuelve `destinatarios`: los usuarios `ALTA` ya ordenados por puntuación y limitados a `limite` (15 por defecto). **El límite se aplica después de ordenar.**
7. Java conserva la responsabilidad de comprobar duplicados y enviar los correos con el servicio de correo/Gmail que ya existe. Si `destinatarios` viene vacío, no se envía nada.

**Este servicio no accede a PostgreSQL, no envía correos y no almacena datos personales.** No necesita nombres ni direcciones de correo. Java debe mantener esos datos localmente y relacionarlos usando `usuarioId`.

## 2. Estructura

```text
eventhive_predictive_python/
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── security.py
│   ├── core/
│   │   ├── config.py
│   │   └── limits.py
│   ├── schemas/
│   │   └── recommendation.py
│   ├── services/
│   │   ├── recommendation_service.py
│   │   ├── scoring.py
│   │   └── selection.py
│   └── main.py
├── tests/
│   ├── test_api.py
│   └── test_scoring.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

- `main.py`: crea la aplicación FastAPI y registra las rutas.
- `api/routes.py`: expone los endpoints HTTP.
- `api/security.py`: valida un token opcional de comunicación entre servicios.
- `core/config.py`: carga configuración desde el entorno; no contiene secretos.
- `core/limits.py`: middleware que limita el tamaño del cuerpo HTTP.
- `schemas/recommendation.py`: valida las solicitudes y define el contrato JSON.
- `services/scoring.py`: calcula la puntuación y el nivel de afinidad.
- `services/recommendation_service.py`: coordina la evaluación y ordena los resultados.
- `services/selection.py`: filtra `ALTA`, ordena y aplica el límite de destinatarios.
- `tests/`: pruebas de la lógica y del endpoint.

## 3. Cálculo de afinidad

La puntuación es una **heurística explicable**, no una probabilidad estadística ni un modelo entrenado.

| Comportamiento | Cálculo | Máximo |
|---|---:|---:|
| Favoritos en la categoría | 8 puntos por favorito, hasta 5 | 40 |
| Eventos comprados en la categoría | 9 puntos por evento, hasta 5 | 45 |
| Entradas compradas en la categoría | 1 punto por entrada, hasta 15 | 15 |
| **Total** | | **100** |

Clasificación inicial:

- `ALTA`: 60 a 100 puntos.
- `MEDIA`: 30 a 59 puntos.
- `BAJA`: 0 a 29 puntos.

Los umbrales son configurables mediante variables de entorno. Para el flujo de correo, Java debe enviar únicamente a usuarios `ALTA` y limitar el envío a 15 por evento. Estos valores son una base inicial para la demostración y se deben ajustar cuando existan resultados reales.

## 4. Contrato HTTP

### `POST /api/v1/recommendations/evaluate`

Solicitud compatible con los nombres camelCase de los DTO Java. No incluir `nombreCompleto` ni `correo` en la petición; Python no los necesita.

```json
{
  "evento": {
    "id": 25,
    "categoriaId": 3,
    "categoriaNombre": "Música"
  },
  "candidatos": [
    {
      "usuarioId": 10,
      "favoritosCategoria": 5,
      "comprasCategoria": 3,
      "entradasCompradas": 4
    },
    {
      "usuarioId": 11,
      "favoritosCategoria": 1,
      "comprasCategoria": 0,
      "entradasCompradas": 0
    }
  ]
}
```

Respuesta:

```json
{
  "recomendaciones": [
    {
      "usuarioId": 10,
      "puntuacion": 71,
      "afinidad": "ALTA"
    },
    {
      "usuarioId": 11,
      "puntuacion": 8,
      "afinidad": "BAJA"
    }
  ],
  "destinatarios": [
    {
      "usuarioId": 10,
      "puntuacion": 71,
      "afinidad": "ALTA"
    }
  ]
}
```

El servicio acepta como máximo 200 candidatos por solicitud, rechaza identificadores repetidos y ordena por puntuación descendente.

`limite` es opcional (por defecto 15, entre 1 y 50). `destinatarios` se calcula en `services/selection.py` con este orden: filtrar `ALTA`, ordenar por puntuación (desempate por `usuarioId`) y recién entonces cortar a `limite`.

**Importante para la consulta SQL de Java:** el tope de 200 candidatos también debe aplicarse después de ordenar. La consulta debe terminar en `ORDER BY <puntuación aproximada> DESC LIMIT 200`; un `LIMIT` sin `ORDER BY` puede dejar fuera a los usuarios con mayor afinidad.

### Otros endpoints

- `GET /health`: comprobación de disponibilidad.
- `GET /docs`: documentación OpenAPI interactiva cuando está habilitada.

## 5. Ejecución local

Requiere Python 3.12 o compatible.

```bash
python -m venv .venv
```

Activar el entorno:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias (`requirements.txt` = producción; `requirements-dev.txt` = producción + pruebas):

```bash
pip install -r requirements-dev.txt
```

Iniciar el servicio:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Comprobar:

```text
GET http://localhost:8000/health
POST http://localhost:8000/api/v1/recommendations/evaluate
```

La documentación interactiva se encuentra en `/docs` si está habilitada.

## 6. Docker

Construir:

```bash
docker build -t eventhive-recommendations .
```

Ejecutar:

```bash
docker run --rm -p 8000:8000 eventhive-recommendations
```

Para una comunicación protegida, configura el mismo token secreto en el entorno del contenedor y en la configuración del cliente Java. No guardes ese secreto en el repositorio ni en el Dockerfile.

## 7. Integración con Spring Boot

Configura en Java la URL base del servicio Python mediante la configuración externa de Spring. El cliente Java debe llamar:

```text
POST /api/v1/recommendations/evaluate
```

El JSON enviado debe seguir el contrato de esta documentación. El DTO que viaja a Python debe contener solo:

- `evento`: `id`, `categoriaId` y, opcionalmente, `categoriaNombre`.
- `candidatos`: `usuarioId`, `favoritosCategoria`, `comprasCategoria` y `entradasCompradas`.

No enviar a Python nombres, correos, teléfonos ni otros datos personales. Java puede mantener un mapa local `usuarioId -> candidato` para recuperar el correo del usuario recomendado.

Flujo recomendado en Java:

1. Publicar el evento y emitir el evento interno de dominio.
2. Procesar la recomendación después del commit de la transacción.
3. Obtener candidatos mediante una consulta SQL selectiva e indexada; no cargar todos los usuarios.
4. Invocar FastAPI con los contadores.
5. Usar `destinatarios` de la respuesta (ya filtrado, ordenado y limitado a 15).
6. Reclamar el envío en `recomendacion_envios` con restricción única `(evento_id, usuario_id)`.
7. Enviar mediante el servicio de correo existente y marcar `ENVIADO` o `ERROR`.

La consulta SQL de candidatos y el registro anti-duplicados pertenecen a Java/PostgreSQL, no a este microservicio.

## 8. Configuración externa

La aplicación lee su configuración desde variables de entorno mediante `pydantic-settings`. `.env.example` contiene nombres y valores vacíos/de ejemplo, no credenciales reales. No se incluyen secretos, URLs de producción ni datos de conexión en el código.

En un despliegue, define la configuración desde el panel de variables/secretos del proveedor. El token de servicio es opcional en desarrollo; en producción se recomienda configurarlo y exigirlo también desde Java.

## 9. Pruebas

```bash
pytest -q
```

Las pruebas cubren los topes del cálculo, los tres niveles de afinidad, el endpoint de salud y el contrato JSON camelCase.

## 10. Uso de memoria

Medido en Python 3.12, con 60 solicitudes simultáneas de 200 candidatos:

| Configuración | Pico de memoria | Hilos |
|---|---:|---:|
| Original (`uvicorn[standard]`, endpoints `def`) | 58 MB | 40 |
| Optimizada | 45 MB | 2 |

Medidas aplicadas:

- Dependencias de producción mínimas: sin extras de uvicorn y sin pytest/httpx en la imagen.
- Endpoint y dependencia de seguridad `async`: el cálculo es liviano y no necesita el pool de hilos.
- `core/limits.py` rechaza con 413 cuerpos mayores a `MAX_BODY_BYTES` mientras llegan, sin cargarlos en memoria (probado con 80 MB: la memoria no se movió).
- Con `DOCS_ENABLED=false` también se desactiva `/openapi.json`.
- Un solo worker y `--limit-concurrency 100`. Para más capacidad, usar más réplicas.

## 11. Despliegue

El proyecto está preparado para desplegarse como un contenedor Docker en un servicio independiente del backend Java:

1. Subir este proyecto a un repositorio Git.
2. Crear un servicio web desde ese repositorio usando el `Dockerfile`.
3. Esperar a que finalice la construcción y el despliegue.
4. Verificar `/health`.
5. Configurar la URL HTTPS del servicio en Spring Boot.
6. Configurar el token compartido, si se habilita la protección.
7. Probar primero la evaluación sin habilitar correos.
8. Activar el flujo real desde Java cuando se haya validado la respuesta y el registro de duplicados.

No es necesario desplegar una base de datos en Python. El servicio es stateless: recibe una evaluación, calcula y responde.

## 12. Consideraciones

- No es machine learning entrenado: es una primera versión basada en comportamiento observable.
- La calidad depende de que las consultas Java calculen correctamente favoritos y compras confirmadas.
- La consulta Java debe usar índices y limitar candidatos; Python también valida el límite de entrada.
- El control de duplicados, consentimiento/preferencias de correo, reintentos y máximo de 15 envíos deben permanecer en Java.
- La respuesta de Python no significa que un correo se haya enviado.
