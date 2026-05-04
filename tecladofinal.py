from pynput import keyboard
import os
import platform
import subprocess
import time

TIMEOUT = 10

# Teclas de prueba — nombres unívocos para ANSI e ISO
# TLDE=izq del 1, AD11=1ra der de P, BKSL=barra \, AC10=Ñ, AC11=1ra der de Ñ, AE12=últ fila núm
TECLAS_PRUEBA = [
    {'nombre': 'Izquierda del 1',             'normal': None, 'shift': None},  # TLDE
    {'nombre': 'Primera a la derecha de P',   'normal': None, 'shift': None},  # AD11
    {'nombre': 'Tecla Ñ',                     'normal': None, 'shift': None},  # AC10
    {'nombre': 'Primera a la derecha de Ñ',   'normal': None, 'shift': None},  # AC11
    {'nombre': 'Tecla barra inversa',         'normal': None, 'shift': None},  # BKSL
    {'nombre': 'Última de la fila de números','normal': None, 'shift': None},  # AE12
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
        'Izquierda del 1':              {'normal': '|',   'shift': '°'},
        'Primera a la derecha de P':    {'normal': DEAD,  'shift': DEAD},
        'Tecla Ñ':                      {'normal': 'ñ',   'shift': 'Ñ'},
        'Primera a la derecha de Ñ':    {'normal': '{',   'shift': '['},
        'Tecla barra inversa':          {'normal': '}',   'shift': ']'},
        'Última de la fila de números': {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano sin teclas muertas (latam nodeadkeys)": {
        # xkb latam nodeadkeys: AD11=grave/asciicircum, AC11=acute/diaeresis, BKSL=ccedilla/Ccedilla
        'Izquierda del 1':              {'normal': '|',   'shift': '°'},
        'Primera a la derecha de P':    {'normal': '`',   'shift': '^'},
        'Tecla Ñ':                      {'normal': 'ñ',   'shift': 'Ñ'},
        'Primera a la derecha de Ñ':    {'normal': '´', 'shift': '¨'},
        'Tecla barra inversa':          {'normal': 'ç',   'shift': 'Ç'},
        'Última de la fila de números': {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano Dvorak (latam dvorak)": {
        # xkb latam dvorak: AC10=s/S (ñ se mueve a AD03), AD11=dead_acute como básico
        'Izquierda del 1':              {'normal': '|',   'shift': '°'},
        'Primera a la derecha de P':    {'normal': DEAD,  'shift': DEAD},
        'Tecla Ñ':                      {'normal': 's',   'shift': 'S'},
        'Primera a la derecha de Ñ':    {'normal': '{',   'shift': '['},
        'Tecla barra inversa':          {'normal': '}',   'shift': ']'},
        'Última de la fila de números': {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano Colemak (latam colemak)": {
        # xkb latam colemak: AC10=o/O (ñ se mueve a AD10), AD11=dead_acute como básico
        'Izquierda del 1':              {'normal': '|',   'shift': '°'},
        'Primera a la derecha de P':    {'normal': DEAD,  'shift': DEAD},
        'Tecla Ñ':                      {'normal': 'o',   'shift': 'O'},
        'Primera a la derecha de Ñ':    {'normal': '{',   'shift': '['},
        'Tecla barra inversa':          {'normal': '}',   'shift': ']'},
        'Última de la fila de números': {'normal': '¿',   'shift': '¡'},
    },
    "Latinoamericano (Windows — variante común)": {
        # Driver latam Windows: AE12=apostrophe/question
        'Izquierda del 1':              {'normal': '|',   'shift': '°'},
        'Primera a la derecha de P':    {'normal': DEAD,  'shift': DEAD},
        'Tecla Ñ':                      {'normal': 'ñ',   'shift': 'Ñ'},
        'Primera a la derecha de Ñ':    {'normal': '{',   'shift': '['},
        'Tecla barra inversa':          {'normal': '}',   'shift': ']'},
        'Última de la fila de números': {'normal': "'",   'shift': '?'},
    },
    # ── España ────────────────────────────────────────────────────────────────
    "Español España (es — ISO)": {
        'Izquierda del 1':              {'normal': 'º',   'shift': 'ª'},
        'Primera a la derecha de P':    {'normal': DEAD,  'shift': DEAD},
        'Tecla Ñ':                      {'normal': 'ñ',   'shift': 'Ñ'},
        'Primera a la derecha de Ñ':    {'normal': DEAD,  'shift': DEAD},
        'Tecla barra inversa':          {'normal': 'ç',   'shift': 'Ç'},
        'Última de la fila de números': {'normal': DEAD,  'shift': DEAD},
    },
    # ── US / UK ───────────────────────────────────────────────────────────────
    "US Internacional (us)": {
        'Izquierda del 1':              {'normal': DEAD,  'shift': '~'},
        'Primera a la derecha de P':    {'normal': '[',   'shift': '{'},
        'Tecla Ñ':                      {'normal': ';',   'shift': ':'},
        'Primera a la derecha de Ñ':    {'normal': "'",   'shift': '"'},
        'Tecla barra inversa':          {'normal': '\\',  'shift': '|'},
        'Última de la fila de números': {'normal': '=',   'shift': '+'},
    },
    "UK Inglés (gb)": {
        'Izquierda del 1':              {'normal': DEAD,  'shift': '¬'},
        'Primera a la derecha de P':    {'normal': '[',   'shift': '{'},
        'Tecla Ñ':                      {'normal': ';',   'shift': ':'},
        'Primera a la derecha de Ñ':    {'normal': "'",   'shift': '@'},
        'Tecla barra inversa':          {'normal': '#',   'shift': '~'},
        'Última de la fila de números': {'normal': '=',   'shift': '+'},
    },
    # ── Europa continental ────────────────────────────────────────────────────
    "Alemán QWERTZ (de)": {
        'Izquierda del 1':              {'normal': '^',   'shift': '°'},
        'Primera a la derecha de P':    {'normal': 'ü',   'shift': 'Ü'},
        'Tecla Ñ':                      {'normal': 'ö',   'shift': 'Ö'},
        'Primera a la derecha de Ñ':    {'normal': 'ä',   'shift': 'Ä'},
        'Tecla barra inversa':          {'normal': '#',   'shift': "'"},
        'Última de la fila de números': {'normal': 'ß',   'shift': '?'},
    },
    "Francés AZERTY (fr)": {
        'Izquierda del 1':              {'normal': '²',   'shift': None},
        'Primera a la derecha de P':    {'normal': '^',   'shift': '¨'},
        'Tecla Ñ':                      {'normal': 'm',   'shift': 'M'},
        'Primera a la derecha de Ñ':    {'normal': 'ù',   'shift': '%'},
        'Tecla barra inversa':          {'normal': '*',   'shift': 'µ'},
        'Última de la fila de números': {'normal': ')',   'shift': '='},
    },
    "Italiano QWERTY (it)": {
        'Izquierda del 1':              {'normal': '\\',  'shift': '|'},
        'Primera a la derecha de P':    {'normal': 'è',   'shift': 'é'},
        'Tecla Ñ':                      {'normal': 'ò',   'shift': 'ç'},
        'Primera a la derecha de Ñ':    {'normal': 'à',   'shift': '°'},
        'Tecla barra inversa':          {'normal': 'ù',   'shift': '§'},
        'Última de la fila de números': {'normal': "'",   'shift': '^'},
    },
    # ── Otros ─────────────────────────────────────────────────────────────────
    "Portugués Brasil ABNT2 (br)": {
        'Izquierda del 1':              {'normal': "'",   'shift': '"'},
        'Primera a la derecha de P':    {'normal': DEAD,  'shift': DEAD},
        'Tecla Ñ':                      {'normal': 'ç',   'shift': 'Ç'},
        'Primera a la derecha de Ñ':    {'normal': '~',   'shift': '^'},
        'Tecla barra inversa':          {'normal': '{',   'shift': '['},
        'Última de la fila de números': {'normal': '=',   'shift': '+'},
    },
    "Canadiense Francés (ca-multix)": {
        'Izquierda del 1':              {'normal': '/',   'shift': '\\'},
        'Primera a la derecha de P':    {'normal': '^',   'shift': DEAD},
        'Tecla Ñ':                      {'normal': ';',   'shift': ':'},
        'Primera a la derecha de Ñ':    {'normal': DEAD,  'shift': DEAD},
        'Tecla barra inversa':          {'normal': '<',   'shift': '>'},
        'Última de la fila de números': {'normal': '-',   'shift': '_'},
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Scoring y lógica de desempate
# ─────────────────────────────────────────────────────────────────────────────

def calcular_scores(teclas):
    """Puntúa cada layout. Solo cuenta teclas capturadas (valor != None)."""
    scores = []
    for nombre_layout, ref in DISTRIBUCIONES.items():
        puntos = 0
        total   = 0
        detalle = []
        for t in teclas:
            n_t = t['nombre']
            if n_t not in ref:
                continue
            ref_n = ref[n_t]['normal']
            ref_s = ref[n_t]['shift']
            if t['normal'] is not None:
                total += 1
                if t['normal'] == ref_n:
                    puntos += 1
                else:
                    got = '[muerta]' if t['normal'] == DEAD else repr(t['normal'])
                    exp = '[muerta]' if ref_n == DEAD else repr(ref_n)
                    detalle.append(f"    {n_t} normal: obtuve {got}, esperaba {exp}")
            if t['shift'] is not None:
                total += 1
                if t['shift'] == ref_s:
                    puntos += 1
                else:
                    got = '[muerta]' if t['shift'] == DEAD else repr(t['shift'])
                    exp = '[muerta]' if ref_s == DEAD else repr(ref_s)
                    detalle.append(f"    {n_t} shift:  obtuve {got}, esperaba {exp}")
        pct = (puntos / total * 100) if total > 0 else 0
        scores.append((pct, nombre_layout, detalle))
    scores.sort(reverse=True)
    return scores


def es_decisivo(scores):
    """True si el ganador está 20 puntos por delante, o tiene ≥90% sin empate."""
    if len(scores) < 2:
        return bool(scores)
    top, second = scores[0][0], scores[1][0]
    return (top - second) >= 20 or (top >= 90 and top > second)


def layouts_empatados(scores, umbral=15):
    """Layouts dentro de `umbral` porcentaje-puntos del líder."""
    if not scores:
        return []
    top = scores[0][0]
    return [name for pct, name, _ in scores if top - pct <= umbral]


def teclas_discriminantes(tied_names, teclas, ya_rechazadas):
    """
    Teclas que aún no fueron capturadas, no fueron rechazadas, y tienen
    valores distintos en al menos dos de los layouts empatados.
    """
    result = []
    for t in teclas:
        if t['nombre'] in ya_rechazadas:
            continue
        if t['normal'] is not None or t['shift'] is not None:
            continue
        vals = set()
        for name in tied_names:
            ref = DISTRIBUCIONES.get(name, {}).get(t['nombre'])
            if ref:
                vals.add((ref.get('normal'), ref.get('shift')))
        if len(vals) > 1:
            result.append(t)
    return result


def mostrar_ranking(scores):
    for i, (pct, nombre, detalle) in enumerate(scores):
        bar_len = int(pct / 5)
        bar = '█' * bar_len + '░' * (20 - bar_len)
        color = bcolors.OKGREEN if pct >= 75 else (bcolors.WARNING if pct >= 45 else bcolors.FAIL)
        print(f"  {color}{bar}{bcolors.ENDC} {pct:5.1f}%  {nombre}")
        if i == 0 and detalle:
            for d in detalle[:4]:
                print(f"{bcolors.WARNING}{d}{bcolors.ENDC}")


# ─────────────────────────────────────────────────────────────────────────────
def pedir_tecla(tecla, es_desempate=False):
    """Pregunta normal+shift para una tecla. Devuelve 'ok', 'skip' o 'cancel'."""
    if es_desempate:
        print(f"\n{bcolors.WARNING}▶  {tecla['nombre']}  (necesaria para el desempate){bcolors.ENDC}")
    else:
        print(f"\n{bcolors.HEADER}▶  {tecla['nombre']}{bcolors.ENDC}")

    print(f"  {bcolors.OKBLUE}[1/2] Normal (sin Shift):{bcolors.ENDC} ", end='', flush=True)
    r = get_key_press(con_shift=False)
    if r['status'] == 'cancel':
        print(f"\n{bcolors.FAIL}Cancelado.{bcolors.ENDC}"); return 'cancel'
    if r['status'] == 'skip':
        print(f"{bcolors.WARNING}omitida{bcolors.ENDC}"); return 'skip'
    if r['status'] == 'valid':
        tecla['normal'] = r['key']
        print(f"{bcolors.OKGREEN}{'[tecla muerta]' if r['key'] == DEAD else repr(r['key'])}{bcolors.ENDC}")
    else:
        print(f"{bcolors.WARNING}timeout{bcolors.ENDC}"); return 'skip'

    print(f"  {bcolors.OKBLUE}[2/2] Con Shift:{bcolors.ENDC} ", end='', flush=True)
    r = get_key_press(con_shift=True)
    if r['status'] == 'cancel':
        return 'cancel'
    if r['status'] == 'valid':
        tecla['shift'] = r['key']
        print(f"{bcolors.OKGREEN}{'[tecla muerta]' if r['key'] == DEAD else repr(r['key'])}{bcolors.ENDC}")
    else:
        print(f"{bcolors.WARNING}—{bcolors.ENDC}")
    return 'ok'


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

    sys_info = detect_system_layout()
    if sys_info:
        print(f"{bcolors.BOLD}Detección automática del sistema:{bcolors.ENDC}")
        for k, v in sys_info.items():
            print(f"  {k}: {bcolors.OKGREEN}{v}{bcolors.ENDC}")
        print()

    print(f"{bcolors.BOLD}Referencia de posiciones (★ = teclas que se van a pedir):{bcolors.ENDC}")
    print(f"  {bcolors.OKBLUE}ANSI{bcolors.ENDC} (Enter 1 fila):  ★  Q  W  E  R  T  Y  U  I  O  P  ★  ...  ★←barra")
    print(f"                          A  S  D  F  G  H  J  K  L  ★Ñ  ★  [Enter─────]")
    print(f"  {bcolors.OKBLUE}ISO {bcolors.ENDC} (Enter 2 filas): ★  Q  W  E  R  T  Y  U  I  O  P  ★       ↵")
    print(f"                          A  S  D  F  G  H  J  K  L  ★Ñ  ★  ★barra  ↵")
    print(f"  Fila de números: 1  2  3  4  5  6  7  8  9  0  ...  ★←última\n")
    print(f"{bcolors.BOLD}Instrucciones:{bcolors.ENDC}")
    print("  · Para cada tecla: primero presionala SIN Shift, luego CON Shift")
    print(f"  · Espacio = omitir    ESC = cancelar    Tiempo por tecla: {TIMEOUT}s")
    print(f"  · Dead keys (´ ` ^ ~ ¨) se detectan automáticamente\n")
    input(f"  {bcolors.WARNING}Presioná Enter para comenzar...{bcolors.ENDC}")

    # ── Ronda inicial (todas las teclas, omisión permitida) ───────────────────
    for tecla in TECLAS_PRUEBA:
        if pedir_tecla(tecla) == 'cancel':
            return

    # ── Rondas de desempate adaptativas ──────────────────────────────────────
    ya_rechazadas = set()

    for ronda in range(4):
        scores = calcular_scores(TECLAS_PRUEBA)
        if es_decisivo(scores):
            break

        tied = layouts_empatados(scores)
        discriminantes = teclas_discriminantes(tied, TECLAS_PRUEBA, ya_rechazadas)
        if not discriminantes:
            break

        clear_screen()
        print(f"{bcolors.HEADER}{bcolors.BOLD}Ronda de desempate {ronda + 1}{bcolors.ENDC}"
              f"  — empate entre {len(tied)} candidatos:")
        for name in tied:
            print(f"  {bcolors.WARNING}· {name}{bcolors.ENDC}")
        print(f"\n{bcolors.OKBLUE}Necesito {len(discriminantes)} tecla(s) más para decidir.")
        print(f"Espacio = esa tecla no existe en mi teclado{bcolors.ENDC}\n")

        for tecla in discriminantes:
            res = pedir_tecla(tecla, es_desempate=True)
            if res == 'cancel':
                break
            if res == 'skip':
                ya_rechazadas.add(tecla['nombre'])

    # ── Ranking final ─────────────────────────────────────────────────────────
    scores = calcular_scores(TECLAS_PRUEBA)
    clear_screen()
    print(f"{bcolors.HEADER}{bcolors.BOLD}Comparación con layouts conocidos{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}{'─'*50}{bcolors.ENDC}\n")
    mostrar_ranking(scores)

    # ── Veredicto ─────────────────────────────────────────────────────────────
    ganador_pct, ganador, _ = scores[0]
    second_pct = scores[1][0] if len(scores) > 1 else 0
    print(f"\n{bcolors.OKBLUE}{'─'*50}{bcolors.ENDC}")

    if es_decisivo(scores):
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}Distribución detectada: {ganador}{bcolors.ENDC}")
    elif ganador_pct - second_pct >= 10:
        print(f"{bcolors.WARNING}{bcolors.BOLD}Distribución probable: {ganador}"
              f"  ({ganador_pct:.0f}% vs {second_pct:.0f}%){bcolors.ENDC}")
        print(f"{bcolors.WARNING}Revisá el detalle arriba si tenés dudas.{bcolors.ENDC}")
    else:
        tied_final = layouts_empatados(scores, umbral=5)
        print(f"{bcolors.FAIL}{bcolors.BOLD}No se pudo determinar con certeza.{bcolors.ENDC}")
        print(f"{bcolors.WARNING}Candidatos indistinguibles con las teclas probadas:{bcolors.ENDC}")
        for name in tied_final[:4]:
            print(f"  {bcolors.WARNING}· {name}{bcolors.ENDC}")

    # ── Confirmación con localectl ─────────────────────────────────────────────
    if sys_info:
        layout  = sys_info.get('x11_layout') or sys_info.get('xkblayout', '')
        variant = sys_info.get('x11_variant') or sys_info.get('xkbvariant', '')
        if layout:
            vs = f"({variant})" if variant else "(sin variante = estándar con teclas muertas)"
            print(f"{bcolors.OKBLUE}Sistema reporta: layout={layout} {vs}{bcolors.ENDC}")
            _latam = {
                '':               'latam estándar (dead_acute en AD11)',
                'nodeadkeys':     'sin teclas muertas (AD11=`/^, AC11=´/¨, BKSL=ç/Ç)',
                'deadtilde':      'estándar + dead_tilde en AD12',
                'dvorak':         'Dvorak (AC10=s, ñ en AD03)',
                'colemak':        'Colemak (AC10=o, ñ en AD10)',
                'colemak-gaming': 'Colemak con WASD en posición QWERTY',
            }
            if layout == 'latam' and variant in _latam:
                print(f"{bcolors.OKBLUE}  → Variante: {_latam[variant]}{bcolors.ENDC}")

if __name__ == '__main__':
    try:
        identificar_distribucion()
    except ImportError:
        print("Error: instalá pynput con:  pip3 install pynput")
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise
