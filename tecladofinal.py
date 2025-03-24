from pynput import keyboard
import os
import platform
import time
from collections import defaultdict

# Configuración
TIMEOUT = 10
TECLAS_PRUEBA = [
    {'nombre': 'Tecla a la izquierda del 1', 'normal': None, 'shift': None},
    {'nombre': 'Tecla arriba de Enter', 'normal': None, 'shift': None},
    {'nombre': 'Letra Ñ/Ç', 'normal': None, 'shift': None},
    {'nombre': 'Tecla a la derecha de la Ñ/Ç', 'normal': None, 'shift': None},
    {'nombre': 'Tecla a la izquierda del Backspace', 'normal': None, 'shift': None},
    {'nombre': 'Tecla @', 'normal': None, 'shift': None},
    {'nombre': 'Tecla #/~', 'normal': None, 'shift': None}
]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if platform.system() == "Windows" else 'clear')

def get_key_press(con_shift=False):
    result = {
        'key': None,
        'code': None,
        'status': None
    }
    shift_pressed = False

    def on_press(key):
        nonlocal shift_pressed
        if key == keyboard.Key.esc:
            result['status'] = 'cancel'
            return False
        elif key == keyboard.Key.space:
            result['status'] = 'skip'
            return False
        elif key in [keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l]:
            shift_pressed = True
            return True
        else:
            try:
                if not con_shift or shift_pressed:
                    result['key'] = key.char
                    result['code'] = key.vk
                    result['status'] = 'valid'
                    return False
                return True
            except AttributeError:
                return True

    with keyboard.Listener(on_press=on_press) as listener:
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            if result['status'] in ['valid', 'skip', 'cancel']:
                break
            time.sleep(0.1)
        else:
            result['status'] = 'timeout'
        listener.stop()

    return result

