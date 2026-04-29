# Teclado

Detecta el layout físico de tu teclado en Linux mediante un cuestionario interactivo de teclas.

Útil cuando `localectl` o `setxkbmap` no te dicen lo que realmente tenés, especialmente en Debian 12 con teclados importados.

## Layouts soportados

| Layout | Descripción |
|---|---|
| Latinoamericano | Estándar Argentina/Latinoamérica (ñ, ¿, ¡) |
| Latinoamericano Dell/HP | Variante con enter vertical |
| Español (España) | ISO europeo |
| US ANSI | Inglés americano estándar |
| US Internacional | Con tildes por dead keys |
| UK (Inglés) | Inglés británico |
| Francés AZERTY | |
| Alemán QWERTZ | |
| Italiano QWERTY | |
| Portugués ABNT2 | Brasil |
| Canadiense Francés CSA | |
| Japonés JIS | |

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

Seguí las instrucciones: el script te pide que presiones teclas específicas y determina el layout con un porcentaje de confianza.

## Notas de compatibilidad

- **Funciona en:** Linux Debian 12, Ubuntu 22.04+
- **Requiere:** acceso al teclado físico (no funciona por SSH)
- **Wayland:** puede requerir ejecutar como root o configurar permisos de `/dev/input`
- **No modifica** el sistema operativo — es solo lectura

## Limitaciones

- No detecta layouts muy poco comunes ni variantes de fabricante
- En Wayland, `pynput` puede necesitar permisos adicionales
- No funciona en Windows ni macOS (usa `localectl` en Linux)

## Motivación

Surgió de un problema real: configurar el teclado en Debian 12 donde los mapeos estándar fallaban. Si tardás más de 10 minutos en saber qué layout tenés, esta herramienta es para vos.

## Licencia

CC BY-SA 4.0 — Carlos Ariel Mammoli, Mendoza, Argentina
