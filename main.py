from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
import mediapipe as mp
import cv2

# ==========================
# CONFIGURACIÓN
# ==========================

MODELO = "pose_landmarker_heavy.task"
IMAGEN = "anatomico.jpg"

# ==========================
# CARGAR MODELO
# ==========================

base_options = BaseOptions(model_asset_path=MODELO)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False
)

detector = vision.PoseLandmarker.create_from_options(options)

# ==========================
# LEER IMAGEN
# ==========================

imagen_mp = mp.Image.create_from_file(IMAGEN)

resultado = detector.detect(imagen_mp)

print("Personas detectadas:", len(resultado.pose_landmarks))

if len(resultado.pose_landmarks) == 0:
    print("No se detectó ninguna persona.")
    exit()

landmarks = resultado.pose_landmarks[0]

# ==========================
# ABRIR CON OPENCV
# ==========================

imagen_cv = cv2.imread(IMAGEN)

alto, ancho, _ = imagen_cv.shape

# ==========================
# FUNCIONES
# ==========================

def pixel(idx):
    """Convierte landmark a coordenadas de píxel"""
    p = landmarks[idx]
    return (
        int(p.x * ancho),
        int(p.y * alto)
    )

# ==========================
# CUELLO VIRTUAL
# ==========================

hombro_izq = landmarks[11]
hombro_der = landmarks[12]

cuello_x = int(((hombro_izq.x + hombro_der.x) / 2) * ancho)
cuello_y = int(((hombro_izq.y + hombro_der.y) / 2) * alto)

# ==========================
# ESQUELETO
# ==========================

conexiones = [

    # Cabeza
    (0, 2),
    (0, 5),

    # Hombros
    (11, 12),

    # Brazo izquierdo
    (11, 13),
    (13, 15),

    # Brazo derecho
    (12, 14),
    (14, 16),

    # Tronco
    (11, 23),
    (12, 24),
    (23, 24),

    # Pierna izquierda
    (23, 25),
    (25, 27),

    # Pierna derecha
    (24, 26),
    (26, 28),

    # Pie izquierdo
    (27, 29),
    (29, 31),

    # Pie derecho
    (28, 30),
    (30, 32)
]

# Dibujar líneas del esqueleto

for inicio, fin in conexiones:

    x1, y1 = pixel(inicio)
    x2, y2 = pixel(fin)

    cv2.line(
        imagen_cv,
        (x1, y1),
        (x2, y2),
        (128, 0, 128),
        3
    )

# ==========================
# CABEZA → CUELLO
# ==========================

nariz_x, nariz_y = pixel(0)

cv2.line(
    imagen_cv,
    (nariz_x, nariz_y),
    (cuello_x, cuello_y),
    (128, 0, 128),
    3
)

# ==========================
# DIBUJAR ARTICULACIONES
# ==========================

landmarks_visibles = [
    0,      # nariz
    2, 5,   # ojos

    11,12,
    13,14,
    15,16,

    23,24,
    25,26,
    27,28,
    29,30,
    31,32
]

for idx in landmarks_visibles:

    x, y = pixel(idx)

    cv2.circle(
        imagen_cv,
        (x, y),
        5,
        (0, 0, 255),
        -1
    )

# Cuello virtual

cv2.circle(
    imagen_cv,
    (cuello_x, cuello_y),
    5,
    (255, 0, 0),
    -1
)

# ==========================
# GUARDAR
# ==========================

cv2.imwrite("salida.jpg", imagen_cv)

print("Imagen guardada como salida.jpg")