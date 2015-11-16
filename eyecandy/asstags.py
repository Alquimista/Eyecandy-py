#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import (absolute_import, division,
                        with_statement, print_function)

import math
import cmath
import operator
import re
import random

try:
    import color
    from color import Color
    from helpers import round_format_str
    import interpolate
except ImportError:
    from . import color
    from .color import Color
    from .helpers import round_format_str
    from . import interpolate


def distanceND(p1, p2):
    if not p2:
        p2 = p1
        p1 = 0, 0
    assert len(p1) == len(p2), 'Vector sizes must match'
    return math.sqrt(math.fsum((p1 - p2)**2 for p1, p2 in zip(p1, p2)))


def distance(x1, y1, x2=None, y2=None):
    if not x2 and not y2:
        dx, dy = x1, y1
    else:
        dx, dy = x2 - x1, y2 - y1
    return math.hypot(dx, dy)


def angle(x1, y1, x2=None, y2=None):
    if not x2 and not y2:
        dx, dy = x1, y1
    else:
        dx, dy = x2 - x1, y2 - y1
    angle = math.atan2(dx, dy)
    return math.degrees(angle)


def change_sign(n):
    return n * -1


def rand(v1, v2=None):
    if not v2:
        v2 = v1
        v1 = -v2
    return random.randint(v1, v2)


def randf(v1=None, v2=None):
    if not v2:
        v2 = v1
        v1 = -v2
    if not v1:
        return random.random()
    return random.uniform(v1, v2)


def rand_range(n, v1, v2=None):
    for i in range(n):
        yield(rand(v1, v2))


def randf_range(n, v1=None, v2=None):
    for i in range(n):
        yield(randf(v1, v2))


def dec2hex(decimal):
    """Convierte un numero decimal a Hexadecimal."""
    return '{:02X}'.format(decimal)


def hex2dec(hexstring):
    """Convierte una cadena hexadecimal y la convierte a un entero decimal."""
    return int(hexstring, 16)


def polar2rec(r, w):
    """
    Convierte de polar a rectangular.

    @r: numero real (radio)
    @w: angulo en grados
    """
    complex_num = cmath.rect(r, math.radians(w))
    return complex_num.real, complex_num.imag


def circle_range(n, x, y, radius, func=interpolate.DEFAULT_INTERPOLATE):
    """)
    Genera una lista con las posiciones para generar un circulo,
    especificando el numero de partículas.

    @n: numero de particulas (el angulo se calculara dependiendo de n).
    @x, @y: centro del circulo.
    @r: radio del circulo.
    """
    crange = list(interpolate.inerpolate_circle_range(n + 1, func))[:-1]
    for angle in crange:
        cx, cy = polar2rec(radius, angle)
        yield x + cx, y + cy


bezier_curve_range = interpolate.bezier_curve_range
interpolate_range = interpolate.interpolate_range


def color_range(n, tipo=1, *colors):
    return (c(tipo, c) for c in color.gradient_bezier(colors, n))


def bord(xb=1, yb=None):
    """
    Especifica el grosor que tendra el borde del texto,
    Puede tener dos parametros uno para "x" y otro para "y".

    Ejemplo:
    >>> bord(1.5)
    '\\bord1.5'
    >>> bord(1.5,2)
    '\\xbord1.5\\ybord2'
    """
    if yb is None or xb == yb:
        return '\\bord' + round_format_str(xb, 2)
    else:
        return xbord(xb) + ybord(yb)


def shad(xs=1, ys=None):
    """
    Especifica a distancia de la sombra del texto,
    Puede tener dos parametros uno para "x" y otro para "y".

    Ejemplo:
    >>> shad(1.5)
    '\\shad1.5'
    >>> shad(1.5,2)
    '\\xshad1.5\\yshad2'
    """
    if ys is None:
        # igual que shad
        return '\\shad' + round_format_str(xs, 2)
    else:
        return xshad(xs) + yshad(ys)


def be(strength=1):
    """
    Crea un difuminado al texto, especificando valores por separado
    para x y para y, si el borde no es cero el difuminado se aplicara
    al borde.

    strength > 1 solo se encuentra para VSFilter 2.39

    @strength: intensidad del difuminado
    @dx, @dy: distancia en x, y
    """
    return '\\be' + str(int(math.ceil(strength)))


