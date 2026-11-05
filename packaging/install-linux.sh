#!/bin/sh
# Lumbuz'u uygulama menüsüne ekler. Arşivi açtığınız klasörde çalıştırın: ./install.sh
# Kaldırmak için: ./install.sh --uninstall
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICONS="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"

# Uygulamanın eski adı Homeflix'ti: onun menü kaydı da kaldırılır.
rm -f "$APPS/homeflix.desktop" "$ICONS/homeflix.png"

if [ "$1" = "--uninstall" ]; then
    rm -f "$APPS/lumbuz.desktop" "$ICONS/lumbuz.png"
    if [ -d "$DATA/lumbuz" ]; then lib="$DATA/lumbuz"; else lib="$DATA/homeflix"; fi
    echo "Lumbuz menüden kaldırıldı. Kütüphane verisi: $lib"
    exit 0
fi

mkdir -p "$APPS" "$ICONS"
cp "$HERE/lumbuz.png" "$ICONS/lumbuz.png"
cat > "$APPS/lumbuz.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Lumbuz
Comment=Ev sineması
Exec="$HERE/Lumbuz/Lumbuz" --browser
Icon=lumbuz
Terminal=false
Categories=AudioVideo;Video;Player;
DESKTOP
chmod +x "$APPS/lumbuz.desktop"
echo "Lumbuz uygulama menüsüne eklendi."
