# NBA Periyot Üst/Alt Analizi

Bir NBA maçında her takımın periyot periyot kaç sayı atacağını tahmin eder. Maç başladıktan sonra canlı skoru ve bahis sitesinin barem/oranlarını girersin, araç da hangi tarafın (ÜST/ALT) daha olası olduğunu ve oranın buna değip değmediğini söyler.

## Model nasıl çalışıyor?

1. **Maç öncesi:** İki kaynak harmanlanır, %65 piyasa ve %35 istatistik:
   - Piyasa: açılış toplamı ve handikaptan çıkan takım toplamları.
   - İstatistik: takımın attığı ortalama ile rakibin yediği ortalama. Buna sakatlık ayarı ve ev sahibi avantajı eklenir.

   Çıkan takım toplamı çeyreklere dağıtılır. Takımın kendi çeyrek profilinin ağırlığı %30, lig ortalamasınınki %70'tir (örneklem küçük).
2. **Canlı:** Geçen süre ve skora göre tempo çarpanı hesaplanır. Bu çarpan küçük örnekleme fazla güvenmemek için ön beklentiye doğru çekilir: 20 dakika oynanmışsa sapmanın yaklaşık yarısı kabul edilir.
   - 4. çeyrekte fark 6 sayı veya daha azsa son 2 dakikaya faul oyunu payı eklenir.
   - Fark 18 sayı veya daha fazlaysa yedekler oyunda varsayılır ve tempo %4 düşürülür.
3. **Dağılım:** Takımın periyot sayısı normal dağılımla modellenir. SD yaklaşık 1.04·√ortalama'dır, yani çeyrekte ±5.5, maçta ±11. İki takım arası korelasyon 0.35 alınır; bu da maç toplamında ±18, farkta ±12.5 eder. Tam sayılı (iade olan) baremler doğru hesaplanır.
4. **Uzatma:** Maç ve 2. yarı pazarlarında dahildir, 4. çeyrek pazarında değildir. İstersen `--uzatmasiz` ile kapatabilirsin.
5. **Bahis kararı:** Önce sitenin marjı ve vigsiz olasılığı çıkarılır. Sonra modelin olasılığı, adil oran ve EV hesaplanır. EV %3'ün üzerindeyse "DEĞER VAR" yazar. Stake önerisi 1/4 Kelly'dir ve en fazla kasanın %5'idir.

## Kullanım

```bash
python nba_analiz.py liste
python nba_analiz.py onmac GSW-LAC
python nba_analiz.py onmac LAL-TOR -b "q1_LAL 29.5 1.85 1.95"

# Canlı: 2. çeyrek, 5:30 kaldı, skor 52-47, 1. çeyrek 30-25 bitti
python nba_analiz.py canli GSW-LAC -p 2 -k 5:30 -s 52-47 -c 30-25 \
    -b "q2_GSW 27.5 1.85 1.95" -b "q2_toplam 54.5 1.87 1.87" -b "mac_toplam 224.5 1.90 1.90"

# Çeyrek skorlarını bilmiyorsan sadece bu periyodun skorunu ver
python nba_analiz.py canli LAL-TOR -p 4 -k 1:10 -s 110-108 -bp 22-24 -b "q4_LAL 25.5 1.9 1.9"
```

**Pazar anahtarı** `<periyot>_<taraf>` biçimindedir:
- Periyot: `q1` `q2` `q3` `q4`, `iy` (ilk yarı), `iy2` (ikinci yarı), `mac`.
- Taraf: `ev`, `dep`, `toplam` ya da takım kodu. Bahis sitesi takım adı yazmaz, "Ev üst / Dep alt" diye yazar. Ev sahibi her zaman maç kodundaki ilk takımdır (GSW-LAC'ta ev GSW, LAL-TOR'da ev LAL).

## Veriyi güncelleme

Tüm veriler `nba/games.json` dosyasında: takım ortalamaları, çeyrek sayıları, sakatlıklar ve açılış baremleri. Yeni bir maç eklemek için `maclar` altına bir kayıt aç. Takım `takimlar` altında yoksa onu da ekle.

> Uyarı: 2026-27 verileri sezonun ilk 5-6 maçından geliyor, bazı değerler türetildi (kaynakları dosyada yazıyor). Model bir karar destek aracıdır, kesin sonuç vermez.