def fscx(scale=100):
    """
    Escalado del ancho del texto.
    """
    return '\\fscx{:d}'.format(int(math.ceil(scale)))


def fscy(scale=100):
    """
    Escalado del alto del texto.
    """
    return '\\fscy{:d}'.format(int(math.ceil(scale)))


def fsc(x=100, y=None):
    """
    Escalado del texto en "x" y "y".
    Si y no es especificado se utilizara el mismo valor de x

    fscxy(escala)
    fscxy(escalax, escalay)
    """
    if y is None:
        return fscx(x) + fscy(x)
    else:
        return fscx(x) + fscy(y)


def frx(amount):
    """Gira el texto a lo largo de "x"."""
    return '\\frx' + round_format_str(amount, 8)


def fry(amount):
    """Gira el texto a lo largo de "y"."""
    return '\\fry' + round_format_str(amount, 8)


def fr(amount):
    """Gira el texto a lo largo de "z"."""
    return '\\frz' + round_format_str(amount, 8)


def c(arg1, arg2=None):
    """
    Aplica el color especificado.

    c(tipo, color)
    c(color)

    @tipo:
    1: Color Primario
    2: Color Secundario
    3: Color del borde
    4: Color de la sombra
    sin tipo es lo mismo que 1

    @color:
    Los codigos de color acepta hexadecimales en el siguiente orden:
    Rojo, Verde, Azul.

    Ejemplo:
    c(1,'fff')
    >>> '\\1c&HFFFFFF&'
    c('ffffff')
    >>> '\\c&HFFFFFF&'  # Si es solo c (igual que tipo = 1)
    """
    if arg2 != None:
        tipo = arg1
        if isinstance(arg2, Color):
            color = arg2
        else:
            color = Color.from_hex(arg2)
        if tipo not in (1, 2, 3, 4):
            raise ValueError('\n\nc(tipo,valor):\n<tipo> solo acepta'
                             ' numeros entre 1 y 4')
        else:
            return '\\{:d}c{:s}'.format(tipo, color.ass)
    else:
        if isinstance(arg1, Color):
            color = arg1
        else:
            color = Color.from_hex(arg1)
        return '\\c{:s}'.format(color.ass)


def a(arg1, arg2=None):
    """
    Opacidad del texto.

    a(tipo, opacity)
    a(opacity)

    @tipo:
    1: Opacidad del relleno
    2: Opacidad del relleno Secundario
    3: Opacidad del borde
    4: Opacidad de la sombra
    sin tipo: Opacidad General

    @opacity:
    Acepta valores decimales entre 0 y 255,
    ó hexadecimales entre "00" y "FF".
    """
    # acepta decimal y hexadecimal
    if arg2 != None:
        tipo = arg1
        opacity = arg2
        try:
            alfa = dec2hex(255 - opacity)
        except (TypeError, ValueError):
            alfa = dec2hex(255 - hex2dec(opacity))
        if tipo not in (1, 2, 3, 4):
            raise ValueError('\n\nc(tipo,valor):\n'
                             '<tipo> solo acepta numeros entre 1 y 4')
        else:
            return '\\{:d}a&H{:s}&'.format(tipo, alfa)
    else:
        opacity = arg1
        try:
            alfa = dec2hex(255 - opacity)
        except (TypeError, ValueError):
            alfa = dec2hex(255 - hex2dec(opacity))
        return '\\alpha&H{:s}&'.format(alfa)


def an(pos=5):
    """
    Alineamiento del texto.

    @pos:
    1: Abajo izquierda
    2: Abajo centro
    3: Abajo derecha
    4: Mitad derecha
    5: Mitad centro
    6: Mitad derecha
    7: Arriba izquierda
    8: Arriba centro
    9: Arriba derecha
    """
    apos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    if pos not in apos:
        raise ValueError('\n\nan(pos):\n<pos> solo acepta los '
                         'sigientes valores: ' + str(apos))
    else:
        return '\\an{:d}'.format(pos)


