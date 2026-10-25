# Tu portal de filtros

Versión propia inspirada en el video, no el código original de la creadora.

## Qué se observa en Download.mp4

La grabación dura 26,91 segundos. Se ve Visual Studio Code en Windows, archivos detectorManos.py y detectorPortal.py, una terminal ejecutando Python y una ventana llamada «Portal de filtros». El código visible incluye cv2.VideoCapture(0, cv2.CAP_DSHOW), que confirma OpenCV y captura de cámara en Windows.

La creadora coloca ambas manos alrededor de una zona de la imagen. Un polígono sigue los dedos y aplica efectos solo dentro de esa zona. Se ven un tinte violeta, contornos sobre fondo oscuro, pixelado y un mapa de colores tipo térmico. No es una cámara térmica: ese aspecto puede obtenerse coloreando intensidades de la imagen. La grabación no muestra el código completo ni permite confirmar la biblioteca que detecta las manos o el mecanismo exacto que cambia los filtros. Tampoco demuestra que haya usado un asistente de IA para programarlo.

## Cómo funciona nuestra versión

Cámara → detección de dos manos → puntas de índice y pulgar → polígono → filtro dentro del polígono → ventana en directo. Usamos Python, OpenCV, NumPy y MediaPipe Hand Landmarker. MediaPipe es nuestra elección para replicarlo; no está confirmado como la biblioteca del original.

## Paso a paso en Windows

1. Instala Python 3.11 de 64 bits desde https://www.python.org/downloads/ y activa «Add Python to PATH». Si ya lo tienes, no hace falta instalarlo de nuevo.
2. Guarda esta carpeta completa en tu computadora. Abre la carpeta en el Explorador, escribe `powershell` en la barra de dirección y presiona Enter.
3. Crea un entorno propio para el proyecto:

   `py -3.11 -m venv .venv`

4. Instala las dependencias:

   `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

5. Inicia el programa:

   `.\.venv\Scripts\python.exe portal.py`

   La primera vez descargará el modelo de manos de Google. Después el procesamiento se realiza localmente. El programa no graba ni envía las imágenes de la cámara.

6. Con buena iluminación, muestra las dos manos enteras. Coloca los índices arriba y los pulgares abajo como si sujetaras las cuatro esquinas de una ventana. Separa las manos y mueve los dedos para cambiar su tamaño y forma.
7. Para cambiar de filtro sin teclado, separa índice y pulgar en ambas manos; luego junta las puntas de índice y pulgar de cualquiera de ellas durante un instante. Cada pinza avanza un filtro. Vuelve a abrir ambas manos antes de repetir. Mantener los dedos juntos no provoca cambios repetidos. También puedes presionar 1 para violeta, 2 para bordes, 3 para pixelado, 4 para aspecto térmico y 5 para negativo. Espacio avanza al siguiente filtro. Q o Escape cierra la aplicación.
8. Para crear tu TikTok, graba la ventana con tu herramienta habitual de captura de pantalla. La aplicación no incluye grabación de video.

## Si algo falla

- Cámara ocupada o negra: cierra las aplicaciones que la estén usando; revisa Configuración → Privacidad y seguridad → Cámara y permite acceso a aplicaciones de escritorio. Prueba `.\.venv\Scripts\python.exe portal.py --camera 1` si tienes varias cámaras.
- No aparece el portal: deben verse dos manos, incluidos índices y pulgares. Evita taparlos o cruzar las manos.
- Va lento: mejora la iluminación, cierra otras aplicaciones y mantén las manos visibles.
- Falla la descarga: comprueba tu conexión y vuelve a iniciar el programa.
- No instala MediaPipe: comprueba que usas Python 3.11 de 64 bits en el entorno indicado.

## Alcance y comprobación

Los filtros se seleccionan con una pinza de índice y pulgar o con teclado. El gesto es una elección de esta recreación; el mecanismo exacto del original no se puede confirmar en el video. Se usa un contorno convexo para evitar que el portal se cruce sobre sí mismo. Es una recreación funcional del concepto, no una réplica exacta de todos sus efectos.

Prueba sin cámara: `.\.venv\Scripts\python.exe portal.py --self-test`. Comprueba los cinco efectos y que la imagen exterior al portal se conserve. La cámara y la fluidez en tu equipo requieren una prueba local.

Documentación: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python
Demostracion: 



https://github.com/user-attachments/assets/9fadf855-96e2-4822-afba-52505dcf3512

