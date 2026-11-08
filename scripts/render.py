"""Procedural raster art for the profile: a particle galaxy around a dark core, and small planets.

Everything is seeded, so a rebuild produces the same images.
"""
import numpy as np
from scipy.ndimage import gaussian_filter, zoom


def _splat(img, x, y, w):
    """Add weights w at float pixel coords (x, y) with bilinear spreading."""
    h, wd = img.shape
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    for dx, dy, k in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi, yi = x0 + dx, y0 + dy
        ok = (xi >= 0) & (xi < wd) & (yi >= 0) & (yi < h)
        np.add.at(img, (yi[ok], xi[ok]), (w * k)[ok])


EXPOSURE = 0.55
R_HOLE = 0.07  # black-hole radius, as a fraction of the disk radius


def galaxy(size=1000, seed=4):
    """Face-on spiral galaxy with a black-hole core. Returns float RGB in [0, 1], shape (size, size, 3)."""
    rng = np.random.default_rng(seed)
    pitch = np.tan(np.radians(12))
    r_hole = R_HOLE

    def arm_particles(n, offset, spread):
        r = r_hole + rng.gamma(1.6, 0.17, n)
        r = r[r < 1.0]
        # Particles follow thin strands, which gives the arms their filament texture.
        strands = 120
        s = rng.integers(0, strands, r.size)
        s_off = rng.normal(0, spread, strands)
        s_gain = rng.lognormal(0, 0.45, strands)
        th = offset + np.log(r / r_hole) / pitch + s_off[s] * (0.6 + r) + rng.normal(0, 0.035, r.size)
        r = r * (1 + rng.normal(0, 0.008, r.size))
        return r, th, s_gain[s]

    parts = [arm_particles(60_000, a, 0.3) for a in (0, np.pi)]
    parts += [arm_particles(20_000, a, 0.45) for a in (np.pi / 2, 3 * np.pi / 2)]
    # Diffuse disk and a dense accretion swirl just outside the core.
    rd = r_hole + rng.exponential(0.32, 45_000)
    rd = rd[rd < 1.05]
    parts.append((rd, rng.uniform(0, 2 * np.pi, rd.size), np.ones(rd.size)))
    ri = r_hole + np.abs(rng.normal(0, 0.05, 18_000))
    parts.append((ri, rng.uniform(0, 2 * np.pi, ri.size), np.ones(ri.size)))
    r = np.concatenate([p[0] for p in parts])
    th = np.concatenate([p[1] for p in parts])
    gain = np.concatenate([p[2] for p in parts])
    lum = gain * rng.lognormal(-0.4, 0.7, r.size) * (0.5 + 0.2 * np.exp(-((r - r_hole) / 0.25))) / (1 + 2.2 * np.exp(-((r - r_hole) / 0.12)))

    c = size / 2
    scale = size / 2 * 0.96
    img = np.zeros((size, size))
    # Each particle is drawn as a short arc along its orbit, so the disk reads as motion-streaked.
    steps = 10
    arc = 0.006 / np.maximum(r, 0.08)
    for j in range(steps):
        t = th - arc * j
        _splat(img, c + scale * r * np.cos(t), c + scale * r * np.sin(t), lum * (1 - j / steps) * 0.6)

    yy, xx = np.mgrid[0:size, 0:size]
    pr = np.hypot(xx - c, yy - c) / scale
    pt = np.arctan2(yy - c, xx - c)
    # Dust lanes trail the inner edge of the main arms.
    phase = pt - np.log(np.maximum(pr, r_hole) / r_hole) / pitch
    lane = np.zeros_like(pr)
    for a in (0, np.pi):
        d = np.angle(np.exp(1j * (phase - a + 0.55)))
        lane = np.maximum(lane, np.exp(-(d ** 2) / (2 * 0.16 ** 2)))
    dust = 1 - 0.55 * lane * np.clip((pr - 0.12) / 0.15, 0, 1) * np.clip((1.0 - pr) / 0.3, 0, 1)

    glow = gaussian_filter(img, 1.0) * 0.15 + gaussian_filter(img, 6) * 0.1 + gaussian_filter(img, 36) * 0.14
    lum_img = (img * 0.8 + glow) * dust
    # Event horizon: black core with a thin bright photon ring.
    ring = np.exp(-(((pr - r_hole * 1.02) / 0.006) ** 2)) * 2.4
    lum_img = lum_img * np.clip((pr - r_hole * 0.9) / (r_hole * 0.25), 0, 1) + ring
    lum_img *= np.clip((1.04 - pr) / 0.2, 0, 1)  # fade the rim

    v = 1 - np.exp(-lum_img * EXPOSURE)
    # Cool arms, faintly warm near the core.
    warm = np.exp(-((pr - r_hole) / 0.22) ** 2)
    rgb = np.stack([v * (0.93 + 0.07 * warm), v * (0.95 + 0.02 * warm), v * (1.0 - 0.06 * warm)], -1)

    # A sprinkle of bright stars, about one in twenty warm amber.
    n = 900
    sr = r_hole * 1.3 + rng.gamma(1.5, 0.2, n)
    st = rng.uniform(0, 2 * np.pi, n)
    sx, sy = (c + scale * sr * np.cos(st)).astype(int), (c + scale * sr * np.sin(st)).astype(int)
    ok = (sx > 1) & (sx < size - 2) & (sy > 1) & (sy < size - 2) & (sr < 1)
    amber = rng.random(n) < 0.05
    for x, y, a in zip(sx[ok], sy[ok], amber[ok]):
        col = np.array([1.0, 0.72, 0.48]) if a else np.array([1.0, 1.0, 1.0])
        b = rng.uniform(0.5, 1.0)
        rgb[y, x] = np.maximum(rgb[y, x], col * b)
        rgb[y - 1:y + 2, x - 1:x + 2] = np.maximum(rgb[y - 1:y + 2, x - 1:x + 2], col * b * 0.35)
    return np.clip(rgb, 0, 1)



def planet(size=128, kind="gas", tint="#D2AD86", seed=1, light=(-0.55, -0.5, 0.67)):
    """Small shaded planet: banded gas giant or rocky world, muted toward grey. Returns float RGBA."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]
    u, v = (xx + 0.5) / size * 2 - 1, (yy + 0.5) / size * 2 - 1
    rr = u ** 2 + v ** 2
    z = np.sqrt(np.clip(1 - rr, 0, 1))

    def noise(cells):
        return zoom(rng.normal(0, 1, (cells, cells)), size / cells, order=3)[:size, :size]

    if kind == "gas":
        warp = noise(4) * 0.6 + noise(10) * 0.25
        tex = 0.5 + 0.5 * np.sin(v * rng.uniform(9, 14) + warp * 1.8) * (0.6 + 0.4 * np.sin(v * 31 + warp))
    else:
        tex = noise(5) + noise(12) * 0.6 + noise(30) * 0.3
        tex = (tex - tex.min()) / (tex.max() - tex.min())
    base = np.array([int(tint[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    base = base * 0.6 + base.mean() * 0.4  # mute toward grey
    col = base * (0.55 + 0.6 * tex[..., None])
    n = np.stack([u, v, z], -1)
    L = np.array(light) / np.linalg.norm(light)
    shade = np.clip((n * L).sum(-1), 0, 1) * 0.95 + 0.03
    col = col * (shade * (0.65 + 0.35 * z))[..., None]
    rgba = np.zeros((size, size, 4))
    rgba[..., :3] = np.clip(col, 0, 1)
    rgba[..., 3] = np.clip((1 - np.sqrt(rr)) * size / 2, 0, 1)
    return rgba