def pos(x, y):
    """Aplica la posición del texto."""
    return '\\pos({:s},{:s})'.format(
        round_format_str(x, 4), round_format_str(y, 4))


def move(arg1, arg2, arg3, arg4, arg5=None, arg6=None):
    """
    Movimiento del texto.

    move(x1, y1, x2, y2)
    move(x1, y1, x2, y2, t1, t2)
    """
    if arg5 == None and arg6 == None:
        x1, y1 = round_format_str(arg1, 4), round_format_str(arg2, 4)
        x2, y2 = round_format_str(arg3, 4), round_format_str(arg4, 4)
        return '\\move({:s},{:s},{:s},{:s})'.format(x1, y1, x2, y2)
    else:
        ti = arg5
        tf = arg6
        x1, y1 = round_format_str(arg1), round_format_str(arg2, 4)
        x2, y2 = round_format_str(arg3), round_format_str(arg4, 4)
        return '\\move({:s},{:s},{:s},{:s},{:d},{:d})'.format(
            x1, y1, x2, y2, ti, tf)


def mov(x1, y1, ix, iy, t1=None, t2=None):
    """
    Movimiento del texto, usando un sistema incremental.

    mov(x, y, incrementox, incrementoy)
    mov(x, y, incrementox, incrementoy, t1, t2)


    Ejemplo:
    >>> inc_move(10, 15, 5, 5)
    '\\move(10,15,15,20)'

    x, y = 10, 15
    move(x, y, x + 5, y + 5) == mov(x, y, 5, 5)
    """
    return move(x1, y1, x1 + ix, y1 + iy, t1, t2)


def org(x, y):
    """Origen de rotación."""
    return '\\org({:s},{:s})'.format(
        round_format_str(x, 4), round_format_str(y, 4))


def fad(ac1, ac2=None, ac3=None, t1=None, t2=None, t3=None, t4=None):
    """Desvanecimiento del texto."""
    if (t1 is None and t2 is None
            and t3 is None and t4 is None):
        dur1, dur2, linedur = ac1, ac2, ac3
        if linedur is None:
            if dur2 is None:
                return '\\fad({:d},{:d})'.format(dur1, dur1)
            else:
                return '\\fad({:d},{:d})'.format(dur1, dur2)
        else:
            start, end = ac1, ac2
            # Desvanecimiento del texto, este usa transición de alphas.
            return '%s\\t(%d,%d,%s)\\t(%d,%d,%s)' % (
                a('ff'),
                0, dur1, a('00'),
                linedur - dur2, linedur, a('ff'))
    else:
        t1, t2 = round_format_str(t1, 2), round_format_str(t2, 2)
        t3, t4 = round_format_str(t3, 2), round_format_str(t4, 2)
    return '\\fade({:s},{:s},{:s},{:s},{:s},{:s},{:s})'.format(
        ac1, ac2, ac3, t1, t2, t3, t4)


def t(arg1, arg2=None, arg3=None, arg4=None):
    """
    Animación de transformación gradual.

    t(modifiers)
    t(accel, modifiers)
    t(t1, t2, style)
    t(t1, t2, accel, modifiers)

    Los tiempos son en milisegundos y son relativos al inicio de la linea

    Funciones que pueden ser animadas:
    fs(), fsp(), c(), a(), fscx(), fscy(), fsc(), frx(), fry(),
    frz(), clip()

    Funciones que pueden ser animadas a partir de VSFilter 2.39:
    fax(), fay(), fa(), be(), blur(), bord(), xbord(), ybord(),
    shad, xshad(), yshad(), iclip()

    Nota: clip() e iclip() solo pueden ser animadas
    en su versión rectangular.
    """
    if arg2 == None and arg3 == None and arg4 == None:
        modifiers = arg1
        return '\\t({:s})'.format(arg1)
    elif arg3 == None and arg4 == None:
        accel, modifiers = arg1, arg2
        return '\\t({:s},{:s})'.format(round_format_str(accel), modifiers)
    elif arg4 == None:
        t1, t2, modifiers = arg1, arg2, arg3
        return '\\t({:s},{:s},{:s})'.format(
            round_format_str(t1), round_format_str(t2), modifiers)
    else:
        t1, t2, accel, modifiers = arg1, arg2, arg3, arg4
        return '\\t({:s},{:s},{:s},{:s})'.format(
            round_format_str(t1), round_format_str(t2),
            round_format_str(accel), modifiers)


