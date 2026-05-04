#!/bin/bash
set -e

LATAM=/usr/share/X11/xkb/symbols/latam
EVDEV_LST=/usr/share/X11/xkb/rules/evdev.lst

echo "==> Haciendo backup de $LATAM..."
cp "$LATAM" "${LATAM}.bak"

echo "==> Actualizando archivo latam..."
if grep -q "xkb_symbols \"xk800\"" "$LATAM"; then
    echo "    Variante xk800 ya presente en latam, saltando."
else
    TMPFILE=$(mktemp)
    # Toma las primeras 238 líneas (hasta el include de colemak-gaming)
    # y agrega el cierre del bloque + la variante xk800.
    # Asume Debian 12 con latam sin parchear (238 líneas hasta ese punto).
    head -n 238 "$LATAM" > "$TMPFILE"
    cat >> "$TMPFILE" << 'XKBEOF'
};

partial alphanumeric_keys
xkb_symbols "xk800" {
    include "latam(nodeadkeys)"
    name[Group1]="Spanish (Latin American, XK-800)";
    key <TLDE> { [ backslash, masculine, ordfeminine, notsign ] };
    key <BKSL> { [ backslash, bar, braceright, braceright ] };
};
XKBEOF
    cp "$TMPFILE" "$LATAM"
    rm -f "$TMPFILE"
    echo "    OK — símbolos actualizados."
fi

echo "==> Registrando variante en evdev.lst..."
if grep -q "xk800" "$EVDEV_LST"; then
    echo "    Ya registrada, saltando."
else
    sed -i '/colemak-gaming.*latam/a\  xk800           latam: Spanish (Latin American, XK-800)' "$EVDEV_LST"
    echo "    OK — variante registrada."
fi

echo "==> Limpiando caché xkb..."
rm -rf /var/lib/xkb/*.xkm 2>/dev/null || true

echo "==> Aplicando layout..."
if [ -n "$DISPLAY" ]; then
    setxkbmap latam xk800
    echo "    OK — layout aplicado en sesión actual."
else
    echo "    Sin DISPLAY disponible (ejecutá como root). Aplicá manualmente:"
    echo "    setxkbmap latam xk800"
fi

echo ""
echo "==> Para hacerlo permanente:"
echo "    localectl set-x11-keymap latam pc105 xk800"
