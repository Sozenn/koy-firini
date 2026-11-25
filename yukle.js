/* Kodvira · cihaza yükleme yardımcısı (tüm oyunlarda aynı dosya).
   Oyun "?yukle" ya da "#yukle" ile açılınca çalışır:
   - Android / bilgisayar (Chrome, Edge, Samsung): tek dokunuşluk "Yükle" düğmesi → tarayıcının kendi yükleme onayı.
   - iPhone / iPad: Apple otomatik yüklemeye izin vermez; Paylaş ve Ana Ekrana Ekle simgeleriyle 2 adımlık rehber.
   - Yükleme desteklemeyen tarayıcı: kısa açıklama.
   Normal açılışta hiçbir şey göstermez ve oyunun kendi yükleme düğmesine (window.__bip) karışmaz. */
(() => {
  const iste = /[?&]yukle\b/.test(location.search) || location.hash === "#yukle";
  let bip = window.__bip || null, kutu = null;
  addEventListener("beforeinstallprompt", e => {
    bip = e;
    if (iste) { e.preventDefault(); window.__bip = e; if (kutu) ciz(); }
  });
  if (!iste) return;
  const kurulu = matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
  if (kurulu) return;
  const ua = navigator.userAgent;
  const ios = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  const ipad = /iPad/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  const android = /Android/.test(ua);
  const sv = (d, dolu) => `<svg viewBox="0 0 24 24" width="22" height="22" fill="${dolu ? "currentColor" : "none"}" stroke="${dolu ? "none" : "currentColor"}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
  const S = {
    paylas: sv('<path d="M8.5 9.5H7a2 2 0 0 0-2 2v7.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7.5a2 2 0 0 0-2-2h-1.5"/><path d="M12 2.8v11.4M8.4 6.3 12 2.8l3.6 3.5"/>'),
    ekle: sv('<rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M12 8v8M8 12h8"/>'),
    menu: sv('<circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/>', true),
    pc: sv('<rect x="2.5" y="3.5" width="19" height="13" rx="2"/><path d="M8 20.5h8M12 7v6.5M9 10.8l3 3 3-3"/>'),
    indir: sv('<path d="M12 3.5v12M7 10.5l5 5 5-5M4.5 20.5h15"/>'),
    tamam: sv('<path d="m5 12.5 4.5 4.5L19 7.5"/>'),
  };
  const chip = (s, t) => `<span class="kvy-chip">${s}${t ? `<b>${t}</b>` : ""}</span>`;
  const css = `
  .kvy{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:flex-end;justify-content:center;background:rgba(10,12,20,.55);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#141826;-webkit-tap-highlight-color:transparent}
  .kvy-k{position:relative;width:min(420px,100%);margin:0 10px calc(14px + env(safe-area-inset-bottom));background:#fff;border-radius:22px;padding:18px 18px 16px;box-shadow:0 20px 60px rgba(0,0,0,.35);animation:kvy-in .25s ease-out}
  @keyframes kvy-in{from{transform:translateY(30px);opacity:0}to{transform:none;opacity:1}}
  .kvy-hd{display:flex;align-items:center;gap:12px;margin-bottom:12px}
  .kvy-hd img{width:52px;height:52px;border-radius:13px;flex:none;background:#0b1020;object-fit:cover}
  .kvy-hd h2{margin:0;font-size:18px;line-height:1.25}
  .kvy-hd small{display:block;color:#69708a;font-size:13px;font-weight:500}
  .kvy-x{position:absolute;top:10px;right:10px;width:34px;height:34px;border:0;border-radius:10px;background:#f1f2f7;color:#69708a;font-size:22px;line-height:1;cursor:pointer}
  .kvy-git{display:flex;align-items:center;justify-content:center;gap:9px;width:100%;margin-top:6px;padding:14px;border:0;border-radius:14px;font:inherit;font-size:17px;font-weight:700;color:#fff;background:linear-gradient(100deg,#8a3dff,#3b82ff);cursor:pointer}
  .kvy-ol{margin:4px 0 0;padding:0;list-style:none;display:grid;gap:12px}
  .kvy-ol li{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  .kvy-n{width:24px;height:24px;border-radius:50%;background:#eef0ff;color:#4a3bd8;font-weight:700;font-size:13px;display:grid;place-items:center;flex:none}
  .kvy-chip{display:inline-flex;align-items:center;gap:6px;padding:5px 10px 5px 7px;border:1px solid #dfe3f0;border-radius:10px;background:#f7f8fc;color:#0a63ff;vertical-align:middle}
  .kvy-chip b{color:#141826;font-weight:600}
  .kvy-not{margin:12px 0 0;color:#69708a;font-size:13px}
  .kvy-ok{position:fixed;left:50%;transform:translateX(-50%);z-index:2147483001;color:#fff;filter:drop-shadow(0 2px 6px rgba(0,0,0,.5));animation:kvy-zip 1.1s ease-in-out infinite}
  .kvy-ok svg{width:44px;height:44px}
  @keyframes kvy-zip{50%{margin-top:10px}}`;
  const st = document.createElement("style"); st.textContent = css;

  let ad = document.title.split(/[–|·-]/)[0].trim(), ikon = (document.querySelector('link[rel="apple-touch-icon"]') || document.querySelector('link[rel~="icon"]') || {}).href || "";
  const man = document.querySelector('link[rel="manifest"]');
  const manOku = man ? fetch(man.href).then(r => r.json()).then(m => {
    ad = m.short_name || m.name || ad;
    const i = (m.icons || []).sort((a, b) => parseInt(b.sizes) - parseInt(a.sizes))[0];
    if (i) ikon = new URL(i.src, man.href).href;
  }).catch(() => {}) : Promise.resolve();

  function kapat() { if (kutu) { kutu.remove(); kutu = null; } document.querySelector(".kvy-ok")?.remove(); history.replaceState(null, "", location.pathname); }
  function ciz(durum) {
    if (!kutu) return;
    const bas = `<button class="kvy-x" type="button" aria-label="Kapat">×</button>
      <div class="kvy-hd"><img src="${ikon}" alt=""><div><h2>${ad}</h2><small>Ücretsiz · mağaza hesabı gerekmez</small></div></div>`;
    let govde;
    if (durum === "tamam") govde = `<p style="margin:4px 0 10px;display:flex;gap:8px;align-items:center;color:#0f7a4f;font-weight:600">${S.tamam} Yüklendi! Oyunu ana ekranından ya da masaüstünden açabilirsin.</p><button class="kvy-git" type="button" data-k>Oynamaya devam et</button>`;
    else if (bip) govde = `<p style="margin:0 0 10px">Oyunu cihazına uygulama gibi yükle; kendi simgesiyle tam ekran açılır, internetsiz de çalışır.</p><button class="kvy-git" type="button" data-y>${S.indir} Yükle</button>`;
    else if (ios) govde = `<ol class="kvy-ol">
        <li><span class="kvy-n">1</span>${ipad ? "Sağ üstteki" : "Alttaki"} ${chip(S.paylas)} simgesine dokun</li>
        <li><span class="kvy-n">2</span>${chip(S.ekle, "Ana Ekrana Ekle")} seç, sonra <b>Ekle</b>'ye dokun</li></ol>
        <p class="kvy-not">iPhone'da yükleme yalnızca bu iki dokunuşla yapılır; Apple başka yola izin vermiyor.</p>`;
    else if (android) govde = `<ol class="kvy-ol">
        <li><span class="kvy-n">1</span>Sağ üstteki ${chip(S.menu)} menüsüne dokun</li>
        <li><span class="kvy-n">2</span>${chip(S.indir, "Uygulamayı yükle")} ya da ${chip(S.ekle, "Ana ekrana ekle")} seç</li></ol>
        <p class="kvy-not">Menüde yükleme seçeneği yoksa oyunu Chrome'da aç.</p>`;
    else govde = `<ol class="kvy-ol">
        <li><span class="kvy-n">1</span>Adres çubuğunun sağındaki ${chip(S.pc)} simgesine tıkla</li>
        <li><span class="kvy-n">2</span>${chip(S.indir, "Yükle")} düğmesine bas</li></ol>
        <p class="kvy-not">Simge görünmüyorsa oyunu Chrome ya da Edge'de aç. Oyun zaten yüklüyse uygulamalarında bulursun.</p>`;
    kutu.querySelector(".kvy-k").innerHTML = bas + govde;
    // iPhone'da Paylaş düğmesi alttaki çubukta: ok ile göster
    document.querySelector(".kvy-ok")?.remove();
    if (!bip && ios && !ipad && durum !== "tamam") {
      const ok = document.createElement("div"); ok.className = "kvy-ok"; ok.style.bottom = "calc(4px + env(safe-area-inset-bottom))";
      ok.innerHTML = sv('<path d="M12 4v15M6 13l6 6 6-6"/>'); document.body.appendChild(ok);
    }
  }
  async function ac() {
    await manOku;
    document.head.appendChild(st);
    kutu = document.createElement("div"); kutu.className = "kvy"; kutu.setAttribute("role", "dialog"); kutu.setAttribute("aria-label", "Cihazına yükle");
    kutu.innerHTML = '<div class="kvy-k"></div>';
    kutu.addEventListener("click", async e => {
      if (e.target === kutu || e.target.closest(".kvy-x,[data-k]")) return kapat();
      if (e.target.closest("[data-y]") && bip) {
        const ev = bip; bip = null; window.__bip = null;
        try { ev.prompt(); const c = await ev.userChoice; if (c && c.outcome === "accepted") return ciz("tamam"); } catch (_) {}
        kapat();
      }
    });
    document.body.appendChild(kutu);
    ciz();
  }
  addEventListener("appinstalled", () => ciz("tamam"));
  // Chrome yükleme olayını sayfa açıldıktan kısa süre sonra verir: bekle, gelmezse rehberi göster
  const basla = () => setTimeout(ac, bip || ios ? 300 : 1500);
  document.readyState === "loading" ? addEventListener("DOMContentLoaded", basla) : basla();
})();
