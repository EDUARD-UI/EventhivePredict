# Documentación de endpoints de EventHive Backend

Este documento describe los principales endpoints del backend, indicando qué reciben, qué validaciones requieren y qué estructura devuelven.

## 1. Estructura general de respuesta

Todos los endpoints responden con un envoltorio `ApiResponse<T>`:

```json
{
  "success": true,
  "mensaje": "Mensaje descriptivo",
  "data": { }
}
```

Ejemplo concreto de un objeto devuelto:

```json
{
  "success": true,
  "mensaje": "Usuario obtenido",
  "data": {
    "id": 1,
    "nombre": "C",
    "edad": 34,
    "correo": "carlos@email.com"
  }
}
```

> Importante: `data` puede contener un objeto simple, un array o un objeto paginado. Si su valor es `null` (por ejemplo, en respuestas `Void` y errores), `ApiResponse` lo omite del JSON. Algunos ejemplos `Void` muestran `data: null` solo como representación conceptual.

La mayoría de respuestas paginadas usan `PagedResponse<T>`:

```json
{
  "content": [
    {}
  ],
  "pageNumber": 0,
  "pageSize": 10,
  "totalElements": 25,
  "totalPages": 3,
  "hasNext": true,
  "hasPrevious": false
}
```

Algunos endpoints devuelven directamente `Page<T>` de Spring Data; su estructura paginada puede incluir metadatos adicionales propios de Spring.

En caso de error, la respuesta suele devolver:

```json
{
  "success": false,
  "mensaje": "Descripción del error"
}
```

---

## 2. Auth

### Base: `/api/auth`

#### `GET /api/auth/me`
- Recibe: no body, requiere sesión activa.
- Devuelve: `ApiResponse<UsuarioSesionDTO>`
- Descripción: devuelve la sesión actual del usuario autenticado.
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Sesión activa",
  "data": {
    "id": 7,
    "nombre": "Carlos",
    "correo": "carlos@email.com",
    "telefono": "+56912345678",
    "imagenPerfil": "https://storage.example/imagenPerfil/user_123.jpg",
    "urlImagenPerfil": "https://storage.example/imagenPerfil/user_123.jpg",
    "rolNombre": "CLIENTE"
  }
}
```

#### `POST /api/auth/login`
- Recibe: body `LoginRequest` con `correo` y `clave`.
- Devuelve: `ApiResponse<LoginResponseDTO>`
- Descripción: autentica al usuario y devuelve tokens/usuario.
- Permisos: público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Login exitoso",
  "data": {
    "id": 7,
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": "eyJzdWIiOiJjYXJsb3NAY...",
    "tipo": "Bearer",
    "correo": "carlos@email.com",
    "rol": "CLIENTE"
  }
}
```

#### `POST /api/auth/refresh`
- Recibe: body `RefreshRequest` con `refreshToken`.
- Devuelve: `ApiResponse<LoginResponseDTO>`
- Descripción: renueva el token de acceso.
- Permisos: público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Token renovado",
  "data": {
    "id": 7,
    "accessToken": "newAccessToken123",
    "refreshToken": "refreshToken456",
    "tipo": "Bearer",
    "correo": "carlos@email.com",
    "rol": "CLIENTE"
  }
}
```

#### `POST /api/auth/logout`
- Recibe: no body.
- Devuelve: `ApiResponse<Void>`
- Descripción: cierra la sesión del usuario.
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Sesión cerrada",
  "data": null
}
```

#### `POST /api/auth/registrar-cliente`
- Recibe: body `RegistroRequest` con nombre, correo, teléfono y clave.
- Devuelve: `ApiResponse<Void>`
- Descripción: registra un usuario cliente.
- Permisos: público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Registro exitoso",
  "data": null
}
```

#### `POST /api/auth/registro-organizador`
- Recibe: body JSON `SolicitudVerificacionRequest` con `nombreCompleto`, `correoUsuario`, `password`, `razonSocial`, `nit` y `correoEmpresarial`.
- Devuelve: `ApiResponse<Void>`
- Descripción: crea la cuenta del representante y la organización en pre-registro. El alta no exige el RUT; el representante puede completar este paso después. Al cargarlo mediante `/api/verificacion/{solicitudId}/subir-rut`, la solicitud queda disponible para revisión del Administrador.
- Permisos: público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Usuario y pre-registro de organización creados con éxito. Ya puedes ingresar al Dashboard.",
  "data": null
}
```

---

## 3. Usuarios

### Base: `/api/usuarios`

#### `GET /api/usuarios`
- Recibe: query params opcionales para filtros combinados o individuales:
  - `nombre` (string): búsqueda parcial insensible a mayúsculas sobre el nombre de usuario.
  - `organizacion` (string): búsqueda parcial insensible a mayúsculas sobre la razón social de la organización asociada.
  - `estado` (string): estado de cuenta del usuario (`ACTIVO`, `INACTIVO`, etc.).
  - `activo` (boolean): flag booleano alternativo de estado activo/inactivo.
  - `rolId` (numérico): identificador del rol.
  - `rolNombre` (string): nombre del rol (`ADMINISTRADOR`, `REPRESENTANTE`, `OPERADOR`, `MODERADOR`, `MARKETING`, `CLIENTE`).
  - `page`, `size`, `sort`: parámetros estándar de paginación.
- Descripción: Directorio general de usuarios para el dashboard de administración. Permite combinar libremente filtros o consultarlos individualmente. Si no se especifican filtros, retorna todos los usuarios de la plataforma de manera paginada.
- Devuelve: `ApiResponse<PagedResponse<UsuarioAdminDTO>>`; incluye teléfono, nombre del rol y resumen de organización (`id`, `razonSocial`), sin exponer datos sensibles.
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Usuarios obtenidos",
  "data": {
    "content": [
      {
        "id": 1,
        "nombre": "Ana Pérez",
        "telefono": "+56912345678",
        "rolNombre": "CLIENTE",
        "organizacion": null
      },
      {
        "id": 2,
        "nombre": "Carlos Gómez",
        "telefono": "+56987654321",
        "rolNombre": "OPERADOR",
        "organizacion": {
          "id": 10,
          "razonSocial": "Eventica SpA"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 2,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/usuarios/buscar`
- Recibe: los mismos parámetros que `GET /api/usuarios` (`nombre`, `organizacion`, `estado`, `activo`, `rolId`, `rolNombre`, `page`, `size`, `sort`).
- Devuelve: `ApiResponse<PagedResponse<UsuarioAdminDTO>>`
- Permisos: ADMINISTRADOR.
- Descripción: Endpoint de búsqueda avanzada para el directorio de usuarios que soporta coincidencia parcial, combinación simultánea de filtros por organización y estado, y paginación.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Resultados de búsqueda",
  "data": {
    "content": [
      {
        "id": 2,
        "nombre": "Luis",
        "correo": "luis@eventhive.com",
        "telefono": "+56987654321",
        "rolNombre": "MARKETING",
        "foto": "https://storage.example/foto/user_2.jpg",
        "urlFoto": "https://storage.example/foto/user_2.jpg",
        "fechaCreacion": "2026-09-15T08:30:00",
        "organizacion": null
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/usuarios/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<UsuarioAdminDTO>`
- Permisos: ADMINISTRADOR.
- Descripción: detalle de solo lectura para el panel de administración, incluyendo correo electrónico, teléfono, rol, organización y foto de perfil.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Usuario obtenido",
  "data": {
    "id": 3,
    "nombre": "María",
    "correo": "maria@eventhive.com",
    "telefono": "+56911112222",
    "rolNombre": "REPRESENTANTE",
    "foto": "https://storage.example/foto/user_3.jpg",
    "urlFoto": "https://storage.example/foto/user_3.jpg",
    "fechaCreacion": "2026-09-10T11:00:00",
    "organizacion": {
      "id": 10,
      "razonSocial": "Eventica SpA"
    }
  }
}
```

#### `GET /api/usuarios/trabajadores/marketing`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<UsuarioAdminDTO>>`
- Permisos: ADMINISTRADOR.
- Descripción: lista los integrantes del equipo que poseen el rol MARKETING, permitiendo identificar su correo electrónico, nombre y fotografía para la gestión del panel.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Trabajadores de marketing obtenidos",
  "data": [
    {
      "id": 5,
      "nombre": "Laura Gómez",
      "correo": "laura.marketing@eventhive.com",
      "telefono": "+56977778888",
      "rolNombre": "MARKETING",
      "foto": "https://storage.example/foto/user_5.jpg",
      "urlFoto": "https://storage.example/foto/user_5.jpg",
      "fechaCreacion": "2026-09-01T09:00:00",
      "organizacion": null
    }
  ]
}
```

#### `PATCH /api/usuarios/{id}/revocar-marketing`
- Recibe: `id` del usuario en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Descripción: revoca el rol de MARKETING asignando al usuario el rol CLIENTE y conservando el resto de su información. Si el usuario no tiene el rol MARKETING, rechaza la operación con error 400 descriptivo.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Rol de marketing revocado exitosamente"
}
```

#### `GET /api/usuarios/misOrganizaciones-seguidas`
- Recibe: sin parámetros necesarios (contexto de usuario autenticado).
- Devuelve: `ApiResponse<List<OrganizacionSeguidaDTO>>`
- Permisos: autenticado.
- Descripción: Retorna la lista de organizaciones seguidas por el usuario autenticado sin duplicados (`DISTINCT`), enriquecida con `urlLogo`, `descripcion` y la cantidad de `eventosActivos`. También disponible vía `GET /api/seguidores/mis-seguidos`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Organizaciones seguidas obtenidas",
  "data": [
    {
      "id": 10,
      "razonSocial": "Eventica SpA",
      "urlLogo": "https://storage.supabase.co/eventhive/logos/eventica.png",
      "descripcion": "Productora de conciertos y festivales culturales de gran escala.",
      "eventosActivos": 4
    }
  ]
}
```

#### `DELETE /api/usuarios/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Usuario eliminado exitosamente",
  "data": null
}
```

#### `GET /api/usuarios/perfil`
- Recibe: no body.
- Devuelve: `ApiResponse<UsuarioDTO>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Perfil obtenido",
  "data": {
    "id": 7,
    "nombre": "Carlos",
    "correo": "carlos@email.com",
    "telefono": "+56912345678",
    "imagenPerfil": "https://storage.example/imagenPerfil/user_123.jpg",
    "urlImagenPerfil": "https://storage.example/imagenPerfil/user_123.jpg",
    "rolNombre": "CLIENTE"
  }
}
```

#### `GET /api/usuarios/perfil/actividad`
- Recibe: no body.
- Devuelve: `ApiResponse<UsuarioActividadDTO>` con compras confirmadas, entradas y eventos comprados, favoritos y total gastado.
- Permisos: autenticado (disponible para todos los roles).
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Actividad obtenida",
  "data": {
    "comprasConfirmadas": 4,
    "entradasCompradas": 7,
    "eventosComprados": 3,
    "favoritos": 5,
    "totalGastado": 175000
  }
}
```

#### `PUT /api/usuarios/perfil`
- Recibe: body `ActualizarPerfilRequest`.
- Content-Type: `application/json`.
- Devuelve: `ApiResponse<UsuarioDTO>`
- Permisos: autenticado.
- Este endpoint actualiza los datos de texto del perfil. Para reemplazar la imagen, usar `PUT /api/usuarios/perfil/imagen`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Perfil actualizado",
  "data": {
    "id": 7,
    "nombre": "Carlos Vega",
    "correo": "carlos@email.com",
    "imagenPerfil": "https://storage.example/imagenPerfil/user_123.jpg",
    "urlImagenPerfil": "https://storage.example/imagenPerfil/user_123.jpg"
  }
}
```

#### `PUT /api/usuarios/perfil/imagen`
- Recibe: `multipart/form-data` con la parte `imagen` obligatoria (archivo PNG o JPG; máximo 5 MB).
- Devuelve: `ApiResponse<UsuarioDTO>` con HTTP 200; incluye la URL actualizada en `imagenPerfil` y `urlImagenPerfil`.
- Permisos: autenticado.
- Descripción: reemplaza únicamente la imagen de perfil del usuario autenticado y la almacena en Supabase Storage.
- Ejemplo de respuesta: misma estructura de `UsuarioDTO` que en `GET /api/usuarios/perfil`.

#### `PUT /api/usuarios/perfil/cambiar-clave`
- Recibe: body `EditarClaveRequest` con clave actual y nueva.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Contraseña actualizada correctamente",
  "data": null
}
```

---

## 4. Eventos

### Base: `/api/eventos`

#### `GET /api/eventos`
- Recibe: `categoriaId` y `fecha` opcionales, y paginación (`page`, `size`, `sort`). La fecha debe enviarse en formato `yyyy-MM-dd` y filtra por ese día exacto.
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`
- Descripción: lista eventos públicos; permite combinar los filtros opcionales de categoría y fecha. El filtro de fecha se evalúa como fecha de calendario sin conversiones de zona horaria, evitando devolver eventos del día anterior. Los promocionados aparecen primero y el orden secundario predeterminado es por fecha, hora e ID ascendente.
- Ejemplos: `/api/eventos?fecha=2026-10-14` o `/api/eventos?categoriaId=1&fecha=2026-10-14`
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Eventos obtenidos",
  "data": {
    "content": [
      {
        "id": 15,
        "titulo": "Festival de Jazz",
        "descripcion": "Evento musical con artistas locales",
        "lugar": "Parque Central, Santiago",
        "foto": "https://storage.example/eventos/festival-jazz.jpg",
        "fecha": "2026-10-14",
        "hora": "19:30:00",
        "estado": "PUBLICADO",
        "promocionado": true,
        "latitud": -33.4489,
        "longitud": -70.6693,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/eventos/primer-destacado`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<PrimerEventoDestacadoDTO>`.
- Permisos: público.
- Descripción: devuelve el primer evento destacado (`promocionado: true` y en estado `PUBLICADO`), priorizando el próximo temporalmente (`fecha ASC, hora ASC, id ASC`).
- Estructura devuelta: `id`, `nombre` (alias `titulo`), `urlImagen` (alias `foto`), `fechaCreacion`, `fecha` (ejecución), `hora`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Primer evento destacado obtenido",
  "data": {
    "id": 12,
    "nombre": "Festival Estéreo Picnic 2026",
    "titulo": "Festival Estéreo Picnic 2026",
    "urlImagen": "https://storage.example/eventos/fep-banner-promocionado.jpg",
    "foto": "https://storage.example/eventos/fep-banner-promocionado.jpg",
    "fechaCreacion": "2026-10-01T15:30:00",
    "fecha": "2026-11-20",
    "hora": "14:00:00"
  }
}
```

#### `GET /api/eventos/destacados`
- Recibe: paginación opcional (`page`, `size`, `sort`); `size` es 10 por defecto.
- Devuelve: `ApiResponse<PagedResponse<EventoDestacadoDTO>>`.
- Descripción: lista eventos `PUBLICADO` que cuentan con una promoción pagada y confirmada (`promocionado: true`), independientemente de si el plan contratado es Estándar o Premium. Se ordenan por fecha, hora e ID ascendente.
- Cada elemento contiene los datos de `EventoDTO` y la propiedad `urlImagenDestacado` (si fue asignada por Marketing).

