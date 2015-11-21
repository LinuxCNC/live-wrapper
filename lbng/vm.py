# live-build-ng - Live-Build NG
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lbng/vm.py - vmdebootstrap helpers

"""
The lbng.vm module provides helpers for calling vmdebootstrap as part of the
image creation process.

.. note::
    This module requires that the vmdebootstrap modules be available in the
    Python path.
"""

import os
from vmdebootstrap.base import runcmd

class VMDebootstrap:

    def __init__(self, distribution, mirror=None):
        self.args = ["vmdebootstrap",
                     "--sudo", "--lock-root-password",
                     "--enable-dhcp", "--configure-apt",
                     "--log", "vmdebootstrap.log", "--squash=cdroot/live/",
                     "--log-level", "debug", "--customize",
                     "hooks/customise.sh"]

        self.args.extend(["--distribution", distribution])

        if mirror is not None:
            self.args.extend(["--mirror", mirror])

    def run(self):
        runcmd(self.args)

def detect_kernels(cdroot):
    versions = []
    filenames = os.listdir("%s/live" % (cdroot,))
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions
