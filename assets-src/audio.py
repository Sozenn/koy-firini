"""Köy Fırını müzik, ortam sesi ve ses efektleri sentezleyicisi.

Hiçbir kayıt kullanılmaz: bütün sesler numpy ile sentezlenir.
  * Bağlama: ek-sesli toplamsal tel sentezi (üst harmonikler hızlı söner) + tezene sesi
  * Kaval: faz birikimli üfleme sesi, gecikmeli titreşim, nefes gürültüsü, notalar arası kayma
  * Klarnet: tek harmonik ağırlıklı kamış sesi
  * Darbuka (düm / tek / ka), def ve zil
Makamlar perde perde (sent) olarak tanımlanır, böylece Uşşak'ın segâh perdesi gibi
koma sesleri de çalınabilir.

Çıktılar: assets/audio/*.mp3 (müzik ve ortam, döngü) ve assets/audio/sfx/*.wav (efekt)
Kullanım: python assets-src/audio.py <ffmpeg.exe yolu>
"""
import glob
import json
import os
import subprocess
import sys
import wave

import numpy as np
from scipy import signal

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'audio')
TMP = os.path.join(ROOT, 'assets-src', 'audio-tmp')
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- yardımcılar
def secs(n):
    return int(round(n * SR))


def hz_from_cents(base, cents):
    return base * 2 ** (cents / 1200)


def env_adsr(n, a=.005, d=.05, s=.7, r=.05):
    a, d, r = secs(a), secs(d), secs(r)
    e = np.ones(n) * s
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a, endpoint=False)
    d = min(d, n - a)
    e[a:a + d] = np.linspace(1, s, d, endpoint=False)
    r = min(r, n)
    e[n - r:] *= np.linspace(1, 0, r)
    return e


def butter(x, kind, f, order=2):
    if kind == 'band':
        sos = signal.butter(order, [max(20, f[0]), min(SR / 2 - 100, f[1])], 'bandpass', fs=SR, output='sos')
    else:
        sos = signal.butter(order, min(f, SR / 2 - 100), kind, fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def noise(n):
    return rng.standard_normal(n)


def place(buf, x, start):
    """x'i buf içine start örneğinden itibaren ekler (taşanı keser)."""
    s = max(0, start)
    e = min(len(buf), start + len(x))
    if e > s:
        buf[s:e] += x[s - start:e - start]


def place_loop(buf, x, start):
    """Döngüsel yerleştirme: sona taşan kısım başa sarılır (dikişsiz döngü için)."""
    n = len(buf)
    start %= n
    first = min(len(x), n - start)
    buf[start:start + first] += x[:first]
    rest = x[first:]
    while len(rest):
        k = min(len(rest), n)
        buf[:k] += rest[:k]
        rest = rest[k:]


def reverb_ir(seconds=2.4, bright=5000, seed=3):
    r = np.random.default_rng(seed)
    n = secs(seconds)
    t = np.arange(n) / SR
    irs = []
    for ch in range(2):
        x = r.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        x = butter(x, 'low', bright)
        x[:secs(.012)] *= np.linspace(0, 1, secs(.012))
        irs.append(x / np.sqrt(np.sum(x ** 2)))
    return irs


def add_reverb(st, wet=.25, seconds=2.4, loop=True):
    """Stereo (2, n) sinyale evrişimli yankı ekler; loop ise kuyruk başa sarılır."""
    irs = reverb_ir(seconds)
    n = st.shape[1]
    out = st.copy()
    for ch in range(2):
        mono = (st[0] + st[1]) * .5
        w = signal.oaconvolve(mono, irs[ch])
        if loop:
            tail = w[n:]
            w = w[:n].copy()
            k = 0
            while k < len(tail):
                m = min(n, len(tail) - k)
                w[:m] += tail[k:k + m]
                k += m
        else:
            w = w[:n]
        out[ch] += w * wet
    return out


def pan(x, p):
    """p: -1 sol, +1 sağ."""
    a = (p + 1) * np.pi / 4
    return np.vstack([x * np.cos(a), x * np.sin(a)])


def normalize(st, peak=.89):
    m = np.max(np.abs(st)) or 1
    return st * (peak / m)


def write_wav(path, st):
    st = np.clip(st, -1, 1)
    if st.ndim == 1:
        data = (st * 32767).astype('<i2').tobytes()
        ch = 1
    else:
        data = (st.T * 32767).astype('<i2').tobytes()
        ch = 2
    with wave.open(path, 'wb') as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)


# ---------------------------------------------------------------- çalgılar
def baglama(f, dur, vel=1., bright=1.):
    """Bağlama teli: toplamsal sentez. Üst harmonikler daha çabuk söner, hafif ek-sesli."""
    n = secs(dur + .9)
    t = np.arange(n) / SR
    out = np.zeros(n)
    pluck_pos = .17
    for k in range(1, 22):
        fk = f * k * (1 + .0007 * k * k)
        if fk > SR / 2.2:
            break
        amp = abs(np.sin(np.pi * k * pluck_pos)) / k ** (1.05 / bright)
        dec = 1.6 + .55 * k
        out += amp * np.sin(2 * np.pi * fk * t + rng.random() * 6.28) * np.exp(-t * dec)
    # tezene vuruşu (kısa tiz gürültü) ve gövde rezonansı
    pick = butter(noise(secs(.02)), 'high', 2500) * np.linspace(1, 0, secs(.02)) * .35
    out[:len(pick)] += pick
    body = butter(out, 'band', (180, 420)) * .3
    out = out + body
    # elle susturma: nota süresi bitince sönüm hızlanır
    cut = secs(dur)
    if cut < n:
        out[cut:] *= np.exp(-np.arange(n - cut) / SR * 14)
    out[:secs(.003)] *= np.linspace(0, 1, secs(.003))
    return out * vel * .22


def kaval(notes, base_t, bpm_beat, vib=.006, breath=.07, legato=True):
    """notes: [(saniye_baslangic, sure, frekans, hiz)]. Tek bir sürekli sinyal döndürür (kaymalı)."""
    if not notes:
        return np.zeros(1)
    end = max(s + d for s, d, f, v in notes) + .6
    n = secs(end)
    freq = np.zeros(n)
    amp = np.zeros(n)
    prev_f = None
    for s, d, f, v in notes:
        a, b = secs(s), secs(s + d)
        b = min(b, n)
        seg = np.full(b - a, f)
        if prev_f and legato:
            g = min(secs(.045), b - a)
            seg[:g] = np.geomspace(prev_f, f, g)
        tt = np.arange(b - a) / SR
        vib_env = np.clip((tt - .22) / .25, 0, 1)
        seg = seg * (1 + vib * vib_env * np.sin(2 * np.pi * 5.4 * tt))
        freq[a:b] = seg
        e = np.ones(b - a) * v
        at = min(secs(.06), b - a)
        e[:at] *= np.linspace(.15, 1, at)
        rl = min(secs(.08), b - a)
        e[-rl:] *= np.linspace(1, .55 if legato else 0, rl)
        amp[a:b] = np.maximum(amp[a:b], e)
        prev_f = f
    amp = signal.lfilter([.004], [1, -.996], amp)  # yumuşatma
    phase = 2 * np.pi * np.cumsum(freq) / SR
    tone = np.sin(phase) + .38 * np.sin(2 * phase + .3) + .16 * np.sin(3 * phase + 1) + .06 * np.sin(4 * phase)
    br = butter(noise(n), 'band', (900, 5200)) * breath
    sig = (tone + br * (1 + np.sin(phase))) * amp
    sig = butter(sig, 'low', 7000)
    return sig * .16


def klarnet(notes, vib=.009):
    end = max(s + d for s, d, f, v in notes) + .5
    n = secs(end)
    freq = np.zeros(n)
    amp = np.zeros(n)
    prev = None
    for s, d, f, v in notes:
        a, b = secs(s), min(secs(s + d), n)
        seg = np.full(b - a, f)
        if prev:
            g = min(secs(.03), b - a)
            seg[:g] = np.geomspace(prev, f, g)
        tt = np.arange(b - a) / SR
        seg *= 1 + vib * np.clip((tt - .15) / .2, 0, 1) * np.sin(2 * np.pi * 6.2 * tt)
        freq[a:b] = seg
        e = np.ones(b - a) * v
        at = min(secs(.025), b - a)
        e[:at] *= np.linspace(0, 1, at)
        rl = min(secs(.05), b - a)
        e[-rl:] *= np.linspace(1, .3, rl)
        amp[a:b] = e
        prev = f
    amp = signal.lfilter([.01], [1, -.99], amp)
    ph = 2 * np.pi * np.cumsum(freq) / SR
    tone = sum((1 / k) * np.sin(k * ph) for k in (1, 3, 5, 7, 9)) + .12 * np.sin(2 * ph)
    sig = butter(tone * amp, 'low', 3800) + butter(noise(n), 'band', (1500, 4000)) * amp * .03
    return sig * .2


def dum(v=1.):
    n = secs(.45)
    t = np.arange(n) / SR
    f = 62 + 70 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    x += butter(noise(n), 'low', 400) * np.exp(-t * 40) * .4
    return x * v * .55


def tek(v=1.):
    n = secs(.16)
    t = np.arange(n) / SR
    x = butter(noise(n), 'band', (2200, 7000)) * np.exp(-t * 55)
    x += np.sin(2 * np.pi * 520 * t) * np.exp(-t * 45) * .35
    return x * v * .3


def ka(v=1.):
    n = secs(.1)
    t = np.arange(n) / SR
    return butter(noise(n), 'band', (1200, 4000)) * np.exp(-t * 70) * v * .18


def deff(v=1., zil=True):
    n = secs(.6)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * np.cumsum(70 + 30 * np.exp(-t * 25)) / SR) * np.exp(-t * 9) * .5
    if zil:
        z = np.zeros(n)
        for fz in (3400, 4700, 5900, 7300, 8800):
            z += np.sin(2 * np.pi * fz * t + rng.random() * 6) * np.exp(-t * (14 + rng.random() * 8))
        z += butter(noise(n), 'high', 6000) * np.exp(-t * 20) * .8
        x += z * .07
    return x * v * .5


def davul(v=1.):
    n = secs(.7)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * np.cumsum(55 + 60 * np.exp(-t * 18)) / SR) * np.exp(-t * 5)
    x += butter(noise(n), 'low', 900) * np.exp(-t * 25) * .5
    return x * v * .6


# ---------------------------------------------------------------- makamlar
USSAK_A = [0, 150, 300, 500, 700, 800, 1000]       # dügah, segâh, çargâh, nevâ, hüseynî, acem, gerdaniye
HICAZ_D = [0, 113, 384, 500, 700, 800, 1000]        # Hicaz dörtlüsü + Buselik/Kürdi
HICAZ_G = HICAZ_D


def deg(scale, base, d):
    o, i = divmod(d, len(scale))
    return hz_from_cents(base, scale[i] + 1200 * o)


# ---------------------------------------------------------------- parça 1: Köy Sabahı (Uşşak, 2/4)
def track_sabah():
    bpm = 104
    e8 = 60 / bpm / 2           # sekizlik
    bar = e8 * 4
    A3 = 220.0
    A = [  # (derece, sekizlik)
        [(4, 2), (3, 1), (2, 1)], [(3, 2), (2, 1), (1, 1)], [(2, 1), (1, 1), (0, 2)], [(0, 4)],
        [(0, 1), (1, 1), (2, 1), (3, 1)], [(4, 2), (5, 1), (4, 1)], [(3, 1), (4, 1), (3, 1), (2, 1)], [(3, 4)],
        [(7, 2), (6, 1), (5, 1)], [(4, 2), (5, 1), (4, 1)], [(3, 1), (2, 1), (1, 1), (2, 1)], [(3, 2), (4, 2)],
        [(4, 1), (3, 1), (2, 1), (1, 1)], [(2, 2), (1, 1), (0, 1)], [(1, 1), (2, 1), (1, 1), (0, 1)], [(0, 4)],
    ]
    B = [
        [(4, 1), (4, 1), (5, 1), (4, 1)], [(3, 1), (3, 1), (4, 1), (3, 1)], [(2, 1), (3, 1), (2, 1), (1, 1)], [(2, 2), (0, 2)],
        [(0, 1), (2, 1), (1, 1), (3, 1)], [(2, 1), (4, 1), (3, 1), (5, 1)], [(4, 1), (3, 1), (2, 1), (1, 1)], [(0, 4)],
        [(7, 1), (7, 1), (8, 1), (7, 1)], [(6, 1), (6, 1), (7, 1), (6, 1)], [(5, 1), (6, 1), (5, 1), (4, 1)], [(5, 2), (3, 2)],
        [(7, 1), (6, 1), (5, 1), (4, 1)], [(5, 1), (4, 1), (3, 1), (2, 1)], [(3, 1), (2, 1), (1, 1), (2, 1)], [(0, 4)],
    ]
    form = [('kaval', A), ('baglama', B), ('kaval2', A)]
    bars = sum(len(p) for _, p in form)
    n = secs(bars * bar)
    L = np.zeros(n)
    R = np.zeros(n)
    kav_notes = []
    t0 = 0.0
    for who, phrase in form:
        for b_i, b in enumerate(phrase):
            t = t0 + b_i * bar
            for d, ln in b:
                f = deg(USSAK_A, A3 * 2, d)  # A4 üzerinden
                if who.startswith('kaval'):
                    kav_notes.append((t, ln * e8 * .98, f * (2 if who == 'kaval2' and b_i >= 8 else 1), .9 if ln >= 2 else .75))
                else:
                    # bağlama tezenesi: her sekizlik iki onaltılık
                    for k in range(ln * 2):
                        v = 1 if k % 2 == 0 else .6
                        place_loop(L, baglama(f, e8 * .55, v * .8, 1.15) * .55, secs(t + k * e8 / 2))
                        place_loop(R, baglama(f, e8 * .55, v * .8, 1.15) * .45, secs(t + k * e8 / 2))
                t += ln * e8
        t0 += len(phrase) * bar
    kv = kaval(kav_notes, 0, e8)
    pl = pan(kv, -.15)
    for ch, buf in ((0, L), (1, R)):
        m = min(n, pl.shape[1])
        buf[:m] += pl[ch][:m]
        if pl.shape[1] > n:
            buf[:pl.shape[1] - n] += pl[ch][n:]
    # eşlik bağlaması: dügah ve nevâ telleri, onaltılık tezene deseni
    pattern = [1, 0, .55, .7, 1, 0, .55, .8]   # 2/4 içinde 8 onaltılık
    roots = {0: (0, 4), 1: (0, 4), 2: (-2, 2), 3: (0, 4)}
    for b_i in range(bars):
        r = roots[(b_i // 2) % 4]
        for k, v in enumerate(pattern):
            if not v:
                continue
            t = b_i * bar + k * e8 / 2
            for dd, pp in ((r[0], -.4), (r[1], .35)):
                x = baglama(deg(USSAK_A, A3, dd), e8 * .45, v * .45, .9)
                place_loop(L, x * (1 - pp) * .5, secs(t))
                place_loop(R, x * (1 + pp) * .5, secs(t))
    # darbuka: düm . tek tek | düm tek . tek  (her ölçü 8 onaltılık)
    darb = [('d', 1), None, ('k', .5), ('t', .9), ('t', .7), ('k', .4), ('t', .9), None]
    darb2 = [('d', 1), None, ('t', .9), ('k', .5), ('d', .8), ('k', .4), ('t', .9), ('t', .6)]
    for b_i in range(bars):
        pat = darb2 if b_i % 4 == 3 else darb
        for k, hit in enumerate(pat):
            if not hit:
                continue
            kind, v = hit
            x = dum(v) if kind == 'd' else tek(v) if kind == 't' else ka(v)
            p = -.1 if kind == 'd' else .25
            place_loop(L, x * (1 - p) * .5, secs(b_i * bar + k * e8 / 2))
            place_loop(R, x * (1 + p) * .5, secs(b_i * bar + k * e8 / 2))
        if b_i % 4 == 0:
            x = deff(.9)
            place_loop(L, x * .35, secs(b_i * bar))
            place_loop(R, x * .65, secs(b_i * bar))
    st = add_reverb(np.vstack([L, R]), .22, 2.2)
    return normalize(st, .8), bars * bar


# ---------------------------------------------------------------- parça 2: Akşam Ezgisi (Hicaz, 3/4, yavaş)
def track_aksam():
    bpm = 66
    q = 60 / bpm
    bar = q * 3
    D4 = 293.66
    mel = [  # (derece, dörtlük) D4 tabanlı; 4=La, 3=Sol, 2=Fa#, 1=Mi bemol, 0=Re
        [(4, 3)], [(3, 1), (2, 1), (1, 1)], [(2, 2), (3, 1)], [(4, 3)],
        [(5, 1), (4, 1), (3, 1)], [(2, 1), (3, 1), (4, 1)], [(3, 1), (2, 1), (1, 1)], [(0, 3)],
        [(7, 2), (6, 1)], [(5, 1), (6, 1), (5, 1)], [(4, 2), (5, 1)], [(4, 3)],
        [(4, 1), (5, 1), (6, 1)], [(5, 1), (4, 1), (3, 1)], [(2, 1), (1, 1), (2, 1)], [(0, 3)],
        [(4, 1.5), (5, .5), (4, 1)], [(3, 2), (2, 1)], [(3, 1), (4, 1), (5, 1)], [(4, 3)],
        [(3, 1), (2, 1), (3, 1)], [(2, 1), (1, 1), (2, 1)], [(1, 1.5), (2, .5), (1, 1)], [(0, 3)],
    ]
    bars = len(mel)
    n = secs(bars * bar)
    L = np.zeros(n)
    R = np.zeros(n)
    notes = []
    t = 0.0
    for b in mel:
        for d, ln in b:
            notes.append((t, ln * q * .97, deg(HICAZ_D, D4, d), .8))
            t += ln * q
    kv = kaval(notes, 0, q, vib=.008, breath=.09)
    pl = pan(kv, 0)
    for ch, buf in ((0, L), (1, R)):
        m = min(n, pl.shape[1])
        buf[:m] += pl[ch][:m] * .9
        if pl.shape[1] > n:
            buf[:pl.shape[1] - n] += pl[ch][n:] * .9
    # bağlama arpejleri: her ölçüde dem perdesi ve Hicaz akoru
    chords = [(0, 2, 4), (0, 2, 4), (-1, 1, 3), (0, 2, 4)]
    for b_i in range(bars):
        c = chords[(b_i // 2) % 4]
        for k, dd in enumerate([c[0], c[1], c[2], c[1], c[2], c[1]]):
            f = deg(HICAZ_D, D4 / 2, dd)
            x = baglama(f, q * .9, .42 if k else .55, .8)
            p = -.35 + .14 * k
            place_loop(L, x * (1 - p) * .5, secs(b_i * bar + k * q / 2))
            place_loop(R, x * (1 + p) * .5, secs(b_i * bar + k * q / 2))
        x = deff(.45, zil=False)
        place_loop(L, x * .5, secs(b_i * bar))
        place_loop(R, x * .5, secs(b_i * bar))
        if b_i % 2:
            x = deff(.25, zil=False)
            place_loop(L, x * .5, secs(b_i * bar + 2 * q))
            place_loop(R, x * .5, secs(b_i * bar + 2 * q))
    # dem: alçak re perdesi
    t = np.arange(n) / SR
    drone = (np.sin(2 * np.pi * 73.4 * t) + .3 * np.sin(2 * np.pi * 146.8 * t)) * .025 * (1 + .2 * np.sin(2 * np.pi * t / bar))
    L += drone
    R += drone
    st = add_reverb(np.vstack([L, R]), .38, 3.2)
    return normalize(st, .72), bars * bar


# ---------------------------------------------------------------- parça 3: Şenlik (Hicaz, 9/8 Roman havası)
def track_senlik():
    e8 = .165
    bar = e8 * 9
    G4 = 392.0
    mel = [  # (derece, sekizlik) toplam 9
        [(4, 2), (5, 1), (4, 1), (3, 2), (2, 3)], [(3, 2), (2, 2), (1, 2), (2, 3)], [(1, 2), (2, 2), (3, 2), (4, 3)], [(4, 2), (3, 2), (2, 2), (1, 1), (0, 2)],
        [(0, 2), (2, 2), (4, 2), (5, 3)], [(6, 2), (5, 2), (4, 2), (3, 3)], [(4, 2), (3, 2), (2, 2), (1, 3)], [(0, 9)],
        [(7, 2), (7, 2), (6, 2), (5, 3)], [(6, 2), (6, 2), (5, 2), (4, 3)], [(5, 2), (4, 2), (3, 2), (2, 3)], [(3, 2), (2, 2), (1, 2), (2, 3)],
        [(4, 2), (5, 1), (4, 1), (3, 2), (2, 3)], [(3, 2), (2, 2), (1, 2), (0, 3)], [(1, 2), (2, 2), (1, 2), (2, 3)], [(0, 9)],
    ]
    form = mel + mel
    bars = len(form)
    n = secs(bars * bar)
    L = np.zeros(n)
    R = np.zeros(n)
    notes = []
    t = 0.0
    for b_i, b in enumerate(form):
        for d, ln in b:
            octv = 2 if b_i >= 16 and b_i % 16 >= 8 else 1
            notes.append((t, ln * e8 * .95, deg(HICAZ_G, G4, d) * (octv if octv == 1 else 1), .85))
            t += ln * e8
    kl = klarnet(notes)
    pl = pan(kl, .1)
    for ch, buf in ((0, L), (1, R)):
        m = min(n, pl.shape[1])
        buf[:m] += pl[ch][:m]
        if pl.shape[1] > n:
            buf[:pl.shape[1] - n] += pl[ch][n:]
    # bağlama ikinci ses (bir oktav aşağı, tezeneli)
    t = 0.0
    for b in form:
        for d, ln in b:
            for k in range(ln):
                x = baglama(deg(HICAZ_G, G4 / 2, d), e8 * .6, .55 if k else .75, 1.2)
                place_loop(L, x * .75, secs(t + k * e8))
                place_loop(R, x * .35, secs(t + k * e8))
            t += ln * e8
    # 9/8 ritim: düm . tek . düm . tek tek tek  (2+2+2+3)
    pat = [('d', 1), None, ('t', .8), ('k', .4), ('d', .9), ('k', .4), ('t', .8), ('t', .6), ('t', .7)]
    for b_i in range(bars):
        for k, hit in enumerate(pat):
            if not hit:
                continue
            kind, v = hit
            x = dum(v) if kind == 'd' else tek(v) if kind == 't' else ka(v)
            place_loop(L, x * .5, secs(b_i * bar + k * e8))
            place_loop(R, x * .5, secs(b_i * bar + k * e8))
        x = davul(.6)
        place_loop(L, x * .4, secs(b_i * bar))
        place_loop(R, x * .4, secs(b_i * bar))
        for k in (0, 4, 6):
            x = deff(.5)
            place_loop(L, x * .3, secs(b_i * bar + k * e8))
            place_loop(R, x * .45, secs(b_i * bar + k * e8))
    st = add_reverb(np.vstack([L, R]), .2, 1.8)
    return normalize(st, .8), bars * bar


# ---------------------------------------------------------------- ortam sesleri
def crossfade_loop(st, fade=1.5):
    """Sonun son 'fade' saniyesini başa karıştırarak dikişsiz döngü yapar."""
    f = secs(fade)
    head = st[:, :f]
    tail = st[:, -f:]
    w = np.linspace(0, 1, f)
    st = st[:, :-f].copy()
    st[:, :f] = head * w + tail * (1 - w)
    return st


def bird_chirp():
    n = secs(rng.uniform(.06, .16))
    t = np.arange(n) / SR
    f0 = rng.uniform(2600, 4200)
    f = f0 + rng.uniform(-900, 1400) * t / t[-1] + 300 * np.sin(2 * np.pi * rng.uniform(25, 60) * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) ** 2
    return x


def amb_ciftlik(dur=40):
    n = secs(dur + 1.5)
    L = np.zeros(n)
    R = np.zeros(n)
    t = np.arange(n) / SR
    wind = butter(noise(n), 'low', 500) * (.5 + .5 * np.sin(2 * np.pi * t / 13) ** 2) * .05
    leaves = butter(noise(n), 'band', (2500, 7000)) * (.3 + .7 * np.sin(2 * np.pi * t / 7.3 + 1) ** 4) * .012
    L += wind + leaves
    R += wind * .9 + leaves * 1.1
    k = 0.3
    while k < dur:
        p = rng.uniform(-.8, .8)
        burst = rng.integers(2, 6)
        for j in range(burst):
            x = bird_chirp() * rng.uniform(.04, .1)
            place(L, x * (1 - p) * .5, secs(k + j * .13))
            place(R, x * (1 + p) * .5, secs(k + j * .13))
        k += rng.uniform(.8, 3.2)
    # uzaktan horoz ve inek
    for when, kind in ((9, 'horoz'), (27, 'inek')):
        x = sfx_rooster() if kind == 'horoz' else sfx_moo()
        x = butter(x, 'low', 3000) * .18
        place(L, x * .6, secs(when))
        place(R, x * .4, secs(when))
    return crossfade_loop(np.vstack([L, R]))


def amb_gece(dur=30):
    n = secs(dur + 1.5)
    t = np.arange(n) / SR
    L = butter(noise(n), 'low', 380) * .03
    R = butter(noise(n), 'low', 380) * .03
    for c in range(5):
        fc = rng.uniform(4200, 5200)
        rate = rng.uniform(2.6, 4.2)
        ph = rng.random()
        gate = (np.sin(2 * np.pi * (rate * t + ph)) > .55).astype(float)
        trill = (np.sin(2 * np.pi * 38 * t) > 0).astype(float)
        env = signal.lfilter([.02], [1, -.98], gate * trill)
        x = np.sin(2 * np.pi * fc * t) * env * rng.uniform(.012, .025) * (.6 + .4 * np.sin(2 * np.pi * t / rng.uniform(5, 11)))
        p = rng.uniform(-.9, .9)
        L += x * (1 - p) * .5
        R += x * (1 + p) * .5
    for when in (6, 19):   # baykuş
        x = sfx_owl() * .12
        place(L, x * .4, secs(when))
        place(R, x * .6, secs(when))
    return crossfade_loop(np.vstack([L, R]))


def amb_firin(dur=24):
    n = secs(dur + 1.5)
    t = np.arange(n) / SR
    roar = butter(noise(n), 'low', 260) * (.7 + .3 * np.sin(2 * np.pi * t / 3.7)) * .07
    L = roar.copy()
    R = roar.copy()
    k = 0.0
    while k < dur:
        m = secs(rng.uniform(.004, .02))
        x = butter(noise(m), 'band', (800, 5000)) * np.exp(-np.arange(m) / SR * rng.uniform(150, 400)) * rng.uniform(.05, .25)
        p = rng.uniform(-.6, .6)
        place(L, x * (1 - p) * .5, secs(k))
        place(R, x * (1 + p) * .5, secs(k))
        k += rng.exponential(.12)
    return crossfade_loop(np.vstack([L, R]))


def amb_yagmur(dur=24):
    n = secs(dur + 1.5)
    L = butter(noise(n), 'band', (400, 9000)) * .06
    R = butter(noise(n), 'band', (400, 9000)) * .06
    k = 0.0
    while k < dur:
        m = secs(.03)
        tt = np.arange(m) / SR
        x = np.sin(2 * np.pi * rng.uniform(1500, 4000) * tt * (1 - tt * 8)) * np.exp(-tt * 140) * rng.uniform(.03, .1)
        p = rng.uniform(-1, 1)
        place(L, x * (1 - p) * .5, secs(k))
        place(R, x * (1 + p) * .5, secs(k))
        k += rng.exponential(.03)
    return crossfade_loop(np.vstack([L, R]))


# ---------------------------------------------------------------- ses efektleri
def tone_sweep(f0, f1, dur, kind='sine', curve='exp'):
    n = secs(dur)
    t = np.arange(n) / SR
    f = np.geomspace(f0, f1, n) if curve == 'exp' else np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'sine':
        return np.sin(ph)
    if kind == 'tri':
        return signal.sawtooth(ph, .5)
    if kind == 'saw':
        return signal.sawtooth(ph)
    return signal.square(ph)


def bell(f, dur=.6, bright=1.):
    n = secs(dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 5), (2.01, .5 * bright, 8), (2.76, .35 * bright, 11), (4.07, .2 * bright, 16), (5.4, .1 * bright, 22)):
        x += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec / dur * .6)
    x[:secs(.002)] *= np.linspace(0, 1, secs(.002))
    return x


def fade(x, a=.002, r=.01):
    a, r = secs(a), secs(r)
    x = x.copy()
    x[:a] *= np.linspace(0, 1, a)
    x[-r:] *= np.linspace(1, 0, r)
    return x


def sfx_pick():
    x = tone_sweep(520, 980, .07) * np.exp(-np.arange(secs(.07)) / SR * 30)
    return fade(x) * .5


def sfx_drop():
    n = secs(.09)
    t = np.arange(n) / SR
    x = tone_sweep(330, 150, .09) * np.exp(-t * 40) + butter(noise(n), 'low', 1800) * np.exp(-t * 70) * .4
    return fade(x) * .55


def sfx_chop():
    n = secs(.14)
    t = np.arange(n) / SR
    f = np.geomspace(1800, 6500, n)
    x = np.zeros(n)
    for i in range(0, n, 256):
        x[i:i + 256] = butter(noise(min(256, n - i)), 'band', (f[i] * .7, f[i] * 1.3), 1)
    x *= np.sin(np.pi * t / t[-1]) ** 1.5
    return fade(x) * .5


def sfx_splash():
    n = secs(.35)
    t = np.arange(n) / SR
    x = butter(noise(n), 'band', (500, 4000)) * np.exp(-t * 9) * .4
    for k in range(6):
        b = tone_sweep(rng.uniform(600, 1400), rng.uniform(1600, 2600), .04) * np.exp(-np.arange(secs(.04)) / SR * 60)
        place(x, b * .5, secs(rng.uniform(0, .25)))
    return fade(x) * .6


def sfx_egg():
    x = bell(1900, .12, .4) * .3
    place(x, bell(1200, .1, .2) * .2, 0)
    return fade(x)


def sfx_milk():
    n = secs(.25)
    t = np.arange(n) / SR
    x = butter(noise(n), 'band', (1500, 5000)) * np.exp(-t * 14) * (1 + .5 * np.sin(2 * np.pi * 28 * t))
    return fade(x) * .4


def sfx_coin():
    x = np.zeros(secs(.45))
    place(x, bell(2093, .3, .8), 0)
    place(x, bell(2794, .4, .8) * .8, secs(.06))
    return fade(x) * .32


def sfx_cash():
    x = np.zeros(secs(.7))
    n = secs(.12)
    drawer = butter(noise(n), 'band', (300, 2500)) * np.exp(-np.arange(n) / SR * 25) * .5
    place(x, drawer, 0)
    place(x, bell(1568, .5) * .45, secs(.08))
    place(x, bell(2093, .55) * .45, secs(.16))
    return fade(x) * .5


def sfx_ding():
    x = np.zeros(secs(.8))
    place(x, bell(1318, .7) * .5, 0)
    place(x, bell(1975, .7) * .4, secs(.09))
    return fade(x) * .45


def sfx_unlock():
    x = np.zeros(secs(1.3))
    for i, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
        place(x, baglama(f, .5, 1.1, 1.4) * 2.2, secs(i * .08))
        place(x, bell(f * 2, .6, .6) * .25, secs(i * .08))
    sh = butter(noise(secs(.6)), 'high', 7000) * np.exp(-np.arange(secs(.6)) / SR * 6) * .08
    place(x, sh, secs(.3))
    return fade(x, r=.1) * .6


def sfx_gold():
    x = np.zeros(secs(1.1))
    for i, f in enumerate([1046.5, 1318.5, 1568, 2093, 2637]):
        place(x, bell(f, .5, .7) * (.35 - i * .03), secs(i * .055))
    sh = butter(noise(secs(.8)), 'high', 8000) * np.exp(-np.arange(secs(.8)) / SR * 5) * np.abs(np.sin(np.arange(secs(.8)) / SR * 40)) * .1
    place(x, sh, secs(.1))
    return fade(x, r=.1) * .55


def sfx_good():
    x = baglama(659.25, .35, 1., 1.2) * 2.5
    return fade(x[:secs(.6)], r=.08) * .5


def sfx_miss():
    n = secs(.35)
    x = tone_sweep(300, 120, .35, 'tri') * np.exp(-np.arange(n) / SR * 8)
    x = butter(x, 'low', 1200)
    return fade(x) * .5


def sfx_angry():
    n = secs(.32)
    t = np.arange(n) / SR
    x = tone_sweep(230, 140, .32, 'saw')
    x = butter(x, 'band', (300, 1500)) * np.sin(np.pi * t / t[-1]) * .7
    return fade(x) * .45


def sfx_no():
    x = np.zeros(secs(.28))
    b = butter(tone_sweep(180, 170, .1, 'square'), 'low', 900) * .5
    place(x, b, 0)
    place(x, b, secs(.14))
    return fade(x) * .4


def sfx_pay():
    return fade(bell(2600, .1, .6)) * .2


def sfx_oven():
    n = secs(.6)
    t = np.arange(n) / SR
    x = butter(noise(n), 'low', 900) * np.sin(np.pi * t / t[-1]) ** 2
    x += butter(noise(n), 'band', (2000, 6000)) * (rng.random(n) > .996) * 3
    return fade(x) * .45


def sfx_alert():
    x = np.zeros(secs(.9))
    place(x, bell(880, .45) * .45, 0)
    place(x, bell(659.25, .55) * .45, secs(.22))
    place(x, dum(.5) * .6, 0)
    return fade(x, r=.08) * .55


def sfx_crow():
    x = np.zeros(secs(.8))
    for k in range(2):
        n = secs(.22)
        t = np.arange(n) / SR
        f = 620 * (1 - .25 * t / t[-1])
        s = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) + .3 * noise(n)
        s = butter(s, 'band', (900, 2600)) * np.sin(np.pi * t / t[-1]) ** .6
        place(x, s * .6, secs(k * .32))
    return fade(x) * .55


def sfx_fox():
    x = np.zeros(secs(.6))
    for k in range(2):
        n = secs(.12)
        t = np.arange(n) / SR
        s = tone_sweep(900, 1500, .12, 'saw')
        s = butter(s, 'band', (900, 3500)) * np.sin(np.pi * t / t[-1])
        place(x, s * .5, secs(k * .2))
    return fade(x) * .5


def sfx_clean():
    n = secs(.5)
    t = np.arange(n) / SR
    x = butter(noise(n), 'band', (1500, 6000)) * (np.abs(np.sin(2 * np.pi * 7 * t)) ** 3) * .5
    return fade(x) * .5


def sfx_level():
    x = np.zeros(secs(.9))
    for i, f in enumerate([392, 523.25, 659.25]):
        place(x, baglama(f, .35, 1.2, 1.3) * 2.2, secs(i * .1))
    return fade(x, r=.08) * .55


def sfx_dayend():
    x = np.zeros(secs(1.8))
    seq = [(0, 659.25), (.18, 587.3), (.36, 554.4), (.54, 587.3), (.9, 440)]
    for tt, f in seq:
        place(x, baglama(f, .4, 1.1, 1.2) * 2, secs(tt))
    return fade(x, r=.2) * .55


def sfx_click():
    n = secs(.03)
    return fade(butter(noise(n), 'band', (1500, 5000)) * np.exp(-np.arange(n) / SR * 200)) * .4


def sfx_horn():
    x = np.zeros(secs(.6))
    for k, f in enumerate((415, 349)):
        n = secs(.22)
        s = butter(signal.square(2 * np.pi * f * np.arange(n) / SR) + signal.square(2 * np.pi * f * 1.26 * np.arange(n) / SR), 'low', 2200)
        place(x, fade(s) * .25, secs(k * .26))
    return x


def sfx_moo():
    n = secs(.9)
    t = np.arange(n) / SR
    f = 140 - 30 * t / t[-1] + 6 * np.sin(2 * np.pi * 5 * t)
    s = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    s = butter(s, 'band', (200, 900)) + butter(s, 'band', (700, 1400)) * .5
    return fade(s * np.sin(np.pi * t / t[-1]) ** .5 * .6, r=.1)


def sfx_rooster():
    n = secs(1.1)
    t = np.arange(n) / SR
    f = np.interp(t, [0, .15, .35, .8, 1.1], [500, 900, 1050, 950, 600])
    s = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) + .2 * noise(n)
    s = butter(s, 'band', (700, 3200)) * np.interp(t, [0, .05, .9, 1.1], [0, 1, .8, 0])
    return s * .5