#### `GET /api/eventos/carrusel`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<EventoCarruselDTO>>`
- Permisos: público.
- Descripción: proporciona los banners elegibles para el carrusel principal de la plataforma.
  - Reglas de negocio:
    1. El evento debe estar en estado `PUBLICADO`.
    2. Debe contar con una promoción pagada y confirmada (`CONFIRMADO`).
    3. El plan de promoción contratado debe ser de tipo `premium = true`.
    4. Debe poseer una imagen destacada válida y no vacía asignada por Marketing (`url_imagen_destacado`).
  - Formato de respuesta: devuelve exclusivamente la propiedad `url_imagen_promocionado` (sin título, descripción, fecha ni campos adicionales).
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Eventos para el carrusel obtenidos",
  "data": [
    {
      "url_imagen_promocionado": "https://storage.example/eventos/banner-destacado-1.jpg"
    },
    {
      "url_imagen_promocionado": "https://storage.example/eventos/banner-destacado-2.jpg"
    }
  ]
}
```

#### `GET /api/eventos/proximos`
- Recibe: paginación (`page`, `size`, `sort`).
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`
- Descripción: lista los eventos en estado `PUBLICADO` cuya fecha y hora de inicio sea igual o posterior al momento actual según la zona horaria oficial `America/Bogota`. Se ordenan estrictamente por proximidad temporal ascendente (`fecha ASC, hora ASC, id ASC`). No se priorizan eventos promocionados ni premium; la cercanía de fecha y hora es el único criterio de prelación.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Próximos eventos obtenidos",
  "data": {
    "content": [
      {
        "id": 18,
        "titulo": "Expo Creativa",
        "descripcion": "Encuentro de arte, diseño y creatividad",
        "lugar": "Centro Cultural, Santiago",
        "foto": "https://storage.example/eventos/expo-creativa.jpg",
        "fecha": "2026-10-20",
        "hora": "10:00:00",
        "estado": "PUBLICADO",
        "latitud": -33.4372,
        "longitud": -70.6506,
        "categoria": {
          "id": 3,
          "nombre": "Arte"
        },
        "organizacion": {
          "id": 21,
          "nombre": "Colectivo Creativo"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/eventos/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<EventoDTO>`
- Descripción: detalle de un evento público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento obtenido",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "PUBLICADO",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica",
      "urlLogo": "https://storage.example/perfilOrganizacion/eventica-logo.jpg",
      "urlImagen": "https://storage.example/perfilOrganizacion/eventica-logo.jpg"
    },
    "localidades": [
      {
        "id": 1,
        "nombre": "General",
        "precio": 25000,
        "capacidad": 150,
        "disponibles": 120
      },
      {
        "id": 2,
        "nombre": "VIP",
        "precio": 60000,
        "capacidad": 40,
        "disponibles": 35
      }
    ]
  }
}
```

#### `GET /api/eventos/organizacion/{organizacionId}`
- Alias disponible: `GET /api/organizaciones/{organizacionId}/eventos`
- Recibe: `organizacionId` en path, opcional `categoriaId`, paginación (`page`, `size`, `sort`).
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`.
- Permisos: público (sin autenticación).
- Descripción: lista los eventos en estado `PUBLICADO` de una organización específica para que los usuarios puedan verlos públicamente en el perfil de la organización. Incluye información de categoría y organización con su respectivo logo.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Eventos de la organización obtenidos",
  "data": {
    "content": [
      {
        "id": 15,
        "titulo": "Festival de Jazz",
        "descripcion": "Evento musical con artistas locales",
        "lugar": "Parque Central, Santiago",
        "foto": "https://storage.example/eventos/festival-jazz.jpg",
        "fecha": "2026-10-14",
        "hora": "19:30:00",
        "estado": "PUBLICADO",
        "promocionado": true,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica",
          "urlLogo": "https://storage.example/perfilOrganizacion/eventica-logo.jpg",
          "urlImagen": "https://storage.example/perfilOrganizacion/eventica-logo.jpg"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/eventos/organizador/{id}`
- Recibe: `id` del evento en path.
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento obtenido",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "BORRADOR",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    },
    "localidades": [
      {
        "id": 1,
        "nombre": "General",
        "precio": 25000,
        "capacidad": 150,
        "disponibles": 120
      }
    ]
  }
}
```

#### `GET /api/eventos/organizador`
- Recibe: query params opcionales `categoriaId` (Long), `estado` (enum `EstadoEvento`: BORRADOR, PUBLICADO, FINALIZADO, etc.), `titulo` (coincidencia parcial en el título) y paginación estándar (`page`, `size`, `sort`).
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`
- Permisos: REPRESENTANTE o OPERADOR de la organización.
- Descripción: lista los eventos pertenecientes a la organización del usuario autenticado, permitiendo combinar filtros por categoría, estado y búsqueda por título de forma eficiente.
- Ejemplo de petición: `/api/eventos/organizador?categoriaId=1&estado=PUBLICADO&titulo=Jazz&page=0&size=10`
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Eventos obtenidos",
  "data": {
    "content": [
      {
        "id": 15,
        "titulo": "Festival de Jazz",
        "descripcion": "Evento musical con artistas locales",
        "lugar": "Parque Central, Santiago",
        "foto": "https://storage.example/eventos/festival-jazz.jpg",
        "fecha": "2026-10-14",
        "hora": "19:30:00",
        "estado": "PUBLICADO",
        "latitud": -33.4489,
        "longitud": -70.6693,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/eventos/admin/{id}`
- Recibe: `id` del evento.
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: MODERADOR o ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento obtenido",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "PENDIENTE_REVISION",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    },
    "localidades": [
      {
        "id": 1,
        "nombre": "General",
        "precio": 25000,
        "capacidad": 150,
        "disponibles": 120
      }
    ]
  }
}
```

#### `GET /api/eventos/mapa`
- Recibe: `categoriaId`, `lat`, `lng`, `radioKm` opcionales.
- Devuelve: `ApiResponse<List<EventoMapaDTO>>`
- Descripción: eventos para renderizar en mapa; los promocionados aparecen primero y luego se ordenan por fecha, hora e ID ascendente.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Eventos para el mapa",
  "data": [
    {
      "id": 15,
      "titulo": "Festival de Jazz",
      "descripcion": "Evento musical con artistas locales",
      "categoriaNombre": "Música",
      "latitud": -33.4489,
      "longitud": -70.6693
    }
  ]
}
```

#### `GET /api/eventos/buscar`
- Recibe: `nombre` o `titulo` para buscar por coincidencia parcial y paginación (`page`, `size`, `sort`). Debe enviarse `nombre` o `titulo`.
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`, con los mismos campos de tarjeta que el listado público.
- Descripción: búsqueda pública de eventos `PUBLICADO` por coincidencia parcial en el título. Los promocionados aparecen primero; el orden predeterminado secundario es por fecha, hora e ID ascendente. Para filtrar por categoría o fecha se utiliza `GET /api/eventos`.
- Ejemplo: `/api/eventos/buscar?titulo=jazz`
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Resultados de búsqueda",
  "data": {
    "content": [
      {
        "id": 15,
        "titulo": "Festival de Jazz",
        "descripcion": "Evento musical con artistas locales",
        "lugar": "Parque Central, Santiago",
        "foto": "https://storage.example/eventos/festival-jazz.jpg",
        "fecha": "2026-10-14",
        "hora": "19:30:00",
        "estado": "PUBLICADO",
        "promocionado": true,
        "latitud": -33.4489,
        "longitud": -70.6693,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/eventos/organizador/buscar`
- Recibe: `titulo` y paginación.
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Resultados de búsqueda",
  "data": {
    "content": [
      {
        "id": 15,
        "titulo": "Festival de Jazz",
        "descripcion": "Evento musical con artistas locales",
        "lugar": "Parque Central, Santiago",
        "foto": "https://storage.example/eventos/festival-jazz.jpg",
        "fecha": "2026-10-14",
        "hora": "19:30:00",
        "estado": "PUBLICADO",
        "latitud": -33.4489,
        "longitud": -70.6693,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/eventos/admin/buscar`
- Recibe: `titulo`, `categoriaId`, `estado`, paginación.
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`
- Permisos: MODERADOR o ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Resultados de búsqueda",
  "data": {
    "content": [
      {
        "id": 15,
        "titulo": "Festival de Jazz",
        "descripcion": "Evento musical con artistas locales",
        "lugar": "Parque Central, Santiago",
        "foto": "https://storage.example/eventos/festival-jazz.jpg",
        "fecha": "2026-10-14",
        "hora": "19:30:00",
        "estado": "PENDIENTE_REVISION",
        "latitud": -33.4489,
        "longitud": -70.6693,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `POST /api/eventos`
- Recibe: multipart/form-data con:
  - `datos`: `EventoRequest` (incluyendo `fecha`, `hora`, y opcionalmente `fechaFin` y `horaFin`).
  - `foto`: archivo opcional
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: REPRESENTANTE o OPERADOR.
- Validaciones de fechas (zona horaria oficial `America/Bogota`):
  - La fecha de inicio (`fecha`) no puede ser anterior al día actual.
  - Si el evento comienza en la fecha actual (hoy), la hora de inicio (`hora`) debe ser estrictamente posterior a la hora actual.
  - Si se proporciona `fechaFin`, debe ser posterior a la fecha y hora de inicio (`fecha` + `hora`). Si coincide en día, `horaFin` debe ser posterior a `hora`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento creado",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "fechaFin": "2026-10-14",
    "horaFin": "23:00:00",
    "estado": "BORRADOR",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    },
    "localidades": []
  }
}
```

#### `PUT /api/eventos/{id}`
- Recibe: multipart/form-data con:
  - `datos`: `EventoRequest`
  - `foto`: archivo opcional
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: REPRESENTANTE o OPERADOR.
- Validaciones de edición y preservación histórica:
  - Si el evento aún no ha iniciado, aplican las mismas validaciones de fecha de inicio futura y hora válida.
  - Si el evento ya inició o es un evento pasado, se permite modificar sus otros campos (título, descripción, lugar, imagen, etc.), pero el backend congela y protege su inicio histórico (`fecha` y `hora`), rechazando con `BusinessException` cualquier intento de alterar retroactivamente su inicio.
  - Si se envía `fechaFin`, debe ser posterior al inicio.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento actualizado",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz Actualizado",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "BORRADOR",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    },
    "localidades": [
      {
        "id": 1,
        "nombre": "General",
        "precio": 25000,
        "capacidad": 150,
        "disponibles": 120
      }
    ]
  }
}
```

#### `PATCH /api/eventos/{id}/cancelar`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "evento cancelado",
  "data": null
}
```

#### `PATCH /api/eventos/{id}/retirar`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento retirado a borrador",
  "data": null
}
```

#### `PATCH /api/eventos/{id}/enviar-revision`
- Recibe: `id` del evento en path, sin body.
- Devuelve: `ApiResponse<Void>`
- Descripción: envía el evento a revisión.
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento enviado a revisión",
  "data": null
}
```

#### `PATCH /api/eventos/{id}/reabrir`
- Recibe: `id` del evento en path, sin body.
- Devuelve: `ApiResponse<Void>`
- Descripción: reabre el evento y lo devuelve a borrador.
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento reabierto a borrador",
  "data": null
}
```

#### `DELETE /api/eventos/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento eliminado",
  "data": null
}
```

---

## 5. Localidades

### Base: `/api/eventos/{eventoId}/localidades`

#### `GET /api/eventos/{eventoId}/localidades`
- Recibe: `eventoId` en path.
- Devuelve: `ApiResponse<List<LocalidadDTO>>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Localidades obtenidas",
  "data": [
    {
      "id": 1,
      "nombre": "General",
      "precio": 25000,
      "capacidad": 150,
      "disponibles": 120
    }
  ]
}
```

#### `POST /api/eventos/{eventoId}/localidades`
- Recibe: `eventoId` en path y body `LocalidadRequest`.
- Devuelve: `ApiResponse<LocalidadDTO>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Localidad agregada",
  "data": {
    "id": 2,
    "nombre": "VIP",
    "precio": 60000,
    "capacidad": 40,
    "disponibles": 40
  }
}
```

#### `PUT /api/eventos/{eventoId}/localidades/{localidadId}`
- Recibe: `eventoId` y `localidadId` en path, body `LocalidadRequest`.
- Devuelve: `ApiResponse<LocalidadDTO>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Localidad actualizada",
  "data": {
    "id": 2,
    "nombre": "VIP Premium",
    "precio": 65000,
    "capacidad": 35,
    "disponibles": 35
  }
}
```

#### `DELETE /api/eventos/{eventoId}/localidades/{localidadId}`
- Recibe: `eventoId` y `localidadId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE o OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Localidad eliminada",
  "data": null
}
```

---

## 6. Compras

### Base: `/api/compras`

#### Reglas de precios y comisiones de boletas
- El precio configurado en cada localidad representa el **precio base** de la organización.
- La comisión comercial de EventHive se **adiciona** al precio base y la asume íntegramente el comprador.
- **Fórmulas oficiales:**
  - `precioBase = sum(localidad.precio * cantidad)`
  - `comisionEventhive = precioBase * comisionPorcentaje / 100`
  - `totalComprador = precioBase + comisionEventhive`
  - `netoOrganizador = precioBase`
- La comisión **no se deduce** de los ingresos de la organización.
- Todo cálculo se efectúa estrictamente en el backend.

#### `GET /api/compras`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<CompraResponseDTO>>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Compras obtenidas",
  "data": {
    "content": [
      {
        "id": 101,
        "fechaCompra": "2026-09-20T14:30:00",
        "total": 55000,
        "comisionEventhive": 5000,
        "netoOrganizador": 50000,
        "metodoPago": "TARJETA",
        "items": [
          {
            "eventoId": 20,
            "localidadId": 1,
            "localidadNombre": "General",
            "eventoNombre": "Festival de Jazz",
            "cantidad": 2,
            "precioUnitario": 25000,
            "subtotal": 50000
          }
        ]
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

#### `GET /api/compras/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<CompraResponseDTO>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Compra obtenida",
  "data": {
    "id": 101,
    "fechaCompra": "2026-09-20T14:30:00",
    "total": 55000,
    "comisionEventhive": 5000,
    "netoOrganizador": 50000,
    "metodoPago": "TARJETA",
    "items": [
      {
        "localidadId": 1,
        "localidadNombre": "General",
        "eventoNombre": "Festival de Jazz",
        "cantidad": 2,
        "precioUnitario": 25000,
        "subtotal": 50000
      }
    ]
  }
}
```

#### `POST /api/compras`
- Recibe: body `CompraRequestDTO`.
- Devuelve: `ApiResponse<CompraResponseDTO>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Compra realizada",
  "data": {
    "id": 102,
    "fechaCompra": "2026-09-21T10:15:00",
    "total": 27500,
    "comisionEventhive": 2500,
    "netoOrganizador": 25000,
    "metodoPago": "TARJETA",
    "items": [
      {
        "eventoId": 20,
        "localidadId": 2,
        "localidadNombre": "General",
        "eventoNombre": "Expo Creativa",
        "cantidad": 1,
        "precioUnitario": 25000,
        "subtotal": 25000
      }
    ]
  }
}
```

#### `POST /api/compras/eventos/{eventoId}/posicionamiento/pagos`
- Recibe: `eventoId` en path y `planId` como query param (`?planId={id}`) o en body JSON (`{ "planId": {id} }`).
- Devuelve: `ApiResponse<PagoPosicionamientoDTO>`.
- Permisos: REPRESENTANTE de la organización propietaria.
- Descripción: solo permite contratar promociones para eventos en estado `PUBLICADO`. Registra un pago `PENDIENTE` con el precio fijo del plan configurado en el backend (el frontend no puede alterar importes).

#### `GET /api/compras/posicionamiento/pagos/{pagoId}`
- Recibe: `pagoId` en path.
- Devuelve: `ApiResponse<PagoPosicionamientoDTO>` con `id`, `eventoId`, `organizacionId`, `precio` y `estado`.
- Permisos: REPRESENTANTE de la organización propietaria.

#### `PATCH /api/compras/posicionamiento/pagos/{pagoId}/confirmar-simulado`
- Recibe: `pagoId` en path.
- Devuelve: `ApiResponse<PagoPosicionamientoDTO>`.
- Permisos: REPRESENTANTE de la organización propietaria.
- Descripción: procesa la confirmación del pago de manera **idempotente** (si ya estaba confirmado, retorna exitosamente sin duplicar correos ni mutaciones).
  - Al confirmarse, el evento se marca como promocionado (`promocionado = true`), lo cual lo clasifica como **Destacado** (tanto para planes estándar como premium).
  - No asigna automáticamente la fotografía a `urlImagenDestacado`. Si el plan es Premium (`premium = true`), Marketing debe asignar posteriormente la imagen destacada para que el evento aparezca en el carrusel principal (`GET /api/eventos/carrusel`).
  - Envía correo de confirmación de forma segura (sin revertir el pago confirmado en caso de incidencia en el servicio de correo).

#### `DELETE /api/compras/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Compra cancelada",
  "data": null
}
```

---

## 7. Boletos

### Base: `/api/boletos`

#### `GET /api/boletos/{compraId}`
- Recibe: `compraId` en path.
- Devuelve: `ApiResponse<BoletosCompraDTO>`
- Permisos: CLIENTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "boletos de Compra obtenida",
  "data": {
    "id": 101,
    "fechaCompra": "2026-09-20T14:30:00",
    "total": 50000,
    "metodoPago": "TARJETA",
    "tiqueteCompras": [
      {
        "id": 501,
        "tiquete": {
          "id": 501,
          "codigoQR": "BOL-001-ABC",
          "localidad": {
            "id": 1,
            "nombre": "General",
            "precio": 25000,
            "evento": {
              "id": 15,
              "titulo": "Festival de Jazz",
              "fecha": "2026-10-14",
              "hora": "19:30:00",
              "lugar": "Parque Central, Santiago"
            }
          }
        }
      }
    ]
  }
}
```

#### `GET /api/boletos/validar/{codigoQR}`
- Recibe: `codigoQR` en path.
- Devuelve: `ApiResponse<BoletoDTO>`
- Permisos: REPRESENTANTE u OPERADOR (debe pertenecer a la organización organizadora del evento y tener permiso `CHECK_IN`).
- Descripción: Escanea y valida si un boleto es auténtico y pertenece a la organización, devolviendo el detalle del boleto, localidad y evento sin marcarlo como consumido.
- Ejemplo de respuesta exitosa:

```json
{
  "success": true,
  "mensaje": "Boleto válido",
  "data": {
    "id": 501,
    "tiquete": {
      "id": 501,
      "codigoQR": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "localidad": {
        "id": 1,
        "nombre": "General",
        "precio": 25000,
        "evento": {
          "id": 15,
          "titulo": "Festival de Jazz",
          "fecha": "2026-10-14",
          "hora": "19:30:00",
          "lugar": "Parque Central, Santiago"
        }
      }
    }
  }
}
```

