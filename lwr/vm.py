# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/vm.py - vmdebootstrap helpers

"""
The lwr.vm module provides helpers for calling vmdebootstrap as part of the
image creation process.

Directory listing of /live/
filesystem.packages
filesystem.packages-remove
filesystem.squashfs
initrd.img
vmlinuz

.. note::
    This module requires that the vmdebootstrap modules be available in the
    Python path.
"""

import os
import logging

import cliapp
from vmdebootstrap.base import runcmd

# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods

class VMDebootstrap(object):

    def __init__(self, distribution, architecture, mirror, cdroot, customise, apt_mirror):
        self.cdroot = cdroot
        self.args = ["vmdebootstrap",
                     "--sudo", "--lock-root-password",
                     "--no-systemd-networkd",
                     "--arch", architecture,
                     "--enable-dhcp", "--configure-apt", "--verbose",
                     "--log", "vmdebootstrap.log",
                     "--squash=%s" % os.path.join(self.cdroot, 'live'),
                     "--log-level", "debug"]
        self.args.extend(["--distribution", distribution])
        self.args.extend(["--mirror", mirror])
        self.args.extend(["--apt-mirror", apt_mirror])

        # FIXME: Logging should happen here
        if os.path.exists(customise):
            self.args.extend(["--customize", customise])
        else:
            raise cliapp.AppException("Could not read customise script at %s" % customise)

    def run(self):
        logging.debug("vmdebootstrap command: %s" % (' '.join(self.args),))
        runcmd(self.args)
        logging.debug("vmdebootstrap completed, see vmdebootstrap.log for details")


def detect_kernels(cdroot):
    versions = []
    filenames = os.listdir(os.path.join(cdroot, "live"))
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions
