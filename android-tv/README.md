# Homeflix TV (Android TV APK)

Homeflix 2 sunucusunu (bilgisayarda çalışan Flask uygulaması) Android TV'de ve Android telefonlarda açan ince bir
WebView uygulaması. Aynı APK ikisinde de çalışır; telefonda ekran döner, bağlantı ekranına dokunmak adresi değiştirir.
Yalnızca ev ağında (sunucuyla aynı Wi-Fi'de) bağlanır.
Sunucu bilgisayarda kalır; TV sadece arayüzü gösterir. mkv/avi dönüştürmesini sunucu yapar.

## Kullanım

1. Bilgisayarda: `./run.sh --headless` (gerekirse `sudo ufw allow 5000/tcp` ve `sudo ufw allow 5099/udp`)
2. APK'yı TV'ye kurun, açın. Uygulama ağdaki Homeflix sunucusunu kendisi bulur (UDP 5099) ve adresini hatırlar.
   Ağda birden fazla Homeflix varsa hangisine bağlanılacağı sorulur; hiç bulunamazsa adres sorulur.
3. Sunucuya ulaşılamazsa uygulama 5 saniyede bir tekrar dener ve ağda bir kez yeniden arar: modem bilgisayara yeni
   bir IP verdiyse yeni adrese kendisi geçer. Adresi elle değiştirmek için o ekranda **OK** tuşuna (ya da kumandada
   varsa **MENU** tuşuna) basın; adres penceresindeki **Otomatik bul** düğmesi sunucuyu tekrar arar.
   Tarayıcıdan bağlanan cihazlar için bilgisayara modemden sabit IP vermek (DHCP rezervasyonu) yine faydalıdır.

Kumanda: yön tuşları gezinir, merkez tuşu tıklar, geri tuşu geri gider. Oynatıcıda play/pause, ileri/geri sarma tuşları çalışır;
tam ekranda sol/sağ ±10 sn, merkez oynat/durdur.

## A) GitHub Actions ile derleme (bilgisayara bir şey kurmadan)

Bu klasörü ve `.github/workflows/android-tv.yml` dosyasını repoya ekleyip push edin.
GitHub > Actions > "Android TV APK" > Run workflow > sunucu adresini yazın.
Bitince "homeflix-tv-apk" çıktısından APK'yı indirin.

## B) Linux Mint'te derleme (yaklaşık 1 GB indirme)

```bash
sudo apt install openjdk-17-jdk unzip curl
# Gradle 8.9 (apt'teki sürüm çok eski)
curl -s "https://get.sdkman.io" | bash && source ~/.sdkman/bin/sdkman-init.sh && sdk install gradle 8.9
# Android komut satırı araçları: developer.android.com/studio#command-line-tools-only
mkdir -p ~/android-sdk/cmdline-tools && unzip commandlinetools-linux-*.zip -d ~/android-sdk/cmdline-tools && mv ~/android-sdk/cmdline-tools/cmdline-tools ~/android-sdk/cmdline-tools/latest
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
yes | sdkmanager --licenses
sdkmanager "platforms;android-34" "build-tools;34.0.0" "platform-tools"

cd android-tv
gradle assembleDebug -PserverUrl=http://192.168.1.50:5000
```

APK: `app/build/outputs/apk/debug/app-debug.apk`

## TV'ye yükleme

TV'de Geliştirici seçenekleri > ağ/USB hata ayıklamayı açın, sonra:

```bash
adb connect <tv-ip>:5555
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Ya da APK'yı USB bellek / "Send Files to TV" ile aktarıp TV'de açın (bilinmeyen kaynaklara izin gerekir).