- Errores de validación:
  - **404 Not Found** (Código QR desconocido o no registrado):
    ```json
    {
      "success": false,
      "mensaje": "Lo siento, este código no es uno de nuestros boletos"
    }
    ```
  - **403 Forbidden** (Operador de otra organización o sin permiso `CHECK_IN`):
    ```json
    {
      "success": false,
      "mensaje": "No está autorizado para operar este tiquete"
    }
    ```
  - **400 Bad Request** (Compra no confirmada):
    ```json
    {
      "success": false,
      "mensaje": "No se puede hacer check-in: la compra se encuentra en estado PENDIENTE"
    }
    ```

#### `POST /api/boletos/checkin/{codigoQR}`
- Recibe: `codigoQR` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE u OPERADOR (debe pertenecer a la organización organizadora del evento y tener permiso `CHECK_IN`).
- Descripción: Escanea el código QR, valida su existencia y autenticidad en la organización y marca el tiquete como utilizado de forma atómica.
- Ejemplo de respuesta exitosa:

```json
{
  "success": true,
  "mensaje": "¡¡Tiquete valido!! check-in realizado"
}
```

- Errores de validación:
  - **404 Not Found** (Código QR desconocido o no registrado):
    ```json
    {
      "success": false,
      "mensaje": "Lo siento, este código no es uno de nuestros boletos"
    }
    ```
  - **400 Bad Request** (Boleto ya utilizado anteriormente):
    ```json
    {
      "success": false,
      "mensaje": "El tiquete ya fue utilizado"
    }
    ```
  - **403 Forbidden** (Operador de otra organización o sin permiso `CHECK_IN`):
    ```json
    {
      "success": false,
      "mensaje": "No está autorizado para operar este tiquete"
    }
    ```
  - **400 Bad Request** (Compra no confirmada):
    ```json
    {
      "success": false,
      "mensaje": "No se puede hacer check-in: la compra se encuentra en estado PENDIENTE"
    }
    ```

---

## 8. Lista de deseos

### Base: `/api/deseos`

#### `GET /api/deseos`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Eventos deseados obtenidos",
  "data": {
    "content": [
      {
        "id": 20,
        "titulo": "Concierto Nocturno",
        "descripcion": "Concierto al aire libre",
        "capacidad": 35,
        "disponibles": 35
        "foto": "https://storage.example/eventos/concierto-nocturno.jpg",
        "fecha": "2026-11-12",
        "hora": "20:00:00",
        "estado": "PUBLICADO",
        "latitud": -33.4489,
        "longitud": -70.6693,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `POST /api/deseos/{eventoId}`
- Recibe: `eventoId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento agregado a tu lista de deseados",
  "data": null
}
```

#### `DELETE /api/deseos/{eventoId}`
- Recibe: `eventoId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento removido de tu lista de deseados",
  "data": null
}
```

---

## 9. Categorías

### Base: `/api/categorias`

#### `GET /api/categorias`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<CategoriaDTO>>`
- `totalEventos`: cuenta exclusivamente los eventos en estado `PUBLICADO` asociados a la categoría (excluye eventos en borrador, cancelados o suspendidos).
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categorías obtenidas",
  "data": {
    "content": [
      {
        "id": 1,
        "nombre": "Música",
        "imagenUrl": "https://.../musica.jpg",
        "totalEventos": 12
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

#### `GET /api/categorias/nombres`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<CategoriaNombreDTO>>`
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categorías obtenidas",
  "data": [
    { "id": 1, "nombre": "Música" },
    { "id": 2, "nombre": "Tecnología" }
  ]
}
```

#### `GET /api/categorias/destacadas`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<CategoriaDTO>>`
- Descripción: lista las 4 categorías con mayor cantidad de eventos `PUBLICADO`.
- `totalEventos`: refleja exclusivamente la cantidad de eventos publicados.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categorías destacadas",
  "data": [
    { "id": 1, "nombre": "Música", "imagenUrl": "https://.../musica.jpg", "totalEventos": 12 },
    { "id": 3, "nombre": "Arte", "imagenUrl": "https://.../arte.jpg", "totalEventos": 6 }
  ]
}
```

#### `GET /api/categorias/con-eventos`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<CategoriaConteoDTO>>`
- Descripción: lista las categorías que poseen al menos un evento en estado `PUBLICADO`.
- `totalEventos`: conteo exclusivo de eventos publicados.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categorías con eventos",
  "data": [
    {
      "id": 1,
      "nombre": "Música",
      "totalEventos": 12
    }
  ]
}
```

#### `GET /api/categorias/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<CategoriaConteoDTO>`
- `totalEventos`: conteo exclusivo de eventos en estado `PUBLICADO`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categoría obtenida",
  "data": {
    "id": 1,
    "nombre": "Música",
    "totalEventos": 12
  }
}
```

#### `POST /api/categorias`
- Recibe: multipart/form-data con `datos` y `foto` opcional.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categoría creada exitosamente",
  "data": null
}
```

#### `PUT /api/categorias/{id}`
- Recibe: multipart/form-data con `datos` y `foto` opcional.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categoría actualizada exitosamente",
  "data": null
}
```

#### `DELETE /api/categorias/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Categoría eliminada exitosamente",
  "data": null
}
```

---

## 10. Organizaciones

### Base: `/api/organizaciones`

#### `GET /api/organizaciones`
- Recibe: parámetro opcional `estado` (enum `EstadoOrganizacion`: `PENDIENTE_REVISION`, `APROBADA`, `RECHAZADA`, `SUSPENDIDA`, insensible a mayúsculas/minúsculas) y parámetros de paginación (`page`, `size`, `sort`).
- Si no se especifica el parámetro `estado`, el endpoint devuelve todas las organizaciones registradas sin discriminación de estado.
- Las organizaciones que ya cuenten con `urlRut` registrado en su entidad son reconocidas y conservadas automáticamente en estado `APROBADA`.
- Devuelve: `ApiResponse<PagedResponse<OrganizacionPublicaDTO>>`
- Permisos: público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Organizaciones obtenidas",
  "data": {
    "content": [
      {
        "id": 10,
        "razonSocial": "Eventica SpA",
        "representante": "Carlos Pérez",
        "fechaCreacion": "2026-09-01T09:00:00",
        "promedioRating": 4.8,
        "totalValoraciones": 25,
        "totalSeguidores": 340,
        "totalEventosCreados": 18,
        "eventosActivos": 4,
        "nivel": "NIVEL_2",
        "estado": "APROBADA"
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

#### `POST /api/organizaciones/buscar`
- Recibe: body JSON `BuscarOrganizacionRequest` con `razonSocial`; parámetro opcional `estado` y parámetros de paginación (`page`, `size`, `sort`) en la query.
- Devuelve: `ApiResponse<PagedResponse<OrganizacionPublicaDTO>>`
- Descripción: busca organizaciones por razón social.
- Permisos: público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Organizaciones encontradas",
  "data": {
    "content": [
      {
        "id": 10,
        "razonSocial": "Eventica SpA",
        "representante": "Carlos Pérez",
        "fechaCreacion": "2026-09-01T09:00:00",
        "promedioRating": 4.8,
        "totalValoraciones": 25,
        "totalSeguidores": 340,
        "totalEventosCreados": 18,
        "eventosActivos": 4,
        "nivel": "NIVEL_2",
        "estado": "APROBADA"
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/organizaciones/{organizacionId}`
- Recibe: `organizacionId` en path.
- Devuelve: `ApiResponse<OrganizacionDTO>`
- Permisos: ADMINISTRADOR.
- Descripción: consulta privada y protegida de la organización para validación y auditoría administrativa. El RUT se expone mediante `urlRutTemporal` con token de acceso seguro y expiración temporal (1 hora).
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Organización obtenida",
  "data": {
    "id": 10,
    "representante": "Carlos Pérez",
    "representanteCorreo": "carlos.perez@eventica.cl",
    "razonSocial": "Eventica SpA",
    "nit": "76.123.456-7",
    "correoContacto": "contacto@eventica.cl",
    "urlLogo": "https://storage.example/perfilOrganizacion/org_123.jpg",
    "fechaCreacion": "2026-09-01T09:00:00",
    "promedioRating": 4.8,
    "totalValoraciones": 25,
    "totalSeguidores": 340,
    "totalEventosCreados": 18,
    "eventosActivos": 4,
    "eventosFinalizados": 12,
    "eventosRechazados": 1,
    "nivel": "NIVEL_2",
    "estado": "APROBADA",
    "estadoValidacionRut": "PENDIENTE",
    "urlRutTemporal": "https://supabase.co/storage/v1/object/sign/documentos-rut/rut_10.pdf?token=..."
  }
}
```

#### `GET /api/organizaciones/{organizacionId}/rut-url`
- Recibe: `organizacionId` en path.
- Devuelve: `ApiResponse<RutUrlDTO>` con `url` temporal y `expiresInSeconds`.
- Descripción: obtiene un enlace temporal para consultar el documento RUT oficial de la organización aprobada. En flujos de verificación previa y auditoría de solicitudes pendientes, el documento a revisar se consulta desde la solicitud (`GET /api/verificacion/{solicitudId}/rut-url`).
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "URL temporal del RUT obtenida",
  "data": {
    "url": "https://storage.example/rut-temporal",
    "expiresInSeconds": 300
  }
}
```

#### `GET /api/organizaciones/top`
- Recibe: parámetro opcional `estado` y paginación (`page`, `size`, `sort`).
- Devuelve: `ApiResponse<PagedResponse<OrganizacionPublicaDTO>>`
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Top de organizaciones",
  "data": {
    "content": [
      {
        "id": 10,
        "razonSocial": "Eventica SpA",
        "representante": "Carlos Pérez",
        "fechaCreacion": "2026-09-01T09:00:00",
        "promedioRating": 4.8,
        "totalValoraciones": 25,
        "totalSeguidores": 340,
        "totalEventosCreados": 18,
        "nivel": "NIVEL_2",
        "estado": "APROBADA"
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/organizaciones/mi-organizacion`
- Recibe: sin body.
- Devuelve: `ApiResponse<OrganizacionDTO>`
- Permisos: REPRESENTANTE u OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Organización obtenida",
  "data": {
    "id": 10,
    "representante": "Carlos Pérez",
    "razonSocial": "Eventica SpA",
    "nit": "76.123.456-7",
    "correoContacto": "contacto@eventica.cl",
    "urlLogo": "https://storage.example/perfilOrganizacion/org_123.jpg",
    "fechaCreacion": "2026-09-01T09:00:00",
    "promedioRating": 4.8,
    "totalValoraciones": 25,
    "totalSeguidores": 340,
    "totalEventosCreados": 18,
    "eventosFinalizados": 12,
    "eventosRechazados": 1,
    "nivel": "NIVEL_2",
    "estado": "APROBADA"
  }
}
```

#### `PUT /api/organizaciones/mi-organizacion`
- Recibe: `multipart/form-data` con la parte `datos` obligatoria (JSON `ActualizarOrganizacionRequest`: `razonSocial`, `descripcion`, `correoContacto`) y la parte `imagen` opcional (archivo PNG o JPG; máximo 5 MB).
- Devuelve: `ApiResponse<OrganizacionDTO>` con HTTP 200, incluyendo `urlLogo` si existe.
- Permisos: REPRESENTANTE.
- Descripción: actualiza los datos de la organización del representante autenticado y, si se envía `imagen`, reemplaza su logo en Supabase Storage. Si no se envía imagen, conserva el logo actual.

#### `GET /api/organizaciones/invitaciones-enviadas`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<InvitacionRolEnviadaDTO>>`
- Permisos: REPRESENTANTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Invitaciones de la organización obtenidas",
  "data": {
    "content": [
      {
        "id": 4,
        "correo": "operador@eventos.com",
        "rol": "OPERADOR",
        "fechaInvitacion": "2026-10-21T18:30:00",
        "fechaExpiracion": "2026-10-22T18:30:00",
        "fechaAceptacion": null,
        "estado": "PENDIENTE",
        "organizacionNombre": "Eventica SpA"
      }
    ]
  }
}
```

#### `GET /api/organizaciones/mis-operadores`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<OperadorDTO>>`
- Permisos: REPRESENTANTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Operadores obtenidos",
  "data": {
    "content": [
      {
        "id": 12,
        "nombreCompleto": "Luis González",
        "correo": "luis@correo.com",
        "permisosEvento": ["CREAR_EVENTO", "EDITAR_EVENTO"]
      }
    ]
  }
}
```

Los operadores se agregan mediante invitación por correo, aceptan o rechazan la invitación y pueden ser expulsados por el representante. No existe un estado organizacional de operador; `usuarios.activo` se reserva para el control de acceso al sistema.

#### `GET /api/organizaciones/mi-organizacion/estadisticas`
- Recibe: paginación estándar (`page`, `size`, `sort`).
- Devuelve: `ApiResponse<PanelEntradasDTO>`
- Permisos: REPRESENTANTE u OPERADOR asociado a la organización.
- Reglas de negocio:
  - `totalBoletas` / `totalBoletasVendidasPorEventosPublicados`: total de boletas vendidas correspondientes **exclusivamente a eventos publicados** (`PUBLICADO`) en compras y pagos confirmados (excluyendo compras pendientes, canceladas o fallidas).
  - `ingresosNetos`: suma de los ingresos netos de la organización (el precio base de las localidades vendidas, sin descontar comisiones adicionales asumidas por el comprador).
  - `totalEventosActivos`: número de eventos en estado `PUBLICADO` de la organización.
  - `eventos`: paginación de `EventoEntradasResumenDTO` con resumen por evento (`id`, `titulo`, `fecha`, `hora`, `estado`, `boletasVendidas`, `ingresosNetos`), omitiendo desglose por localidades por optimización del contrato.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Estadísticas de la organización obtenidas",
  "data": {
    "totalEventos": 4,
    "totalEventosActivos": 4,
    "totalBoletas": 240,
    "totalBoletasVendidasPorEventosPublicados": 240,
    "ingresosNetos": 12000000,
    "eventos": {
      "content": [
        {
          "id": 15,
          "titulo": "Festival de Jazz",
          "fecha": "2026-10-14",
          "hora": "19:30:00",
          "estado": "PUBLICADO",
          "boletasVendidas": 240,
          "ingresosNetos": 12000000
        }
      ],
      "pageNumber": 0,
      "pageSize": 10,
      "totalElements": 1,
      "totalPages": 1,
      "hasNext": false,
      "hasPrevious": false
    }
  }
}
```

#### `GET /api/organizaciones/mi-organizacion/valoraciones`
- Recibe: paginación estándar (`page`, `size`, `sort`).
- Devuelve: `ApiResponse<PagedResponse<ValoracionDTO>>`.
- Permisos: REPRESENTANTE u OPERADOR asociado a la organización. La organización se determina desde el usuario autenticado.

#### `GET /api/organizaciones/mi-organizacion/seguidores`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<UsuarioDTO>>`
- Permisos: REPRESENTANTE u OPERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Seguidores de la organizacion obtenidos",
  "data": {
    "content": [
      {
        "id": 7,
        "nombre": "Carlos",
        "correo": "carlos@email.com",
        "telefono": "+56912345678",
        "rolNombre": "CLIENTE"
      }
    ]
  }
}
```

#### `PATCH /api/organizaciones/operadores/{operadorId}/actualizar-permisos`
- Recibe: `operadorId` y body `PermisosOperadorRequest`.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Permisos actualizados",
  "data": null
}
```

#### `DELETE /api/organizaciones/expulsar-operador/{operadorId}`
- Recibe: `operadorId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Operador removido de la organización",
  "data": null
}
```

#### `POST /api/organizaciones/invitar`
- Recibe: query param `correo`; envía una invitación nueva para el rol OPERADOR.
- Devuelve: `ApiResponse<Void>`
- Permisos: REPRESENTANTE.
- El destinatario acepta desde el enlace de correo, que vence en 24 horas; puede completar una cuenta nueva o actualizar una cuenta CLIENTE existente.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Invitación enviada",
  "data": null
}
```

#### `GET /api/organizaciones/sugerencias-pendientes`
- Recibe: paginación.
- Devuelve: `ApiResponse<Page<SugerenciaAscensoDTO>>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Sugerencias de ascenso pendientes",
  "data": {
    "content": [
      {
        "id": 5,
        "organizacionId": 10,
        "organizacionNombre": "Eventica SpA",
        "nivelActual": "BRONCE",
        "nivelSugerido": "PLATA",
        "estado": "PENDIENTE",
        "fechaGeneracion": "2026-09-26T10:30:00",
        "fechaResolucion": null
      }
    ]
  }
}
```

#### `PATCH /api/organizaciones/{sugerenciaId}/aprobar-sugerencia`
- Recibe: `sugerenciaId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Ascenso aprobado",
  "data": null
}
```

#### `PATCH /api/organizaciones/{sugerenciaId}/rechazar-sugerencia`
- Recibe: `sugerenciaId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Ascenso rechazado",
  "data": null
}
```

---

## 11. Seguidoras / seguidores

### Base: `/api/seguidores`

#### `POST /api/seguidores/{organizacionId}/seguir`
- Recibe: `organizacionId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Ahora sigues a este organizador",
  "data": null
}
```

#### `DELETE /api/seguidores/{organizacionId}/seguir`
- Recibe: `organizacionId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Dejaste de seguir al organizador",
  "data": null
}
```

#### `GET /api/seguidores/mis-seguidos`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<OrganizacionSeguidaDTO>>`
- Permisos: autenticado.
- Descripción: Retorna la lista de organizaciones seguidas por el usuario en sesión sin duplicados (`DISTINCT`), enriquecida con `urlLogo`, `descripcion` y la cantidad de `eventosActivos`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Organizaciones seguidas obtenidas",
  "data": [
    {
      "id": 10,
      "razonSocial": "Eventica SpA",
      "urlLogo": "https://storage.supabase.co/eventhive/logos/eventica.png",
      "descripcion": "Productora de conciertos y festivales culturales de gran escala.",
      "eventosActivos": 4
    }
  ]
}
```

---

## 12. Valoraciones

### Base: `/api/valoraciones`

#### `GET /api/valoraciones/usuario`
- Recibe: paginación.
- Devuelve: `ApiResponse<Page<ValoracionDTO>>`
- Permisos: CLIENTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Valoraciones obtenidas",
  "data": {
    "content": [
      {
        "id": 1,
        "comentario": "Excelente servicio",
        "calificacion": 5,
        "organizacionId": 10,
        "organizacionNombre": "Eventica SpA",
        "clienteId": 7,
        "clienteNombre": "Carlos"
      }
    ]
  }
}
```

