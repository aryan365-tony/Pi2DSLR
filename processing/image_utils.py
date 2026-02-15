import numpy as np


def align_frames_fast(frames, scale=4, search=5):
    base_full = frames[0][:, :, :3].astype(np.float32)
    base_small = base_full[::scale, ::scale]
    base_gray = np.mean(base_small, axis=2)

    aligned = [base_full]

    for frame in frames[1:]:
        full = frame[:, :, :3].astype(np.float32)
        small = full[::scale, ::scale]
        gray = np.mean(small, axis=2)

        best_score = float("inf")
        best_shift = (0, 0)

        sh, sw = gray.shape

        for dy in range(-search, search + 1):
            for dx in range(-search, search + 1):
                y1 = max(0, dy)
                y2 = min(sh, sh + dy)
                x1 = max(0, dx)
                x2 = min(sw, sw + dx)

                ref = base_gray[y1:y2, x1:x2]
                cmp = gray[y1 - dy:y2 - dy,
                           x1 - dx:x2 - dx]

                if ref.size == 0:
                    continue

                diff = ((ref - cmp) ** 2).mean()

                if diff < best_score:
                    best_score = diff
                    best_shift = (dy, dx)

        dy, dx = best_shift

        shifted = np.roll(
            full,
            shift=(dy * scale, dx * scale),
            axis=(0, 1),
        )

        aligned.append(shifted)

    return aligned
