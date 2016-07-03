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
from vmdebootstrap.base import runcmd

# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods

class VMDebootstrap(object):

    def __init__(self, distribution, architecture, mirror=None, cdroot='/tmp/'):
        self.cdroot = cdroot
        # FIXME: needs to be arch dependent, esp. for --use-uefi/isolinux/grub support.
        # FIXME: use arch_table from vmdebootstrap.constants
        self.args = ["vmdebootstrap",
                     "--sudo", "--lock-root-password",
                     "--arch", architecture,
                     "--enable-dhcp", "--configure-apt", "--verbose",
                     "--log", "vmdebootstrap.log",
                     "--squash=%s" % os.path.join(self.cdroot, 'live'),
                     "--log-level", "debug", "--customize", "--use-uefi",
                     "hooks/customise.sh"]
        self.args.extend(["--distribution", distribution])

        if mirror is not None:
            # specify the local mirror used to build the vm
            self.args.extend(["--mirror", mirror])
            # FIXME: apt-mirror is for what the booted image will use
            # this needs to be accessible over http://, not just file://
            self.args.extend(["--apt-mirror", 'http://localhost/mirror/debian'])

    def run(self):
        print(' '.join(self.args))
        runcmd(self.args)  # FIXME: may want to use a method which prints output in realtime
        print('vmdebootstrap complete')


def detect_kernels(cdroot):
    versions = []
    filenames = os.listdir(os.path.join(cdroot, "live"))
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions
