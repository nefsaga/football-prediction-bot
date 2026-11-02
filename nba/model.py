"""NBA periyot bazlı sayı tahmin modeli.

Maç öncesi:
  * Piyasa (açılış toplamı + handikap) -> takım toplam beklentisi
  * İstatistik (takım sayı ort. + rakibin yediği ort., sakatlık ayarı)
  * İkisi harmanlanır, sonra takımın çeyrek paylarına (lig ortalamasına
    doğru çekilmiş) dağıtılır.

Canlı:
  * Geçen süre ve skora göre tempo / verim düzeltmesi (küçük örneklem
    lig/ön-maç beklentisine doğru çekilir - "sıcak el" abartılmaz).
  * Kalan sayılar normal dağılım (varyans ~ ortalama) ile modellenir;
    skorlar tam sayı olduğu için süreklilik düzeltmesi yapılır.
  * Bahis sitesinin baremi ve oranları ile olasılık, adil oran, EV ve
    Kelly hesaplanır.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

VERI_DOSYASI = os.path.join(os.path.dirname(__file__), "games.json")

# --- Model sabitleri -------------------------------------------------------
PIYASA_AGIRLIK = 0.65      # ön maç: piyasa vs istatistik harmanı
CEYREK_PAY_AGIRLIK = 0.30  # takımın kendi çeyrek profiline verilen ağırlık
SD_KATSAYI = 1.04          # takım sayısı SD ~ 1.04*sqrt(ortalama) (çeyrek ~5.5, maç ~11)
TAKIM_KORELASYON = 0.35    # iki takımın sayıları (ortak tempo) -> maç toplam SD ~18, fark SD ~12.5
OT_CARPAN = 1.8            # normal dağılım beraberliği az tahmin eder (gerçek NBA uzatma oranı ~%6)
K_TEMPO_DK = 20.0          # canlı tempo düzeltmesi için ön bilgi gücü (dakika)
K_VERIM_DK = 36.0          # takımlar arası verim farkı için ön bilgi gücü (dakika)
CEYREK_DK = 12.0
UZATMA_DK = 5.0


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def veri_yukle(yol: str = VERI_DOSYASI) -> dict:
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Ön maç projeksiyonu
# ---------------------------------------------------------------------------
@dataclass
class Projeksiyon:
    ev: str
    dep: str
    ceyrek: dict  # takım -> [q1..q4] beklenen sayı
    detay: dict = field(default_factory=dict)

    def mac(self, t: str) -> float:
        return sum(self.ceyrek[t])


def _ceyrek_paylari(takim: dict, lig_pay: list[float]) -> list[float]:
    cs = takim.get("ceyrek_sayi")
    if not cs:
        return list(lig_pay)
    top = sum(cs)
    kendi = [c / top for c in cs]
    pay = [CEYREK_PAY_AGIRLIK * k + (1 - CEYREK_PAY_AGIRLIK) * l for k, l in zip(kendi, lig_pay)]
    s = sum(pay)
    return [p / s for p in pay]


def onmac_projeksiyon(veri: dict, mac_kodu: str) -> Projeksiyon:
    mac = veri["maclar"][mac_kodu]
    lig = veri["lig"]
    ev, dep = mac["ev"], mac["dep"]
    T = veri["takimlar"]
    ort = lig["takim_mac_ort"]

    # İstatistik tabanlı beklenti: (hücum + rakip savunma) - lig ort.
    ist = {}
    for t, r in ((ev, dep), (dep, ev)):
        hucum = T[t]["sayi_ort"] + T[t].get("sakatlik_ayari", 0.0)
        savunma = T[r]["yenen_ort"] - T[r].get("sakatlik_ayari", 0.0) * 0.3
        ist[t] = hucum + savunma - ort
    ist[ev] += 1.2   # ev sahibi avantajı (~2.4 puan fark)
    ist[dep] -= 1.2

    # Piyasa tabanlı beklenti
    p = mac.get("piyasa") or {}
    if "toplam" in p and "ev_handikap" in p:
        top, h = p["toplam"], p["ev_handikap"]
        piy = {ev: top / 2 - h / 2, dep: top / 2 + h / 2}
        w = PIYASA_AGIRLIK
    else:
        piy, w = ist, 0.0

    beklenen = {t: w * piy[t] + (1 - w) * ist[t] for t in (ev, dep)}

    ceyrek = {}
    for t in (ev, dep):
        pay = _ceyrek_paylari(T[t], lig["ceyrek_paylari"])
        ceyrek[t] = [beklenen[t] * x for x in pay]

    return Projeksiyon(ev, dep, ceyrek, {"istatistik": ist, "piyasa": piy, "piyasa_agirlik": w})


# ---------------------------------------------------------------------------
# Canlı durum
# ---------------------------------------------------------------------------
@dataclass
class CanliDurum:
    periyot: int            # 1-4, 5+ = uzatma
    kalan_dk: float         # mevcut periyotta kalan dakika
    skor: dict              # takım -> toplam sayı
    biten_ceyrekler: list   # [(ev, dep), ...] tamamlanmış periyot skorları
    bu_periyot: tuple | None = None  # (ev, dep) mevcut periyotta atılan sayılar (opsiyonel)

    @property
    def gecen_dk(self) -> float:
        if self.periyot <= 4:
            return CEYREK_DK * (self.periyot - 1) + (CEYREK_DK - self.kalan_dk)
        return 48.0 + UZATMA_DK * (self.periyot - 5) + (UZATMA_DK - self.kalan_dk)


def sure_parse(s: str) -> float:
    """'5:30' -> 5.5 dakika, '7' -> 7.0"""
    s = s.strip()
    if ":" in s:
        m, sn = s.split(":")
        return int(m) + float(sn) / 60.0
    return float(s)


def _periyot_dk(p: int) -> float:
    return CEYREK_DK if p <= 4 else UZATMA_DK


class Motor:
    """Ön maç projeksiyonu + (varsa) canlı durumu birleştirip
    herhangi bir periyot kümesi için dağılım verir."""

    def __init__(self, veri: dict, mac_kodu: str, canli: CanliDurum | None = None):
        self.veri = veri
        self.kod = mac_kodu
        self.proj = onmac_projeksiyon(veri, mac_kodu)
        self.ev, self.dep = self.proj.ev, self.proj.dep
        self.canli = canli
        self.uzatma_takim = veri["lig"].get("uzatma_takim_sayi", 11.0)
        self.carpan = {self.ev: 1.0, self.dep: 1.0}
        self.notlar: list[str] = []
        if canli:
            self._canli_duzeltme()

    # -- yardımcılar --
    def _periyot_ort(self, t: str, p: int) -> float:
        if p <= 4:
            return self.proj.ceyrek[t][p - 1]
        return self.uzatma_takim * (self.proj.mac(t) / self.veri["lig"]["takim_mac_ort"])

    def _beklenen_simdiye_kadar(self, t: str) -> float:
        c = self.canli
        top = sum(self._periyot_ort(t, p) for p in range(1, c.periyot))
        oran = 1 - c.kalan_dk / _periyot_dk(c.periyot)
        return top + self._periyot_ort(t, c.periyot) * oran

    def _canli_duzeltme(self):
        c = self.canli
        E = c.gecen_dk
        if E <= 0:
            return
        bek = {t: self._beklenen_simdiye_kadar(t) for t in (self.ev, self.dep)}
        gozl = {t: float(c.skor[t]) for t in (self.ev, self.dep)}
        bek_top, gozl_top = sum(bek.values()), sum(gozl.values())

        # 1) Ortak tempo/skor seviyesi (shrinkage)
        dk_basi = bek_top / E
        f_mac = (gozl_top + K_TEMPO_DK * dk_basi) / (bek_top + K_TEMPO_DK * dk_basi)

        # 2) Takımlar arası pay farkı (daha güçlü shrinkage)
        w = E / (E + K_VERIM_DK)
        for t in (self.ev, self.dep):
            if gozl_top > 0:
                r = (gozl[t] / gozl_top) / (bek[t] / bek_top)
            else:
                r = 1.0
            self.carpan[t] = f_mac * (1 + w * (r - 1))

        self.notlar.append(
            f"Şu ana kadar beklenen {bek_top:.1f}, gerçekleşen {gozl_top:.0f} sayı "
            f"-> kalan süre tempo çarpanı x{f_mac:.3f} "
            f"({self.ev} x{self.carpan[self.ev]:.3f}, {self.dep} x{self.carpan[self.dep]:.3f})"
        )

    def _gec_oyun_ayari(self, t: str, p: int, kalan_ort: float, kalan_dk_p: float) -> float:
        """4. çeyrek son dakikalar: yakın maçta faul oyunu (+), farklı maçta yedekler (-)."""
        if not self.canli or p != 4:
            return kalan_ort
        c = self.canli
        fark = abs(c.skor[self.ev] - c.skor[self.dep])
        if fark >= 18:
            return kalan_ort * 0.96
        if fark <= 6:
            # son 2 dakikada faul oyunu ~ takım başı +1.5 sayı
            son2 = min(2.0, kalan_dk_p)
            return kalan_ort + 1.5 * (son2 / 2.0)
        return kalan_ort

    def periyot_dagilim(self, t: str, p: int) -> tuple[float, float, float]:
        """(kesinleşmiş sayı, kalan beklenti, kalan varyans) — tek periyot, tek takım."""
        c = self.canli
        ort = self._periyot_ort(t, p)
        if not c or p > c.periyot:
            kalan = ort * self.carpan[t]
            kalan = self._gec_oyun_ayari(t, p, kalan, _periyot_dk(p)) if c else kalan
            return 0.0, kalan, SD_KATSAYI ** 2 * kalan
        if p < c.periyot:
            if len(c.biten_ceyrekler) >= p:
                ev_s, dep_s = c.biten_ceyrekler[p - 1]
                return float(ev_s if t == self.ev else dep_s), 0.0, 0.0
            raise ValueError(f"{p}. periyot skoru bilinmiyor (--ceyrekler ile verin)")
        # mevcut periyot
        if c.bu_periyot is not None:
            simdi = c.bu_periyot[0] if t == self.ev else c.bu_periyot[1]
        elif len(c.biten_ceyrekler) >= c.periyot - 1:
            once = sum((e if t == self.ev else d) for e, d in c.biten_ceyrekler[: c.periyot - 1])
            simdi = c.skor[t] - once
        else:
            raise ValueError("Mevcut periyot skoru bilinmiyor: --ceyrekler (biten periyotlar) "
                             "veya --bu-periyot (bu periyotta atılan) verin")
        oran = c.kalan_dk / _periyot_dk(p)
        kalan = ort * oran * self.carpan[t]
        kalan = self._gec_oyun_ayari(t, p, kalan, c.kalan_dk)
        return float(simdi), kalan, SD_KATSAYI ** 2 * kalan

    def segment(self, takimlar: list[str], periyotlar: list[int]) -> tuple[float, float, float]:
        """(kesinleşmiş, kalan ort, kalan SD) — takım(lar) toplamı."""
        kes = ort = 0.0
        var_t = {t: 0.0 for t in takimlar}
        c = self.canli
        if c and 4 in periyotlar and 1 in periyotlar and c.periyot >= 5:
            periyotlar = list(range(1, c.periyot + 1))
        # 1..mevcut periyot kümesi: periyot skorları olmadan toplam skordan hesapla
        tam_bas = bool(c) and all(p in periyotlar for p in range(1, c.periyot + 1)) \
            and len(c.biten_ceyrekler) < c.periyot - 1
        for t in takimlar:
            if tam_bas:
                kes += c.skor[t]
                p = c.periyot
                m = self._periyot_ort(t, p) * (c.kalan_dk / _periyot_dk(p)) * self.carpan[t]
                m = self._gec_oyun_ayari(t, p, m, c.kalan_dk)
                ort += m
                var_t[t] += SD_KATSAYI ** 2 * m
            for p in periyotlar:
                if tam_bas and p <= c.periyot:
                    continue
                k, m, v = self.periyot_dagilim(t, p)
                kes += k
                ort += m
                var_t[t] += v
        var = sum(var_t.values())
        if len(takimlar) == 2:
            a, b = (math.sqrt(var_t[x]) for x in takimlar)
            var += 2 * TAKIM_KORELASYON * a * b
        return kes, ort, math.sqrt(var)

    def _kalan_regulasyon(self, t: str) -> tuple[float, float]:
        """Normal sürenin kalanı için (ortalama, varyans) — periyot skoru gerektirmez."""
        c = self.canli
        bas = c.periyot if c else 1
        m = 0.0
        for p in range(bas, 5):
            ort = self._periyot_ort(t, p) * self.carpan[t]
            dk = _periyot_dk(p)
            if c and p == c.periyot:
                ort *= c.kalan_dk / dk
                dk = c.kalan_dk
            m += self._gec_oyun_ayari(t, p, ort, dk) if c else ort
        return m, SD_KATSAYI ** 2 * m

    def uzatma_olasiligi(self) -> float:
        """Normal süre sonunda beraberlik olasılığı."""
        c = self.canli
        if c and c.periyot >= 5:
            return 1.0
        me, ve = self._kalan_regulasyon(self.ev)
        md, vd = self._kalan_regulasyon(self.dep)
        se = c.skor[self.ev] if c else 0
        sd_ = c.skor[self.dep] if c else 0
        fark_ort = (se + me) - (sd_ + md)
        fark_sd = math.sqrt(max(ve + vd - 2 * TAKIM_KORELASYON * math.sqrt(ve * vd), 0.0) + 0.25)
        p = phi((0.5 - fark_ort) / fark_sd) - phi((-0.5 - fark_ort) / fark_sd)
        return min(0.95, p * OT_CARPAN)


# ---------------------------------------------------------------------------
# Bahis pazarları
# ---------------------------------------------------------------------------
PERIYOT_ADI = {"q1": [1], "q2": [2], "q3": [3], "q4": [4], "iy": [1, 2], "h1": [1, 2],
               "iy2": [3, 4], "h2": [3, 4], "mac": [1, 2, 3, 4]}


def pazar_coz(motor: Motor, anahtar: str) -> tuple[list[str], list[int], str]:
    """'q2_GSW', 'q3_toplam', 'iy_ev', 'mac_toplam' ..."""
    try:
        per, kim = anahtar.lower().split("_", 1)
    except ValueError:
        raise ValueError(f"Pazar biçimi hatalı: {anahtar} (örn. q2_ev, q3_toplam, mac_GSW)")
    if per not in PERIYOT_ADI:
        raise ValueError(f"Bilinmeyen periyot: {per} (q1-q4, iy, iy2, mac)")
    if kim in ("ev", "evsahibi", "e", "home", motor.ev.lower()):
        tk, ad = [motor.ev], motor.ev
    elif kim in ("dep", "deplasman", "d", "away", motor.dep.lower()):
        tk, ad = [motor.dep], motor.dep
    elif kim in ("toplam", "top", "total"):
        tk, ad = [motor.ev, motor.dep], "Toplam"
    else:
        raise ValueError(f"Bilinmeyen taraf: {kim} (ev, dep, toplam veya takım kodu)")
    etiket = {"q1": "1.Çeyrek", "q2": "2.Çeyrek", "q3": "3.Çeyrek", "q4": "4.Çeyrek",
              "iy": "İlk Yarı", "h1": "İlk Yarı", "iy2": "İkinci Yarı", "h2": "İkinci Yarı",
              "mac": "Maç"}[per]
    return tk, PERIYOT_ADI[per], f"{etiket} {ad}"


def ust_olasilik(motor: Motor, takimlar, periyotlar, barem: float, uzatma_dahil: bool = True):
    """(P(üst), P(alt), P(iade), ortalama, sd)"""
    kes, ort, sd = motor.segment(takimlar, periyotlar)

    def p_ust(mu, s):
        if s < 1e-6:
            tot = kes
            return (1.0 if tot > barem else 0.0), (1.0 if tot == barem else 0.0)
        if float(barem).is_integer():
            k = barem - kes  # tam bu sayı = iade
            pu = 1 - phi((k + 0.5 - mu) / s)
            pi = phi((k + 0.5 - mu) / s) - phi((k - 0.5 - mu) / s)
            return pu, pi
        k = math.ceil(barem) - kes
        return 1 - phi((k - 0.5 - mu) / s), 0.0

    pu, pi = p_ust(ort, sd)
    toplam_ort = kes + ort
    # Uzatma: maç ve 2. yarı pazarlarında dahil (sitelerin çoğu böyle), 4. çeyrek pazarında değil
    if uzatma_dahil and 4 in periyotlar and len(periyotlar) > 1:
        p_ot = motor.uzatma_olasiligi()
        if p_ot < 1.0:
            ek = sum(motor._periyot_ort(t, 5) for t in takimlar)
            ek_sd = math.sqrt(sd ** 2 + SD_KATSAYI ** 2 * ek)
            pu2, pi2 = p_ust(ort + ek, ek_sd)
            pu = (1 - p_ot) * pu + p_ot * pu2
            pi = (1 - p_ot) * pi + p_ot * pi2
            toplam_ort += p_ot * ek
    return pu, max(0.0, 1 - pu - pi), pi, toplam_ort, sd


def bahis_degerlendir(p_ust, p_alt, p_iade, oran_ust, oran_alt):
    """Her taraf için EV ve Kelly; iade durumunda para geri gelir."""
    sonuc = {}
    for ad, p, o in (("ÜST", p_ust, oran_ust), ("ALT", p_alt, oran_alt)):
        if not o:
            continue
        ev = p * o + p_iade - 1.0
        b = o - 1.0
        q = 1.0 - p - p_iade
        kelly = max(0.0, (b * p - q) / b) if b > 0 else 0.0
        adil = (1.0 - p_iade) / p if p > 0 else float("inf")
        sonuc[ad] = {"olasilik": p, "oran": o, "adil_oran": adil, "ev": ev, "kelly": kelly}
    if oran_ust and oran_alt:
        imp_u, imp_a = 1 / oran_ust, 1 / oran_alt
        marj = imp_u + imp_a - 1
        sonuc["_piyasa"] = {"marj": marj, "ust_vigsiz": imp_u / (imp_u + imp_a)}
    return sonuc


def adil_barem(motor: Motor, takimlar, periyotlar, uzatma_dahil=True):
    """P(üst) ~ %50 olan .5'lik barem (periyot bittiyse None)."""
    _, _, _, mu, sd = ust_olasilik(motor, takimlar, periyotlar, 0.5, uzatma_dahil)
    if sd < 0.5:
        return None
    best, fark = None, 9
    base = math.floor(mu) + 0.5
    for d in range(-6, 7):
        b = base + d
        pu = ust_olasilik(motor, takimlar, periyotlar, b, uzatma_dahil)[0]
        if abs(pu - 0.5) < fark:
            best, fark = b, abs(pu - 0.5)
    return best
