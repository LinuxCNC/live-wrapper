# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/disk.py - .disk folder helpers

"""
This module provides helpers for generating the metadata stored in .disk/ on
the cdroot.
"""

import os


def install_disk_info():
    """
    This function creates the .disk/info metadata and installs it into the
    cdroot.
    """

    os.mkdir("cdroot/.disk")
    with open("cdroot/.disk/info", "w") as i:
        i.write("HELLO")
