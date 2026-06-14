# Especificación Técnica: Análisis de Carrera mediante Detección de Articulaciones

**Versión:** 1.1  
**Fecha:** Junio 2026

---

## Tabla de Contenidos

1. [Descripción General](#1-descripción-general)
2. [Alcance del Proyecto](#2-alcance-del-proyecto)
3. [Requisitos Funcionales](#3-requisitos-funcionales)
4. [Requisitos No Funcionales](#4-requisitos-no-funcionales)
5. [Arquitectura del Sistema](#5-arquitectura-del-sistema)
6. [Tecnologías Propuestas](#6-tecnologías-propuestas)
7. [Flujo de Procesamiento](#7-flujo-de-procesamiento)
8. [API REST — Endpoints](#8-api-rest--endpoints)
9. [Estructura de Datos](#9-estructura-de-datos)
10. [Gestión de Estados y Errores](#10-gestión-de-estados-y-errores)
11. [Interfaz de Usuario](#11-interfaz-de-usuario)
12. [Criterios de Aceptación](#12-criterios-de-aceptación)
13. [Mejoras Futuras](#13-mejoras-futuras)
14. [Entregables](#14-entregables)

---

## 1. Descripción General

### Objetivo

Desarrollar una aplicación web local que permita al usuario cargar un video de una persona corriendo, detectar automáticamente las articulaciones corporales mediante visión por computadora, y generar un nuevo video con el esqueleto biomecánico superpuesto sobre el original.

El sistema debe permitir visualizar:

- El video original.
- El video procesado con el esqueleto superpuesto.
- Comparación lado a lado de ambos videos.

### Contexto de Despliegue

| Atributo         | Valor                                         |
|------------------|-----------------------------------------------|
| Tipo             | Aplicación de escritorio local (localhost)    |
| Usuarios         | Un único usuario                              |
| Entorno          | Computadora personal (Windows / macOS / Linux)|
| Acceso           | Navegador web apuntando a `localhost`         |
| Concurrencia     | Un procesamiento a la vez                     |

> La app **no está pensada para ser desplegada en internet**. Corre enteramente en la máquina del usuario.

---

## 2. Alcance del Proyecto

### 2.1 Funcionalidades Incluidas

#### Carga de Video

- Seleccionar un archivo de video desde el dispositivo.
- Arrastrar y soltar archivos (Drag & Drop).
- Visualizar información básica del video: nombre, duración, resolución y tamaño.

#### Procesamiento de Video

1. Extraer los fotogramas del video.
2. Detectar la persona presente en cada fotograma.
3. Detectar los puntos articulares (landmarks).
4. Dibujar el esqueleto biomecánico frame a frame.
5. Generar un nuevo video con las articulaciones superpuestas.
6. Mantener el resultado disponible durante la sesión activa.

#### Visualización

- Reproducir el video original.
- Reproducir el video procesado.
- Comparar ambos videos en pantalla dividida.

#### Exportación

- Descargar el video procesado en formato `.mp4`.
- Descargar una imagen de un fotograma específico *(opcional)*.

---

## 3. Requisitos Funcionales

### RF-01: Carga de Video

El sistema debe permitir cargar archivos en los siguientes formatos:

| Formato   | Extensión |
|-----------|-----------|
| MPEG-4    | `.mp4`    |
| QuickTime | `.mov`    |
| AVI       | `.avi`    |

**Tamaño máximo:** 500 MB

### RF-02: Validación

El sistema debe validar antes de procesar:

- Formato de archivo permitido.
- Que el tamaño no supere el máximo.
- Que el archivo no esté corrupto (verificación de cabecera).

### RF-03: Detección de Pose

El sistema detecta automáticamente los puntos corporales usando MediaPipe Pose Landmarker.

Un landmark se considera **válido** cuando su campo `visibility` es mayor a `0.5`.

**33 landmarks objetivo:**

| Zona    | Puntos                                      |
|---------|---------------------------------------------|
| Cabeza  | Nariz, ojos, orejas                         |
| Tronco  | Hombros, caderas                            |
| Brazos  | Codos, muñecas                              |
| Piernas | Rodillas, tobillos, talones, dedos del pie  |

### RF-04: Generación del Esqueleto

El sistema debe:

- Conectar los landmarks mediante segmentos (bones).
- Dibujar el esqueleto sobre la imagen de cada frame.
- Mantener la posición relativa correcta entre articulaciones.
- Ignorar landmarks con `visibility < 0.5` sin interrumpir el procesamiento.

### RF-05: Generación de Video

El sistema debe crear un nuevo archivo `.mp4` que contenga:

- Cada frame del video original con el esqueleto superpuesto.
- El mismo FPS que el video original.
- La misma duración que el video original.

### RF-06: Visualización del Resultado

| Modo   | Descripción                           | MVP |
|--------|---------------------------------------|-----|
| Modo 1 | Video original                        | Sí  |
| Modo 2 | Video con esqueleto                   | Sí  |
| Modo 3 | Pantalla dividida (original/procesado)| No  |

> El Modo 3 queda diferido a Fase 2.

### RF-07: Descarga

El sistema debe permitir descargar el video procesado como `.mp4` mediante el navegador (descarga directa).

---

## 4. Requisitos No Funcionales

### RNF-01: Rendimiento

**Hardware objetivo (baseline):**

| Componente | Especificación mínima                        |
|------------|----------------------------------------------|
| CPU        | Intel Core i5 8va gen / AMD Ryzen 5 3000+    |
| RAM        | 8 GB                                         |
| GPU        | No requerida (CPU-only como baseline)        |
| Almacenamiento | 1 GB libre para archivos temporales      |

**Tiempo máximo de procesamiento en el hardware baseline:**

| Duración del video | Tiempo máximo |
|--------------------|---------------|
| 30 segundos        | 60 segundos   |
| 60 segundos        | 2 minutos     |
| 5 minutos          | 10 minutos    |

> Si el hardware disponible tiene GPU NVIDIA, se puede activar aceleración por CUDA en MediaPipe/OpenCV para reducir los tiempos a la mitad o menos.

### RNF-02: Precisión

La detección debe alcanzar una precisión mínima del **85% de landmarks válidos** por frame, entendiendo por válido un landmark con `visibility ≥ 0.5` correctamente posicionado.

### RNF-03: Compatibilidad

**Navegadores soportados (desktop únicamente):**

- Google Chrome (versión 110+)
- Microsoft Edge (versión 110+)
- Mozilla Firefox (versión 110+)

> La aplicación no requiere soporte móvil.

### RNF-04: Gestión de Archivos

Dado que la app es local y de un solo usuario:

- Los archivos temporales se almacenan en la carpeta `./tmp/jobs/` del backend.
- El video procesado **permanece disponible** durante toda la sesión activa (mientras el backend esté corriendo).
- Al iniciar el backend, la carpeta `./tmp/jobs/` se limpia automáticamente (archivos de sesiones anteriores).
- No se requiere HTTPS: la comunicación es sobre `localhost`.

### RNF-05: Simplicidad de Arquitectura

La arquitectura prioriza simplicidad sobre escalabilidad:

- Un único proceso de backend atiende un único usuario.
- No hay base de datos: el estado del job se mantiene en memoria durante la sesión.
- No hay autenticación ni autorización.
- Preparada para agregar aceleración GPU en el futuro sin cambiar la interfaz.

---

## 5. Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│              Navegador (localhost)           │
│         React + TypeScript + Tailwind       │
│                                             │
│  Comunicación de progreso: SSE              │
│  Comunicación de datos: HTTP REST           │
└─────────────────┬───────────────────────────┘
                  │ HTTP (localhost)
┌─────────────────▼───────────────────────────┐
│           FastAPI (localhost:8000)           │
│                                             │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Upload &     │  │  Job Manager         │ │
│  │ Validation   │  │  (estado en memoria) │ │
│  └──────────────┘  └──────────────────────┘ │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │         Pipeline de Procesamiento    │   │
│  │                                      │   │
│  │  OpenCV (frames) → MediaPipe (pose)  │   │
│  │       → OpenCV (dibujo) → FFmpeg     │   │
│  └──────────────────────┬───────────────┘   │
└─────────────────────────┼───────────────────┘
                          │
              ┌───────────▼──────────┐
              │   ./tmp/jobs/{id}/   │
              │   input.mp4          │
              │   output.mp4         │
              └──────────────────────┘
```

---

## 6. Tecnologías Propuestas

| Capa                | Tecnología                         |
|---------------------|------------------------------------|
| Frontend            | React 18, TypeScript, Tailwind CSS |
| Backend             | Python 3.11+, FastAPI              |
| Detección de Pose   | MediaPipe Pose Landmarker          |
| Procesamiento Video | OpenCV 4.x                         |
| Ensamblado Video    | FFmpeg (via subprocess)            |
| Progreso en tiempo real | Server-Sent Events (SSE)       |

### Por qué SSE y no WebSockets

Para este caso de uso (un único canal de progreso unidireccional servidor → cliente), SSE es suficiente y más simple de implementar que WebSockets. FastAPI tiene soporte nativo con `StreamingResponse`.

### Alternativas futuras para detección de pose

- YOLO Pose (mejor para múltiples personas)
- MoveNet (más liviano, menor precisión)
- RTMPose (alta precisión, requiere más recursos)

---

## 7. Flujo de Procesamiento

```
[1] Usuario selecciona video
        │
        ▼
[2] Frontend valida formato y tamaño
        │  Si inválido → muestra error, fin
        ▼
[3] POST /api/upload → Backend recibe archivo
        │  Guarda en ./tmp/jobs/{job_id}/input.mp4
        │  Retorna job_id
        ▼
[4] Frontend abre stream SSE: GET /api/jobs/{job_id}/events
        │  (mantiene conexión abierta para recibir progreso)
        ▼
[5] Backend procesa en background thread
        │
        ├── Extraer frames con OpenCV
        │     → SSE: {stage: "extracting", percent: 0-20}
        │
        ├── Detectar landmarks con MediaPipe (frame a frame)
        │     → SSE: {stage: "detecting", percent: 20-80}
        │
        ├── Dibujar esqueleto sobre cada frame
        │     → SSE: {stage: "drawing", percent: 80-90}
        │
        └── Ensamblar video con FFmpeg
              → SSE: {stage: "encoding", percent: 90-100}
        │
        ▼
[6] SSE: {event: "completed", job_id: "abc123"}
        │
        ▼
[7] Frontend habilita reproductor y botón de descarga
        │
        ▼
[8] Usuario descarga → GET /api/jobs/{job_id}/download
        │
        ▼
[9] Archivo permanece en ./tmp/ hasta que el backend se reinicie
```

---

## 8. API REST — Endpoints

### Base URL

```
http://localhost:8000/api
```

### Endpoints

#### `POST /api/upload`

Recibe el archivo de video y crea un nuevo job de procesamiento.

**Request:** `multipart/form-data`

| Campo | Tipo   | Descripción           |
|-------|--------|-----------------------|
| file  | File   | Archivo de video      |

**Response `202 Accepted`:**

```json
{
  "job_id": "abc123",
  "status": "processing",
  "filename": "carrera.mp4",
  "duration": 24.6,
  "fps": 30,
  "resolution": "1920x1080",
  "size_mb": 45.2
}
```

**Errores:**

| Código | Causa                        |
|--------|------------------------------|
| 400    | Formato no permitido         |
| 413    | Archivo supera 500 MB        |
| 422    | Archivo corrupto o inválido  |

---

#### `GET /api/jobs/{job_id}/events`

Stream SSE con el progreso del procesamiento. El cliente mantiene esta conexión abierta hasta recibir `completed` o `error`.

**Eventos:**

```
event: progress
data: {"stage": "detecting", "percent": 45, "frames_done": 332, "frames_total": 738}

event: completed
data: {"job_id": "abc123"}

event: error
data: {"message": "No se detectó ninguna persona en el video."}
```

---

#### `GET /api/jobs/{job_id}/video`

Streaming del video procesado para reproducción en el navegador.

Soporta el header `Range` para que el `<video>` de HTML pueda hacer seek.

**Response:** `video/mp4` con soporte de `206 Partial Content`.

---

#### `GET /api/jobs/{job_id}/download`

Descarga del video procesado como archivo adjunto.

**Response:** `video/mp4` con header `Content-Disposition: attachment`.

---

#### `GET /api/jobs/{job_id}/status`

Retorna el estado actual del job (útil si se pierde la conexión SSE).

**Response `200 OK`:**

```json
{
  "job_id": "abc123",
  "status": "processing",
  "stage": "detecting",
  "percent": 45
}
```

---

#### `DELETE /api/jobs/{job_id}`

Cancela el procesamiento en curso (si aplica) y elimina los archivos del job.

**Response `204 No Content`**

---

## 9. Estructura de Datos

### Landmark

```json
{
  "id": 11,
  "name": "left_shoulder",
  "x": 0.42,
  "y": 0.31,
  "z": -0.12,
  "visibility": 0.98
}
```

> Solo se dibujan landmarks con `visibility ≥ 0.5`.

### Evento de Progreso (SSE payload)

```json
{
  "stage": "detecting",
  "percent": 45,
  "frames_done": 332,
  "frames_total": 738,
  "elapsed_seconds": 14.2
}
```

### Estado del Job (en memoria, backend)

```json
{
  "job_id": "abc123",
  "status": "processing",
  "stage": "detecting",
  "percent": 45,
  "input_path": "./tmp/jobs/abc123/input.mp4",
  "output_path": "./tmp/jobs/abc123/output.mp4",
  "metadata": {
    "duration": 24.6,
    "fps": 30,
    "frames_total": 738,
    "resolution": "1920x1080"
  },
  "error": null
}
```

---

## 10. Gestión de Estados y Errores

### Estados del Job

```
idle ──► uploading ──► validating ──► processing ──► completed
                                           │
                                           └──────────► failed
```

| Estado      | Descripción                                        |
|-------------|----------------------------------------------------|
| `uploading` | Archivo siendo recibido por el backend             |
| `validating`| Verificación de formato, tamaño e integridad       |
| `processing`| Pipeline en ejecución (extracción, detección, etc.)|
| `completed` | Video procesado listo para reproducir y descargar  |
| `failed`    | Error durante el procesamiento                     |

### Errores Definidos

| Código de Error         | Causa                                          | Mensaje al usuario                                        |
|-------------------------|------------------------------------------------|-----------------------------------------------------------|
| `INVALID_FORMAT`        | Extensión no permitida                         | "Formato no soportado. Usa MP4, MOV o AVI."              |
| `FILE_TOO_LARGE`        | Supera 500 MB                                  | "El archivo es demasiado grande (máximo 500 MB)."        |
| `CORRUPT_FILE`          | No se puede leer el archivo                    | "El archivo parece estar dañado."                        |
| `NO_PERSON_DETECTED`    | MediaPipe no encuentra persona en ningún frame | "No se detectó ninguna persona en el video."             |
| `PROCESSING_FAILED`     | Error inesperado durante el pipeline           | "Error durante el procesamiento. Intenta con otro video."|

### Comportamiento ante errores

- El frontend muestra el mensaje de error en lugar de la barra de progreso.
- El archivo de entrada se elimina inmediatamente al detectar un error.
- El usuario puede cargar un nuevo video sin reiniciar la app.

---

## 11. Interfaz de Usuario

### Pantalla Principal (flujo único)

```
┌──────────────────────────────────────────┐
│  ZONA DE CARGA                           │
│  ┌────────────────────────────────────┐  │
│  │  Arrastrá tu video acá             │  │
│  │  o [Seleccionar archivo]           │  │
│  └────────────────────────────────────┘  │
│  (aparece info del video al cargar)      │
├──────────────────────────────────────────┤
│  PROGRESO (visible solo durante proceso) │
│  Etapa: Detectando articulaciones...     │
│  ████████████░░░░░░░░ 45%  (332/738)    │
├──────────────────────────────────────────┤
│  RESULTADO (visible al completar)        │
│  ┌──────────────┐  ┌──────────────────┐  │
│  │ Video        │  │ Video procesado  │  │
│  │ original     │  │ (con esqueleto)  │  │
│  └──────────────┘  └──────────────────┘  │
│                    [Descargar MP4]        │
└──────────────────────────────────────────┘
```

| Sección      | Visible cuando          | Elementos                                         |
|--------------|-------------------------|---------------------------------------------------|
| Carga        | Siempre (estado inicial)| Área drag & drop, botón seleccionar               |
| Info video   | Tras seleccionar archivo| Nombre, duración, resolución, tamaño, botón iniciar|
| Progreso     | Durante procesamiento   | Barra de progreso, etapa actual, frames procesados|
| Error        | Si falla               | Mensaje de error, botón para volver a intentar    |
| Resultados   | Al completar           | Reproductor original, reproductor procesado, botón descargar |

---

## 12. Criterios de Aceptación

### CA-01: Carga de Video

**Dado** un archivo `.mp4` de 45 MB y 30 segundos de duración,  
**Cuando** el usuario lo arrastra al área de carga,  
**Entonces** el sistema muestra el nombre, duración, resolución y tamaño del archivo en menos de 2 segundos.

### CA-02: Rechazo de Archivo Inválido

**Dado** un archivo `.pdf`,  
**Cuando** el usuario intenta cargarlo,  
**Entonces** el sistema muestra el mensaje "Formato no soportado. Usa MP4, MOV o AVI." y no inicia el procesamiento.

### CA-03: Progreso en Tiempo Real

**Dado** un video en procesamiento,  
**Cuando** el backend avanza entre etapas,  
**Entonces** el frontend actualiza la barra de progreso y la etapa actual en menos de 1 segundo de latencia.

### CA-04: Resultado Correcto

**Dado** un procesamiento exitoso sobre un video con una persona corriendo,  
**Cuando** el usuario reproduce el resultado,  
**Entonces** el esqueleto aparece correctamente superpuesto sobre la persona en al menos el 85% de los frames.

### CA-05: Descarga Funcional

**Dado** un resultado generado,  
**Cuando** el usuario hace clic en "Descargar MP4",  
**Entonces** el navegador descarga un archivo `.mp4` reproducible con la misma duración que el original.

### CA-06: Recuperación ante Error

**Dado** un video en el que no se detecta ninguna persona,  
**Cuando** el procesamiento falla,  
**Entonces** el sistema muestra el mensaje de error correspondiente y permite cargar un nuevo video sin necesidad de reiniciar la app.

---

## 13. Mejoras Futuras

### Fase 2

- Cálculo automático de ángulos articulares.
- Visualización cuadro por cuadro (frame scrubber).
- Exportación CSV de landmarks por frame.
- Modo 3 de visualización: pantalla dividida original/procesado.
- Seguimiento de centro de masa.
- Detección de eventos de carrera:
  - Contacto inicial.
  - Medio apoyo.
  - Despegue.
  - Fase aérea.

### Fase 3

- Análisis biomecánico automático.
- Comparación entre atletas.
- Detección de errores técnicos.
- Dashboard de métricas de carrera.
- IA para recomendaciones de entrenamiento.

---

## 14. Entregables

| # | Entregable                                          |
|---|-----------------------------------------------------|
| 1 | Código fuente Frontend (React + TypeScript)         |
| 2 | Código fuente Backend (Python + FastAPI)            |
| 3 | Documentación de la API REST (OpenAPI / Swagger)   |
| 4 | Script de instalación y arranque local             |
| 5 | Manual de usuario                                   |
| 6 | Documentación técnica                               |
| 7 | Video de demostración                               |
