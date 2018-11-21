# -*- coding: utf-8 -*-

"""
===========================================
  page_main.py
  https://github.com/ConnectBox/NEO_BatteryLevelShutdown
  License: MIT
  Version 1.0
  GeoDirk - May 2018
===========================================
"""

import os.path
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import subprocess

from .HAT_Utilities import get_device, GetReleaseVersion


def get_connected_users():
    c = subprocess.run(['iw', 'dev', 'wlan0', 'station',
                        'dump'], stdout=subprocess.PIPE)
    connected_user_count = len([line for line in c.stdout.decode(
        "utf-8").split('\n') if line.startswith("Station")])
    return "%s" % connected_user_count


def get_cpu_temp():
    with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as f:
        tempC = f.readline()
    return int(tempC)/1000


def draw_page(device, axp):
    # get an image
    dir_path = os.path.dirname(os.path.abspath(__file__))
    img_path = dir_path + '/assets/main_page.png'
    base = Image.open(img_path).convert('RGBA')
    fff = Image.new(base.mode, base.size, (255,) * 4)
    img = Image.composite(base, fff, base)

    # make a blank image for the text, initialized to transparent text color
    txt = Image.new('RGBA', base.size, (255, 255, 255, 0))

    # get a font
    font_path = dir_path + '/assets/connectbox.ttf'
    font30 = ImageFont.truetype(font_path, 30)
    font20 = ImageFont.truetype(font_path, 20)
    font14 = ImageFont.truetype(font_path, 14)

    # get a drawing context
    d = ImageDraw.Draw(txt)

    # ConnectBox Banner
    d.text((2, 0), 'ConnectBox', font=font30, fill="black")
    # Image version name/number
    d.text((38, 32), GetReleaseVersion(), font=font14, fill="black")

    # connected users
    d.text((13, 35), get_connected_users(), font=font20, fill="black")

    if not axp.power_input_status.acin_present:
        # not charging - cover up symbol
        d.rectangle((64, 48, 71, 61), fill="white")  # charge symbol

    # draw battery fill lines
    if not axp.battery_exists:
        # cross out the battery
        d.line((37, 51, 57, 58), fill="black", width=2)
        d.line((37, 58, 57, 51), fill="black", width=2)
    else:
        # get the percent filled and draw a rectangle
        percent = axp.battery_gauge
        if percent > 0 and percent < 10:
            d.rectangle((37, 51, 39, 58), fill="black")
            d.text((43, 51), "!", font=font14, fill="black")
        elif percent > 10:
            # start of battery level= 37px, end = 57px
            x = int((57 - 37) * (percent / 100)) + 37
            d.rectangle((37, 51, x, 58), fill="black")

    # percent charge left
    d.text((75, 49), "%.0f%%" % axp.battery_gauge, font=font14, fill="black")
    # cpu temp
    d.text((105, 49), "%.0fC" % get_cpu_temp(), font=font14, fill="black")

    out = Image.alpha_composite(img, txt)
    device.display(out.convert(device.mode))


def main(axp):
    device = get_device()
    draw_page(device, axp)
    return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
