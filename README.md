# Teclado

Teclado es una herramienta desarrollada en Python que identifica la distribución física de tu teclado mediante una serie de preguntas interactivas. Nació de la necesidad de detectar con precisión el layout en sistemas Linux —especialmente en Debian 12— y está orientada a quienes enfrentan dificultades para saber con certeza qué distribución están utilizando.

## 🎯 Motivación

Durante una experiencia que duro más de lo que esperaba para algo sencillo (idealmente) como configurar un teclado en un Debian 12, donde surgieron constantes problemas de mapeo de teclas, hubo una enorme perdida de tiempo, nació esta herramienta, luego de incontables pruebas, errores y frustraciones con configuraciones estándar del sistema.

> *Me llevó tanto tiempo resolver esto, que la única forma de que haya valido la pena es compartirlo y facilitarle el camino a otros en situaciones similares. Valoro enormemente el feedback de la comunidad para mejorar y adaptar esta herramienta a diferentes entornos y necesidades.*

⚠️ Nota de advertencia

Este proyecto fue desarrollado en el transcurso de un solo día, con el foco puesto en que fuera funcional y útil desde el primer momento.
Seguramente tenga algunos bugs o comportamientos inesperados en casos particulares, pero puede ejecutarse con total seguridad: no modifica el sistema ni realiza acciones fuera del entorno del script.

En la práctica, va a funcionar correctamente en el 95% de los casos, y en el restante 5%, incluso con errores menores, va a identificar correctamente la distribución del teclado.

Si encontrás algún problema, estaré muy agradecido si me lo hacés saber para poder corregirlo lo antes posible. 🙏

## ✨ Características

- **Interacción sencilla**: Responde a una serie de preguntas sobre teclas específicas para determinar el layout.
- **Soporte para múltiples distribuciones**: Incluye firmas de layouts comunes como Latinoamericano, Español (España), US (ANSI), US-Intl y BR ABNT2.
- **Resultados detallados**: Proporciona un porcentaje de coincidencia con cada distribución analizada.


## 💻 Requisitos

- Python 3.x
- [`pynput`](https://pypi.org/project/pynput/)

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
