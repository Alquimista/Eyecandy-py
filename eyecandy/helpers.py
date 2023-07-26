#!/usr/bin/env python
# -*- coding: utf-8 -*-
import decimal
import os
import subprocess
import sys
import time


def generate_effect():
    # input, output, effect
    subprocess.call(["python", sys.argv[3], sys.argv[1], sys.argv[2]])


def progressbar(it, prefix="Processing", prog="#", sufix="Dialog Lines", size=70):
    """Progress Bar"""
    count = len(it)
    lenstrcount = len(str(count))
    size = size - len(prefix) - len(sufix) - (lenstrcount * 2) - 4

    def _show(i):
        x = int(size * i / count)
        percent = i / count
        formatnum = "{:" + str(lenstrcount) + "d}/" "{:" + str(lenstrcount) + "d}"
        progress = "{:s}: [{:s}{:s}] " + formatnum + " {:s} ({:d}%)\r"
        # print(progress.format(
        #     prefix, prog * x, '.' * (size - x), i, count, sufix))
        sys.stdout.write(
            progress.format(
                prefix,
                prog * x,
                "." * (size - x),
                i,
                count,
                sufix,
                int(round(percent * 100)),
            )
        )
        sys.stdout.flush()

    _show(0)
    for i, item in enumerate(it):
        i += 1
        _show(i)
        yield item


def timer():
    """Cross platform timer"""
    if os.name == "nt":
        return time.clock()
    else:
        return time.time()


# decorator
def timeit(method):
    """Timer decorator"""

    def timed(*args, **kw):
        ts = timer()
        result = method(*args, **kw)
        te = timer()
        time_diff = int(round((te - ts) * 1000, 0))

        seg, ms = divmod(time_diff, 1000)
        m, s = divmod(seg, 60)
        h, m = divmod(m, 60)

        hstr = mstr = sstr = ""

        if h:
            hstr = " {:d} hours ".format(h)
        if m:
            mstr = " {:d} minutes ".format(m)
        if s:
            sstr = " {:d} seconds ".format(s)

        time_message = "\n{:s} took {:s}{:s}{:s}" "{:3d} miliseconds.\n".format(
            method.__name__, hstr, mstr, sstr, ms
        )

        sys.stdout.write(time_message)
        sys.stdout.flush()

        return result

    return timed


def round_format_str(number, decimals=5):
    """Round a number and remove trailing zeros"""
    prec = len(str(float(number)).split(".")[0]) + decimals
    context = decimal.Context(prec=prec)
    dec = context.create_decimal_from_float(float(number))
    tup = dec.as_tuple()
    delta = len(tup.digits) + tup.exponent
    digits = "".join(str(d) for d in tup.digits)
    if delta <= 0:
        zeros = abs(tup.exponent) - len(tup.digits)
        val = "0." + ("0" * zeros) + digits
    else:
        val = digits[:delta] + ("0" * tup.exponent) + "." + digits[delta:]
    val = val.rstrip("0")
    if val[-1] == ".":
        val = val[:-1]
    if tup.sign:
        val = "-" + val
    integer, decimals = str(float(val)).split(".")
    if decimals == "0":
        return integer
    else:
        return val


def start_file(filename):
    if os.name == "mac":
        subprocess.call(("open", filename))
    elif os.name == "nt":
        os.startfile(filename)
    elif os.name == "posix":
        subprocess.call(("xdg-open", filename))