def clip(x1, y1=None, x2=None, y2=None, reverse=False):
    """
    Clip del texto, la parte encerrada en el texto es visible.

    clip(x1, x2, x3, x4)
    clip(vector)
    """
    tipo = ""
    if reverse:
        tipo = "i"
    if y1 == None and x2 == None and y2 == None:
        vector = x1    # clip vectorial
        return '\\{:s}clip({:s})'.format(tipo, vector)
    elif x2 == None and y2 == None:
        scale, vector = x1, y1    # clip vectorial
        return '\\{:s}clip({:d},{:s})'.format(tipo, scale, vector)
    else:
        x1, y1 = int(math.ceil(x1)), int(math.ceil(y1))
        x2, y2 = int(math.ceil(x2)), int(math.ceil(y2))
        return '\\{:s}clip({:d},{:d},{:d},{:d})'.format(tipo, x1, y1, x2, y2)


def p(mode, code=None):
    """Dibuja la figura especificada."""
    if not code:
        code, mode = mode, 1
    return '{\\p%d}%s{\\p0}' % (mode, code)


def blur(strength=1, dx=None, dy=None):
    """
    Crea un difuminado gaussiano al texto,
    especificando valores por separado para x y para y,
    si el borde no es cero el difuminado se aplicara al borde.


    @blr: intensidad del blur
    @dx, @dy: distancia en x, y
    """
    return '\\blur' + round_format_str(strength, 2)


def fax(factor):
    """Distorsión de perspectiva del texto en "x"."""
    # Usually factor will be a small number,
    # not larger than 2 as that creates a very strong distortion.
    if factor > 2:
        return '\\fax2'
    else:
        return '\\fax' + round_format_str(factor)


def fay(factor):
    """Distorsión de perspectiva del texto en "y"."""
    if factor > 2:
        return '\\fay2'
    else:
        return '\\fay' + round_format_str(factor)


def xbord(valor=1):
    """Tamaño del Borde en "x"."""
    return '\\xbord' + round_format_str(valor, 2)


def ybord(valor=1):
    """Tamaño del Borde en "y"."""
    return '\\ybord' + round_format_str(valor, 2)


def xshad(depth=1):
    """Que tan alejada esta la sombra del texto en el eje de las "x"."""
    return '\\xshad' + round_format_str(depth, 2)


def yshad(depth=1):
    """Que tan alejada esta la sombra del texto en el eje de las "y"."""
    return '\\yshad' + round_format_str(depth, 2)


def cycletags(inicio, duracion, intervalo, *tags):
    """
    Crea un intervalo de tags, que se iran rotando,
    segun el intervalo de tiempo, y la duracion especificada

    @inicio: tiempo de inicio
    @duracion: duracion del efecto
    @intervalo: intervalo de tiempo que durara cada grupo de tags
    @tags: grupos de tags separadas por una coma (pueden ser mas de 2)

    Ejemplo:
    cycletags(200, 1000, 100, be(1), be(2))
    >>> '\\t(200,300,\\be1)\t(300,400,\\be2)..\\t(900,1000,\\be2)'
    """
    i = 0
    n = len(tags)
    ttags = ''
    start_time = inicio
    end_time = start_time + intervalo
    while end_time < duracion:
        ttags += t(start_time, end_time, tags[i % n])
        start_time = end_time
        end_time += intervalo
        i += 1
    else:
        ttags += t(start_time, duracion, tags[i % n])
    return ttags


# Draw commands
def draw(tipo, x, y):
    """
    Comando de dibujo

    @tipo: tipo de comando de dibujo (m, n, l, p, c)
    @x: posición en el eje x
    @y: posición en el eje y

    Ejemplo:
    draw("m", 10, 30)
    >>> 'm 10 30 '
    """
    return '{:s} {:s} {:s} '.format(
        tipo, round_format_str(x, ), round_format_str(y, 2))


