from pynput import keyboard
import os
import platform
import subprocess
import time

TIMEOUT = 10

# Teclas de prueba — evitamos dead keys intencionalmente para mayor fiabilidad
TECLAS_PRUEBA = [
    {'nombre': 'Tecla a la izquierda del 1',   'normal': None, 'shift': None},
    {'nombre': 'Tecla arriba de Enter (AD11)',  'normal': None, 'shift': None},
    {'nombre': 'Letra Ñ / posición Ñ',         'normal': None, 'shift': None},
    {'nombre': 'Tecla a la derecha de la Ñ',   'normal': None, 'shift': None},
    {'nombre': 'Tecla entre Ñ y Enter (BKSL)', 'normal': None, 'shift': None},
    {'nombre': 'Tecla antes del Backspace',     'normal': None, 'shift': None},
]

# Sentinel para teclas muertas (dead keys): producen key.char == None en pynput
DEAD = '<muerta>'

class bcolors:
    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'
    BOLD    = '\033[1m'

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# ─────────────────────────────────────────────────────────────────────────────
# Detección automática del layout del sistema (Linux / macOS / Windows)
# ─────────────────────────────────────────────────────────────────────────────
def detect_system_layout():
    info = {}
    # Linux: localectl
    try:
        out = subprocess.run(['localectl', 'status'], capture_output=True, text=True, timeout=3).stdout
        for line in out.splitlines():
            if 'X11 Layout' in line:
                info['x11_layout'] = line.split(':')[-1].strip()
            elif 'X11 Variant' in line:
                v = line.split(':')[-1].strip()
                if v:
                    info['x11_variant'] = v
            elif 'VC Keymap' in line:
                info['vc_keymap'] = line.split(':')[-1].strip()
    except Exception:
        pass
    # Linux: /etc/default/keyboard
    if not info:
        try:
            with open('/etc/default/keyboard') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('XKBLAYOUT='):
                        info['xkblayout'] = line.split('=', 1)[1].strip('"\'')
                    elif line.startswith('XKBVARIANT='):
                        info['xkbvariant'] = line.split('=', 1)[1].strip('"\'')
        except Exception:
            pass
    # macOS
    if not info and platform.system() == 'Darwin':
        try:
            out = subprocess.run(
                ['defaults', 'read', 'com.apple.HIToolbox', 'AppleSelectedInputSources'],
                capture_output=True, text=True, timeout=3
            ).stdout
            info['macos_raw'] = out[:200]
        except Exception:
            pass
    return info

