# Teclado

Detecta el layout físico de tu teclado en Linux mediante un cuestionario interactivo de teclas.

Útil cuando `localectl` o `setxkbmap` no te dicen lo que realmente tenés, especialmente en Debian 12 con teclados importados o de gaming.

## Layouts soportados

| Layout | xkb / descripción |
|---|---|
| Latinoamericano estándar | `latam` |
| Latinoamericano sin teclas muertas | `latam nodeadkeys` |
| Latinoamericano Dvorak | `latam dvorak` |
| Latinoamericano Colemak | `latam colemak` |
| Latinoamericano Colemak gaming | `latam colemak-gaming` |
| Latinoamericano variante gaming/AR | `latam xk800` (ej. Soul XK-800) |
| Latinoamericano Windows | Variante común de teclados genéricos |
| Español (España) | `es` — ISO europeo |
| US ANSI | `us` — inglés americano estándar |
| US Internacional | `us intl` — tildes por dead keys |
| UK (Inglés) | `gb` — inglés británico |
| Francés AZERTY | `fr` |
| Alemán QWERTZ | `de` |
| Portugués ABNT2 | `br abnt2` — Brasil |

## Cómo funciona

El script hace preguntas sobre teclas en posiciones concretas (neutral respecto a ANSI/ISO), captura los caracteres reales que produce tu teclado y calcula un score de coincidencia contra cada layout. Si el resultado no es decisivo, el script sigue preguntando sobre teclas adicionales que discriminan entre los candidatos empatados, hasta llegar a una conclusión o agotar las posibilidades.

- Detecta **teclas muertas** (`dead_acute`, `dead_diaeresis`, etc.) — aparecen como `<muerta>` en lugar de ningún carácter
- Compatible con teclados **ANSI** (Enter de una fila) e **ISO** (Enter de dos filas)
- Las preguntas usan descripciones de posición relativa, no nombres técnicos de keycodes

## Instalación

```bash
git clone https://github.com/camammoli/Teclado.git
cd Teclado

# Con venv (recomendado)
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# O directo
pip install pynput>=1.7
```

## Uso

```bash
python tecladofinal.py
```

Seguí las instrucciones en pantalla. Al final obtenés un ranking con porcentaje de coincidencia para cada layout.

## Notas de compatibilidad

- **Funciona en:** Linux Debian 12, Ubuntu 22.04+
- **Requiere:** acceso al teclado físico (no funciona por SSH sin reenvío)
- **Wayland:** puede requerir ejecutar como root o configurar permisos de `/dev/input`
- **No modifica** el sistema operativo — es solo lectura

## Variante xk800 (Soul XK-800 y similares)

Algunos teclados de gaming tienen `\` en TLDE (izquierda del 1) y `\|` en BKSL en lugar de los valores latam estándar. Esta variante **no existe en Debian por defecto** — hay que agregarla manualmente.

Usar [`fix_xk800_layout.sh`](fix_xk800_layout.sh) con sudo para instalar la variante `latam xk800` en el sistema xkb y aplicarla con `setxkbmap`. El script es idempotente: si ya está aplicado, lo detecta y no modifica nada.

```bash
sudo bash fix_xk800_layout.sh
```

Para aplicarlo de forma permanente al sistema:

```bash
localectl set-x11-keymap latam pc105 xk800
```

## Licencia

MIT License — Carlos Ariel Mammoli, Mendoza, Argentina
