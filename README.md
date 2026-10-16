# Köy Fırını

Tarayıcıda ve telefonda oynanan bir köy fırını işletme oyunu: çiftlikten malzeme topla, değirmende un öğüt, fırında pişir, sat; kafeni, şubelerini ve otomasyonunu büyüt.

**Oyna:** https://sozenn.github.io/koy-firini/ (telefonda "Ana ekrana ekle" ile uygulama gibi kurulur, internetsiz de açılır)

Aynı depoda ayrı bir oyun daha var: [Plaza Yazılım](https://sozenn.github.io/koy-firini/plaza-yazilim.html), bir yazılım ofisi işletme oyunu.

## v21 · Büyük yenileme

### Oynanış
- **Usta işi:** Otomasyon kurulunca oyuncuya iş kalmıyordu. Artık fırının önünde **Usta işi** düğmesine (Boşluk / E) basıp dönen ibreyi altın dilimde durdurarak **altın ürün** pişiriyorsun. Bunu hiçbir çalışan ya da makine yapamaz.
- **Usta rafı ve gurme müşteriler:** Altın ürünler usta rafına dizilir, gurme müşteriler normal fiyatın 3 katını öder. Yeni geliştirmeler: *Usta eli* (altın dilimi genişletir, çifte altın şansı) ve *Usta rafını büyüt*.
- **Usta siparişleri:** Ara sıra yalnızca altın ürün isteyen özel müşteri gelir; büyük ödül ve köy pulu verir. Kasiyer bunlara yardım edemez.
- **Aksilikler:** Otomasyondan sonra kargalar tarlaya konar, tilki kümese dadanır, arılar oğul verir, bacayı is basar, değirmen taşı körelir. Ekranda uyarı ve yön oku çıkar; yerine gidince çözülür ve ödül verir. Çözülmezse ilgili üretim yavaşlar ama oyun kilitlenmez, iki dakika sonra kendiliğinden geçer.
- **Yağmurlu gün** etkinliği, 7 yeni görev, v21 yenilikler penceresi ve yeni açılış ekranı.

### Görsel
- 23 ürün, malzeme ve arayüz ikonu SVG olarak yeniden çizildi (`assets/items.png` atlası); oyunda ve menülerde aynı ikonlar kullanılıyor.
- Yeni logo ve uygulama ikonları, Baloo 2 yazı tipi, ceviz ahşabı göstergeler ve parşömen paneller.
- Karakterler dış çizgili, gölgeli, kolları ve ayakkabılarıyla yeniden çizildi; altın parıltısı, kargalar, tilki, arı oğulu, isli baca ve yağmur efektleri eklendi.

### Ses
- Bağlama, kaval, darbuka, def ve klarnetle sentezlenmiş üç özgün parça: gündüz **Köy Sabahı** (Uşşak, 2/4), akşam ve gece **Akşam Ezgisi** (Hicaz, 3/4), bayram ve pazar günleri **Şenlik** (Hicaz, 9/8).
- Kameranın baktığı yere göre karışan ortam sesleri: çiftlikte kuşlar ve rüzgâr, dükkânda fırın çıtırtısı, gece cırcır böcekleri ve baykuş, yağmur.
- 27 gerçek ses efekti (orak, kova, kasa, para, korna, inek, tavuk, karga...). Dosyalar inmeden önce eski osilatör sesleri yedek olarak çalar.

### Düzeltmeler
- "Nasıl oynanır" metnindeki olmayan "Bantlar" sekmesi ve artık çalışmayan çevrimdışı kazanç anlatımı düzeltildi.
- "Bırak" düğmesi altın ürünleri yok etmiyor; servis çalışanı önbelleği güncellendi ve kısmi (206) yanıtları saklamıyor.

Kayıtlar korunur: v20 ve öncesinden gelen oyuncular kaldıkları yerden devam eder.

## Yapı

| Dosya | İçerik |
|---|---|
| `index.html` | Oyunun tamamı (HTML, CSS, JavaScript; kütüphane yok, Canvas 2D ve Web Audio) |
| `sw.js` | Servis çalışanı: çevrimdışı açılış ve önbellek |
| `assets/` | Üretilmiş varlıklar: ikon atlası, logo, yazı tipi, müzik ve efektler |
| `assets-src/` | Varlıkları üreten betikler ve SVG kaynakları |
| `plaza-yazilim.html` | Ayrı oyun: Plaza Yazılım |

Geliştirme için adrese `?debug` eklenirse tarayıcı konsolunda `KF` nesnesiyle oyun durumuna erişilir.

## Varlıkları yeniden üretmek

Gerekenler: Python 3 (`numpy`, `scipy`, `pillow`, `fonttools`, `brotli`), [Inkscape](https://inkscape.org), [FFmpeg](https://ffmpeg.org).

```sh
python assets-src/icons.py                       # ikonlar → assets/items.png (Inkscape ile)
python assets-src/font.py Baloo2[wght].ttf       # yazı tipi → assets/fonts/*.woff2
python assets-src/logo.py assets/fonts/baloo2-800.ttf   # logo ve uygulama ikonları
python assets-src/audio.py ffmpeg.exe            # müzik, ortam sesleri, efektler → assets/audio
```

Baloo 2 değişken fontu Google Fonts deposundan (`ofl/baloo2`) alınır. Varlıklar değişince `index.html` ve `sw.js` içindeki `?v=` sürümünü artır.

## Lisanslar

- Baloo 2 yazı tipi: SIL Open Font License 1.1 (`assets/fonts/OFL.txt`).
- Bütün görseller ve sesler bu depodaki betiklerle üretilmiştir; dışarıdan kayıt ya da görsel kullanılmamıştır.