# ─────────────────────────────────────────────────────────────────────────────
# Referencia de layouts
# Fuentes: xkb symbols files, MSKLC, Apple keyboard layouts
# Tecla muerta (dead key) → DEAD  (pynput devuelve key.char == None)
# ─────────────────────────────────────────────────────────────────────────────
#
# Mapa de teclas físicas → nombres de script:
#   TLDE  = izquierda del 1
#   AD11  = última tecla fila QWERTY izq-Enter  (derecha de P)
#   AC10  = Ñ / posición Ñ
#   AC11  = derecha de Ñ
#   BKSL  = entre fila Ñ y Enter (ISO) / derecha de AC11
#   AE12  = última tecla fila de números (izq del Backspace)
#
DISTRIBUCIONES = {
    # ── Latinoamérica ─────────────────────────────────────────────────────────
    "Latinoamericano estándar (latam)": {
        # xkb latam basic: AD11=dead_acute/dead_diaeresis, AC11={/[, BKSL=}/]
        'Tecla a la izquierda del 1':   {'normal': '|',   'shift': '°'},
        'Tecla arriba de Enter (AD11)': {'normal': DEAD,  'shift': DEAD},
        'Letra Ñ / posición Ñ':         {'normal': 'ñ',   'shift': 'Ñ'},
        'Tecla a la derecha de la Ñ':   {'normal': '{',   'shift': '['},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '}',   'shift': ']'},
        'Tecla antes del Backspace':    {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano sin teclas muertas (latam nodeadkeys)": {
        # xkb latam nodeadkeys: AD11=grave/asciicircum, AC11=acute/diaeresis, BKSL=ccedilla/Ccedilla
        'Tecla a la izquierda del 1':   {'normal': '|',   'shift': '°'},
        'Tecla arriba de Enter (AD11)': {'normal': '`',   'shift': '^'},
        'Letra Ñ / posición Ñ':         {'normal': 'ñ',   'shift': 'Ñ'},
        'Tecla a la derecha de la Ñ':   {'normal': '´',   'shift': '¨'},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': 'ç',   'shift': 'Ç'},
        'Tecla antes del Backspace':    {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano Dvorak (latam dvorak)": {
        # xkb latam dvorak: AC10=s/S (ñ se mueve a AD03), AD11=dead_acute como básico
        'Tecla a la izquierda del 1':   {'normal': '|',   'shift': '°'},
        'Tecla arriba de Enter (AD11)': {'normal': DEAD,  'shift': DEAD},
        'Letra Ñ / posición Ñ':         {'normal': 's',   'shift': 'S'},
        'Tecla a la derecha de la Ñ':   {'normal': '{',   'shift': '['},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '}',   'shift': ']'},
        'Tecla antes del Backspace':    {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano Colemak (latam colemak)": {
        # xkb latam colemak: AC10=o/O (ñ se mueve a AD10), AD11=dead_acute como básico
        'Tecla a la izquierda del 1':   {'normal': '|',   'shift': '°'},
        'Tecla arriba de Enter (AD11)': {'normal': DEAD,  'shift': DEAD},
        'Letra Ñ / posición Ñ':         {'normal': 'o',   'shift': 'O'},
        'Tecla a la derecha de la Ñ':   {'normal': '{',   'shift': '['},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '}',   'shift': ']'},
        'Tecla antes del Backspace':    {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano (Windows — variante común)": {
        # Driver latam Windows: AE12=apostrophe/question (distinto al xkb)
        'Tecla a la izquierda del 1':   {'normal': '|',   'shift': '°'},
        'Tecla arriba de Enter (AD11)': {'normal': DEAD,  'shift': DEAD},
        'Letra Ñ / posición Ñ':         {'normal': 'ñ',   'shift': 'Ñ'},
        'Tecla a la derecha de la Ñ':   {'normal': '{',   'shift': '['},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '}',   'shift': ']'},
        'Tecla antes del Backspace':    {'normal': "'",   'shift': '?'},
    },
    # ── España ────────────────────────────────────────────────────────────────
    "Español España (es — ISO)": {
        'Tecla a la izquierda del 1':   {'normal': 'º',   'shift': 'ª'},
        'Tecla arriba de Enter (AD11)': {'normal': DEAD,  'shift': DEAD},
        'Letra Ñ / posición Ñ':         {'normal': 'ñ',   'shift': 'Ñ'},
        'Tecla a la derecha de la Ñ':   {'normal': DEAD,  'shift': DEAD},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': 'ç',   'shift': 'Ç'},
        'Tecla antes del Backspace':    {'normal': DEAD,  'shift': DEAD},
    },
    # ── US / UK ───────────────────────────────────────────────────────────────
    "US Internacional (us)": {
        'Tecla a la izquierda del 1':   {'normal': DEAD,  'shift': '~'},
        'Tecla arriba de Enter (AD11)': {'normal': '[',   'shift': '{'},
        'Letra Ñ / posición Ñ':         {'normal': ';',   'shift': ':'},
        'Tecla a la derecha de la Ñ':   {'normal': "'",   'shift': '"'},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '\\',  'shift': '|'},
        'Tecla antes del Backspace':    {'normal': '=',   'shift': '+'},
    },
    "UK Inglés (gb)": {
        'Tecla a la izquierda del 1':   {'normal': DEAD,  'shift': '¬'},
        'Tecla arriba de Enter (AD11)': {'normal': '[',   'shift': '{'},
        'Letra Ñ / posición Ñ':         {'normal': ';',   'shift': ':'},
        'Tecla a la derecha de la Ñ':   {'normal': "'",   'shift': '@'},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '#',   'shift': '~'},
        'Tecla antes del Backspace':    {'normal': '=',   'shift': '+'},
    },
    # ── Europa continental ────────────────────────────────────────────────────
    "Alemán QWERTZ (de)": {
        'Tecla a la izquierda del 1':   {'normal': '^',   'shift': '°'},
        'Tecla arriba de Enter (AD11)': {'normal': 'ü',   'shift': 'Ü'},
        'Letra Ñ / posición Ñ':         {'normal': 'ö',   'shift': 'Ö'},
        'Tecla a la derecha de la Ñ':   {'normal': 'ä',   'shift': 'Ä'},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '#',   'shift': "'"},
        'Tecla antes del Backspace':    {'normal': 'ß',   'shift': '?'},
    },
    "Francés AZERTY (fr)": {
        'Tecla a la izquierda del 1':   {'normal': '²',   'shift': None},
        'Tecla arriba de Enter (AD11)': {'normal': '^',   'shift': '¨'},
        'Letra Ñ / posición Ñ':         {'normal': 'm',   'shift': 'M'},
        'Tecla a la derecha de la Ñ':   {'normal': 'ù',   'shift': '%'},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '*',   'shift': 'µ'},
        'Tecla antes del Backspace':    {'normal': ')',   'shift': '='},
    },
    "Italiano QWERTY (it)": {
        'Tecla a la izquierda del 1':   {'normal': '\\',  'shift': '|'},
        'Tecla arriba de Enter (AD11)': {'normal': 'è',   'shift': 'é'},
        'Letra Ñ / posición Ñ':         {'normal': 'ò',   'shift': 'ç'},
        'Tecla a la derecha de la Ñ':   {'normal': 'à',   'shift': '°'},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': 'ù',   'shift': '§'},
        'Tecla antes del Backspace':    {'normal': "'",   'shift': '^'},
    },
    # ── Otros ─────────────────────────────────────────────────────────────────
    "Portugués Brasil ABNT2 (br)": {
        'Tecla a la izquierda del 1':   {'normal': "'",   'shift': '"'},
        'Tecla arriba de Enter (AD11)': {'normal': DEAD,  'shift': DEAD},
        'Letra Ñ / posición Ñ':         {'normal': 'ç',   'shift': 'Ç'},
        'Tecla a la derecha de la Ñ':   {'normal': '~',   'shift': '^'},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '{',   'shift': '['},
        'Tecla antes del Backspace':    {'normal': '=',   'shift': '+'},
    },
    "Canadiense Francés (ca-multix)": {
        'Tecla a la izquierda del 1':   {'normal': '/',   'shift': '\\'},
        'Tecla arriba de Enter (AD11)': {'normal': '^',   'shift': DEAD},
        'Letra Ñ / posición Ñ':         {'normal': ';',   'shift': ':'},
        'Tecla a la derecha de la Ñ':   {'normal': DEAD,  'shift': DEAD},
        'Tecla entre Ñ y Enter (BKSL)': {'normal': '<',   'shift': '>'},
        'Tecla antes del Backspace':    {'normal': '-',   'shift': '_'},
    },
}

