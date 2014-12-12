import math
import sys


PROG_NAME = 'XKCD Color Finder'
PROG_VERSION = '0.1'
RESULT_COUNT = 8

# These are completely made up. Tune them to your liking.
WEIGHT_HUE        = 3.0
WEIGHT_SATURATION = 1.0
WEIGHT_INTENSITY  = 1.0


def RGBtoHSI(RGB):
    # From http://en.wikipedia.org/wiki/HSL_and_HSV
    (R, G, B) = RGB

    # H = atan2(sqrt(3) * (G - B), 2*R - G - B)
    alpha = (2 * R - G - B) / 2
    beta = math.sqrt(3) * (G - B) / 2
    H = math.atan2(beta, alpha)

    I = (R + G + B) / 3

    m = min(R, G, B)
    if I != 0:
        S = 1 - m / I
    else:
        S = 0

    return (H, S, I)


def Diff3(a, b):
    return (abs(a[0] - b[0]),
            abs(a[1] - b[1]),
            abs(a[2] - b[2]))


def Distance_Manhattan(a, b):
    diffs = Diff3(a, b)
    return diffs[0] + diffs[1] + diffs[2]


def DistanceTo_WeightedHSI(a, b):
    a = RGBtoHSI(a)
    b = RGBtoHSI(b)

    diffs = Diff3(a, b)

    return (diffs[0] * WEIGHT_HUE +
            diffs[1] * WEIGHT_SATURATION +
            diffs[2] * WEIGHT_INTENSITY)


fnDistance = DistanceTo_WeightedHSI


def IntToHex2(val):
    assert val >= 0
    val = hex(val)[2:]

    while len(val) < 2:
        val = '0' + val

    return val[-2:]


def FloatToHex2(val):
    assert val >= 0
    assert val <= 1.0

    val = int(val * 255.0)
    return IntToHex2(val)


class Color:
    def __init__(self, name, red, green, blue):
        self.name = name
        self.red = red
        self.green = green
        self.blue = blue
        return


    def ToRGB(self):
        return (self.red, self.green, self.blue)


    def ToHTMLColor(self):
        ret = [
            '#',
            FloatToHex2(self.red),
            FloatToHex2(self.green),
            FloatToHex2(self.blue),
        ]
        return ''.join(ret)


# Form of '#rrggbb'
def ParseHTMLColor(colorStr):
    assert len(colorStr) == 7

    red   = int(colorStr[1:3], 16) / 255.0
    green = int(colorStr[3:5], 16) / 255.0
    blue  = int(colorStr[5:7], 16) / 255.0

    return (red, green, blue)


def MakeColor(name, htmlColor):
    (red, green, blue) = ParseHTMLColor(htmlColor)
    return Color(name, red, green, blue)


def LoadColorList(path):
    colorList = []

    with open(path, 'rb') as f:
        for line in f:
            if not line:
                continue

            split = line.split('#', 1)
            assert len(split) == 2
            (name, htmlColor) = split

            name = name.strip()
            htmlColor = '#' + htmlColor.strip()

            color = MakeColor(name, htmlColor)
            colorList.append(color)
            continue

    return colorList


if __name__ == '__main__':
    colorList = LoadColorList('rgb.txt')

    args = sys.argv
    print(args)

    if len(args) == 1:
        sys.stderr.write(PROG_NAME + ' v.' + PROG_VERSION)
        exit(0)

    if len(args) != 2:
        sys.stderr.write('Error: Too many args.')
        exit(1)

    htmlColor = '#' + args[1]
    targetColor = MakeColor(None, htmlColor)
    targetRGB = targetColor.ToRGB()

    distanceList = []
    for color in colorList:
        distance = fnDistance(targetRGB, color.ToRGB()) * 255
        pair = (distance, color)
        distanceList.append(pair)
        continue

    distanceList.sort(key=lambda x: x[0])

    for i in range(RESULT_COUNT):
        (distance, color) = distanceList[i]
        text = '{}: {} (+/-{})'.format(color.name, color.ToHTMLColor(),
                                       str(distance))
        sys.stdout.write(text + '\n')
        continue

    exit(0)