def sfx_owl():
    x = np.zeros(secs(1.4))
    for k, (st_, d) in enumerate(((0, .25), (.4, .5))):
        n = secs(d)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * np.cumsum(390 - 30 * t / d) / SR) * np.sin(np.pi * t / d) ** 2
        place(x, s * .5, secs(st_))
    return x


def sfx_cluck():
    x = np.zeros(secs(.5))
    for k in range(3):
        n = secs(.07)
        s = butter(tone_sweep(700, 450, .07, 'saw'), 'band', (500, 2500)) * np.hanning(n)
        place(x, s * .5, secs(k * .11))
    return x


SFX = {
    'pick': sfx_pick, 'drop': sfx_drop, 'chop': sfx_chop, 'splash': sfx_splash, 'egg': sfx_egg, 'milk': sfx_milk,
    'coin': sfx_coin, 'cash': sfx_cash, 'ding': sfx_ding, 'unlock': sfx_unlock, 'gold': sfx_gold, 'good': sfx_good,
    'miss': sfx_miss, 'angry': sfx_angry, 'no': sfx_no, 'pay': sfx_pay, 'oven': sfx_oven, 'alert': sfx_alert,
    'crow': sfx_crow, 'fox': sfx_fox, 'clean': sfx_clean, 'level': sfx_level, 'dayend': sfx_dayend, 'click': sfx_click,
    'horn': sfx_horn, 'moo': sfx_moo, 'cluck': sfx_cluck,
}


def encode(ffmpeg, wav, mp3, kbps=112):
    subprocess.run([ffmpeg, '-y', '-loglevel', 'error', '-i', wav, '-codec:a', 'libmp3lame', '-b:a', f'{kbps}k', mp3], check=True)


def main():
    ffmpeg = sys.argv[1]
    os.makedirs(os.path.join(OUT, 'sfx'), exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    meta = {}
    for name, fn in (('sabah', track_sabah), ('aksam', track_aksam), ('senlik', track_senlik)):
        st, length = fn()
        wav = os.path.join(TMP, name + '.wav')
        write_wav(wav, st)
        encode(ffmpeg, wav, os.path.join(OUT, 'muzik-' + name + '.mp3'), 128)
        meta['muzik-' + name] = round(st.shape[1] / SR, 4)
        print('muzik', name, round(length, 1), 'sn')
    for name, fn in (('ciftlik', amb_ciftlik), ('gece', amb_gece), ('firin', amb_firin), ('yagmur', amb_yagmur)):
        st = normalize(fn(), .5)
        wav = os.path.join(TMP, 'ortam-' + name + '.wav')
        write_wav(wav, st)
        encode(ffmpeg, wav, os.path.join(OUT, 'ortam-' + name + '.mp3'), 96)
        meta['ortam-' + name] = round(st.shape[1] / SR, 4)
        print('ortam', name)
    for name, fn in SFX.items():
        x = fn()
        x = x / max(1e-9, np.max(np.abs(x))) * .9   # oyun her efektin seviyesini kendisi ayarlar
        write_wav(os.path.join(OUT, 'sfx', name + '.wav'), x.astype(float))
    print('efekt', len(SFX))
    with open(os.path.join(OUT, 'audio.json'), 'w', encoding='utf-8') as f:
        json.dump({'loops': meta, 'sfx': sorted(SFX)}, f)
    for p in glob.glob(os.path.join(TMP, '*.wav')):
        os.remove(p)
    os.rmdir(TMP)


if __name__ == '__main__':
    main()