# ─────────────────────────────────────────────────────────────────────────────
def get_key_press(con_shift=False):
    """Captura una tecla. Dead keys → DEAD. Modifica con_shift para requerir Shift."""
    result = {'key': None, 'code': None, 'status': None}
    shift_pressed = False

    def on_press(key):
        nonlocal shift_pressed
        if key == keyboard.Key.esc:
            result['status'] = 'cancel'; return False
        if key == keyboard.Key.space:
            result['status'] = 'skip'; return False
        if key in (keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l):
            shift_pressed = True; return True
        try:
            if not con_shift or shift_pressed:
                char = key.char
                # char es None para dead keys (´ ` ^ ~ ¨ etc.) en pynput/X11
                result['key']    = DEAD if char is None else char
                result['code']   = getattr(key, 'vk', None)
                result['status'] = 'valid'
                return False
            return True
        except AttributeError:
            # Tecla especial sin char (F1, Insert, etc.) — ignorar
            return True

    def on_release(key):
        if key in (keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l):
            nonlocal shift_pressed
            shift_pressed = False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        start = time.time()
        while time.time() - start < TIMEOUT:
            if result['status'] in ('valid', 'skip', 'cancel'):
                break
            time.sleep(0.05)
        else:
            result['status'] = 'timeout'
        listener.stop()
    return result

