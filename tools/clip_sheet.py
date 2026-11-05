"""Planche de contrôle des plans animés : une image toutes les 0,33 s pour chaque clip, avec le temps écrit dessus.
    python3 tools/clip_sheet.py SORTIE.jpg clip1.mp4 clip2.mp4 ...
À regarder avec Read AVANT le montage : un plan peut contenir un défaut invisible sur sa première image (exemple du pilote : l'œil reste fermé de 1,5 à 3,4 s)."""
import sys
import cv2, numpy as np


def main():
    out, clips = sys.argv[1], sys.argv[2:]; rows = []
    for path in clips:
        c = cv2.VideoCapture(path); fps = c.get(cv2.CAP_PROP_FPS) or 24; n = int(c.get(cv2.CAP_PROP_FRAME_COUNT)); ims = []
        for k in range(0, n, max(1, int(fps / 3))):
            c.set(cv2.CAP_PROP_POS_FRAMES, k); ok, f = c.read()
            if not ok: break
            f = cv2.resize(f, (135, 240), interpolation=cv2.INTER_AREA); cv2.putText(f, f'{k / fps:.2f}', (4, 234), 0, .45, (0, 255, 255), 1); ims.append(f)
        rows.append(np.hstack(ims))
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(out, np.vstack([cv2.copyMakeBorder(r, 0, 0, 0, w - r.shape[1], cv2.BORDER_CONSTANT) for r in rows]), [cv2.IMWRITE_JPEG_QUALITY, 85]); print(out)


if __name__ == '__main__':
    main()
