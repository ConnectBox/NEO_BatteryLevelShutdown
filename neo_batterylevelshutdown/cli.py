# -*- coding: utf-8 -*-

"""Console script for neo_batterylevelshutdown."""

import logging

import axp209
import click
import RPi.GPIO as GPIO  #pylint: disable=import-error
import neo_batterylevelshutdown.hats as hats
from .HAT_Utilities import get_device


def getHATVersion():
    GPIO.setup(hats.AbstractHAT.PA6, GPIO.IN)
    # As PA6 is set to be a pulldown resistor on system startup by the
    #  pa6-pulldown.service, and the HAT sets PA6 HIGH, so we check the
    #  value of PA6, knowing non-HAT NEOs will read LOW.
    #
    # We assume the HAT is not present if we're unable to setup the pin
    #  or read from it. That's the safe option and means that we won't
    #  immediately shutdown devices that don't have a HAT if we've incorrect
    #  detected the presence of a HAT
    if GPIO.input(hats.AbstractHAT.PA6) == GPIO.LOW:
        logging.info("NEO HAT not detected")
        return hats.DummyHAT

    try:
        axp = axp209.AXP209()
        axp.close()
        # AXP209 found... we have HAT from Q3Y2018 or later
        try:
            # See if we can find an OLED
            get_device()
        except OSError:
            # No OLED. This is a standard Axp209 HAT
            logging.info("OLED-less Axp209 HAT Detected")
            return hats.Axp209HAT
        # Test PA1... LOW => Q4Y2018; HIGH => Q3Y2018
        GPIO.setup(hats.q3y2018HAT.PA1, GPIO.IN)
        if GPIO.input(hats.q3y2018HAT.PA1) == GPIO.LOW:
            logging.info("Q4Y2018 HAT Detected")
            return hats.q4y2018HAT
        else:
            logging.info("Q3Y2018 HAT Detected")
            return hats.q3y2018HAT
    except OSError:
        # There is no AXP209 on the Q12018 HAT
        logging.info("Q1Y2018 HAT Detected")
        return hats.q1y2018HAT
    except KeyboardInterrupt:
        pass

    return hats.DummyHAT


@click.command()
@click.option('-v', '--verbose', is_flag=True, default=False)
def main(verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    GPIO.setmode(GPIO.BOARD)
    hat = getHATVersion()
    logging.info("starting main loop")
    try:
        hat().mainLoop()
    except KeyboardInterrupt:
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    GPIO.cleanup()           # clean up GPIO on normal exit


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
