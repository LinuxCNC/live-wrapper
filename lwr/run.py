# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/run.py - Live Wrapper (Application)

"""
This script is the main script for the live-wrapper application. It is
intended to be run from the command line.

See live-wrapper(8) for more information.
"""

import sys
import os
import cliapp
import logging
import pycurl
import tempfile
import subprocess
from shutil import rmtree
from tarfile import TarFile
from lwr.vm import VMDebootstrap
from lwr.isolinux import install_isolinux
from lwr.bootloader import BootloaderConfig
from lwr.disk import install_disk_info
from lwr.disk import get_default_description
from lwr.grub import install_grub
from lwr.xorriso import Xorriso
from lwr.apt_udeb import AptUdebDownloader
from lwr.utils import cdrom_image_url, KERNEL, RAMDISK
from lwr.cdroot import CDRoot

__version__ = '0.6'

class LiveWrapper(cliapp.Application):

    # Instance variables
    cdroot = None  # The path to the chroot the CD is being built in
    kernel_path = None
    ramdisk_path = None
    gtk_kernel_path = None
    gtk_ramdisk_path = None


    def add_settings(self):
        default_arch = subprocess.check_output(["dpkg", "--print-architecture"]).decode('utf-8').strip()
        self.settings.string(
            ['o', 'image_output'], 'Location for built image',
            metavar='/PATH/TO/FILE.ISO',
            default='live.iso', group='Base Settings')
        self.settings.string(
            ['d', 'distribution'], 'Debian release to use (default: %default)',
            metavar='NAME',
            default='stretch', group='Base Settings')
        self.settings.string(
            ['architecture'], 'architecture to use (%default)',
            metavar='ARCH', default=default_arch)
        self.settings.string(
            ['m', 'mirror'], 'Mirror to use for image creation (default: %default)',
            metavar='MIRROR',
            group='Base Settings',
            default='http://deb.debian.org/debian/')
         self.settings.string(
            ['apt-mirror'], 'Mirror to configure in the built image (default: %default)',
            metavar='APT-MIRROR',
            group='Base Settings',
            default='http://deb.debian.org/debian/')
        self.settings.string(
	    ['description'], 'Description for the image to be created. A '
			     'description will be automatically generated based '
			     'on the distribution chosen if none is specified. '
                             '(default: %s)' % (get_default_description(None),),
            metavar='DESCRIPTION',
            group='Base Settings',
            default=None)
        self.settings.string(
            ['t', 'tasks'], 'Task packages to install',
            metavar='"task-TASK1 task-TASK2 ..."',
            group='Packages')
        self.settings.string(
            ['e', 'extra'], 'Extra packages to install',
            metavar='"PKG1 PKG2 ..."',
            group='Packages')
        self.settings.string(
            ['f', 'firmware'], 'Firmware packages to install',
            metavar='"PKG1 PKG2 ..."',
            group='Packages')
        self.settings.boolean(
            ['isolinux'], 'Add isolinux bootloader to the image '
            '(default: %default)', default=True, group="Bootloaders")
        self.settings.boolean(
            ['grub'], 'Add GRUB bootloader to the image (for EFI support) '
            '(default: %default)', default=True, group="Bootloaders")
        self.settings.boolean(
            ['grub-loopback-only'], 'Only install the loopback.cfg GRUB '
            'configuration (for loopback support) (overrides --grub) '
            '(default: %default)', default=False, group="Bootloaders")
        self.settings.boolean(
            ['installer'], 'Include Debian Installer in the Live image',
            default=True, group="Debian Installer")
        self.settings.boolean(
            ['di-daily'], 'Use the daily Debian Installer builds not releases',
            default=False, group="Debian Installer")
        self.settings.string(
            ['customise'], 'Customisation script to run with vmdebootstrap (default: %default)',
            metavar='CUSTOMISE',
            group='Base Settings',
            default='/usr/share/live-wrapper/customise.sh')
        # Logging overrides
        for s in ['log']:
            self.settings._canonical_names.remove(s)
            self.settings._settingses.pop(s)
        log_group_name = 'Logging'
        self.settings.string(['log'],
                    'write log entries to FILE (default is to not write log '
                    'files at all); use "syslog" to log to system log, '
                    '"stderr" to log to the standard error output, '
                    'or "none" to disable logging',
                    metavar='FILE', group=log_group_name, default='stderr')

    def process_args(self, args):
        if os.path.exists(self.settings['image_output']):
            raise cliapp.AppException("Image '%s' already exists" % self.settings['image_output'])
        if not self.settings['isolinux'] and not self.settings['grub']:
            raise cliapp.AppException("You must enable at least one bootloader!")
        if self.settings['grub'] and self.settings['grub-loopback-only']:
            self.settings['grub'] = False
        if os.geteuid() != 0:
            sys.exit("You need to have root privileges to run this script.")
        # FIXME: cleanup on error.
        self.start_ops()

    def download_file(self, url, filehandle):
        try:
            curl = pycurl.Curl()
            curl.setopt(curl.URL, url)
            curl.setopt(curl.WRITEDATA, filehandle)
            curl.perform()
            curl.close()
        except pycurl.error:
            logging.critical("Failed to fetch %s. Cannot continue!" % (url,))
            sys.exit(1)

    def fetch_di_helpers(self, mirror, suite, architecture):
        logging.info("Downloading helper files from debian-installer team...")
        urls = cdrom_image_url(mirror, suite, architecture, gtk=False, daily=self.settings['di-daily'])
        bootdir = self.cdroot['boot'].path
        ditar = tempfile.NamedTemporaryFile(delete=False)  # pylint: disable=redefined-variable-type
        self.download_file(urls[3], ditar)
        ditar.close()
        info = TarFile.open(ditar.name, 'r:gz')
        if self.settings['isolinux']:
            isolinuxdir = self.cdroot['isolinux'].path
            isolinux_filenames = ['./isolinux.cfg', './stdmenu.cfg', './splash.png']
            isolinux_files = [f for f in info if f.name in isolinux_filenames]
            info.extractall(members=isolinux_files, path=isolinuxdir)
        if self.settings['grub']:
            # The act of fetching the path creates the directory
            logging.info("Created GRUB directory at %s" % (self.cdroot['boot']['grub'].path,))
            grub_files = [f for f in info if f.name.startswith('./grub/')]
            info.extractall(members=grub_files, path=bootdir)
        info.close()
        os.remove(ditar.name)

    def fetch_di_installer(self, mirror, suite, architecture):
        logging.info("Downloading installer files from debian-installer team...")
        bootdir = self.cdroot['boot'].path
        if self.settings['installer']:
            logging.debug("Created d-i kernel and ramdisk directory at %s" % (self.cdroot['d-i'].path,))
            logging.debug("Created d-i GTK kernel and ramdisk directory at %s" % (self.cdroot['d-i']['gtk'].path,))
            self.kernel_path = os.path.join(self.cdroot['d-i'].path, KERNEL)
            self.ramdisk_path = os.path.join(self.cdroot['d-i'].path, RAMDISK)

        if self.settings['installer']:
            # fetch debian-installer
            urls = cdrom_image_url(mirror, suite, architecture, gtk=False, daily=self.settings['di-daily'])
            with open(self.kernel_path, 'w') as kernel:
                self.download_file(urls[1], kernel)
            with open(self.ramdisk_path, 'w') as ramdisk:
                self.download_file(urls[2], ramdisk)

            # Now get the graphical installer.
            urls = cdrom_image_url(mirror, suite, architecture, gtk=True, daily=self.settings['di-daily'])
            self.gtk_kernel_path = os.path.join(self.cdroot['d-i']['gtk'].path, KERNEL)
            self.gtk_ramdisk_path = os.path.join(self.cdroot['d-i']['gtk'].path, RAMDISK)
            with open(self.gtk_kernel_path, 'w') as kernel:
                self.download_file(urls[1], kernel)
            with open(self.gtk_ramdisk_path, 'w') as ramdisk:
                self.download_file(urls[2], ramdisk)

    def start_ops(self):  # pylint: disable=too-many-statements
        """
        This function creates the live image using the settings determined by
        the arguments passed on the command line.

        .. note::
            This function is called by process_args() once all the arguments
            have been validated.
        """

        # Create work directory
        self.cdroot = CDRoot()  # all other directories are based off this
        logging.debug("Created temporary work directory (cdroot) at %s."
                      % (self.cdroot.path,))

        # Make options available to customise hook in vmdebootstrap
        os.environ['LWR_MIRROR'] = self.settings['mirror']
        os.environ['LWR_DISTRIBUTION'] = self.settings['distribution']
        os.environ['LWR_TASK_PACKAGES'] = self.settings['tasks']
        os.environ['LWR_EXTRA_PACKAGES'] = self.settings['extra']
        os.environ['LWR_FIRMWARE_PACKAGES'] = self.settings['firmware']

        for envvar in os.environ.keys():
            if envvar.startswith('LWR_'):
                logging.debug("environment: %s = '%s'" % (envvar, os.environ[envvar]))

        # Run vmdebootstrap, putting files in /live/
        if os.environ.get("LWR_DEBUG") and "skipvm" in os.environ.get('LWR_DEBUG'):
            logging.warning("The debug option to skip running vmdebootstrap was enabled.")
            logging.info("Creating a dummy live/ directory at %s, but not installing a live system." % (self.cdroot['live'].path,))
        else:
            logging.info("Running vmdebootstrap...")
            vm = VMDebootstrap(self.settings['distribution'],
                               self.settings['architecture'],
                               self.settings['mirror'],
                               self.cdroot.path,
                               self.settings['customise'],
                               self.settings['apt-mirror'])
            vm.run()

        # Initialise menu
        # Fetch D-I helper archive
        self.fetch_di_helpers(
            self.settings['mirror'],
            self.settings['distribution'],
            self.settings['architecture'])

        # Fetch D-I installers if needed???
        if self.settings['installer']:
            print("Fetching Debian Installer")
            self.fetch_di_installer(
                self.settings['mirror'],
                self.settings['distribution'],
                self.settings['architecture'])

        # Download the udebs
        if self.settings['installer']:
            print("Downloading udebs for Debian Installer...")  # FIXME: self.message()
            logging.info("Downloading udebs for Debian Installer...")
            # FIXME: get exclude_list from user
            exclude_list = []
            # FIXME: may need a change to the download location
            di_root = self.cdroot['d-i'].path
            apt_udeb = AptUdebDownloader(destdir=di_root)
            apt_udeb.mirror = self.settings['mirror']
            apt_udeb.architecture = self.settings['architecture']
            apt_udeb.codename = self.settings['distribution']
            print("Updating a local cache for %s %s ..." % (apt_udeb.architecture, apt_udeb.codename))  # FIXME: self.message()
            logging.debug("Updating local cache...")
            apt_udeb.prepare_apt()
            # FIXME: add support for a custom apt source on top.

            # download all udebs in the suite, except exclude_list
            apt_udeb.download_udebs(exclude_list)
            # FIXME: generate a Release file
            apt_udeb.clean_up_apt()
            print("... completed udeb downloads")
            logging.info("... completed udeb downloads")

        # Download the firmware debs if desired
        if len(self.settings['firmware']) > 0:
            logging.info("Downloading firmware debs...")

            # FIXME: may need a change to the download location
            fw_root = self.cdroot['firmware'].path
            handler = get_apt_handler(fw_root,
                                      self.settings['mirror'],
                                      self.settings['distribution'],
                                      self.settings['architecture'])
            for pkg in self.settings['firmware'].split(' '):
                filename = handler.download_package(pkg, fw_root)
            handler.clean_up_apt()
            logging.info("... firmware deb downloads")

        # Generate boot config
        bootconfig = BootloaderConfig(self.cdroot.path)

        if os.environ.get("LWR_DEBUG") is None or not 'skipvm' in os.environ['LWR_DEBUG']:
            bootconfig.add_live()
            locallivecfg = BootloaderConfig(self.cdroot.path)
            locallivecfg.add_live_localisation()
            bootconfig.add_submenu('Debian Live with Localisation Support', locallivecfg)
        if self.settings['installer']:
            bootconfig.add_installer(self.kernel_path, self.ramdisk_path)

        # Install isolinux if selected
        if self.settings['isolinux']:
            logging.info("Performing isolinux installation...")
            # FIXME: catch errors and cleanup.
            install_isolinux(
                self.cdroot['isolinux'].path,
                self.settings['mirror'],
                self.settings['distribution'],
                self.settings['architecture'],
                bootconfig)

        # Install GRUB if selected
        if self.settings['grub'] or self.settings['grub-loopback-only']:
            logging.info("Performing GRUB installation...")
            install_grub(self.cdroot.path, bootconfig) # FIXME: pass architecture & uefi settings.

        # Install .disk information
        logging.info("Installing the disk metadata ...")
        install_disk_info(self.cdroot, self.settings['description'] if
                                       self.settings['description'] else
                                       get_default_description(self.settings['distribution']))

        # Create ISO image
        logging.info("Creating the ISO image with Xorriso...")
        xorriso = Xorriso(self.settings['image_output'],
                          isolinux=self.settings['isolinux'],
                          grub=self.settings['grub'])
        xorriso.build_args(self.cdroot.path)
        xorriso.build_image()

        # Remove the temporary directories
        logging.info("Removing temporary work directories...")
        if self.settings['installer']:
            apt_udeb.clean_up_apt()
        print("Use the -cdrom option to test the image using qemu-system.")

def main():
    LiveWrapper(version=__version__).run()
