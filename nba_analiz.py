#!/usr/bin/env python3
"""NBA periyot bazlı üst/alt analiz aracı.

Örnekler:
  python nba_analiz.py liste
  python nba_analiz.py onmac GSW-LAC
  python nba_analiz.py onmac LAL-TOR -b "q1_LAL 29.5 1.85 1.95"

  # Canlı: 2. çeyrek, 5:30 kaldı, toplam skor 52-47, 1. çeyrek 28-25 bitti
  python nba_analiz.py canli GSW-LAC -p 2 -k 5:30 -s 52-47 -c 28-25 \\
      -b "q2_GSW 27.5 1.85 1.95" -b "q2_toplam 54.5 1.87 1.87" -b "mac_toplam 218.5 1.90 1.90"

Pazar anahtarları: <periyot>_<taraf>
  periyot : q1 q2 q3 q4 iy (ilk yarı) iy2 (ikinci yarı) mac
  taraf   : ev | dep | toplam | takım kodu (GSW, LAC, LAL, TOR)
Bahis:   "<pazar> <barem> <üst oranı> <alt oranı>"  (ondalık oran; alt oranı opsiyonel)
Çeyrek skorlarını bilmiyorsanız sadece bu periyodun skorunu -bp 14-11 ile verebilirsiniz.
"""

from __future__ import annotations

import argparse
import sys

from nba.model import (CanliDurum, Motor, adil_barem, bahis_degerlendir, pazar_coz,
                       sure_parse, ust_olasilik, veri_yukle)

EV_ESIK = 0.03   # %3 üzeri beklenen değer = "değer var"
KELLY_TAVAN = 5.0  # stake önerisi: 1/4 Kelly, en fazla kasanın %5'i


def _skor_parse(s: str, motor_ev: str, motor_dep: str) -> dict:
    a, b = s.replace(":", "-").split("-")
    return {motor_ev: int(a), motor_dep: int(b)}


def _ceyrek_parse(s: str | None) -> list:
    if not s:
        return []
    out = []
    for parca in s.split(","):
        a, b = parca.strip().replace(":", "-").split("-")
        out.append((int(a), int(b)))
    return out


def _yazdir_projeksiyon(m: Motor):
    ev, dep = m.ev, m.dep
    canli = m.canli is not None
    print(f"\n{'Periyot':<10}{ev:>8}{dep:>8}{'Toplam':>9}{'Adil barem (E/D/Top)':>26}")
    print("-" * 61)
    for ad, per in (("1.Çeyrek", [1]), ("2.Çeyrek", [2]), ("3.Çeyrek", [3]), ("4.Çeyrek", [4]),
                    ("İlk Yarı", [1, 2]), ("2. Yarı", [3, 4]), ("Maç*", [1, 2, 3, 4])):
        try:
            se = m.segment([ev], per)
            sd = m.segment([dep], per)
        except ValueError:
            print(f"{ad:<10}{'(periyot skoru yok)':>40}")
            continue
        e, d = se[0] + se[1], sd[0] + sd[1]
        bar = [adil_barem(m, [ev], per, False), adil_barem(m, [dep], per, False),
               adil_barem(m, [ev, dep], per, False)]
        bar = ["bitti" if x is None else x for x in bar]
        print(f"{ad:<10}{e:>8.1f}{d:>8.1f}{e + d:>9.1f}{bar[0]:>10}{bar[1]:>8}{bar[2]:>8}")
    p_ot = m.uzatma_olasiligi()
    print(f"* Maç satırı normal süre. Uzatma olasılığı: %{100 * p_ot:.1f}"
          + ("" if canli else ""))


def _yazdir_bahisler(m: Motor, bahisler: list[str], uzatma: bool):
    if not bahisler:
        return
    print("\n" + "=" * 61)
    print("BAHİS DEĞERLENDİRMESİ")
    print("=" * 61)
    ozet = []
    for b in bahisler:
        parca = b.split()
        if len(parca) < 3:
            print(f"! Hatalı bahis girdisi: '{b}' -> \"pazar barem üst_oran [alt_oran]\"")
            continue
        anahtar, barem, o_ust = parca[0], float(parca[1].replace(",", ".")), float(parca[2].replace(",", "."))
        o_alt = float(parca[3].replace(",", ".")) if len(parca) > 3 else None
        try:
            tk, per, etiket = pazar_coz(m, anahtar)
            pu, pa, pi, mu, sd = ust_olasilik(m, tk, per, barem, uzatma)
        except ValueError as e:
            print(f"! {anahtar}: {e}")
            continue
        sonuc = bahis_degerlendir(pu, pa, pi, o_ust, o_alt)
        kes = m.segment(tk, per)[0] if m.canli else 0
        print(f"\n▶ {etiket}  barem {barem}")
        durum = f"  Model beklentisi: {mu:.1f} (±{sd:.1f})"
        if m.canli and kes:
            durum += f"  | şu an: {kes:.0f}, kalan beklenti: {mu - kes:.1f}"
        print(durum)
        if pi > 0.001:
            print(f"  İade (tam barem) olasılığı: %{100 * pi:.1f}")
        if "_piyasa" in sonuc:
            pz = sonuc["_piyasa"]
            print(f"  Site marjı: %{100 * pz['marj']:.1f} | sitenin vigsiz ÜST olasılığı: %{100 * pz['ust_vigsiz']:.1f}")
        en_iyi = None
        for taraf in ("ÜST", "ALT"):
            if taraf not in sonuc:
                continue
            s = sonuc[taraf]
            isaret = "✅" if s["ev"] > EV_ESIK else ("➖" if s["ev"] > 0 else "❌")
            print(f"  {isaret} {taraf:<4} olasılık %{100 * s['olasilik']:5.1f} | oran {s['oran']:.2f} "
                  f"| adil oran {s['adil_oran']:.2f} | EV {100 * s['ev']:+.1f}% "
                  f"| stake: kasanın %{min(25 * s['kelly'], KELLY_TAVAN):.1f}")
            if en_iyi is None or s["ev"] > en_iyi[1]["ev"]:
                en_iyi = (taraf, s)
        if en_iyi:
            t, s = en_iyi
            if s["ev"] > EV_ESIK:
                karar = f"DEĞER VAR -> {t} {barem} @ {s['oran']:.2f} (EV {100 * s['ev']:+.1f}%)"
            elif s["ev"] > 0:
                karar = f"Hafif avantaj {t} (EV {100 * s['ev']:+.1f}%) - sınırda, pas geçilebilir"
            else:
                yuksek = "ÜST" if pu > pa else "ALT"
                karar = f"Değer yok - daha olası taraf {yuksek} ama oran karşılamıyor -> PAS"
            print(f"  ➜ {karar}")
            ozet.append((s["ev"], etiket, barem, t, s))
    if len(ozet) > 1:
        print("\nSIRALAMA (EV'ye göre):")
        for ev, etiket, barem, t, s in sorted(ozet, reverse=True):
            print(f"  {100 * ev:+6.1f}%  {etiket} {t} {barem} @ {s['oran']:.2f}  (olasılık %{100 * s['olasilik']:.1f})")


def cmd_liste(veri, _args):
    for kod, mac in veri["maclar"].items():
        ev, dep = veri["takimlar"][mac["ev"]]["ad"], veri["takimlar"][mac["dep"]]["ad"]
        print(f"{kod:<9} {mac['baslama_tsi']} TSİ  {ev} v {dep}  ({mac['salon']})")


def cmd_onmac(veri, args):
    m = Motor(veri, args.mac)
    mac = veri["maclar"][args.mac]
    T = veri["takimlar"]
    print(f"=== {T[m.ev]['ad']} v {T[m.dep]['ad']} | {mac['baslama_tsi']} TSİ ===")
    d = m.proj.detay
    print(f"İstatistik modeli : {m.ev} {d['istatistik'][m.ev]:.1f} - {m.dep} {d['istatistik'][m.dep]:.1f}")
    print(f"Piyasa (açılış)   : {m.ev} {d['piyasa'][m.ev]:.1f} - {m.dep} {d['piyasa'][m.dep]:.1f}"
          f"   [{mac.get('piyasa_kaynak', '')}]")
    print(f"Harman (piyasa %{100 * d['piyasa_agirlik']:.0f})")
    for t in (m.ev, m.dep):
        print(f"  Sakatlar {t}: {T[t].get('sakatlar', '-')}")
    if mac.get("not"):
        print(f"  Not: {mac['not']}")
    _yazdir_projeksiyon(m)
    _yazdir_bahisler(m, args.bahis or [], not args.uzatmasiz)


def cmd_canli(veri, args):
    mac = veri["maclar"][args.mac]
    ev, dep = mac["ev"], mac["dep"]
    durum = CanliDurum(
        periyot=args.periyot,
        kalan_dk=sure_parse(args.kalan),
        skor=_skor_parse(args.skor, ev, dep),
        biten_ceyrekler=_ceyrek_parse(args.ceyrekler),
        bu_periyot=(tuple(_ceyrek_parse(args.bu_periyot)[0]) if args.bu_periyot else None),
    )
    if durum.biten_ceyrekler:
        top_e = sum(a for a, _ in durum.biten_ceyrekler)
        top_d = sum(b for _, b in durum.biten_ceyrekler)
        if top_e > durum.skor[ev] or top_d > durum.skor[dep]:
            sys.exit("Hata: biten çeyrek toplamı mevcut skordan büyük olamaz.")
    m = Motor(veri, args.mac, durum)
    T = veri["takimlar"]
    print(f"=== CANLI: {T[ev]['ad']} {durum.skor[ev]} - {durum.skor[dep]} {T[dep]['ad']} "
          f"| {args.periyot}. periyot, {args.kalan} kaldı ===")
    for n in m.notlar:
        print("  " + n)
    _yazdir_projeksiyon(m)
    _yazdir_bahisler(m, args.bahis or [], not args.uzatmasiz)


def main(argv=None):
    ap = argparse.ArgumentParser(description="NBA periyot bazlı üst/alt analiz",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--veri", help="games.json yolu (varsayılan nba/games.json)")
    sub = ap.add_subparsers(dest="komut", required=True)

    sub.add_parser("liste", help="Tanımlı maçlar")

    def ortak(p):
        p.add_argument("mac", help="Maç kodu, örn. GSW-LAC")
        p.add_argument("-b", "--bahis", action="append",
                       help='"pazar barem üst_oran [alt_oran]"  örn. "q2_GSW 27.5 1.85 1.95"')
        p.add_argument("--uzatmasiz", action="store_true",
                       help="Maç toplamı baremlerinde uzatmayı dahil etme")

    p1 = sub.add_parser("onmac", help="Maç öncesi periyot projeksiyonu")
    ortak(p1)

    p2 = sub.add_parser("canli", help="Canlı skorla güncel analiz")
    ortak(p2)
    p2.add_argument("-p", "--periyot", type=int, required=True, help="Mevcut periyot (1-4, 5=uzatma)")
    p2.add_argument("-k", "--kalan", required=True, help="Periyotta kalan süre, örn. 5:30")
    p2.add_argument("-s", "--skor", required=True, help="Toplam skor ev-dep, örn. 52-47")
    p2.add_argument("-c", "--ceyrekler", help="Biten periyot skorları, örn. 28-25,30-27")
    p2.add_argument("-bp", "--bu-periyot", help="Mevcut periyotta atılan sayılar ev-dep, örn. 14-11 "
                    "(--ceyrekler yerine, sadece bu periyot pazarları için)")

    args = ap.parse_args(argv)
    veri = veri_yukle(args.veri) if args.veri else veri_yukle()
    if getattr(args, "mac", None):
        args.mac = args.mac.upper()
        if args.mac not in veri["maclar"]:
            sys.exit(f"Bilinmeyen maç: {args.mac}. Mevcut: {', '.join(veri['maclar'])}")
    {"liste": cmd_liste, "onmac": cmd_onmac, "canli": cmd_canli}[args.komut](veri, args)


if __name__ == "__main__":
    main()
