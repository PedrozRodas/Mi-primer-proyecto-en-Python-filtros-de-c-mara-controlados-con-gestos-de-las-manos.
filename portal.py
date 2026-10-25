"""Portal de filtros local: python portal.py; prueba sin cámara: --self-test."""
import argparse
from pathlib import Path
import time
import urllib.request
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
NAMES = ['Violeta', 'Bordes', 'Pixelado', 'Termico', 'Negativo']


class PinchSwitch:
    """Una pinza estable cambia una vez; abrir ambas manos rearma el gesto."""
    def __init__(self):
        self.armed = False
        self.since = None

    def update(self, ratios, now):
        if len(ratios) != 2:
            self.armed = False
            self.since = None
            return False
        if min(ratios) > .55:
            self.armed = True
            self.since = None
        elif min(ratios) < .30 and self.armed:
            if self.since is None:
                self.since = now
            if now - self.since >= .15:
                self.armed = False
                self.since = None
                return True
        else:
            self.since = None
        return False


def pinch_ratio(hand, width, height):
    def point(i):
        return np.array([hand[i].x * width, hand[i].y * height])
    return np.linalg.norm(point(8) - point(4)) / max(np.linalg.norm(point(9) - point(0)), 1)


def effect(frame, mode):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if mode == 0:
        tint = np.full_like(frame, (170, 35, 120))
        return cv2.addWeighted(frame, .45, tint, .55, 0)
    if mode == 1:
        return cv2.cvtColor(cv2.Canny(gray, 70, 150), cv2.COLOR_GRAY2BGR)
    if mode == 2:
        h, w = frame.shape[:2]
        small = cv2.resize(frame, (max(1, w//18), max(1, h//18)))
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    if mode == 3:
        return cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    return cv2.bitwise_not(frame)


def composite(frame, points, mode):
    # El contorno convexo evita polígonos cruzados al girar las manos.
    hull = cv2.convexHull(np.asarray(points, dtype=np.int32))
    if cv2.contourArea(hull) < 600:
        return frame.copy()
    mask = np.zeros(frame.shape[:2], np.uint8)
    cv2.fillConvexPoly(mask, hull, 255)
    out = frame.copy()
    filtered = effect(frame, mode)
    out[mask > 0] = filtered[mask > 0]
    cv2.polylines(out, [hull], True, (240, 240, 240), 2, cv2.LINE_AA)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        gesture = PinchSwitch()
        assert not gesture.update([.1, 1], 0)  # Inicio cerrado: no cambia.
        assert not gesture.update([1, 1], .1)
        assert not gesture.update([.1, 1], .2)
        assert gesture.update([.1, 1], .4)
        assert not gesture.update([.1, 1], 2)  # Mantener pinza: no repite.
        assert not gesture.update([1, 1], 3)
        assert not gesture.update([1, .1], 3.1)
        assert gesture.update([1, .1], 3.3)
        assert not gesture.update([], 4)
        assert not gesture.update([1, .1], 5)  # Recuperar manos no cambia.
        frame = np.random.default_rng(1).integers(0, 256, (240, 320, 3), dtype=np.uint8)
        for mode in range(5):
            out = composite(frame, [(60, 50), (250, 60), (240, 190), (70, 180)], mode)
            assert out.shape == frame.shape
            assert np.array_equal(out[0, 0], frame[0, 0])
            assert not np.array_equal(out[100, 100], frame[100, 100])
        print('OK: cinco filtros, composicion y cambio por pinza; camara no comprobada.')
        return
    import mediapipe as mp
    model = ROOT / 'hand_landmarker.task'
    if not model.exists():
        print('Descargando modelo de manos de Google (solo la primera vez)...')
        temporary = model.with_suffix('.download')
        urllib.request.urlretrieve(MODEL_URL, temporary)
        temporary.replace(model)
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=.5,
        min_tracking_confidence=.5)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise RuntimeError('No se pudo abrir la camara. Cierra otras apps o prueba --camera 1.')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    mode, smooth, last_timestamp = 0, None, -1
    gesture = PinchSwitch()
    try:
        with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:
            while True:
                ok, frame = cap.read()
                if not ok:
                    raise RuntimeError('La camara dejo de entregar imagenes.')
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp = max(last_timestamp + 1, time.monotonic_ns() // 1_000_000)
                last_timestamp = timestamp
                result = detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp)
                out = frame.copy()
                if len(result.hand_landmarks) == 2:
                    hands = sorted(result.hand_landmarks, key=lambda hand: hand[0].x)
                    h, w = frame.shape[:2]
                    if gesture.update([pinch_ratio(hand, w, h) for hand in hands], time.monotonic()):
                        mode = (mode + 1) % len(NAMES)
                    points = np.array([(hand[i].x*w, hand[i].y*h) for hand in hands for i in (8, 4)])
                    smooth = points if smooth is None else .65*points + .35*smooth
                    out = composite(frame, smooth, mode)
                else:
                    gesture.update([], time.monotonic())
                    smooth = None
                    cv2.putText(out, 'Muestra ambas manos: indice arriba, pulgar abajo', (15, 60), 0, .55, (255,255,255), 1)
                cv2.putText(out, f'{NAMES[mode]} | Pinza: siguiente | Abre ambas para repetir | Q: salir', (15, 28), 0, .55, (255,255,255), 1)
                cv2.imshow('Portal de filtros', out)
                key = cv2.waitKey(1) & 0xff
                if key in (ord('q'), 27):
                    break
                if ord('1') <= key <= ord('5'):
                    mode = key - ord('1')
                elif key == 32:
                    mode = (mode + 1) % 5
                if cv2.getWindowProperty('Portal de filtros', cv2.WND_PROP_VISIBLE) < 1:
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
