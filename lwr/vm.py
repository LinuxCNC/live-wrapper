# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/vm.py - vmdebootstrap helpers

"""
The lwr.vm module provides helpers for calling vmdebootstrap as part of the
image creation process.

.. note::
    This module requires that the vmdebootstrap modules be available in the
    Python path.
"""

import os
from vmdebootstrap.base import runcmd


class VMDebootstrap:

    def __init__(self, distribution, mirror=None, cdroot='/tmp/'):
        self.args = ["vmdebootstrap",
                     "--sudo", "--lock-root-password",
                     "--enable-dhcp", "--configure-apt", "--verbose",
                     "--log", "vmdebootstrap.log", "--squash=%s/live/" % cdroot,
                     "--log-level", "debug", "--customize", "--use-uefi",
                     "hooks/customise.sh"]

        self.args.extend(["--distribution", distribution])

        if mirror is not None:
            # specify the local mirror used to build the vm
            self.args.extend(["--mirror", mirror])
            # FIXME: apt-mirror is for what the booted image will use
            # this should not be the local mirror used to build the vm
            self.args.extend(["--apt-mirror", 'http://localhost/mirror/debian'])

    def run(self):
        print(' '.join(self.args))
        runcmd(self.args)  # FIXME: may want to use a method which prints output in realtime
        print('vmdebootstrap complete')


def detect_kernels():
    versions = []
    filenames = os.listdir("cdroot/live")  # static directory for squashfs support
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions
