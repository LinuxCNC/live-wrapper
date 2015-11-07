"""
live-build-ng - Live-Build NG
(C) Iain R. Learmonth 2015 <irl@debian.org>
See COPYING for terms of usage, modification and redistribution.

lbng/xorriso.py - xorriso helpers
"""

from vmdebootstrap.base import runcmd

class Xorriso:

        def __init__(self, image_output, isolinux=True, grub=True):
                self.image_output = image_output
                self.isolinux = isolinux
                self.grub = grub

        def _build_args(self):
                self.args = ['xorriso']
                self.args.extend(['-outdev', self.image_output])
                self.args.extend(['map', 'cdroot/', '/'])
                
                if self.isolinux:
                    self.args.extend(['-boot_image', 'isolinux', 'dir=/boot/isolinux'])

                if self.grub:
                    self.args.extend(['-as', 'mkisofs', '-eltorito-alt-boot', '-e', 'boot/grub/efi.img', '-no-emul-boot', '-isohybrid-gpt-basdat'])

        def build_image(self):
                self._build_args()
                runcmd(self.args)
