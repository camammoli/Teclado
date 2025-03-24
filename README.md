# Teclado

**Teclado** es una herramienta desarrollada en Python que, a través de una serie de preguntas interactivas, determina la distribución física de tu teclado. Este proyecto nació de la necesidad de identificar con precisión el layout de teclados en sistemas Linux, específicamente en Debian 12.

## Motivación

Despues de bastante tiempo perdido, muchas pruebas y mas errores (y horrores) para algo tan simple como identificar correctamente la distribución de mi teclado en Linux Debian 12, decidí crear esta herramienta. Decidi que compartir esta solución podría ahorrar tiempo y esfuerzo a otros en situaciones similares. Valoro enormemente el feedback de la comunidad para mejorar y adaptar esta herramienta a diferentes entornos y necesidades.

## Características

- **Interacción sencilla**: Responde a una serie de preguntas sobre teclas específicas para determinar el layout.
- **Soporte para múltiples distribuciones**: Incluye firmas de layouts comunes como Latinoamericano, Español (España), US (ANSI), US-Intl y BR ABNT2.
- **Resultados detallados**: Proporciona un porcentaje de coincidencia con cada distribución analizada.

## Requisitos

- Python 3.x
- Biblioteca `pynput`

## Instalación

1. **Clona el repositorio**:

   ```bash
   git clone https://github.com/camammoli/Teclado.git
   ```

2. **Navega al directorio del proyecto**:

   ```bash
   cd Teclado
   ```

3. **Instala la biblioteca necesaria**:

   ```bash
   pip install pynput
   ```

## Uso

Ejecuta el script principal:

```bash
python tecladofinal.py
```

Sigue las instrucciones en pantalla, presionando las teclas solicitadas. Al finalizar, se mostrará el layout detectado junto con el porcentaje de coincidencia.

## Notas

- Esta herramienta ha sido probada principalmente en **Linux Debian 12**. Su comportamiento en otros sistemas puede variar.
- Se agradece cualquier retroalimentación o reporte de bugs para mejorar la herramienta.

## Futuras Mejoras

- Ampliar la base de datos de layouts para incluir más distribuciones.
- Adaptar la herramienta para su uso en otros sistemas operativos.
- Mejorar la precisión en la detección de layouts menos comunes.

## Bugs Conocidos

- En algunos entornos, la detección de combinaciones de teclas puede ser imprecisa debido a limitaciones del sistema o conflictos con otras aplicaciones.

## Proyectos Similares

- No los encontré pero me interesaría mucho saber si los hay y tratar de ayudar (y aprender) de ellos.

## Licencia

Este proyecto está licenciado bajo la **Creative Commons Atribución-CompartirIgual 4.0 Internacional**. Esto significa que eres libre de compartir y adaptar el material, siempre y cuando se otorgue el crédito adecuado y las nuevas creaciones se licencien bajo los mismos términos.

Para más detalles, consulta el archivo `LICENSE`.

## Contacto

Para sugerencias, reportes de bugs o contribuciones, por favor abre un issue en el repositorio o contacta directamente a través de GitHub.