def identificar_distribucion():
    clear_screen()
    print(f"{bcolors.HEADER}Identificador Avanzado de Distribuciones de Teclado{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}------------------------------------------------------{bcolors.ENDC}")

    # Mapa completo de distribuciones (12 layouts)
    distribuciones = {
        # Layouts Latinoamericanos
        "Latinoamericano (Estándar)": {
            'Tecla a la izquierda del 1': {'normal': 'º', 'shift': 'ª'},
            'Tecla arriba de Enter': {'normal': '´', 'shift': '¨'},
            'Letra Ñ/Ç': {'normal': 'ñ', 'shift': 'Ñ'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '[', 'shift': '{'},
            'Tecla a la izquierda del Backspace': {'normal': ']', 'shift': '}'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+Q'},
            'Tecla #/~': {'normal': None, 'shift': 'AltGr+3'}
        },
        "Latinoamericano (Dell/HP)": {
            'Tecla a la izquierda del 1': {'normal': '|', 'shift': '¬'},
            'Tecla arriba de Enter': {'normal': '\\', 'shift': '|'},
            'Letra Ñ/Ç': {'normal': 'ñ', 'shift': 'Ñ'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '´', 'shift': '¨'},
            'Tecla a la izquierda del Backspace': {'normal': '}', 'shift': ']'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+2'},
            'Tecla #/~': {'normal': None, 'shift': 'AltGr+3'}
        },
        
        # Layouts Europeos
        "Español (España - ISO)": {
            'Tecla a la izquierda del 1': {'normal': 'º', 'shift': 'ª'},
            'Tecla arriba de Enter': {'normal': 'ç', 'shift': 'Ç'},
            'Letra Ñ/Ç': {'normal': 'ñ', 'shift': 'Ñ'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '´', 'shift': '¨'},
            'Tecla a la izquierda del Backspace': {'normal': '`', 'shift': '^'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+2'},
            'Tecla #/~': {'normal': None, 'shift': 'AltGr+3'}
        },
        "Francés (AZERTY)": {
            'Tecla a la izquierda del 1': {'normal': '²', 'shift': '~'},
            'Tecla arriba de Enter': {'normal': '$', 'shift': '£'},
            'Letra Ñ/Ç': {'normal': 'ç', 'shift': 'Ç'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '^', 'shift': '¨'},
            'Tecla a la izquierda del Backspace': {'normal': '*', 'shift': 'µ'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+à'},
            'Tecla #/~': {'normal': 'ù', 'shift': '%'}
        },
        "Alemán (QWERTZ)": {
            'Tecla a la izquierda del 1': {'normal': '^', 'shift': '°'},
            'Tecla arriba de Enter': {'normal': 'ß', 'shift': '?'},
            'Letra Ñ/Ç': {'normal': 'ö', 'shift': 'Ö'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': 'ä', 'shift': 'Ä'},
            'Tecla a la izquierda del Backspace': {'normal': 'ü', 'shift': 'Ü'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+Q'},
            'Tecla #/~': {'normal': '´', 'shift': '`'}
        },
        "Italiano (QWERTY)": {
            'Tecla a la izquierda del 1': {'normal': '\\', 'shift': '|'},
            'Tecla arriba de Enter': {'normal': 'è', 'shift': 'é'},
            'Letra Ñ/Ç': {'normal': 'ò', 'shift': 'ç'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': 'à', 'shift': '°'},
            'Tecla a la izquierda del Backspace': {'normal': 'ù', 'shift': '§'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+ò'},
            'Tecla #/~': {'normal': 'ì', 'shift': '^'}
        },
        
        # Layouts Internacionales
        "US Internacional": {
            'Tecla a la izquierda del 1': {'normal': '`', 'shift': '~'},
            'Tecla arriba de Enter': {'normal': '\\', 'shift': '|'},
            'Letra Ñ/Ç': {'normal': ';', 'shift': ':'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '\'', 'shift': '"'},
            'Tecla a la izquierda del Backspace': {'normal': '[', 'shift': '{'},
            'Tecla @': {'normal': None, 'shift': 'Shift+2'},
            'Tecla #/~': {'normal': None, 'shift': 'Shift+3'}
        },
        "UK (Inglés)": {
            'Tecla a la izquierda del 1': {'normal': '`', 'shift': '¬'},
            'Tecla arriba de Enter': {'normal': '#', 'shift': '~'},
            'Letra Ñ/Ç': {'normal': ';', 'shift': ':'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '\'', 'shift': '@'},
            'Tecla a la izquierda del Backspace': {'normal': '[', 'shift': '{'},
            'Tecla @': {'normal': None, 'shift': 'Shift+\''},
            'Tecla #/~': {'normal': '\\', 'shift': '|'}
        },
        
        # Layouts Especializados
        "Portugués (Brasil - ABNT2)": {
            'Tecla a la izquierda del 1': {'normal': '´', 'shift': '`'},
            'Tecla arriba de Enter': {'normal': '~', 'shift': '^'},
            'Letra Ñ/Ç': {'normal': 'ç', 'shift': 'Ç'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '[', 'shift': '{'},
            'Tecla a la izquierda del Backspace': {'normal': ']', 'shift': '}'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+2'},
            'Tecla #/~': {'normal': None, 'shift': 'AltGr+3'}
        },
        "Canadiense Francés (CSA)": {
            'Tecla a la izquierda del 1': {'normal': '|', 'shift': '\\'},
            'Tecla arriba de Enter': {'normal': 'ç', 'shift': 'Ç'},
            'Letra Ñ/Ç': {'normal': 'é', 'shift': 'É'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': 'è', 'shift': 'È'},
            'Tecla a la izquierda del Backspace': {'normal': 'à', 'shift': 'À'},
            'Tecla @': {'normal': None, 'shift': 'AltGr+à'},
            'Tecla #/~': {'normal': 'ù', 'shift': 'Ù'}
        },
        "Japonés (QWERTY JIS)": {
            'Tecla a la izquierda del 1': {'normal': '半角', 'shift': '全角'},
            'Tecla arriba de Enter': {'normal': '¥', 'shift': '|'},
            'Letra Ñ/Ç': {'normal': 'ñ', 'shift': 'Ñ'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': '変換', 'shift': '無変換'},
            'Tecla a la izquierda del Backspace': {'normal': 'ー', 'shift': '―'},
            'Tecla @': {'normal': None, 'shift': 'Shift+2'},
            'Tecla #/~': {'normal': '＃', 'shift': '〜'}
        },
        "Coreano (Dubeolsik)": {
            'Tecla a la izquierda del 1': {'normal': 'ㅁ', 'shift': 'ㅀ'},
            'Tecla arriba de Enter': {'normal': 'ㅎ', 'shift': 'ㅌ'},
            'Letra Ñ/Ç': {'normal': 'ㅠ', 'shift': 'ㅋ'},
            'Tecla a la derecha de la Ñ/Ç': {'normal': 'ㅜ', 'shift': 'ㅊ'},
            'Tecla a la izquierda del Backspace': {'normal': 'ㅡ', 'shift': 'ㅍ'},
            'Tecla @': {'normal': None, 'shift': 'Shift+2'},
            'Tecla #/~': {'normal': 'ㅆ', 'shift': 'ㅒ'}
        }
    }

    print(f"\n{bcolors.BOLD}Instrucciones:{bcolors.ENDC}")
    print("1. Para cada tecla, primero presionala NORMAL (sin Shift)")
    print("2. Luego presionala con SHIFT")
    print(f"3. Para omitir: {bcolors.WARNING}Espacio{bcolors.ENDC}")
    print(f"4. Para cancelar: {bcolors.FAIL}ESC{bcolors.ENDC}")
    print(f"\n{bcolors.BOLD}Tiempo máximo por tecla: {TIMEOUT} segundos{bcolors.ENDC}\n")

    # Probar cada tecla en modo normal y con shift
    for tecla in TECLAS_PRUEBA:
        print(f"\n{bcolors.HEADER}Prueba: {tecla['nombre']}{bcolors.ENDC}")
        
        # Primero sin shift
        print(f"{bcolors.OKBLUE}Presiona la tecla NORMAL (sin Shift):{bcolors.ENDC}")
        key_data = get_key_press(con_shift=False)
        
        if key_data['status'] == 'cancel':
            print(f"{bcolors.FAIL}Prueba cancelada{bcolors.ENDC}")
            return
        elif key_data['status'] == 'skip':
            print(f"{bcolors.WARNING}Tecla omitida{bcolors.ENDC}")
            continue
        elif key_data['status'] == 'valid':
            tecla['normal'] = key_data['key']
            print(f"{bcolors.OKGREEN}Registrado: {key_data['key']}{bcolors.ENDC}")
        else:
            print(f"{bcolors.WARNING}Tiempo agotado{bcolors.ENDC}")
            continue
        
        # Luego con shift
        print(f"{bcolors.OKBLUE}Ahora presiona la misma tecla CON SHIFT:{bcolors.ENDC}")
        key_data = get_key_press(con_shift=True)
        
        if key_data['status'] == 'valid':
            tecla['shift'] = key_data['key']
            print(f"{bcolors.OKGREEN}Registrado: {key_data['key']}{bcolors.ENDC}")
        else:
            print(f"{bcolors.WARNING}No se registró con Shift{bcolors.ENDC}")

    # Mostrar resultados y determinar distribución
    clear_screen()
    print(f"{bcolors.HEADER}Resultados Obtenidos{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}-------------------{bcolors.ENDC}\n")
    
    for tecla in TECLAS_PRUEBA:
        if tecla['normal'] or tecla['shift']:
            print(f"{bcolors.BOLD}{tecla['nombre']}:{bcolors.ENDC}")
            print(f"  Normal: {tecla['normal'] if tecla['normal'] else 'N/A'}")
            print(f"  Shift: {tecla['shift'] if tecla['shift'] else 'N/A'}\n")

    # Comparar con distribuciones conocidas
    print(f"\n{bcolors.HEADER}Posible Distribución Detectada{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}------------------------------{bcolors.ENDC}")

    mejor_coincidencia = None
    mejor_puntaje = 0

    for nombre_dist, teclas_dist in distribuciones.items():
        puntaje = 0
        total = 0
        
        for tecla_prueba in TECLAS_PRUEBA:
            nombre_tecla = tecla_prueba['nombre']
            if nombre_tecla in teclas_dist:
                total += 1
                if (tecla_prueba['normal'] == teclas_dist[nombre_tecla]['normal'] and
                    tecla_prueba['shift'] == teclas_dist[nombre_tecla]['shift']):
                    puntaje += 2
                elif (tecla_prueba['normal'] == teclas_dist[nombre_tecla]['normal'] or
                      tecla_prueba['shift'] == teclas_dist[nombre_tecla]['shift']):
                    puntaje += 1
        
        if total > 0:
            porcentaje = (puntaje / (total * 2)) * 100
            print(f"{nombre_dist}: {porcentaje:.1f}%")
            
            if porcentaje > mejor_puntaje:
                mejor_puntaje = porcentaje
                mejor_coincidencia = nombre_dist

    if mejor_coincidencia:
        print(f"\n{bcolors.OKGREEN}Conclusión: {mejor_coincidencia}{bcolors.ENDC}")
    else:
        print(f"\n{bcolors.FAIL}No se pudo determinar la distribución{bcolors.ENDC}")

if __name__ == "__main__":
    try:
        identificar_distribucion()
    except ImportError:
        print("Error: Necesitas instalar pynput con: pip install pynput")
    except Exception as e:
        print(f"Error inesperado: {e}")
