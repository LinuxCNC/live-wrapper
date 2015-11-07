"""
live-build-ng - Live-Build NG
(C) Iain R. Learmonth 2015 <irl@debian.org>
See COPYING for terms of usage, modification and redistribution.

lbng/grub.py - Grub 2 helpers
"""

import os

class GrubConfig():
    """
    Helper class that creates a Grub 2 configuration based on a
    vmdebootstrap squashfs output directory.
    """

    versions = []
    name = "Custom Live"

    def __init__(self, directory):
        filenames = os.listdir(directory)
        for filename in filenames:
            if filename[0:8] == "vmlinuz-":
                self.add_version(filename[8:])

    def add_version(self, version):
        self.versions.add(version)

    def generate_cfg(self):
        ret = str()
        versions.sort(reverse=True)
        for version in versions:
            ret += "menuentry \"Debian GNU/Linux Live (kernel %s)\" {\n" % (version,)
            ret += "  linux  /live/vmlinuz-%s boot=live components\n"  % (version,)
            ret += "  initrd /live/initrd.img-%s\n" % (version,)
            ret += "}\n"
        return ret