#### `GET /api/valoraciones/organizacion/{organizacionId}`
- Recibe: `organizacionId` en path, paginación.
- Devuelve: `ApiResponse<Page<ValoracionDTO>>`
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Valoraciones de la organización",
  "data": {
    "content": [
      {
        "id": 1,
        "comentario": "Muy buena atención",
        "calificacion": 4,
        "organizacionId": 10,
        "organizacionNombre": "Eventica SpA",
        "clienteId": 8,
        "clienteNombre": "Ana"
      }
    ]
  }
}
```

Para el panel autenticado se recomienda `GET /api/organizaciones/mi-organizacion/valoraciones`, que aplica el mismo paginado sin recibir un ID de organización desde el frontend.

#### `POST /api/valoraciones`
- Recibe: body `ValoracionRequest` con `organizacionId`, `comentario`, `calificacion`.
- Devuelve: `ApiResponse<Void>`
- Permisos: CLIENTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Valoración creada exitosamente",
  "data": null
}
```

#### `PUT /api/valoraciones/{id}`
- Recibe: `id` en path y query params `comentario` y `calificacion`.
- Devuelve: `ApiResponse<Void>`
- Permisos: CLIENTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Valoración actualizada exitosamente",
  "data": null
}
```

#### `DELETE /api/valoraciones/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: CLIENTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Valoración eliminada exitosamente",
  "data": null
}
```

---

## 13. Notificaciones

### Base: `/api/notificaciones`

#### `GET /api/notificaciones`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<NotificationDTO>>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Notificaciones obtenidas",
  "data": [
    {
      "id": "n1",
      "titulo": "Nuevo evento",
      "mensaje": "Se ha publicado un nuevo evento",
      "tipoNotificacion": "NUEVO_EVENTO",
      "organizacionId": 10,
      "eventoId": 15,
      "nombreEvento": "Festival de Jazz",
      "leida": false,
      "fechaCreacion": "2026-09-26T10:30:00"
    }
  ]
}
```

#### `GET /api/notificaciones/no-leidas`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<Long>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Total no leídas",
  "data": 3
}
```

#### `PUT /api/notificaciones/{id}/leer`
- Recibe: `id` de notificación en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Notificación marcada como leída",
  "data": null
}
```

#### `DELETE /api/notificaciones/limpiar`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<Void>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Notificaciones leídas eliminadas",
  "data": null
}
```

---

## 14. Verificación de organizaciones

### Base: `/api/verificacion`

#### `GET /api/verificacion/mis-solicitudes`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<SolicitudVerificacionDTO>`
- Permisos: REPRESENTANTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Solicitud obtenida",
  "data": {
    "id": 5,
    "organizacionId": 10,
    "representanteId": 7,
    "representanteNombre": "Carlos Pérez",
    "representanteCorreo": "carlos@email.com",
    "razonSocial": "Eventica SpA",
    "nit": "76.123.456-7",
    "representanteLegal": 7,
    "correoEmpresarial": "contacto@eventica.cl",
    "mensaje": null,
    "urlRut": "documentos-rut/rut_org_10_20261021.pdf",
    "estado": "PENDIENTE",
    "fechaSolicitud": "2026-09-26T10:30:00",
    "fechaResolucion": null,
    "administradorNombre": null,
    "motivoRechazo": null
  }
}
```

#### `GET /api/verificacion/pendientes`
- Recibe: paginación.
- Devuelve: `ApiResponse<Page<SolicitudVerificacionDTO>>`
- Descripción: lista las solicitudes con RUT enviado que esperan verificación administrativa.
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Solicitudes obtenidas",
  "data": {
    "content": [
      {
        "id": 5,
        "organizacionId": 10,
        "representanteId": 7,
        "representanteNombre": "Carlos Pérez",
        "representanteCorreo": "carlos@email.com",
        "razonSocial": "Eventica SpA",
        "nit": "76.123.456-7",
        "representanteLegal": 7,
        "correoEmpresarial": "contacto@eventica.cl",
        "mensaje": "Documento recibido",
        "urlRut": "documentos-rut/rut_org_10_20261021.pdf",
        "estado": "PENDIENTE",
        "fechaSolicitud": "2026-09-26T10:30:00",
        "fechaResolucion": null,
        "administradorNombre": null,
        "motivoRechazo": null
      }
    ]
  }
}
```

#### `GET /api/verificacion/{solicitudId}`
- Recibe: `solicitudId` en path.
- Devuelve: `ApiResponse<SolicitudVerificacionDTO>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Solicitud obtenida",
  "data": {
    "id": 5,
    "organizacionId": 10,
    "representanteId": 7,
    "representanteNombre": "Carlos Pérez",
    "representanteCorreo": "carlos@email.com",
    "razonSocial": "Eventica SpA",
    "nit": "76.123.456-7",
    "representanteLegal": 7,
    "correoEmpresarial": "contacto@eventica.cl",
    "mensaje": "Documento recibido",
    "urlRut": "documentos-rut/rut_org_10_20261021.pdf",
    "estado": "PENDIENTE",
    "fechaSolicitud": "2026-09-26T10:30:00",
    "fechaResolucion": null,
    "administradorNombre": null,
    "motivoRechazo": null
  }
}
```

#### `GET /api/verificacion/{solicitudId}/rut-url`
- Recibe: `solicitudId` en path (admite alias `/{solicitudId}/rut_url`).
- Devuelve: `ApiResponse<RutUrlDTO>` con `url` temporal firmada de Supabase Storage y `expiresInSeconds`.
- Descripción: **Punto de acceso oficial del Administrador y Moderador para auditar el documento RUT cargado en la solicitud pendiente.** Obtiene la URL directamente desde la entidad `SolicitudVerificacion` (evitando consultar prematuramente la entidad `Organizacion`).
- Permisos: `ADMINISTRADOR`, `MODERADOR`, `REPRESENTANTE`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "URL temporal del RUT obtenida",
  "data": {
    "url": "https://supabase.co/storage/v1/object/sign/documentos-rut/rut_org_10_20261021.pdf?token=eyJhbG...",
    "expiresInSeconds": 3000
  }
}
```

#### `POST /api/verificacion/registro-organizador`
- Recibe: body JSON `SolicitudVerificacionRequest` con `nombreCompleto`, `correoUsuario`, `password`, `razonSocial`, `nit` y `correoEmpresarial`.
- Devuelve: `ApiResponse<Void>`; crea la cuenta y la organización en pre-registro sin exigir el RUT en el alta. El representante puede cargar el documento después. Este flujo también está disponible en `POST /api/auth/registro-organizador`.
- Permisos: público.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Cuenta y organización creadas. Completa tu RUT para publicar eventos.",
  "data": null
}
```

#### `PATCH /api/verificacion/{solicitudId}/subir-rut`
- Recibe: `solicitudId` en path y archivo obligatorio `rut` como multipart/form-data.
- Devuelve: `ApiResponse<Void>`
- Descripción: carga el RUT de la organización en `SolicitudVerificacion` y envía la solicitud a la cola de verificación del Administrador. El registro inicial puede existir sin este documento.
- Permisos: REPRESENTANTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "RUT cargado. Tu solicitud entró a cola de revisión.",
  "data": null
}
```

#### `PUT /api/verificacion/{solicitudId}/aprobar`
- Recibe: `solicitudId` en path.
- Devuelve: `ApiResponse<String>` con mensaje de éxito.
- Descripción: Aprueba la verificación de la organización en una **transacción atómica** (`@Transactional`):
  1. Cambia el estado de `SolicitudVerificacion` a `ACEPTADA`.
  2. Obtiene la URL del RUT almacenada en la solicitud y la transfiere a la entidad `Organizacion`.
  3. Actualiza el estado de `Organizacion` a `APROBADA`.
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Organización verificada.",
  "data": null
}
```

```json
{
  "success": true,
  "mensaje": "Organización verificada.",
  "data": null
}
```

#### `PUT /api/verificacion/{solicitudId}/rechazar`
- Recibe: `solicitudId` en path y parámetro de query `motivo`.
- Devuelve: `ApiResponse<Void>`
- Descripción: rechaza la solicitud de verificación de la organización.
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Solicitud rechazada",
  "data": null
}
```

#### `PATCH /api/verificacion/{solicitudId}/solicitar-correccion`
- Recibe: `solicitudId` en path y parámetro de query `motivo`.
- Devuelve: `ApiResponse<SolicitudVerificacionDTO>` (el endpoint actualmente deja `data` en `null`).
- Descripción: solicita al Representante corregir la solicitud de verificación; luego podrá actualizar los datos y reenviarla.
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Solicitud marcada para corrección",
  "data": null
}
```

#### `PATCH /api/verificacion/{solicitudId}/reenviar`
- Recibe: `solicitudId` en path y multipart/form-data con `datos` (`SolicitudVerificacionRequest`) obligatorio y `rut` opcional.
- Devuelve: `ApiResponse<Void>`
- Descripción: permite al Representante reenviar los datos corregidos y, opcionalmente, reemplazar el RUT.
- Permisos: REPRESENTANTE.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Solicitud reenviada a revisión",
  "data": null
}
```

---

## 15. Moderaciones

### Base: `/api/moderaciones`

#### `GET /api/moderaciones/estadisticas`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<ModeracionEstadisticasDTO>` con las cuatro estadísticas solicitadas de la plataforma: `publicados` (número de eventos publicados), `pendientesRevision` (revisiones pendientes), `enCorreccion` (eventos en corrección) y `rechazados` (eventos rechazados), manteniendo además compatibilidad con `aprobados`, `revisados` y `correccionesSolicitadas`.
- Permisos: MODERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Estadísticas de moderación obtenidas",
  "data": {
    "publicados": 18,
    "pendientesRevision": 24,
    "enCorreccion": 4,
    "rechazados": 2,
    "aprobados": 18,
    "revisados": 24,
    "correccionesSolicitadas": 4
  }
}
```

#### `GET /api/moderaciones/moderadores`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<UsuarioDTO>>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Moderadores obtenidos",
  "data": {
    "content": [
      {
        "id": 22,
        "nombre": "Sofía",
        "correo": "sofia@eventhive.com",
        "telefono": "+56912345678",
        "rolNombre": "MODERADOR"
      }
    ]
  }
}
```

#### `PUT /api/moderaciones/moderadores/{moderadorId}/revocar`
- Recibe: `moderadorId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Rol de moderador revocado correctamente",
  "data": null
}
```

#### `PUT /api/moderaciones/moderadores/{moderadorId}/asignar`
- Recibe: `moderadorId` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Rol de moderador asigando correctamente",
  "data": null
}
```

#### `GET /api/moderaciones/eventos/pendientes`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<EventoDTO>>`
- Descripción: lista exclusivamente los eventos que las reglas del sistema derivaron a revisión humana; no representa todos los eventos enviados para publicación.
- Permisos: MODERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Eventos pendientes de revisión",
  "data": {
    "content": [
      {
        "id": 15,
        "titulo": "Festival de Jazz",
        "descripcion": "Evento musical con artistas locales",
        "lugar": "Parque Central, Santiago",
        "foto": "https://storage.example/eventos/festival-jazz.jpg",
        "fecha": "2026-10-14",
        "hora": "19:30:00",
        "estado": "PENDIENTE_REVISION",
        "latitud": -33.4489,
        "longitud": -70.6693,
        "categoria": {
          "id": 1,
          "nombre": "Música"
        },
        "organizacion": {
          "id": 20,
          "nombre": "Eventica"
        }
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `GET /api/moderaciones/eventos/{eventoId}/moderaciones`
- Recibe: `eventoId` en path, paginación.
- Devuelve: `ApiResponse<Page<ModeracionEventoDTO>>`
- Permisos: autenticado.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Historial de moderación",
  "data": {
    "content": [
      {
        "id": 1,
        "accion": "CORRECCION_SOLICITADA",
        "moderadorId": 22,
        "moderadorNombre": "Sofía",
        "eventoId": 15,
        "eventoNombre": "Festival de Jazz",
        "estadoResultante": "EN_CORRECCION",
        "motivo": "INFORMACION_INSUFICIENTE",
        "observacion": "Falta información de ubicación",
        "fecha": "2026-09-26T10:30:00"
      }
    ]
  }
}
```

#### `PATCH /api/moderaciones/eventos/{eventoId}/aprobar`
- Recibe: `eventoId` en path.
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: MODERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento aprobado y publicado",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "PUBLICADO",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    }
  }
}
```

#### `PATCH /api/moderaciones/eventos/{eventoId}/solicitar-correccion`
- Recibe: `eventoId` y body `ModeracionEventoRequest`.
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: MODERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Se solicitaron correcciones al organizador",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "EN_CORRECCION",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    }
  }
}
```

#### `PATCH /api/moderaciones/eventos/{eventoId}/rechazar`
- Recibe: `eventoId` y body `ModeracionEventoRequest`.
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: MODERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento rechazado",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "RECHAZADO",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    }
  }
}
```

#### `PATCH /api/moderaciones/eventos/{eventoId}/suspender`
- Recibe: `eventoId` y body `ModeracionEventoRequest`.
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento suspendido",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "SUSPENDIDO",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    }
  }
}
```

#### `PATCH /api/moderaciones/eventos/{eventoId}/reactivar`
- Recibe: `eventoId` en path.
- Devuelve: `ApiResponse<EventoDTO>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Evento reactivado y publicado exitosamente",
  "data": {
    "id": 15,
    "titulo": "Festival de Jazz",
    "descripcion": "Evento musical con artistas locales",
    "lugar": "Parque Central, Santiago",
    "foto": "https://storage.example/eventos/festival-jazz.jpg",
    "fecha": "2026-10-14",
    "hora": "19:30:00",
    "estado": "PUBLICADO",
    "latitud": -33.4489,
    "longitud": -70.6693,
    "categoria": {
      "id": 1,
      "nombre": "Música"
    },
    "organizacion": {
      "id": 20,
      "nombre": "Eventica"
    }
  }
}
```

---

## 16. Promoción pagada de eventos

La promoción de eventos es distinta a ofrecer descuentos en boletos. Los
descuentos de compra ya no están disponibles ni se aplican al checkout.

#### `GET /api/promociones/planes`
- Público. Devuelve los planes activos con precio, comisión, bandera `premium` y `pautaRedes`.
- También incluye `detallePublicidad`. Impulso Digital inicia en $500.000/10% (anuncios pagados en redes por 1-2 semanas); Sold Out Absoluto inicia en $1.000.000/15% (Premium, carrusel, pauta de alto presupuesto y publicaciones fijas).

#### `POST /api/compras/eventos/{eventoId}/posicionamiento/pagos`
- Permisos: REPRESENTANTE del evento.
- Parámetros/Body: Recibe `planId` como query param (`?planId={id}`) o en JSON body (`{ "planId": {id} }`).
- Registra una intención de pago simulada usando el precio vigente del plan.

#### `PATCH /api/compras/posicionamiento/pagos/{pagoId}/confirmar-simulado`
- Permisos: REPRESENTANTE propietario.
- Confirma el pago simulado, destaca el evento y conserva la comisión contratada.
- En producción debe reemplazarse la confirmación simulada por una confirmación de pasarela.

#### `GET /api/eventos/destacados`
- Devuelve todos los eventos publicados con promoción pagada y confirmada (`promocionado: true`), ya sea con plan Estándar o Premium.
- La lista está ordenada por fecha y hora del evento ascendente.

#### `GET /api/eventos/carrusel`
- Exclusivo para eventos publicados con promoción pagada y confirmada que hayan contratado un plan con `premium = true` y que tengan asignada su `url_imagen_destacado` por Marketing.
- Devuelve exclusivamente el array con la propiedad `url_imagen_promocionado`.

#### `POST /api/promociones/eventos/{eventoId}/posicionar`
- Permisos: MARKETING o ADMINISTRADOR (el cliente o la organización no pueden asignar directamente esta imagen).
- Requiere que el evento esté en estado `PUBLICADO`, tenga un pago de posicionamiento `CONFIRMADO` y que el plan contratado tenga `premium = true`.
- Soporta dos formatos de envío:
  1. JSON (`application/json`): `{ "urlImagenDestacado": "https://..." }` validando que pertenezca al bucket de eventos configurado.
  2. Archivo directo (`multipart/form-data`): campo `imagen` con el archivo a subir. El servidor valida formato, tamaño y almacena de forma segura devolviendo `{ "urlImagenDestacado": "https://..." }`.

### Dashboard MARKETING

#### `GET /api/marketing/estadisticas`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<MarketingEstadisticasDTO>` con:
  - `eventosActivosPromocionados`: número de eventos activos (PUBLICADOS) con plan de promoción pagado y confirmado.
  - `eventosPorPlan`: lista de objetos `PlanPromocionConteoDTO` con `planId`, `planCodigo`, `planNombre` y `cantidadEventos` contratados.
