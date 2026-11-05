**Lumbuz** (eski adıyla Homeflix), kişisel film ve dizi platformunuz: bilgisayarınızdaki filmleri ve dizileri ev ağındaki telefon, TV ve tarayıcılardan Netflix tarzı bir arayüzle izleyin.

![Lumbuz ana sayfa](https://raw.githubusercontent.com/kaptanoguz/Lumbuz/__VERSION__/docs/screenshots/home.jpg)

## İndir

| Sistem | Dosya | Not |
|---|---|---|
| 🪟 **Windows** 10/11 (64-bit) | [`Lumbuz-__VERSION__-windows-x64.exe`](https://github.com/kaptanoguz/Lumbuz/releases/download/__VERSION__/Lumbuz-__VERSION__-windows-x64.exe) | Kurulum gerekmez, çift tıklayıp açın |
| 🍎 **macOS** Apple Silicon (M1–M4) | [`Lumbuz-__VERSION__-macos-arm64.dmg`](https://github.com/kaptanoguz/Lumbuz/releases/download/__VERSION__/Lumbuz-__VERSION__-macos-arm64.dmg) | macOS 12 ve üzeri |
| 🍎 **macOS** Intel | [`Lumbuz-__VERSION__-macos-x64.dmg`](https://github.com/kaptanoguz/Lumbuz/releases/download/__VERSION__/Lumbuz-__VERSION__-macos-x64.dmg) | macOS 12 ve üzeri |
| 🐧 **Linux** (64-bit) | [`Lumbuz-__VERSION__-linux-x64.tar.gz`](https://github.com/kaptanoguz/Lumbuz/releases/download/__VERSION__/Lumbuz-__VERSION__-linux-x64.tar.gz) | Ubuntu 22.04+, Debian 12+, Fedora 38+ |
| 📺 **Android TV / telefon** | [Lumbuz TV](https://github.com/kaptanoguz/Lumbuz/releases/tag/android-tv-v1.1) | Sunucuya bağlanan uygulama |

Python ya da başka bir şey kurmanız gerekmez.

## Kurulum

**Windows:** `.exe` dosyasını indirip açın. SmartScreen uyarısı çıkarsa *Ek bilgi → Yine de çalıştır*'a tıklayın.

**macOS:** `.dmg` dosyasını açın ve **Lumbuz**'u *Uygulamalar* klasörüne sürükleyin. Uygulama imzasız olduğu için ilk açılışta macOS engeller: *Sistem Ayarları → Gizlilik ve Güvenlik → Yine de Aç*'a tıklayın (ya da Terminal'de `xattr -dr com.apple.quarantine /Applications/Lumbuz.app`).

**Linux:**
```bash
tar xzf Lumbuz-__VERSION__-linux-x64.tar.gz
cd Lumbuz-__VERSION__-linux-x64
./install.sh            # uygulama menüsüne ekler (isteğe bağlı)
./Lumbuz/Lumbuz     # ya da doğrudan çalıştırın
```
Linux'ta arayüz varsayılan tarayıcıda açılır. Sadece sunucu olarak çalıştırmak için: `./Lumbuz/Lumbuz --headless`

## İlk açılış

1. Lumbuz açılınca **Ayarlar**'dan film ve dizi klasörlerinizi seçin.
2. Diğer cihazlardan `http://<bilgisayarın-ip-adresi>:5000` adresine girin (adres Ayarlar ekranında yazar).
3. MKV/AVI gibi dosyaları canlı dönüştürmek ve gömülü altyazılar için **ffmpeg** gerekir:
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` (Fedora: `sudo dnf install ffmpeg`)
   - Windows: `winget install ffmpeg`

Kütüphane verisi (veritabanı, posterler, `secrets.json`) şurada tutulur. Uygulamanın eski adı Homeflix'ti; daha önce kurduysanız kütüphaneniz eski `Homeflix` klasöründe kalır ve olduğu gibi kullanılır:
- Windows: `%APPDATA%\Lumbuz`
- macOS: `~/Library/Application Support/Lumbuz`
- Linux: `~/.local/share/lumbuz`

TMDb anahtarınızı `secrets.json` dosyasına bu klasörde ekleyebilirsiniz (örnek: [`secrets.example.json`](https://github.com/kaptanoguz/Lumbuz/blob/main/secrets.example.json)).

## Özellikler

- 🏠 Netflix tarzı ana sayfa: öne çıkanlar, İzlemeye Devam Et, Listem, Son Eklenenler, türlere göre satırlar
- 🎞️ TMDb'den poster, açıklama ve puanlar; seri filmler otomatik **Koleksiyon** olur
- 📺 Diziler: bölüm adları, görselleri, izlendi işareti, sonraki bölüme otomatik geçiş
- ▶️ Tarayıcının açamadığı dosyalar (mkv, avi, ts) canlı dönüştürülür; ses dili seçimi
- 💬 Altyazı: yerel dosyalar, mkv içindeki altyazılar ve otomatik Türkçe altyazı
- 🌐 **Online** sekmesi: kütüphanenizde olmayan filmleri ve dizileri izleyin
- 📡 **Canlı TV**: yayıncıların kendi sitelerinden 60'tan fazla ücretsiz kanal
- 🎵 **Klipler**: müzik klibi klasörünüzden sanatçı sayfaları ve arka arkaya oynatma
- 🧸 **Kids Zone**: sadece çizgi filmler, animasyonlar ve aile filmleri
- 📱 Kaldığınız yer sunucuda saklanır, telefonda durdurduğunuz filme bilgisayarda devam edersiniz
