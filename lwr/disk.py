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
from datetime import datetime

def get_default_description(distribution):
    distribution = distribution if distribution else "dist"
    if 'official' in os.environ.get('LWR_DEBUG', ''):
        return "Official Debian GNU/Linux '%s' Live" % (distribution,)
    else:
        return "Unofficial Debian GNU/Linux '%s' Live" % (distribution,)


def install_disk_info(cdroot, description):
    """
    This function creates the .disk/ metadata and installs it into the
    specified cdroot.
    """

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    metadir = cdroot['.disk'].path
    with open(os.path.join(metadir, "info"), "w") as i:
        i.write("%s %s" % (description, timestamp,))
    with open(os.path.join(metadir, "udeb_include"), "w") as i:
        i.write("netcfg\nethdetect\npcmciautils-udeb\nlive-installer\n")
    with open(os.path.join(metadir, "cd_type"), "w") as i:
        i.write("live")
    with open(os.path.join(metadir, "base_installable"), "w") as i:
        i.write("")
    with open(os.path.join(metadir, "base_components"), "w") as i:
        i.write("main")