def draw_shape(*points):
    for i, (x, y) in enumerate(points):
        if i == 0:
            shape = draw("m", x, y)
        else:
            shape += draw("l", x, y)
    return shape


def draw_bezier(x1, y1, x2, y2, x3, y3):
    return 'b %s %s %s %s %s %s ' % (
        round_format_str(x1, 2), round_format_str(y1, 2),
        round_format_str(x2, 2), round_format_str(y2, 2),
        round_format_str(x3, 2), round_format_str(y3, 2))


def draw_spline(*posiciones):
    bspline = 's '
    for pos in posiciones:
        bspline += '%s ' % round_format_str(pos, 2)
    return bspline + ' c'


def shape_poligon(radio, lados):
    """
    Comando de dibujo  (Polígono Regular)

    @radio: radio del poligono
    @lados: lados del poligonos

    Ejemplo:
    poligon(15, 5)
    >>>
    """
    iangle = 360 / lados
    # horizontal symmetry position
    if lados % 2 != 0:
        angle = 90 + (iangle / 2)
    else:
        angle = 90
    pdraw = []
    for i in range(lados + 1):
        # ass draw commands
        if i == 0:
            dcommand = "m"    # start drawing
        else:
            dcommand = "l"    # join points with lines
        # convert polar to rectangular
        pdraw.append(draw(dcommand, *polar2rec(radio, angle)))
        angle += iangle

    return translate_shape("".join(pdraw), radio, radio)


def shape_star(radio1, radio2, spikes):
    # the smallest radio is always the inner circle
    if radio1 > radio2:
        radio1, radio2 = radio2, radio1
    iangle = 360 / spikes
    # horizontal symmetry position
    if spikes % 2 == 0:
        angle1 = 90 + (iangle / 2)
    else:
        angle1 = 90
    angle2 = angle1 + (iangle / 2)
    pdraw = []
    for i in range(spikes + 1):
        # ass draw commands
        if i == 0:
            dcommand = "m"    # start drawing
        else:
            dcommand = "l"    # join points with lines
        # convert polar to rectangular
        pdraw.append(draw(dcommand, *polar2rec(radio1, angle1)))
        pdraw.append(draw("l", *polar2rec(radio2, angle2)))
        angle1 += iangle
        angle2 += iangle
    return translate_shape("".join(pdraw), radio2, radio2)


def shape_pentagon(r):
    """Comando de dibujo  (Polígono Regular)

    @r: radio del poligono

    Ejemplo:
    pentagon(15)
    >>>
    """
    return shape_poligon(r, 5)


def shape_circle(radio, substract=False):

    def resize(m):
        num = (float(m.group(0)) / 100) * radio * 2
        return round_format_str(num, 2)

    def swap_coords(m):
        return m.group(2) + " " + m.group(1)

    shape = ("m 50 0 b 22 0 0 22 0 50 b 0 78 22 100 50 100 b "
             "78 100 100 78 100 50 b 100 22 78 0 50 0 ")

    if substract:
        shape = shape_filter(shape, swap_coords)

    return re.sub("\d+", resize, shape)


def shape_ellipse(w, h):

    def rstr(n):
        return round_format_str(n, 2)

    w2, h2 = w / 2, h / 2
    shape = (
        "m %d %s "
        "b %d %s %d %d %s %d "
        "%s %d %s %d %s %s "
        "%s %s %s %s %s %s "
        "%s %s %d %s %d %s")
    return shape % (
        0, rstr(h2),  # move
        0, rstr(h2), 0, 0, rstr(w2), 0,  # curve 1
        rstr(w2), 0, rstr(w), 0, rstr(w), rstr(h2),  # curve 2
        rstr(w), rstr(h2), rstr(w), rstr(h), rstr(w2), rstr(h),  # curve 3
        rstr(w2), rstr(h), 0, rstr(h), 0, rstr(h2))  # curve 4


def shape_pixel():
    return shape_square(width=1, height=1)


def shape_square(width=1, height=1):
    pt = draw('m', 0, 0)
    pt += draw('l', width, 0)
    pt += draw('l', width, height)
    pt += draw('l', 0, height)
    return pt


def shape_triangle(size):

    def rstr(n):
        return round_format_str(n, 2)

    h = math.sqrt(3) * (size / 2)
    base = -h
    shape = 'm %s %s l %s %s 0 %s %s %s' % (
        rstr(size / 2), rstr(base),
        rstr(size), rstr(base + h),
        rstr(base + h), rstr(size / 2), rstr(base))
    return translate_shape(shape, 0, h)


def shape_ring(radio, outline_width):
    radio2 = radio - outline_width
    circle2 = shape_circle(radio2, substract=True)
    circle2 = translate_shape(circle2, -radio2, -radio2)
    circle2 = translate_shape(circle2, radio, radio)
    return shape_circle(radio) + circle2


def shape_heart(size=30):

    def resize(m):
        num = (float(m.group(0)) / 30) * size
        return round_format_str(num, 2)

    path = ("m 15 30 b 27 22 30 18 30 14 30 8 22 "
            "0 15 10 8 0 0 8 0 14 0 18 3 22 15 30")
    return re.sub("\d+", resize, path)


def shape_filter(shape, function):
    return re.sub("(-?\d+.d+|-?\d+)\s(-?\d+.d+|-?\d+)", function, shape)


def shape_max(shape):

    def abs_float(n):
        return abs(float(n))

    pattern = "(-?\d+.d+|-?\d+)\s(-?\d+.d+|-?\d+)"
    coords = [map(abs_float, n) for n in re.findall(pattern, shape)]
    maxx = max(coords, key=operator.itemgetter(0))[0]
    maxy = max(coords, key=operator.itemgetter(1))[1]
    return maxx, maxy


def shape_min(shape):

    def abs_float(n):
        return abs(float(n))

    pattern = "(-?\d+.d+|-?\d+)\s(-?\d+.d+|-?\d+)"
    coords = [map(abs_float, n) for n in re.findall(pattern, shape)]
    maxx = min(coords, key=operator.itemgetter(0))[0]
    maxy = min(coords, key=operator.itemgetter(1))[1]
    return maxx, maxy


def rotate_shape(shape, angle):
    theta = math.radians(angle)

    # translate to origin
    # rotate
    # translate original position

    def rotate(m):
        x, y = float(m.group(1)), float(m.group(2))
        x1 = x * math.cos(theta) - y * math.sin(theta)
        y1 = x * math.sin(theta) + y * math.cos(theta)
        return round_format_str(x1, 2) + " " + round_format_str(y1, 2)

    maxx, maxy = shape_max(shape)
    shape_origin = translate_shape(shape, -maxx / 2, -maxy / 2)
    shape_rotated = shape_filter(shape_origin, rotate)
    maxx, maxy = shape_max(shape_rotated)
    shape_opos = translate_shape(shape_rotated, maxx, maxy)

    return shape_opos


def translate_shape(shape, x, y):

    def move(m):
        px, py = float(m.group(1)) + x, float(m.group(2)) + y
        return round_format_str(px, 2) + " " + round_format_str(py, 2)

    return shape_filter(shape, move)


def scale_shape(shape, x, y=None):

    # translate to origin
    # rotate
    # translate original position

    if not y:
        y = x

    def scale(m):
        px, py = float(m.group(1)) * x, float(m.group(2)) * y
        return round_format_str(px, 2) + " " + round_format_str(py, 2)

    return shape_filter(shape, scale)


def shape_to_bezier(steps, shape):
    pattern = "(-?\d+.d+|-?\d+)\s(-?\d+.d+|-?\d+)"
    mx, my = map(float, re.search("m\s" + pattern, shape).groups())
    shape = re.search("b\s(.*)", shape).group(0).replace("b ", "")
    points_str = re.findall(pattern, shape)
    points = [(mx, my)]
    for x, y in points_str:
        points.append((float(x), float(y)))
    return bezier_curve_range(steps, points)


# TODO: SVG path to Qt path to ASS shape or SVG to ASS
# def svg_to_ass(svg):
#     svg_commands = 'MmLlHhVvCcSsQqTtZz'
#     ass_commands "mlbsc"


if __name__ == '__main__':
    print(shape_circle(10))