- Permisos: MARKETING o ADMINISTRADOR.

#### `POST /api/marketing/imagenes`
- Recibe: `multipart/form-data` con campo `imagen`.
- Devuelve: `ApiResponse<Map<String, String>>` con `{ "url": "https://..." }`.
- Permisos: MARKETING o ADMINISTRADOR.
- Valida tipo de archivo (magic bytes y MIME) y tamaño máximo (5MB) para evitar subir archivos peligrosos.

#### `POST /api/marketing/planes`
- Recibe: body JSON `PlanPromocionRequest` con:
  - `nombre` (obligatorio, no vacío)
  - `codigo` (obligatorio, único en el sistema)
  - `precio` (obligatorio, no negativo)
  - `detallePublicidad` (texto descriptivo)
  - `premium` (booleano)
  - `pautaRedes` / `llevaPautaRedes` (booleano)
  - `comisionPorcentaje` / `porcentajeComision` (número entre 0.00 y 100.00)
- Devuelve: `ApiResponse<PlanPromocionDTO>` (incluye tanto `comisionPorcentaje` como `porcentajeComision`).
- Permisos: MARKETING o ADMINISTRADOR.
- Descripción: crea un nuevo plan publicitario de precio fijo y comisión configurable.

#### `GET /api/marketing/planes`
- Lista todos los planes configurados en el sistema ordenados por precio ascendente.
- Permisos: MARKETING o ADMINISTRADOR.

#### `PUT /api/marketing/planes/{id}`
- Recibe: `id` del plan en path y body `PlanPromocionRequest`.
- Devuelve: `ApiResponse<PlanPromocionDTO>`
- Permisos: MARKETING o ADMINISTRADOR.
- Descripción: actualiza nombre, código, precio fijo, porcentaje de comisión (entre 0 y 100), Premium, pauta en redes y detalle publicitario, conservando la comisión existente si el campo no se envía.

#### `GET /api/marketing/eventos-promocionados`
- Permisos: MARKETING o ADMINISTRADOR.
- Lista eventos y organizaciones con pago confirmado, plan contratado y estado de campaña, garantizando que no existan eventos duplicados (mostrando la contratación más reciente por evento).

#### Banners del Home
- `GET /api/banners-home/admin` y las operaciones de escritura de `/api/banners-home` permiten ADMINISTRADOR y MARKETING. Banners soportan posiciones 1 y 2 con carga directa de imágenes mediante `multipart/form-data`.

La aplicación usa `spring.jpa.hibernate.ddl-auto=none`. Antes de desplegar
esta versión, aplicar una vez
[`V1__marketing_invitations_and_paid_promotions.sql`](./demo/src/main/resources/db/manual/V1__marketing_invitations_and_paid_promotions.sql).
Configurar el envío por Brevo SMTP mediante las variables `MAIL_HOST`,
`MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM` y
`eventhive.frontend-url` (URL base de la web para aceptar invitaciones).

---

## 17. Roles

### Base: `/api/roles`

#### `GET /api/roles`
- Recibe: paginación.
- Devuelve: `ApiResponse<PagedResponse<RolDTO>>`
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Roles obtenidos",
  "data": {
    "content": [
      { "id": 1, "nombre": "CLIENTE" },
      { "id": 2, "nombre": "REPRESENTANTE" }
    ]
  }
}
```

#### `POST /api/roles`
- Recibe: body `RolRequest`.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Rol creado exitosamente",
  "data": null
}
```

#### `PUT /api/roles/{id}`
- Recibe: `id` en path y query param `nombre`.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Rol actualizado exitosamente",
  "data": null
}
```

#### `DELETE /api/roles/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`
- Permisos: ADMINISTRADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Rol eliminado exitosamente",
  "data": null
}
```

### Invitaciones de roles por enlace temporal

Una Administración autenticada puede invitar a MODERADOR o MARKETING; un
REPRESENTANTE solo puede invitar a OPERADOR. Se puede invitar un correo
sin cuenta o uno que ya tenga una cuenta CLIENTE. El enlace de Brevo es
de un solo uso y vence 24 horas después del envío.

#### `POST /api/invitaciones/roles`
- Body: `{ "correo": "persona@correo.com", "rol": "MARKETING" }`.
- Permisos: ADMINISTRADOR o REPRESENTANTE. La autorización limita qué roles puede asignar cada remitente.

#### `GET /api/invitaciones/roles/validar?token={token}`
- Público; devuelve el correo, rol y fecha de expiración para mostrar el formulario.

#### `POST /api/invitaciones/roles/aceptar`
- Público. Para una cuenta nueva, body: `{ "token": "...", "nombre": "Nombre", "telefono": "+573001112233", "clave": "contraseña segura" }`. Para una cuenta CLIENTE existente basta con `{ "token": "..." }`.
- La cuenta CLIENTE conserva nombre, teléfono y contraseña; al aceptar se cambia su rol y, para OPERADOR, se vincula a la organización que envió la invitación. Los demás roles existentes (REPRESENTANTE, MODERADOR, OPERADOR, ADMINISTRADOR o MARKETING) no pueden aceptar otra invitación.

#### `POST /api/invitaciones/roles/rechazar`
- Público. Permite al invitado rechazar la invitación explícitamente.
- Parámetro: Puede enviarse como query param `?token=...` o como JSON en el body `{ "token": "..." }`.
- Marca la invitación con `fechaRechazo`. Una invitación pendiente no puede ser reenviada; debe ser aceptada o rechazada. Una vez rechazada, ya no se puede utilizar ni validar, y se habilita la posibilidad de emitir una nueva invitación si es necesario.

#### `GET /api/invitaciones/roles/enviadas`
- ADMINISTRADOR o REPRESENTANTE. Devuelve la lista paginada de invitaciones enviadas por la persona autenticada.

#### Preparación de despliegue y prueba SMTP
- Antes del primer despliegue, ejecutar una vez `demo/src/main/resources/db/migration/20261012_correo_invitaciones.sql` contra PostgreSQL/Supabase. `spring.jpa.hibernate.ddl-auto=none` está configurado, así que las tablas no se crean automáticamente.
- Configurar `MAIL_HOST` (opcional; por defecto `smtp-relay.brevo.com`), `MAIL_PORT` (opcional; por defecto `587`), `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM` (remitente verificado por Brevo), `MAIL_FROM_NAME` (opcional; por defecto `EventHive`) y `FRONTEND_URL` (origen del frontend que recibe los enlaces).
- Para probar el envío real, autenticar un ADMINISTRADOR y llamar a `POST /api/invitaciones/roles` con `{"correo":"destino@correo.com","rol":"MARKETING"}`; un REPRESENTANTE puede probar con `"rol":"OPERADOR"`. Un envío SMTP fallido responde con error y no deja guardada la invitación.

---

## 18. Enums / motivos de rechazo

### Base: `/api/enums`

#### `GET /api/enums/motivos-rechazos`
- Recibe: sin parámetros.
- Devuelve: `ApiResponse<List<MotivosRechazos>>`
- Permisos: ADMINISTRADOR o MODERADOR.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Motivos de rechazos obtenidos",
  "data": [
    "INFORMACION_INSUFICIENTE",
    "DOCUMENTACION_INVALIDA",
    "VIOLACION_POLITICA"
  ]
}
```

---

## 19. Estadísticas de administración

### Base: `/api/admin/estadisticas`

Todos los endpoints son de solo lectura, no reciben parámetros y requieren rol ADMINISTRADOR.

#### `GET /api/admin/estadisticas/organizaciones-por-validacion`
- Devuelve: `ApiResponse<OrganizacionesPorValidacionDTO>` con conteos de organizaciones según el estado de validación del RUT.
- Ejemplo de `data`:

```json
{
  "pendientesValidacionRut": 3,
  "sinRut": 2,
  "total": 12,
  "porEstado": [
    { "estado": "APROBADA", "cantidad": 7 },
    { "estado": "PENDIENTE_REVISION", "cantidad": 3 },
    { "estado": "SUSPENDIDA", "cantidad": 2 }
  ]
}
```

#### `GET /api/admin/estadisticas/eventos-por-estado`
- Devuelve: `ApiResponse<List<EventoEstadoConteoDTO>>`.
- Ejemplo de `data`:

```json
[
  { "estado": "PUBLICADO", "cantidad": 18 },
  { "estado": "PENDIENTE_REVISION", "cantidad": 4 }
]
```

#### `GET /api/admin/estadisticas/eventos-por-categoria`
- Devuelve: `ApiResponse<List<EventosPorCategoriaDTO>>`.
- Ejemplo de `data`:

```json
[
  { "categoriaId": 1, "nombre": "Música", "cantidadEventos": 12 },
  { "categoriaId": 3, "nombre": "Arte", "cantidadEventos": 6 }
]
```

#### `GET /api/admin/estadisticas/ingresos-plataforma`
- Devuelve: `ApiResponse<IngresosPlataformaDTO>` con el desglose de métricas financieras de la plataforma:
  - `ventaBrutaTotal`: suma total de la venta bruta de boletas (incluyendo la comisión comercial pagada por el comprador) más los pagos confirmados de promociones.
  - `comisionesVentas`: comisiones comerciales de EventHive obtenidas exclusivamente de la venta de boletas.
  - `ingresosPagoPromocion`: recaudación total generada por la contratación de planes de promoción pagados y confirmados.
  - `ingresosOrganizaciones`: importe neto correspondiente a las organizaciones por sus ventas de boletas.
  - `totalIngresos`: ingresos brutos de la plataforma (`comisionesVentas` + `ingresosPagoPromocion`).
  - Nota: la métrica obsoleta de tickets emitidos fue retirada del modelo financiero.
- Ejemplo de `data`:

```json
{
  "totalIngresos": 250000.00,
  "comisionesVentas": 50000.00,
  "ingresosPagoPromocion": 200000.00,
  "ingresosOrganizaciones": 500000.00,
  "ventaBrutaTotal": 750000.00,
  "comisionesPosicionados": 15000.00
}
```

#### `GET /api/admin/estadisticas/top-eventos-ventas`
- Devuelve: `ApiResponse<List<TopEventoVentasDTO>>` con los cinco eventos con mayor volumen de ventas de entradas.
- Regla: se calcula **exclusivamente sobre eventos en estado `PUBLICADO`** con compras confirmadas.
- Ejemplo de `data`:

```json
[
  {
    "eventoId": 15,
    "nombre": "Festival de Jazz",
    "organizacionId": 10,
    "organizacion": "Eventica SpA",
    "entradasVendidas": 240,
    "totalVentas": 6000000
  }
]
```

#### `GET /api/admin/estadisticas/top-organizaciones-ventas`
- Devuelve: `ApiResponse<List<TopOrganizacionVentasDTO>>` con las cinco organizaciones con mayor recaudación.
- Regla: se calcula a partir de las ventas de sus **eventos promocionados que se encuentren en estado `PUBLICADO`**.
- Ejemplo de `data`:

```json
[
  {
    "organizacionId": 10,
    "razonSocial": "Eventica SpA",
    "entradasVendidas": 480,
    "totalVentas": 12000000
  }
]
```

---

## 20. Envío de correos administrativos

### Base: `/api/admin/correos`

#### `POST /api/admin/correos/enviar`
- Recibe: body JSON `CorreoAdministrativoRequest` con:
  - `destinatario`: correo electrónico válido (obligatorio).
  - `asunto`: asunto del mensaje (obligatorio, no vacío).
  - `mensaje`: cuerpo del correo electrónico en texto plano o HTML (obligatorio, no vacío).
- Devuelve: `ApiResponse<Map<String, Object>>`
- Permisos: ADMINISTRADOR.
- Descripción: envía un correo administrativo oficial a través del servicio integrado (Gmail API con OAuth 2.0).
  - Remitente oficial: la dirección autorizada del sistema (`MAIL_FROM`). No se permite suplantación arbitraria de remitente.
  - Registro de auditoría: el administrador autenticado queda registrado como el iniciador del envío (`iniciadoPor`).
  - Respuesta: devuelve el estado de aceptación de la solicitud de envío (`ACEPTADO`).
- Ejemplo de petición:

```json
{
  "destinatario": "representante@organizacion.com",
  "asunto": "Validación de documentación RUT - EventHive",
  "mensaje": "Estimado organizador, le informamos que su RUT ha sido validado satisfactoriamente."
}
```

- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Solicitud de envío de correo administrativo aceptada",
  "data": {
    "destinatario": "representante@organizacion.com",
    "iniciadoPor": "admin@eventhive.com",
    "estado": "ACEPTADO"
  }
}
```

---

## 21. Palabras prohibidas

### Base: `/api/administracion/palabras-prohibidas`

Todos los endpoints de este módulo requieren rol ADMINISTRADOR. `PalabraProhibidaRequest` recibe `palabra` (texto de hasta 100 caracteres) y `severidad` (`GRAVE` o `SOSPECHOSA`, enum `SeveridadPalabra`).

#### `GET /api/administracion/palabras-prohibidas`
- Recibe: parámetros de paginación (`page`, `size`, `sort`).
- Devuelve: `ApiResponse<PagedResponse<PalabraProhibidaDTO>>`; cada elemento contiene `id`, `palabra`, `severidad`, `activa` y `fechaCreacion`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Palabras prohibidas obtenidas",
  "data": {
    "content": [
      {
        "id": 1,
        "palabra": "ejemplo",
        "severidad": "GRAVE",
        "activa": true,
        "fechaCreacion": "2026-09-26T10:30:00"
      }
    ],
    "pageNumber": 0,
    "pageSize": 10,
    "totalElements": 1,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

#### `POST /api/administracion/palabras-prohibidas`
- Recibe: body JSON `PalabraProhibidaRequest` con `palabra` y `severidad`.
- Devuelve: `ApiResponse<PalabraProhibidaDTO>`.
- Ejemplo de respuesta:

```json
{
  "success": true,
  "mensaje": "Palabra creada",
  "data": {
    "id": 1,
    "palabra": "ejemplo",
    "severidad": "GRAVE",
    "activa": true,
    "fechaCreacion": "2026-09-26T10:30:00"
  }
}
```

#### `PUT /api/administracion/palabras-prohibidas/{id}`
- Recibe: `id` en path y body JSON `PalabraProhibidaRequest` con `palabra` y `severidad`.
- Devuelve: `ApiResponse<PalabraProhibidaDTO>`.
- Ejemplo de respuesta: `data` contiene el DTO actualizado con `id`, `palabra`, `severidad`, `activa` y `fechaCreacion`.

#### `PATCH /api/administracion/palabras-prohibidas/{id}/activa`
- Recibe: `id` en path y parámetro de query booleano `activa`.
- Devuelve: `ApiResponse<Void>`.
- Ejemplo de respuesta: `{"success":true,"mensaje":"Palabra desactivada","data":null}`. Si `activa=true`, el mensaje es `Palabra activada`.

#### `DELETE /api/administracion/palabras-prohibidas/{id}`
- Recibe: `id` en path.
- Devuelve: `ApiResponse<Void>`.
- Ejemplo de respuesta: `{"success":true,"mensaje":"Palabra eliminada","data":null}`.

---

## 22. Banners del Home

### Base: `/api/banners-home`

Este módulo administra los dos espacios promocionales propios de Eventhive. No está relacionado con organizaciones, eventos ni con el módulo `/api/promociones`. Las únicas posiciones válidas son `1` y `2`.

#### `GET /api/banners-home`
- Público.
- Devuelve: `ApiResponse<List<BannerHomeDTO>>` con los banners configurados, ordenados por posición. Los espacios vacíos no se incluyen.
- Cada `BannerHomeDTO` contiene `id`, `titulo`, `imagenUrl`, `textoBoton`, `enlaceUrl` y `posicion`.
- Respuesta: HTTP 200.

```json
{
  "success": true,
  "mensaje": "Banners del Home obtenidos",
  "data": [
    {
      "id": 1,
      "titulo": "Promociona tu evento en Eventhive",
      "imagenUrl": "https://storage.example/banners-home/banner-1",
      "textoBoton": "Conocer más",
      "enlaceUrl": "https://eventhive.example/promociones",
      "posicion": 1
    }
  ]
}
```

#### `GET /api/banners-home/admin`
- Requiere rol `ADMINISTRADOR`.
- Devuelve: `ApiResponse<List<BannerHomeDTO>>` con exactamente los dos espacios administrativos (posiciones 1 y 2). Si un espacio no tiene banner, sus campos son `null`, excepto `posicion`.
- Respuesta: HTTP 200.

#### `POST /api/banners-home`
- Requiere rol `ADMINISTRADOR`.
- Content-Type: `multipart/form-data`.
- Parámetros: `posicion` (int: 1 o 2), `titulo` (string), `textoBoton` (string), `enlaceUrl` (string), `imagen` (archivo obligatorio).
- Devuelve: `ApiResponse<BannerHomeDTO>` con HTTP 201 Created.
- Validaciones: posición válida, la posición debe estar vacía, los campos de texto no pueden estar vacíos y la imagen es obligatoria. No se puede crear un tercer espacio ni duplicar una posición.
- Imagen: se carga a Supabase Storage (PNG, JPG o WebP, máximo 5 MB); la respuesta contiene `imagenUrl`, no el archivo.

#### `POST /api/banners-home/{posicion}`
- Requiere rol `ADMINISTRADOR`.
- Content-Type: `multipart/form-data`.
- Parámetros: `posicion` en el path (int: 1 o 2), `titulo`, `textoBoton`, `enlaceUrl` e `imagen` (archivo obligatorio).
- Devuelve: `ApiResponse<BannerHomeDTO>` con HTTP 201 Created.
- Aplica las mismas validaciones de creación; si la posición ya existe, devuelve error 400.

#### `PUT /api/banners-home/{posicion}`
- Requiere rol `ADMINISTRADOR`.
- Content-Type: `multipart/form-data`.
- Parámetros: `posicion` en el path (int: 1 o 2), `titulo`, `textoBoton`, `enlaceUrl` e `imagen` (archivo opcional; si se omite, se conserva la imagen actual).
- Devuelve: `ApiResponse<BannerHomeDTO>` con HTTP 200.
- Validaciones: los campos de texto no pueden estar vacíos y la posición debe tener un banner creado; si no existe, devuelve error 404.

#### `DELETE /api/banners-home/{posicion}`
- Requiere rol `ADMINISTRADOR`.
- Parámetro: `posicion` en el path (int: 1 o 2).
- Elimina el registro de la posición indicada y libera ese espacio. Si no existe, devuelve error 404.
- Devuelve `ApiResponse<Void>` con HTTP 200 y el mensaje `Banner eliminado exitosamente`.

#### Respuestas de error
- Posición distinta de `1` o `2`, campos de texto vacíos, creación sobre una posición ocupada o imagen faltante al crear: HTTP 400.
- Intentar actualizar o eliminar una posición sin banner: HTTP 404.
- Usuario sin rol `ADMINISTRADOR`: HTTP 403.

---

## 23. Invitaciones a roles y flujo seguro

### Base: `/api/invitaciones/roles`

#### `POST /api/invitaciones/roles`
- **Roles autorizados**: `ADMINISTRADOR`, `REPRESENTANTE`.
- **Content-Type**: `application/json`.
- **Body**: `InvitacionRolRequest`:
  ```json
  {
    "correo": "usuario@example.com",
    "rol": "MODERADOR"
  }
  ```
- **Reglas de autorización y negocio**:
  - `ADMINISTRADOR`: solo puede invitar a `MODERADOR` o `MARKETING`. La organización asociada es `null`. No puede concederse a sí mismo privilegios ni invitar `ADMINISTRADOR` ni `OPERADOR`.
  - `REPRESENTANTE`: solo puede invitar a `OPERADOR` para su propia organización (determinada por el representante autenticado). No puede invitar moderadores, marketing ni administradores.
  - La cuenta de destino no debe poseer ya un rol administrativo o estar vinculada a una organización distinta.
  - Si ya existe una invitación pendiente para ese correo, el sistema realiza un reenvío seguro: invalida el token previo, genera un nuevo token criptográfico de 32 bytes con expiración de 24 horas y reenvía el correo, previniendo duplicados en la base de datos.
  - Si el envío de correo falla (SMTP), la transacción se revierte por completo evitando dejar invitaciones huérfanas.
- **Respuesta**: HTTP 201 Created.
  ```json
  {
    "success": true,
    "mensaje": "Invitación enviada por correo"
  }
  ```

#### `GET /api/invitaciones/roles/validar`
- **Roles autorizados**: Público (cualquier usuario con enlace de invitación).
- **Parámetro**: `token` (query param, string).
- **Descripción**: Comprueba la autenticidad y vigencia de la invitación mediante el hash SHA-256 del token.
- **Devuelve**: `ApiResponse<InvitacionRolDTO>`
- **Ejemplo de respuesta**:
  ```json
  {
    "success": true,
    "mensaje": "Invitación válida",
    "data": {
      "correo": "persona@example.com",
      "rol": "OPERADOR",
      "fechaEnvio": "2026-10-21T18:30:00",
      "fechaExpiracion": "2026-10-22T18:30:00",
      "organizacionNombre": "Organización Viva",
      "estado": "PENDIENTE"
    }
  }
  ```

#### `GET /api/invitaciones/roles/enviadas`
- **Roles autorizados**: `ADMINISTRADOR`, `REPRESENTANTE`.
- **Parámetros**: Parámetros estándar de paginación (`page`, `size`, `sort`).
- **Descripción**: Consulta las invitaciones emitidas por la administración (si es administrador) o para su organización (si es representante). **Filtra estrictamente para devolver únicamente invitaciones en estado `PENDIENTE` o `EXPIRADA`**. El rol está asociado como entidad JPA `Rol`.
- **Devuelve**: `ApiResponse<PagedResponse<InvitacionRolEnviadaDTO>>`
- **Ejemplo de respuesta**:
  ```json
  {
    "success": true,
    "mensaje": "Invitaciones enviadas",
    "data": {
      "content": [
        {
          "id": 1,
          "correo": "operador@eventos.com",
          "rol": "OPERADOR",
          "fechaInvitacion": "2026-10-21T18:30:00",
          "fechaEnvio": "2026-10-21T18:30:00",
          "fechaExpiracion": "2026-10-22T18:30:00",
          "fechaAceptacion": null,
          "estado": "PENDIENTE",
          "organizacionNombre": "Eventos SAS"
        }
      ],
      "pageNumber": 0,
      "pageSize": 10,
      "totalElements": 1,
      "totalPages": 1,
      "hasNext": false,
      "hasPrevious": false
    }
  }
  ```

#### `POST /api/invitaciones/roles/aceptar`
- **Roles autorizados**: Público / Destinatario de la invitación.
- **Body**: `AceptarInvitacionRolRequest`:
  ```json
  {
    "token": "dGhpcy1pcy1hLXNlY3VyZS10b2tlbi0yNTYtYml0cw",
    "nombre": "Carlos Gómez",
    "telefono": "+573001234567",
    "clave": "ContraseñaSegura123!"
  }
  ```
- **Reglas**:
  - Si el correo ya tiene una cuenta `CLIENTE`, se asocia directamente el nuevo rol y la organización definida por la invitación; los datos personales y contraseña existentes no se sobreescriben.
  - Si el usuario no existe, se crea la cuenta con estado activo y las credenciales proporcionadas.
  - El rol (`Rol`) y la organización provienen exclusivamente del registro backend de la invitación; el cliente no puede alterar el rol asignado.
  - **Aceptación y eliminación automática:** En el mismo flujo transaccional (`@Transactional`), la invitación es eliminada de la base de datos tras otorgar el rol con éxito, garantizando que no queden registros pendientes ni inconsistencias.
- **Respuesta**: HTTP 201 Created.
  ```json
  {
    "success": true,
    "mensaje": "Invitación aceptada correctamente"
  }
  ```

#### `POST /api/invitaciones/roles/rechazar`
- **Roles autorizados**: Público / Destinatario de la invitación.
- **Parámetro**: Acepta `token` vía query param (`?token=...`) o JSON en el body (`{ "token": "..." }`).
- **Reglas**:
  - Invalida y remueve la invitación sin requerir columnas huérfanas de rechazo.
- **Respuesta**: HTTP 200 OK.
  ```json
  {
    "success": true,
    "mensaje": "Invitación rechazada correctamente"
  }
  ```

#### `DELETE /api/invitaciones/roles/{id}`
- **Roles autorizados**: `ADMINISTRADOR`, `REPRESENTANTE`.
- **Parámetro**: `id` en path.
- **Descripción**: Permite cancelar y eliminar una invitación enviada. Valida los permisos de pertenencia a la organización del representante o de la administración.
- **Respuesta**: HTTP 200 OK.
  ```json
  {
    "success": true,
    "mensaje": "Invitación eliminada correctamente"
  }
  ```

#### `POST /api/invitaciones/roles/{id}/reenviar`
- **Roles autorizados**: `ADMINISTRADOR`, `REPRESENTANTE`.
- **Parámetro**: `id` en path.
- **Descripción y Reglas de Negocio**:
  - **Condición obligatoria**: Solo se permite reenviar invitaciones que se encuentren en estado `EXPIRADA`.
  - Si una invitación aún está en estado `PENDIENTE`, el backend bloquea la acción con un error de negocio (`400 Bad Request`), impidiendo spam innecesario.
  - Al reenviarse:
    1. Actualiza su estado de `EXPIRADA` a `PENDIENTE`.
    2. Actualiza `fechaInvitacion` y `fechaEnvio` a la fecha/hora actual.
    3. Extiende la vigencia a 24 horas a partir del momento del reenvío.
    4. Genera un nuevo token criptográfico seguro de 32 bytes.
    5. Despacha el correo electrónico con el enlace de acceso.
- **Respuesta**: HTTP 200 OK.
  ```json
  {
    "success": true,
    "mensaje": "Invitación reenviada correctamente"
  }
  ```

---

## 24. Correos administrativos oficiales

### Base: `/api/admin/correos`

#### `POST /api/admin/correos/enviar`
- **Roles autorizados**: `ADMINISTRADOR`.
- **Descripción**: Envía un comunicado oficial por correo electrónico a un destinatario determinado. Este endpoint es estrictamente para comunicación y **no** asigna roles ni genera tokens de privilegios.
- **Body**: `CorreoAdministrativoRequest`:
  ```json
  {
    "destinatario": "usuario@example.com",
    "asunto": "Aviso importante de administración",
    "mensaje": "Se informa que su cuenta requiere actualización de información fiscal."
  }
  ```
- **Respuesta**: HTTP 200 OK.
  ```json
  {
    "success": true,
    "mensaje": "Solicitud de envío de correo administrativo aceptada",
    "data": {
      "destinatario": "usuario@example.com",
      "iniciadoPor": "admin@eventhive.com",
      "estado": "ACEPTADO"
    }
  }
  ```

#### `POST /api/admin/correos/invitar`
- **Roles autorizados**: `ADMINISTRADOR`.
- **Descripción**: Endpoint administrativo para emitir invitaciones con asignación de rol (`MODERADOR` o `MARKETING`).
- **Body**: `InvitacionRolRequest`:
  ```json
  {
    "correo": "nuevo.moderador@eventhive.com",
    "rol": "MODERADOR"
  }
  ```
- **Respuesta**: HTTP 201 Created.
  ```json
  {
    "success": true,
    "mensaje": "Invitación administrativa enviada por correo"
  }
  ```

---

## 25. Gestión de operadores e invitaciones de organización

### Base: `/api/organizaciones`

#### `POST /api/organizaciones/invitar`
- **Roles autorizados**: `REPRESENTANTE`.
- **Parámetros**: Admite query param `?correo=...` o cuerpo JSON `{"correo": "..."}`.
- **Descripción**: El representante invita exclusivamente a un `OPERADOR` para unirse a su propia organización.
- **Respuesta**: HTTP 200 OK.
  ```json
  {
    "success": true,
    "mensaje": "Invitación enviada por correo; el enlace vence en 24 horas"
  }
  ```

#### `GET /api/organizaciones/invitaciones-enviadas`
- **Roles autorizados**: `REPRESENTANTE`.
- **Descripción**: Consulta el historial y estado de invitaciones emitidas para la organización del representante.
- **Devuelve**: `ApiResponse<PagedResponse<InvitacionRolEnviadaDTO>>`
- **Respuesta**: HTTP 200 OK.

#### `GET /api/organizaciones/mis-operadores`
- **Roles autorizados**: `REPRESENTANTE`.
- **Descripción**: Lista todos los operadores activos pertenecientes a la organización del representante con sus respectivos permisos granulares sobre eventos.
- **Devuelve**: `ApiResponse<PagedResponse<OperadorDTO>>`
- **Ejemplo de respuesta**:
  ```json
  {
    "success": true,
    "mensaje": "Operadores obtenidos",
    "data": {
      "content": [
        {
          "id": 14,
          "nombreCompleto": "Andrés Operador",
          "correo": "andres@eventos.com",
          "permisosEvento": ["CHECK_IN", "CREAR_EVENTO", "EDITAR_EVENTO"]
        }
      ],
      "pageNumber": 0,
      "pageSize": 10,
      "totalElements": 1,
      "totalPages": 1
    }
  }
  ```

#### `PATCH /api/organizaciones/operadores/{operadorId}/actualizar-permisos`
- **Roles autorizados**: `REPRESENTANTE`.
- **Descripción**: Permite al representante asignar o revocar permisos a un operador de su propia organización. Permisos soportados: `CHECK_IN`, `CREAR_EVENTO`, `EDITAR_EVENTO`, `CANCELAR_EVENTO`. Un operador sin un permiso específico recibirá HTTP 403 Forbidden si intenta invocar las acciones restringidas.
- **Body**: `PermisosOperadorRequest`:
  ```json
  {
    "permisos": ["CHECK_IN", "EDITAR_EVENTO"]
  }
  ```
- **Respuesta**: HTTP 200 OK.
  ```json
  {
    "success": true,
    "mensaje": "Permisos actualizados"
  }
  ```

#### `DELETE /api/organizaciones/expulsar-operador/{operadorId}`
- **Roles autorizados**: `REPRESENTANTE`.
- **Descripción**: Desvincula al operador de la organización, remueve todos sus permisos sobre eventos y restablece su rol a `CLIENTE`.
- **Respuesta**: HTTP 200 OK.
  ```json
  {
    "success": true,
    "mensaje": "Operador removido de la organización"
  }
  ```

---

## 26. Marketing y Posicionamiento de Eventos

### Base: `/api/marketing`, `/api/promociones`, `/api/compras`

#### `GET /api/promociones/planes`
- **Roles autorizados**: Público / Autenticado.
- **Descripción**: Devuelve la lista de planes publicitarios activos disponibles para contratación.
- **Devuelve**: `ApiResponse<List<PlanPromocionDTO>>`
- **Respuesta**: HTTP 200 OK.

#### `GET /api/marketing/planes`
- **Roles autorizados**: `MARKETING`, `ADMINISTRADOR`.
- **Descripción**: Devuelve la totalidad de planes promocionales (activos e inactivos) para gestión publicitaria.
- **Respuesta**: HTTP 200 OK.

#### `POST /api/marketing/planes`
- **Roles autorizados**: `MARKETING`, `ADMINISTRADOR`.
- **Descripción**: Crea un nuevo plan publicitario.
- **Body**: `PlanPromocionRequest` (`codigo`, `nombre`, `precio`, `comisionPorcentaje`, `premium`, `pautaRedes`, `detallePublicidad`, `activo`).
- **Respuesta**: HTTP 201 Created.

#### `PUT /api/marketing/planes/{id}`
- **Roles autorizados**: `MARKETING`, `ADMINISTRADOR`.
- **Descripción**: Actualiza los atributos de un plan promocional existente.
- **Respuesta**: HTTP 200 OK.

#### `GET /api/marketing/eventos-promocionados`
- **Roles autorizados**: `MARKETING`, `ADMINISTRADOR`.
- **Descripción**: Lista todos los eventos que cuentan con una promoción confirmada y pagada.
- **Devuelve**: `ApiResponse<List<EventoPromocionadoMarketingDTO>>`
- **Respuesta**: HTTP 200 OK.

#### `POST /api/promociones/eventos/{eventoId}/posicionar`
- **Roles autorizados**: `MARKETING`, `ADMINISTRADOR`.
- **Descripción**: Asigna la URL de la imagen destacada (del bucket Supabase de eventos) a un evento que cuenta con promoción confirmada de tipo Premium.
- **Body**: `PosicionamientoSeoRequest`:
  ```json
  {
    "urlImagenDestacado": "https://[supabase-url]/storage/v1/object/public/eventos-images/destacado_123.jpg"
  }
  ```
- **Respuesta**: HTTP 200 OK.

#### `POST /api/compras/eventos/{eventoId}/posicionamiento/pagos`
- **Roles autorizados**: `REPRESENTANTE`.
- **Parámetros / Body**: Admite `planId` como query param (`?planId={planId}`) o en JSON body (`{ "planId": {planId} }`).
- **Descripción**: Inicia la contratación de un plan publicitario para un evento publicado perteneciente a la organización del representante autenticado.
- **Devuelve**: `ApiResponse<PagoPosicionamientoDTO>` con estado `PENDIENTE`.
- **Respuesta**: HTTP 201 Created.

#### `PATCH /api/compras/posicionamiento/pagos/{pagoId}/confirmar-simulado`
- **Roles autorizados**: `REPRESENTANTE`.
- **Descripción**: Confirma el pago simulado del plan contratado, marcando el pago como `CONFIRMADO`, activando `evento.promocionado = true` y enviando notificación de correo confirmada.
- **Respuesta**: HTTP 200 OK.

---

## 27. Resumen de permisos por rol

- **Público**:
  - Registro y login (`/api/auth/login`, `/api/auth/registro`).
  - Consulta pública de eventos (`GET /api/eventos`, `GET /api/eventos/destacados`, `GET /api/eventos/carrusel`, `GET /api/eventos/mapa`).
  - Banners del home (`GET /api/banners-home`).
  - Consulta de organizaciones públicas (`GET /api/organizaciones`).
  - Validación y aceptación de invitaciones por token (`GET /api/invitaciones/roles/validar`, `POST /api/invitaciones/roles/aceptar`).
  - Consulta de planes disponibles de promoción (`GET /api/promociones/planes`).
- **Autenticado (Cualquier rol con sesión activa)**:
  - Perfil propio y cambio de clave (`/api/usuarios/perfil`, `/api/usuarios/perfil/cambiar-clave`).
  - Lista de deseos y seguimiento de organizaciones.
  - Consulta y descarga de boletos adquiridos (`/api/boletos/mis-boletos`).
  - Historial de compras (`GET /api/compras`).
- **CLIENTE**:
  - Compra de tiquetes y confirmación de pagos.
  - Emisión de valoraciones sobre organizaciones.
- **REPRESENTANTE**:
  - Administración del perfil de su organización (`PUT /api/organizaciones/mi-organizacion`).
  - Consulta de estadísticas y ventas de la organización.
  - Invitación de operadores exclusivamente para su organización (`POST /api/organizaciones/invitar`).
  - Consulta de invitaciones emitidas (`GET /api/organizaciones/invitaciones-enviadas`).
  - Gestión de operadores y asignación granular de permisos (`GET /api/organizaciones/mis-operadores`, `PATCH .../actualizar-permisos`, `DELETE .../expulsar-operador/{id}`).
  - Control total sobre creación, edición, publicación y cancelación de eventos de su organización.
  - Contratación y confirmación de planes publicitarios de posicionamiento para sus eventos.
- **OPERADOR**:
  - Actúa exclusivamente bajo los permisos asignados por su representante:
    - `CREAR_EVENTO`: creación de eventos en borrador para su organización.
    - `EDITAR_EVENTO`: modificación de eventos, localidades y envío a revisión.
    - `CANCELAR_EVENTO`: cancelación, suspensión o retiro de eventos.
    - `CHECK_IN`: validación de tiquetes y registro de ingreso a eventos.
  - Si carece de alguno de estos permisos o intenta operar eventos de otra organización, el backend responde con **HTTP 403 Forbidden**.
  - No puede invitar usuarios, modificar permisos ni alterar su propio rol.
- **MODERADOR**:
  - Bandeja de eventos pendientes de revisión (`GET /api/moderaciones/eventos/pendientes`).
  - Aprobación o solicitud de correcciones en eventos (`PATCH .../aprobar`, `PATCH .../solicitar-correccion`).
  - Consulta de eventos administrativos.
- **MARKETING**:
  - Gestión de planes promocionales y comisiones (`/api/marketing/planes`).
  - Consulta de campañas y eventos con promoción pagada (`GET /api/marketing/eventos-promocionados`).
  - Asignación de imagen destacada a eventos con plan promocional confirmado (`POST /api/promociones/eventos/{id}/posicionar`).
- **ADMINISTRADOR**:
  - Invitación y asignación de roles a `MODERADOR` y `MARKETING` vía `/api/invitaciones/roles` y `/api/admin/correos/invitar`.
  - Envío de comunicados oficiales administrativos (`POST /api/admin/correos/enviar`).
  - Revocación de roles y eliminación administrativa de cuentas.
  - Aprobación de organizaciones, validación de RUT y gestión de niveles.
  - Administración de banners del home, categorías y palabras prohibidas.
  - Métricas globales de la plataforma.

---

## 28. Chatbot y Asistente Virtual

### Base: `/api/chatbot`

Módulo del asistente virtual inteligente de EventHive para atención a visitantes y usuarios sobre la cartelera de eventos, compra de boletería y registro de organizadores. Cuenta con integración a Groq (Llama 3.1), resolución directa de eventos publicados en PostgreSQL (Supabase), guardrails para ahorro de tokens y un plan de contingencia ante caídas de red o límites de cuota.

#### `POST /api/chatbot/mensaje`
- **Público**: no requiere token JWT ni autenticación (excluido explícitamente en `JwtAuthFilter` y habilitado con `permitAll()` en `SecurityConfig`).
- Content-Type: `application/json`.
- Recibe: `ChatbotPreguntaRequest` validado con `@NotBlank` y longitud máxima de 350 caracteres para optimizar tokens.
- Devuelve: `ApiResponse<ChatbotRespuestaDTO>`.
- Atributos del objeto devuelto en `data`:
  - `respuesta` (String): texto de respuesta al usuario.
  - `fuente` (String): origen de la resolución (`IA_GROQ`, `LOCAL_RULE`, `LOCAL_GUARDRAIL`, `LOCAL_EVENTOS`, `CONTINGENCIA`).
  - `modoContingencia` (boolean): `true` si la respuesta fue resuelta por el sistema de emergencia local ante saturación o fallos de red; `false` en operación ordinaria.
- Respuesta: HTTP 200 en éxito, HTTP 400 si el mensaje no cumple las validaciones.

##### Ejemplo de solicitud (Request):
```json
{
  "mensaje": "¿Cuáles son los próximos eventos disponibles?"
}
```

##### Ejemplo de respuesta con IA Groq:
```json
{
  "success": true,
  "mensaje": "Respuesta obtenida con éxito",
  "data": {
    "respuesta": "En EventHive puedes explorar una gran variedad de conciertos, festivales y eventos deportivos. Ingresa a la pantalla principal para seleccionar tu localidad y comprar tus entradas de forma segura.",
    "fuente": "IA_GROQ",
    "modoContingencia": false
  }
}
```

##### Ejemplo de respuesta con eventos reales de base de datos (0 tokens consumidos):
```json
{
  "success": true,
  "mensaje": "Respuesta obtenida con éxito",
  "data": {
    "respuesta": "Aquí tienes algunos de los próximos eventos destacados en EventHive:\n• Concierto Rock Fest (2026-11-15 en Estadio El Campín)\n• Festival Gastronómico (2026-11-20 en Plaza Central)\n\nPuedes ver más detalles y comprar tus entradas en la sección principal.",
    "fuente": "LOCAL_EVENTOS",
    "modoContingencia": false
  }
}
```

##### Ejemplo de respuesta interceptada por Guardrail local (0 tokens consumidos):
```json
{
  "success": true,
  "mensaje": "Respuesta obtenida con éxito",
  "data": {
    "respuesta": "Lo siento, soy el asistente virtual exclusivo de EventHive. Solo puedo ayudarte con cartelera de eventos, compra de entradas y cómo publicar eventos.",
    "fuente": "LOCAL_GUARDRAIL",
    "modoContingencia": false
  }
}
```

---

## 29. Variables de entorno y configuración del sistema

Para la operación en producción (por ejemplo en Render) y desarrollo local, se deben definir las siguientes variables de entorno:

| Variable | Descripción | Valor recomendado / Ejemplo |
|---|---|---|
| `GROQ_API_KEY` / `Eventhive-HiveBot` | Clave de API gratuita generada en Groq Cloud | `gsk_...` |
| `GROQ_MODEL` | Identificador del modelo de lenguaje en Groq | `llama-3.1-8b-instant` |
| `GROQ_BASE_URL` | URL base compatible con OpenAI de Groq | `https://api.groq.com/openai/v1` |
| `GROQ_RPM_LIMIT` | Límite preventivo de peticiones por minuto (margen de seguridad) | `25` |
| `MAIL_HOST` | Host del servidor relay SMTP de Brevo / Gmail API | `smtp-relay.brevo.com` |
| `MAIL_PORT` | Puerto SMTP con STARTTLS | `587` |
| `MAIL_USERNAME` | Usuario SMTP (clave de API Brevo o login de relay) | `7a1b2c...@smtp-brevo.com` |
| `MAIL_PASSWORD` | Contraseña SMTP (Master SMTP Key de Brevo) | `xsmtpsib-...` |
| `MAIL_FROM` | Remitente verificado en la consola de correos | `eventhiveContacto@gmail.com` |
| `MAIL_FROM_NAME` | Nombre visible del remitente en los correos | `EventHive` |
| `MAIL_MAX_REINTENTOS` | Número de intentos automáticos ante fallos de conexión | `2` |
| `FRONTEND_URL` | URL base del frontend para enlaces de invitación | `https://eventhive-ruby-zeta.vercel.app` |
| `DB_URL` | URL de conexión JDBC a PostgreSQL (Supabase Session Pooler) | `jdbc:postgresql://...` |
| `DB_USERNAME` | Usuario de base de datos PostgreSQL | `postgres.[id_proyecto]` |
| `DB_PASSWORD` | Contraseña de base de datos PostgreSQL | `...` |
| `JWT_SECRET` | Clave secreta para firma HMAC de tokens JWT | `64+ caracteres aleatorios` |
| `SUPABASE_URL` | URL del proyecto Supabase Storage | `https://[ref].supabase.co` |
| `SUPABASE_SECRET_KEY` | Llave de servicio de Supabase | `...` |
| `RECOMMENDATION_SERVICE_URL` | URL base del microservicio FastAPI de recomendaciones | `http://localhost:8001` o `https://api-predictive.render.com` |
| `RECOMMENDATION_SERVICE_TIMEOUT_CONNECT_MS` | Timeout de conexión HTTP hacia el servicio Python (ms) | `3000` |
| `RECOMMENDATION_SERVICE_TIMEOUT_READ_MS` | Timeout de lectura/respuesta HTTP hacia el servicio Python (ms) | `5000` |
| `RECOMMENDATION_SERVICE_TOKEN` | Token Bearer opcional para autenticación inter-servicio | `sec_token_...` |

---

## 30. Arquitectura de Caché en Memoria (Caffeine Cache)

El backend de EventHive cuenta con una capa de aceleración en memoria RAM utilizando el motor nativo de **Spring Boot Cache** potenciado por **Caffeine Cache**. No requiere servicios externos (como Redis) y reduce el tiempo de respuesta de las consultas frecuentes a **menos de 2 milisegundos**.

### 30.1. Flujo de datos y desvío rápido
1. **Petición del cliente**: El frontend consulta un endpoint público (por ejemplo, listado de eventos, categorías, banners o mapa).
2. **Revisión en RAM**: Spring Boot intercepta la llamada con `@Cacheable`. Si los datos ya se encuentran en memoria, se devuelven al instante sin realizar consultas a PostgreSQL ni a Supabase Storage.
3. **Carga en frío**: Si no están en caché, se consultan en la base de datos o almacenamiento, se almacenan en la memoria RAM con su respectivo tiempo de expiración y se entregan al cliente.

### 30.2. Manejo de URLs de Supabase Storage (Imágenes públicas vs. Documentos privados)
- **Buckets Públicos (`banners-home`, `categorias-images`, `eventos-images`)**:
  - Las URLs son permanentes y no caducan.
  - Tienen TTLs prolongados en memoria sin riesgo de enlaces caídos.
- **Bucket Privado (`verificacion-docs` para RUTs de Organizaciones)**:
  - Utiliza **URLs firmadas temporales** generadas por Supabase Storage con vigencia de **60 minutos** (3600 segundos).
  - El caché `rutFirmado` tiene un TTL estricto de **50 minutos** (`expireAfterWrite(50, TimeUnit.MINUTES)`).
  - Al expirar **10 minutos antes** de que la firma venza en Supabase, la plataforma regenera automáticamente una URL firmada fresca, eliminando cualquier riesgo de enlaces rotos para los revisores.

### 30.3. Tabla de Cachés y Tiempos de Vida (TTL)

| Nombre de Caché | Endpoints asociados | TTL (Tiempo de expiración) | Capacidad Máxima |
|---|---|---|---|
| `banners` | `GET /api/banners-home`<br>`GET /api/banners-home/admin` | 24 horas | 50 entradas |
| `categorias` | `GET /api/categorias/{id}`<br>`GET /api/categorias/nombres`<br>`GET /api/categorias/top4`<br>`GET /api/categorias/con-eventos` | 24 horas | 100 entradas |
| `eventosPublicos` | `GET /api/eventos`<br>`GET /api/eventos/proximos`<br>`GET /api/eventos/categoria/{id}` | 30 minutos | 500 entradas |
| `eventosCarrusel` | `GET /api/eventos/carrusel` | 30 minutos | 50 entradas |
| `eventosDestacados`| `GET /api/eventos/destacados` | 30 minutos | 100 entradas |
| `primerDestacado` | `GET /api/eventos/primer-destacado` | 15 minutos | 20 entradas |
| `eventosMapa` | `GET /api/eventos/mapa` | 15 minutos | 200 entradas |
| `rutFirmado` | `SupabaseStorageService.generarUrlFirmada` | 50 minutos | 200 entradas |

### 30.4. Desalojo Reactivo Inmediato (`@CacheEvict`)
Aunque las consultas se sirvan desde la memoria RAM, **si ocurre cualquier cambio en los datos, el caché se purga de inmediato** para que la siguiente consulta cargue la información actualizada:

- **Eventos (`crear`, `actualizar`, `aprobar`, `solicitar corrección`, `rechazar`, `suspender`, `cancelar`, `finalizar`, `eliminar`)**:
  - Invalida simultáneamente los cachés `eventosPublicos`, `eventosCarrusel`, `eventosDestacados`, `primerDestacado`, `eventosMapa` y `categorias` (para refrescar el conteo de eventos por categoría).
  - Un nuevo evento publicado aparece al instante a todos los usuarios.
- **Categorías y Banners (`crear`, `actualizar`, `eliminar`)**:
  - Desalojan inmediatamente su caché respectivo.
- **Documentos de Verificación RUT**:
  - Al reenviar o subir un nuevo RUT diferido, se purga de inmediato el caché de la URL firmada para emitir la nueva referencia.

---

## 31. Monitoreo de Salud y Keep-Alive

### Base: `/api/health` y `/health`

Endpoints ultraligeros de sondeo de estado operativo, diseñados para consumir 0 memoria RAM y no realizar consultas a la base de datos ni procesamiento de seguridad JWT.

#### `GET /api/health` o `GET /health`
- **Público**: libre acceso (excluido de `JwtAuthFilter` y configurado con `permitAll()` en `SecurityConfig`).
- Devuelve: `{"status":"UP"}` con Content-Type `application/json` y código HTTP 200 OK.
- **Keep-Alive automático**: Tarea programada cada 13 minutos (`@Scheduled(fixedRate = 780000)`) que efectúa un ping HTTP ligero al servicio (usando `RENDER_EXTERNAL_URL` o `http://localhost:PORT/api/health`), evitando que instancias gratuitas en plataformas en la nube (Render, Koyeb) entren en suspensión por inactividad.

---

## 32. Sistema de Recomendaciones Predictivas y Notificaciones de Afinidad

### Base: `/api/recommendations` (alias `/api/recomendaciones`)

El sistema de recomendaciones personalizadas de EventHive integra el backend Spring Boot con un microservicio predictivo desarrollado en **Python FastAPI** (`eventhive_predictive_python`). El sistema opera bajo un esquema híbrido de consulta bajo demanda y notificaciones reactivas de alta afinidad por correo electrónico.

#### `GET /api/recommendations` o `GET /api/recomendaciones`
- **Roles autorizados**: Autenticado (`CLIENTE`, `REPRESENTANTE`, `OPERADOR`, `MODERADOR`, `MARKETING`, `ADMINISTRADOR`).
- **Parámetros**:
  - `limit` (query param, entero opcional, por defecto `10`): cantidad máxima de eventos recomendados a devolver.
- **Descripción del flujo**:
  1. Identifica al usuario autenticado en sesión.
  2. Consulta sus preferencias y afinidades históricas por categoría (eventos favoritos y compras confirmadas).
  3. Solicita al microservicio predictivo la puntuación y ordenamiento de eventos activos recomendados para el perfil.
  4. **Fallback resiliente**: Si el microservicio Python se encuentra fuera de línea, agota los timeouts configurados (3 segundos de conexión, 5 segundos de lectura) o el usuario es nuevo sin interacciones, el backend ejecuta un fallback transparente devolviendo los eventos públicos más populares y con mejor valoración sin interrumpir la experiencia del usuario.
- **Devuelve**: `ApiResponse<List<EventoDTO>>`
- **Ejemplo de respuesta**:

```json
{
  "success": true,
  "mensaje": "Recomendaciones obtenidas",
  "data": [
    {
      "id": 15,
      "nombre": "Festival Musical de Verano 2026",
      "descripcion": "El encuentro musical independiente más grande de la región.",
      "fecha": "2026-12-15T18:00:00",
      "lugar": "Parque Metropolitano",
      "ciudad": "Bogotá",
      "direccion": "Calle 63 # 45-10",
      "categoriaId": 3,
      "categoriaNombre": "Música",
      "organizacionId": 5,
      "organizacionNombre": "Festivales Viva",
      "urlPortada": "https://supabase.co/storage/v1/object/public/eventos/festival2026.jpg",
      "precioMinimo": 45000.0,
      "precioMaximo": 120000.0,
      "estado": "PUBLICADO",
      "puntuacionMedia": 4.9,
      "totalValoraciones": 32
    }
  ]
}
```

#### Flujo Reactivo de Notificación por Publicación (`EventoPublicadoEvent`)
Al publicar un evento (transición al estado `PUBLICADO`), el sistema ejecuta de forma automática y asíncrona un proceso de segmentación y notificación:
1. `ServiceEvento` dispara el evento de dominio Spring `EventoPublicadoEvent`.
2. `ServicioRecomendacion` captura el evento en segundo plano mediante `@Async` y `@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)`.
3. Se recopila el universo de candidatos activos con historial en la categoría del evento.
4. Se envían los candidatos al microservicio Python (`POST /api/v1/recommendations/evaluate`).
5. Se seleccionan hasta **15 usuarios con el mayor nivel de afinidad**.
6. **Deduplicación atómica**: Cada recomendación se registra en la tabla `recomendacion_envios` (`RecomendacionEnvio`) vinculando `evento_id` y `usuario_id` con constraint `UNIQUE`. Si el usuario ya fue notificado previamente para ese evento, el sistema omite el envío.
7. Se despachan los correos personalizados de recomendación vía Gmail API (`ServiceCorreo.enviarRecomendacionEvento`).

---

## 33. Guía de Flujos Complejos y de Mayor Importancia

Esta sección detalla cómo utilizar los endpoints de EventHive en los procesos neurálgicos de la plataforma, acompañados de diagramas de secuencia, reglas de negocio y consideraciones técnicas.

---

### Flujo 1: Registro, Verificación de RUT y Aprobación de Organizaciones

El proceso de verificación garantiza que las organizaciones sean entidades legales válidas antes de permitirles publicar eventos masivos. Contempla tanto el registro estándar diferido como la importación acelerada de datos con RUT precargado.

```mermaid
sequenceDiagram
    autonumber
    actor Rep as Representante Legal
    actor Admin as Administrador
    participant Auth as Auth / Verificación Controller
    participant DB as PostgreSQL (Supabase)
    participant Storage as Supabase Storage

    alt Escenario A: Organización con RUT precargado en DB
        Rep->>Auth: Inicia sesión / Consulta estado
        Auth->>DB: Verifica Organizacion.urlRut != null
        Auth-->>Rep: Estado APROBADA (RUT ya validado)
    else Escenario B: Registro diferido estándar
        Rep->>Auth: POST /api/auth/registro-organizador
        Auth->>DB: Crea Usuario (REPRESENTANTE) + Organizacion (PENDIENTE_REVISION)
        Auth-->>Rep: Cuenta creada (sin exigir RUT inmediato)
        Rep->>Storage: Carga PDF de RUT
        Rep->>Auth: PATCH /api/verificacion/{solicitudId}/subir-rut (multipart/form-data)
        Auth->>DB: Guarda urlRut en SolicitudVerificacion (estado PENDIENTE)
        Auth-->>Rep: Solicitud en cola de revisión
        
        Admin->>Auth: GET /api/verificacion/pendientes
        Auth->>DB: Consulta solicitudes con estado PENDIENTE
        Auth-->>Admin: Lista de solicitudes con datos de empresa y urlRut
        
        Admin->>Auth: GET /api/verificacion/{solicitudId}/rut-url
        Auth->>Storage: Genera enlace firmado temporal (50 min)
        Auth-->>Admin: { url: "https://...supabase.co/.../sign/rut.pdf", expiresInSeconds: 3000 }
        
        alt Aprobación
            Admin->>Auth: PUT /api/verificacion/{solicitudId}/aprobar
            Auth->>DB: @Transactional: 1) Solicitud -> ACEPTADA<br/>2) Copia urlRut a Organizacion<br/>3) Organizacion -> APROBADA
            Auth-->>Admin: Organización verificada
        else Solicitud de Corrección
            Admin->>Auth: PATCH /api/verificacion/{solicitudId}/solicitar-correccion?motivo=...
            Auth->>DB: Solicitud -> EN_CORRECCION
            Auth-->>Admin: Solicitud devuelta para corrección
            Rep->>Auth: PATCH /api/verificacion/{solicitudId}/reenviar
        else Rechazo Definitivo
            Admin->>Auth: PUT /api/verificacion/{solicitudId}/rechazar?motivo=...
            Auth->>DB: Solicitud -> RECHAZADA (No transfiere RUT a Organizacion)
            Auth-->>Admin: Solicitud rechazada
        end
    end
```

#### Reglas de Negocio Clave del Flujo de RUT:
1. **Prioridad de RUT precargado**: Si la entidad `Organizacion` ya contiene un valor en su columna `url_rut`, el backend la considera de inmediato como `APROBADA`. No se le vuelve a exigir el documento ni se duplican solicitudes.
2. **Fuente de auditoría para el Administrador**: Al auditar solicitudes en revisión, el Administrador debe consumir el documento desde `GET /api/verificacion/{solicitudId}/rut-url` (entidad `SolicitudVerificacion`), **nunca** directamente desde `Organizacion`.
3. **Transaccionalidad en la aprobación**: La aprobación (`PUT /api/verificacion/{solicitudId}/aprobar`) se ejecuta en una sola transacción atómica:
   - Marca la solicitud como `ACEPTADA`.
   - Transfiere la `urlRut` desde la solicitud a la entidad `Organizacion`.
   - Modifica el estado de la organización a `APROBADA`.
   - Invalida los cachés correspondientes.
4. **Rechazo seguro**: Un rechazo (`PUT /api/verificacion/{solicitudId}/rechazar`) cambia el estado de la solicitud pero **no** asigna el RUT ni aprueba a la organización.

---

### Flujo 2: Sistema de Invitaciones y Roles en Organizaciones

Permite a los Representantes sumar Operadores a su organización y a los Administradores incorporar Moderadores o miembros de Marketing, con validación criptográfica y auto-limpieza.

```mermaid
sequenceDiagram
    autonumber
    actor Inviter as Administrador / Representante
    actor Dest as Usuario Invitado
    participant API as InvitacionRolApiController
    participant Service as ServiceInvitacionRol
    participant Mail as CorreoSender (Gmail API)
    participant DB as PostgreSQL

    Inviter->>API: POST /api/invitaciones/roles { correo, rol }
    API->>Service: invitar(correo, rol)
    Note over Service: Valida permisos:<br/>Admin -> MODERADOR / MARKETING<br/>Representante -> OPERADOR (su org)
    Service->>DB: Persiste InvitacionRol con RolDestino (Entidad Rol)<br/>Genera Token SHA-256 (32 bytes) y fechaEnvio = now()
    Service->>Mail: enviarInvitacionRol(correo, rol, token)
    Mail-->>Service: Envío exitoso
    Service-->>API: 201 Created
    API-->>Inviter: Invitación enviada

    Note over API,DB: Consulta de invitaciones enviadas:<br/>GET /api/invitaciones/roles/enviadas<br/>Solo retorna estados PENDIENTE o EXPIRADA

    alt Caso: Invitación vencida (> 24 horas)
        Inviter->>API: POST /api/invitaciones/roles/{id}/reenviar
        API->>Service: reenviar(id)
        Note over Service: Verifica estado == EXPIRADA.<br/>Si está PENDIENTE -> Lanza 400 Bad Request
        Service->>DB: Actualiza estado a PENDIENTE, nuevo token, fechaEnvio = now()
        Service->>Mail: Reenvía correo con nuevo enlace
        Service-->>Inviter: 200 OK (Invitación reenviada)
    end

    alt Caso: Eliminación manual de invitación
        Inviter->>API: DELETE /api/invitaciones/roles/{id}
        API->>Service: eliminar(id)
        Service->>DB: Remueve registro de InvitacionRol
        Service-->>Inviter: 200 OK (Invitación eliminada)
    end

    alt Caso: Aceptación de la invitación
        Dest->>API: GET /api/invitaciones/roles/validar?token=...
        API->>Service: validar(token)
        Service-->>Dest: { correo, rol, fechaExpiracion, estado: "PENDIENTE" }

        Dest->>API: POST /api/invitaciones/roles/aceptar { token, nombre, clave, telefono }
        API->>Service: aceptar(request)
        Note over Service: @Transactional:<br/>1) Asigna Rol y Organización al usuario<br/>2) Elimina automáticamente la entidad InvitacionRol
        Service->>DB: invitaciones.delete(invitacion)
        Service-->>Dest: 201 Created (Invitación aceptada y procesada)
    end
```

#### Reglas de Negocio Clave del Sistema de Invitaciones:
1. **Entidad Rol obligatoria**: El rol destino se persiste como relación `@ManyToOne Rol rolDestino`, impidiendo el uso de strings libres propensos a errores tipográficos.
2. **Listado depurado**: `GET /api/invitaciones/roles/enviadas` únicamente devuelve invitaciones en estado `PENDIENTE` o `EXPIRADA`.
3. **Reenvío condicional estricto**: `POST /api/invitaciones/roles/{id}/reenviar` rechaza llamadas si la invitación todavía se encuentra en estado `PENDIENTE`. Solo procede si `isExpirada()` es verdadero.
4. **Auto-eliminación tras aceptación**: Cuando el invitado completa el registro o vinculación mediante `POST /api/invitaciones/roles/aceptar`, la invitación se elimina físicamente de la base de datos dentro de la misma transacción para evitar duplicados o registros residuales.
5. **Sin campo `fechaRechazo`**: El campo y columna `fecha_rechazo` ha sido eliminado por completo del modelo.

---

### Flujo 3: Ciclo de Vida, Moderación y Publicación de Eventos

Controla la creación de eventos, su revisión humana o automática y su posterior publicación global.

```mermaid
stateDiagram-v2
    [*] --> BORRADOR: Guardar borrador inicial
    BORRADOR --> PENDIENTE_REVISION: Solicitar publicación
    
    state Moderacion {
        PENDIENTE_REVISION --> EN_CORRECCION: Moderador solicita corrección
        EN_CORRECCION --> PENDIENTE_REVISION: Organizador actualiza datos
        PENDIENTE_REVISION --> RECHAZADO: Contenido viola políticas
        PENDIENTE_REVISION --> PUBLICADO: Aprobación humana o automática
    }

    state Publicado {
        PUBLICADO --> [*]: Desalojo reactivo de caché (@CacheEvict)
        PUBLICADO --> DisparoRecomendaciones: EventoPublicadoEvent
    }

    PUBLICADO --> FINALIZADO: Fecha de evento concluida
    PUBLICADO --> CANCELADO: Cancelación justificada
```

#### Pasos para Publicar un Evento:
1. **Creación**: El representante o un operador con permiso `CREAR_EVENTO` crea el evento en `BORRADOR` mediante `POST /api/eventos`.
2. **Carga de localidades y tiquetes**: Se configuran las zonas de admisión en `POST /api/localidades`.
3. **Solicitud de revisión**: Se invoca `POST /api/eventos/{id}/solicitar-revision`, pasando el estado a `PENDIENTE_REVISION`.
4. **Moderación**:
   - El sistema ejecuta un primer filtrado de palabras prohibidas con `ServiceModeracionAutomatica`.
   - Los moderadores consultan `GET /api/moderaciones/eventos/pendientes`.
   - Pueden aprobar (`PATCH /api/moderaciones/eventos/{id}/aprobar`) o requerir cambios (`PATCH /api/moderaciones/eventos/{id}/solicitar-correccion?motivo=...`).
5. **Publicación y Efectos Secundarios**:
   - Al pasar a `PUBLICADO`, Spring desaloja de inmediato los cachés en memoria de eventos destacados, carrusel y categorías.
   - Se emite de inmediato un `EventoPublicadoEvent` que despierta al motor de recomendaciones.

---

### Flujo 4: Motor de Recomendaciones Predictivas e Integración Híbrida Java-Python

Orquesta la comunicación síncrona y asíncrona entre el backend en Spring Boot y el microservicio predictivo en Python FastAPI.

```mermaid
sequenceDiagram
    autonumber
    participant Evento as ServiceEvento
    participant Rec as ServicioRecomendacion
    participant Client as ClientePythonRecomendacion
    participant Python as Microservicio FastAPI (Python)
    participant DB as PostgreSQL (recomendacion_envios)
    participant Mail as CorreoSender (Gmail API)

    Evento->>Rec: EventoPublicadoEvent (Asíncrono, post-commit)
    Note over Rec: Recopila usuarios activos con interés<br/>en la categoría del evento
    Rec->>Client: evaluarCandidatos(evento, candidatos)
    Client->>Python: POST /api/v1/recommendations/evaluate<br/>(Timeout: 3s connect, 5s read)
    
    alt Servicio Python responde exitosamente
        Python-->>Client: { recomendaciones: [ { usuarioId, puntuacion, afinidad } ] }
        Client-->>Rec: EvaluacionRecomendacionResponse
        Note over Rec: Ordena por afinidad y selecciona<br/>hasta 15 usuarios prioritarios
        loop Por cada usuario seleccionado
            Rec->>DB: Verifica y registra en recomendacion_envios (UNIQUE: evento_id, usuario_id)
            alt No notificado previamente
                Rec->>Mail: enviarRecomendacionEvento(usuario.correo, evento)
                Mail-->>Rec: Correo enviado
                Rec->>DB: Actualiza estado = ENVIADO
            else Ya notificado
                Note over Rec: Omite envío duplicado
            end
        end
    else Timeout o Caída del Microservicio Python
        Client-->>Rec: Fallback vacío / Manejo de excepción seguro
        Note over Rec: Registra warning sin lanzar error.<br/>La publicación del evento NO se interrumpe.
    end
```

#### Contrato de Comunicación con el Microservicio Python:
- **Endpoint**: `POST /api/v1/recommendations/evaluate`
- **Request Body**:
  ```json
  {
    "evento": {
      "id": 15,
      "categoriaId": 3,
      "categoriaNombre": "Música"
    },
    "candidatos": [
      {
        "usuarioId": 42,
        "favoritosCategoria": 8,
        "comprasCategoria": 3,
        "entradasCompradas": 7
      }
    ]
  }
  ```
- **Response Body**:
  ```json
  {
    "recomendaciones": [
      {
        "usuarioId": 42,
        "puntuacion": 0.89,
        "afinidad": "ALTA"
      }
    ]
  }
  ```

---

### Flujo 5: Gestión Flexible y Defensiva de Archivos Multimedia en Supabase Storage

EventHive acepta y gestiona referencias de imágenes provistas por diferentes vías: subidas desde el frontend, URLs directas de Supabase Storage o imágenes externas ingresadas manualmente en scripts de poblamiento (Unsplash, CDNs, URLs relativas).

```mermaid
flowchart TD
    A[Operación: Actualizar o Eliminar Imagen] --> B{¿URL es nula o vacía?}
    B -- Sí --> C[No ejecutar ninguna acción sobre Storage]
    B -- No --> D{extraerRutaEnBucket}
    
    D --> E{¿Pertenece al Storage de Supabase?}
    E -- No (ej: Unsplash, placeholder) --> F[Ignorar borrado físico de Storage<br/>Actualizar solo base de datos]
    E -- Sí --> G[Extraer ruta relativa limpia del objeto]
    
    G --> H[Llamada defensiva a SupabaseStorageService.eliminarImagen]
    H --> I{¿Respuesta de Storage?}
    I -- Éxito --> J[Archivo eliminado físicamente]
    I -- Error / 404 / Timeout --> K[Capturar Throwable en bloque try-catch<br/>Registrar warn en logs]
    
    J --> L[Completar transacción de Base de Datos]
    K --> L[Completar transacción de Base de Datos sin fallar]
    F --> L
    C --> L
```

#### Buenas Prácticas para el Manejo de Archivos:
1. **Nunca asumir formato fijo**: No asumir que todas las imágenes contienen el subdominio de Supabase o la estructura `/object/public/`.
2. **Prioridad a la consistencia de datos**: Si un archivo previo no puede identificarse o eliminarse físicamente en el storage, **la transacción de base de datos nunca debe cancelarse ni arrojar HTTP 500**.
3. **Imágenes por defecto**: Las entidades `Evento`, `Organizacion`, `Usuario`, `Categoria` y `Banner` aceptan URLs externas como portadas o logos de prueba sin provocar errores al ser reemplazadas o eliminadas.