# ─────────────────────────────────────────────────────────────────────────────
def identificar_distribucion():
    clear_screen()
    print(f"{bcolors.HEADER}{bcolors.BOLD}Identificador de distribución de teclado{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}{'─'*50}{bcolors.ENDC}\n")

    # Mostrar detección del sistema antes de pedir nada
    sys_info = detect_system_layout()
    if sys_info:
        print(f"{bcolors.BOLD}Detección automática del sistema:{bcolors.ENDC}")
        for k, v in sys_info.items():
            print(f"  {k}: {bcolors.OKGREEN}{v}{bcolors.ENDC}")
        print()

    print(f"{bcolors.BOLD}Instrucciones:{bcolors.ENDC}")
    print("  · Para cada tecla: primero presionala SIN Shift, luego CON Shift")
    print(f"  · Espacio = omitir    ESC = cancelar")
    print(f"  · Tiempo por tecla: {TIMEOUT}s")
    print(f"  · Las teclas muertas (dead keys: ´ ` ^ ~ ¨) se detectan automáticamente\n")

    input(f"  {bcolors.WARNING}Presioná Enter para comenzar...{bcolors.ENDC}")

    for tecla in TECLAS_PRUEBA:
        print(f"\n{bcolors.HEADER}▶  {tecla['nombre']}{bcolors.ENDC}")

        # Sin Shift
        print(f"  {bcolors.OKBLUE}[1/2] Normal (sin Shift):{bcolors.ENDC} ", end='', flush=True)
        r = get_key_press(con_shift=False)
        if r['status'] == 'cancel':
            print(f"\n{bcolors.FAIL}Cancelado.{bcolors.ENDC}"); return
        if r['status'] == 'skip':
            print(f"{bcolors.WARNING}omitida{bcolors.ENDC}"); continue
        if r['status'] == 'valid':
            tecla['normal'] = r['key']
            label = '[tecla muerta]' if r['key'] == DEAD else repr(r['key'])
            print(f"{bcolors.OKGREEN}{label}{bcolors.ENDC}")
        else:
            print(f"{bcolors.WARNING}timeout{bcolors.ENDC}"); continue

        # Con Shift
        print(f"  {bcolors.OKBLUE}[2/2] Con Shift:{bcolors.ENDC} ", end='', flush=True)
        r = get_key_press(con_shift=True)
        if r['status'] == 'valid':
            tecla['shift'] = r['key']
            label = '[tecla muerta]' if r['key'] == DEAD else repr(r['key'])
            print(f"{bcolors.OKGREEN}{label}{bcolors.ENDC}")
        else:
            print(f"{bcolors.WARNING}—{bcolors.ENDC}")

    # ── Resultados ────────────────────────────────────────────────────────────
    clear_screen()
    print(f"{bcolors.HEADER}{bcolors.BOLD}Resultados capturados{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}{'─'*50}{bcolors.ENDC}\n")

    for t in TECLAS_PRUEBA:
        if t['normal'] is not None or t['shift'] is not None:
            n = ('[muerta]' if t['normal'] == DEAD else repr(t['normal'])) if t['normal'] is not None else 'N/A'
            s = ('[muerta]' if t['shift']  == DEAD else repr(t['shift']))  if t['shift']  is not None else 'N/A'
            print(f"  {bcolors.BOLD}{t['nombre']}{bcolors.ENDC}")
            print(f"    Normal: {n}   Shift: {s}")

    # ── Scoring ───────────────────────────────────────────────────────────────
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}Comparación con layouts conocidos{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}{'─'*50}{bcolors.ENDC}\n")

    scores = []
    for nombre, ref in DISTRIBUCIONES.items():
        puntos = 0
        total  = 0
        detalle = []
        for t in TECLAS_PRUEBA:
            nombre_t = t['nombre']
            if nombre_t not in ref:
                continue
            total += 2
            ref_n = ref[nombre_t]['normal']
            ref_s = ref[nombre_t]['shift']
            match_n = (t['normal'] == ref_n)
            match_s = (t['shift']  == ref_s)
            if match_n: puntos += 1
            if match_s: puntos += 1
            if not match_n or not match_s:
                got_n = ('[muerta]' if t['normal'] == DEAD else repr(t['normal'])) if t['normal'] is not None else 'N/A'
                exp_n = '[muerta]' if ref_n == DEAD else repr(ref_n)
                got_s = ('[muerta]' if t['shift'] == DEAD else repr(t['shift'])) if t['shift'] is not None else 'N/A'
                exp_s = '[muerta]' if ref_s == DEAD else repr(ref_s)
                if not match_n:
                    detalle.append(f"    {nombre_t} normal: obtuve {got_n}, esperaba {exp_n}")
                if not match_s:
                    detalle.append(f"    {nombre_t} shift:  obtuve {got_s}, esperaba {exp_s}")
        pct = (puntos / total * 100) if total > 0 else 0
        scores.append((pct, nombre, detalle))

    scores.sort(reverse=True)

    for i, (pct, nombre, detalle) in enumerate(scores):
        bar_len = int(pct / 5)
        bar = '█' * bar_len + '░' * (20 - bar_len)
        color = bcolors.OKGREEN if pct >= 70 else (bcolors.WARNING if pct >= 40 else bcolors.FAIL)
        print(f"  {color}{bar}{bcolors.ENDC} {pct:5.1f}%  {nombre}")
        if i == 0 and detalle:
            for d in detalle[:4]:
                print(f"{bcolors.WARNING}{d}{bcolors.ENDC}")

    ganador_pct, ganador, _ = scores[0]
    print(f"\n{bcolors.OKBLUE}{'─'*50}{bcolors.ENDC}")
    if ganador_pct >= 60:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}Distribución detectada: {ganador}{bcolors.ENDC}")
    elif ganador_pct >= 40:
        print(f"{bcolors.WARNING}{bcolors.BOLD}Distribución probable: {ganador}  ({ganador_pct:.0f}% coincidencia){bcolors.ENDC}")
        print(f"{bcolors.WARNING}Resultado poco concluyente. Revisá los detalles arriba.{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}{bcolors.BOLD}No se pudo identificar la distribución con certeza.{bcolors.ENDC}")

    # Cruzar con localectl para confirmar o sugerir variante
    if sys_info:
        layout  = sys_info.get('x11_layout') or sys_info.get('xkblayout', '')
        variant = sys_info.get('x11_variant') or sys_info.get('xkbvariant', '')
        if layout:
            variant_str = f"({variant})" if variant else "(sin variante = estándar con teclas muertas)"
            print(f"{bcolors.OKBLUE}Sistema reporta: layout={layout} {variant_str}{bcolors.ENDC}")
            # Tabla de variantes conocidas de latam
            _latam_variants = {
                '':            'latam estándar (con teclas muertas, dead_acute en AD11)',
                'nodeadkeys':  'sin teclas muertas (AD11=`/^, AC11=´/¨, BKSL=ç/Ç)',
                'deadtilde':   'estándar + dead_tilde en AD12',
                'dvorak':      'Dvorak (AC10=s, ñ en AD03)',
                'colemak':     'Colemak (AC10=o, ñ en AD10)',
                'colemak-gaming': 'Colemak con WASD en posición QWERTY',
            }
            if layout == 'latam' and variant in _latam_variants:
                print(f"{bcolors.OKBLUE}  → Variante: {_latam_variants[variant]}{bcolors.ENDC}")

if __name__ == '__main__':
    try:
        identificar_distribucion()
    except ImportError:
        print("Error: instalá pynput con:  pip3 install pynput")
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise
