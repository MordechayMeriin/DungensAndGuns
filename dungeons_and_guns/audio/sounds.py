# -*- coding: utf-8 -*-
"""מנוע צלילים למשחק.

הקולות לא מגיעים מקבצים - הם מחושבים כאן בתוך הקוד בזמן פתיחת המשחק
(רעש לירייה, צליל יורד למוות, צלילים עולים לאיסוף וכו').
אם אין כרטיס קול במחשב, הכל פשוט שקט והמשחק ממשיך לעבוד.
"""

import array
import math
import random

import pygame

RATE = 22050


# ---------- לבני בניין של גלי קול ----------
def tone(freq, dur, kind="sine", vol=1.0, sweep_to=None):
    """צליל בגובה מסוים. sweep_to מחליק את הגובה עד לתדר אחר."""
    count = max(1, int(RATE * dur))
    out = []
    phase = 0.0
    for i in range(count):
        f = freq if sweep_to is None else freq + (sweep_to - freq) * i / count
        phase += 2.0 * math.pi * f / RATE
        if kind == "square":
            sample = 1.0 if math.sin(phase) >= 0 else -1.0
        elif kind == "saw":
            sample = ((phase / math.pi) % 2.0) - 1.0
        else:
            sample = math.sin(phase)
        out.append(sample * vol)
    return out


def noise(dur, vol=1.0):
    return [random.uniform(-1.0, 1.0) * vol for _ in range(max(1, int(RATE * dur)))]


def decay(samples, power=4.0, attack=0.003):
    """עוטף את הצליל: עלייה מהירה ואז דעיכה."""
    count = len(samples)
    rise = max(1, int(RATE * attack))
    out = []
    for i, sample in enumerate(samples):
        if i < rise:
            level = i / float(rise)
        else:
            level = math.exp(-power * (i - rise) / float(max(1, count - rise)))
        out.append(sample * level)
    return out


def lowpass(samples, alpha=0.2):
    """מעגל את הרעש - ככל ש-alpha קטן יותר הצליל עמום ונמוך יותר."""
    out = []
    prev = 0.0
    for sample in samples:
        prev += alpha * (sample - prev)
        out.append(prev)
    return out


def mix(*layers):
    length = max(len(layer) for layer in layers)
    out = [0.0] * length
    for layer in layers:
        for i, sample in enumerate(layer):
            out[i] += sample
    return out


def chain(*parts):
    out = []
    for part in parts:
        out.extend(part)
    return out


def scale(samples, factor):
    return [s * factor for s in samples]


# ---------- הקולות עצמם ----------
def gunshot(body, dur, bright=0.35, punch=1.0):
    crack = decay(lowpass(noise(dur), bright), power=5.5)
    thump = decay(tone(body, dur * 0.55, "square", 0.55, sweep_to=body * 0.4), power=7)
    return mix(scale(crack, punch), thump)


def whoosh(dur, bright=0.08, vol=0.7):
    return decay(lowpass(noise(dur, vol), bright), power=3.0, attack=dur * 0.35)


def blips(freqs, step=0.075, kind="sine", vol=0.55):
    parts = []
    for freq in freqs:
        parts.append(decay(tone(freq, step, kind, vol), power=4.5))
    return chain(*parts)


def build_library():
    """מחזיר מילון: שם הקול -> רשימת דגימות."""
    lib = {}

    # ירי של השחקן, לפי סוג הנשק
    lib["shot_pistol"] = gunshot(230, 0.10, 0.38)
    lib["shot_smg"] = gunshot(270, 0.07, 0.46, 0.9)
    lib["shot_rifle"] = gunshot(175, 0.13, 0.30, 1.05)
    lib["shot_shotgun"] = gunshot(95, 0.30, 0.18, 1.25)
    lib["shot_sniper"] = mix(gunshot(72, 0.34, 0.15, 1.3),
                             decay(lowpass(noise(0.34, 0.35), 0.05), power=2.0, attack=0.05))
    lib["shot_mg"] = gunshot(125, 0.11, 0.24, 1.1)
    lib["shot_bow"] = mix(decay(tone(320, 0.26, "saw", 0.5, sweep_to=110), power=5),
                          decay(noise(0.05, 0.3), power=8))
    lib["shot_sling"] = decay(tone(520, 0.12, "square", 0.4, sweep_to=180), power=7)
    lib["shot_shuriken"] = whoosh(0.16, 0.3, 0.5)

    # נשק קר וזריקות
    lib["swing"] = whoosh(0.2, 0.09, 0.8)
    lib["throw"] = whoosh(0.22, 0.06, 0.6)
    lib["explosion"] = mix(decay(lowpass(noise(0.75), 0.05), power=2.2),
                           decay(tone(70, 0.6, "sine", 0.9, sweep_to=28), power=2.6),
                           decay(noise(0.12, 0.8), power=6))
    lib["hiss"] = decay(lowpass(noise(0.9, 0.5), 0.5), power=1.4, attack=0.08)

    # פגיעות
    lib["hit"] = mix(decay(lowpass(noise(0.06), 0.55), power=9),
                     decay(tone(520, 0.05, "square", 0.35), power=9))
    lib["hurt"] = mix(decay(tone(300, 0.24, "saw", 0.55, sweep_to=110), power=4),
                      decay(noise(0.1, 0.35), power=7))
    lib["enemy_die"] = decay(tone(440, 0.38, "square", 0.45, sweep_to=70), power=3.2)

    # איסוף, קנייה ותיבות
    lib["pickup"] = blips([660, 990], 0.065)
    lib["buy"] = blips([880, 1320], 0.06)
    lib["crate_good"] = blips([523, 659, 880], 0.07)
    lib["crate_bad"] = blips([392, 294, 196], 0.1, "square", 0.5)
    lib["crate_empty"] = mix(decay(tone(120, 0.18, "sine", 0.5), power=6),
                             decay(lowpass(noise(0.12, 0.4), 0.12), power=7))
    lib["potion"] = blips([392, 523, 698], 0.06)
    lib["splash"] = mix(decay(lowpass(noise(0.32), 0.25), power=3.5),
                        decay(tone(700, 0.18, "sine", 0.3, sweep_to=1200), power=5))
    lib["sick"] = decay(tone(200, 0.5, "saw", 0.4, sweep_to=150), power=2.5)
    lib["no"] = blips([300, 220], 0.08, "square", 0.4)
    lib["tick"] = decay(tone(900, 0.035, "square", 0.35), power=10)

    # שלבים
    lib["level"] = blips([523, 659, 784, 1046], 0.085)
    lib["gameover"] = blips([392, 330, 262, 175], 0.16, "saw", 0.5)

    # ירי של אויבים - אותם קולות, עמומים ורחוקים יותר
    for name, base in (("enemy_pistol", "shot_pistol"), ("enemy_smg", "shot_smg"),
                       ("enemy_rifle", "shot_rifle"), ("enemy_shotgun", "shot_shotgun"),
                       ("enemy_sniper", "shot_sniper"), ("enemy_mg", "shot_mg")):
        lib[name] = scale(lowpass(lib[base], 0.28), 0.62)
    return lib


class SoundBank:
    """בונה את כל הקולות פעם אחת ומנגן אותם לפי שם."""

    def __init__(self, volume=0.6):
        global RATE
        self.enabled = False
        self.volume = volume
        self.channels = 1
        self.sounds = {}
        self.last_played = {}
        try:
            # pygame.init פותח את הערוץ בהגדרות שלו, אז סוגרים ופותחים מחדש
            pygame.mixer.quit()
            pygame.mixer.init(RATE, -16, 1, 512)
            setup = pygame.mixer.get_init()
            if not setup:
                return
            RATE, _, self.channels = setup       # בונים לפי מה שהכרטיס באמת נתן
            pygame.mixer.set_num_channels(24)
        except pygame.error:
            return                      # אין כרטיס קול - ממשיכים בשקט
        try:
            for name, samples in build_library().items():
                self.sounds[name] = self._to_sound(samples)
            self.enabled = True
        except (pygame.error, ValueError):
            self.sounds = {}

    def _to_sound(self, samples):
        buf = array.array("h")
        for sample in samples:
            value = sample * self.volume
            value = -1.0 if value < -1.0 else (1.0 if value > 1.0 else value)
            value = int(value * 30000)
            buf.append(value)
            if self.channels > 1:                # אותו קול בשני הרמקולים
                buf.append(value)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def play(self, name, gap=0):
        """מנגן קול. gap = כמה מילישניות לחכות לפני שאותו קול חוזר."""
        if not self.enabled or name not in self.sounds:
            return
        if gap:
            now = pygame.time.get_ticks()
            if now - self.last_played.get(name, -99999) < gap:
                return
            self.last_played[name] = now
        try:
            self.sounds[name].play()
        except pygame.error:
            pass

    def toggle(self):
        self.enabled = not self.enabled and bool(self.sounds)
        if not self.enabled:
            try:
                pygame.mixer.stop()
            except pygame.error:
                pass
        return self.enabled
