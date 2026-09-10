# Auditar la paleta activa

Esta herramienta **no recolorea ni modifica imágenes**. Tampoco cambia voz,
MP4, composiciones, generadores, progreso de producción o fuentes de entrada.
Su única salida es `qa/blue-palette-validation.json`.

Desde `videos`, con Python 3.12 y Pillow disponible (validado con Pillow 11.3.0):

```powershell
# Durante producción: guía, biblioteca, generadores, laboratorio y HTML de 01–12.
.\.venv\Scripts\python.exe tools/audit_course_palette.py --sources-only

# Auditoría final: exige también 144 cuadros vigentes, doce por MP4 final.
.\.venv\Scripts\python.exe tools/audit_course_palette.py
```

Si Pillow falta: `python -m pip install Pillow==11.3.0` en el entorno elegido.
El modo de fuentes no importa Pillow ni equivale a una aprobación de los videos.
Un HTML de composición anterior que todavía conserve verde se señala incluso
si su generador ya cambió. Vuelve a auditar después de completar los doce renders.

Se buscan literales hexadecimales CSS de 3/4/6/8 dígitos y RGB/RGBA numéricos o
porcentuales, incluidas las propiedades de color de animaciones. Se registran
archivo, línea, columna, color normalizado, hue y saturación. No es un intérprete
de CSS: colores con nombre, expresiones calculadas y hojas externas quedan fuera.

La selección de píxeles candidatos usa hue de **60 a 180 grados**, saturación
HSV de al menos **20%**, valor mínimo **20/255** y diferencia entre canales de al
menos **16/255**. El sector de hue se calcula exactamente mediante `G >= R` y
`G >= B`, sin convertir a un canal HSV cuantizado. La saturación también se
compara con una fracción exacta. Los límites de valor y diferencia de canales
excluyen colores casi grises o muy oscuros.

La aprobación exige **cero literales verdes/teal en las fuentes activas**, revisión
visual vigente sin incidencias y **cero regiones significativas en los cuadros
decodificados de los MP4**. Una región significativa es un componente de al menos
**16 píxeles candidatos unidos por vecindad de ocho direcciones**, incluidas las
diagonales. Los componentes menores conservan su cantidad, tamaño y posición en
el informe. No se afirma que existan cero píxeles con valores verdes.

Para imágenes se utilizan operaciones de canales de Pillow y componentes por
tramos horizontales. El informe conserva cantidad, porcentaje, componentes y
rectángulos que contienen los píxeles detectados, sin guardar ni alterar imágenes.
Cada muestra debe pertenecer a un checkpoint `rendered`,
tener SHA correcto frente al MP4 actual y mantener todos los hashes de input
vigentes. También se contrastan el manifiesto, el timeline, los doce identificadores
de escena, los tiempos medios, los SHA de los PNG y las observaciones visuales
del agente ligadas al mismo MP4. Las muestras obsoletas se rechazan; no se cuentan
como cuadros aprobados.

## Diagnóstico del rasterizado y la compresión

La comparación conservada en
[palette-mask-investigation.json](../qa/palette-mask-investigation.json) revisó
**144 pares**: cada PNG decodificado del MP4 y el PNG nativo de Hyperframes en el
mismo punto medio. Registra sus SHA-256, coordenadas, RGB/HSV exactos y componentes.
En 298,598,400 píxeles decodificados, la máscara inicial contaba **4,226**; admitía
30 píxeles con hue real ligeramente mayor de 180° por la cuantización HSV. La
máscara exacta encuentra **4,196 candidatos** (aproximadamente **0.00140523%**),
distribuidos en **2,306 componentes**. El mayor tiene **8 píxeles**; los dos máximos
son grupos de 2×4. No hay regiones de 16 píxeles o más en esas muestras MP4.

Los PNG nativos también presentan franjas de color del rasterizado: 25,758
candidatos, componentes de hasta 27 píxeles y ninguno con un bloque sólido de
2×2 píxeles. Los componentes nativos mayores son columnas de un píxel de ancho
en los bordes de caracteres. La comparación muestra que numerosos candidatos
decodificados corresponden a azul oscuro, texto claro o blanco en el PNG nativo.
La evidencia es consistente con antialiasing subpíxel y conversión/compresión
YUV420; no prueba que todo candidato tenga una única causa.

El criterio espacial de 16 píxeles se aplica a los **cuadros finales de los MP4**,
junto con las fuentes limpias y la revisión visual. Los PNG nativos son evidencia
diagnóstica, no una segunda puerta de aprobación con ese umbral. Esta decisión
separa regiones detectables de franjas diminutas y mantiene visibles todos los
conteos. No se recolorearon archivos para eliminar esas franjas. Los valores
anteriores pertenecen a los archivos firmados en el diagnóstico; una auditoría
posterior calcula de nuevo sus propios resultados.

La implementación se contrastó con 40 comprobaciones: tres casos de componentes,
30 máscaras aleatorias comparadas con un recorrido independiente, cinco colores
incluidas las fronteras de hue/saturación, y los límites espaciales de 15 y 16
píxeles. Una segunda lectura de los 144 PNG reprodujo los 4,196 candidatos,
2,306 componentes, máximo de 8 y cero regiones significativas, sin escribir
imágenes ni sustituir el informe de auditoría final.

Se excluyen históricos, calibraciones 00/98, dependencias/assets y hojas de
contacto. El alcance es **sampled frames**: doce cuadros medios por video. Un
resultado aprobado no certifica todos los cuadros, todos los estados del
navegador, ausencia de franjas subpíxel ni todos los colores poco saturados.
La preservación de la narración
se mantiene durante la auditoría: solo se leen sus hashes como parte de la
procedencia y no se sintetiza ni escribe audio.

Código de salida: 0 con fuentes limpias y sin regiones significativas en el
alcance elegido; 1 con literales verdes/teal o regiones significativas; 2 con
archivos ausentes, obsoletos o cambiados durante la revisión.
Solo el modo final con 144 cuadros puede registrar
`finalCoursePaletteAuditPassed: true`.
