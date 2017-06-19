# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) 2016 Neil Williams <codehelp@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/apt.py - .apt folder helpers

# depends debian-archive-keyring vmdebootstrap python-apt

import os
import re
import sys
import shutil
import tempfile
import logging
import apt
import apt_pkg
import cliapp
from vmdebootstrap.base import copy_files, runcmd
from subprocess import check_output
import distro_info

# handle a list of package names (udebs)
# handle a list of excluded package names
# handle a supplementary apt source for local udebs
# unique sort the combined package names


class AptUdebDownloader(object):

    def __init__(self, destdir):
        self.architecture = 'armhf'
        self.mirror = None
        self.codename = None
        self.components = [
            'main/debian-installer', 'contrib/debian-installer',
            'non-free/debian-installer']
        self.dirlist = []
        self.cache = None
        self.destdir = destdir

    def prepare_apt(self):
        distroinfo = distro_info.DebianDistroInfo()
        if distroinfo.testing() == self.codename:
            self.suite = "testing"
        elif self.codename == "sid":
            self.suite = "unstable"
        else:
            self.suite = "stable"
        if not self.codename or not self.mirror:
            raise cliapp.AppException("Misconfiguration: no codename or mirror set")
        state_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(state_dir, 'lists'))
        self.dirlist.append(state_dir)
        cache_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(cache_dir, 'archives', 'partial'))
        self.dirlist.append(cache_dir)
        etc_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(etc_dir, 'apt.conf.d'))
        os.mkdir(os.path.join(etc_dir, 'preferences.d'))
        os.mkdir(os.path.join(etc_dir, 'trusted.gpg.d'))
        copy_files(
            '/etc/apt/trusted.gpg.d',
            os.path.join(etc_dir, 'trusted.gpg.d')
        )
        with open(os.path.join(etc_dir, 'sources.list'), 'w') as sources:
            sources.write('deb %s %s %s\n' % (
                self.mirror, self.codename, ' '.join(self.components)))
        self.dirlist.append(etc_dir)
        updates = {
            'APT::Architecture': str(self.architecture),
            'APT::Architectures': str(self.architecture),
            'Dir::State': state_dir,
            'Dir::Cache': cache_dir,
            'Dir::Etc': etc_dir,
        }
        for key, value in updates.items():
            try:
                apt_pkg.config[key] = value # pylint: disable=no-member
            except TypeError as exc:
                print(key, value, exc)
            continue

        self.cache = apt.cache.Cache()
        try:
            self.cache.update()
            self.cache.open()
        except apt.cache.FetchFailedException as exc:
            raise cliapp.AppException('Unable to update cache: %s' % exc)
        if not os.path.exists(self.destdir):
            raise cliapp.AppException('Destination directory %s does not exist' % self.destdir)

    def download_package(self, name, destdir):
        if not self.cache:
            raise cliapp.AppException('No cache available.')
        if name not in self.cache:
            raise cliapp.AppException('%s is not available' % name)
        pkg = self.cache[name]
        if not hasattr(pkg, 'versions'):
            raise cliapp.AppException('%s has no available versions.' % name)
        if len(pkg.versions) > 1:
            pkg.version_list.sort(apt_pkg.version_compare) # pylint: disable=no-member
            version = pkg.version_list[0]
            print("Multiple versions returned for %s - using newest: %s" % (name, pkg.version_list[0]))
        else:
            version = pkg.versions[0]
        if not version.uri:
            raise cliapp.AppException('Not able to download %s' % name)
        try:
            version.fetch_binary(destdir=destdir)
        except TypeError as exc:
            return None
        except apt.package.FetchError as exc:
            raise cliapp.AppException('Unable to fetch %s: %s' % (name, exc))
        filename = os.path.join(destdir, os.path.basename(version.record['Filename']))
        if os.path.exists(filename):
            return filename
        return None


    def download_udebs(self, exclude_list):
        if not self.cache:
            raise cliapp.AppException('No cache available.')
        main_pool = os.path.join(self.destdir, '..', 'pool', 'main')
        os.makedirs(main_pool)
        for pkg_name in self.cache.keys():
            prefix = pkg_name[0]
            # destdir is just a base, needs pool/main/[index]/[name]
            if pkg_name[:3] == 'lib':
                prefix = pkg_name[:4]
            pkg_dir = os.path.join(main_pool, prefix, pkg_name)
            if pkg_name in exclude_list:
                continue
            pkg = self.cache[pkg_name]
            if not hasattr(pkg, 'versions'):
                continue
            if len(pkg.versions) > 1:
                pkg.version_list.sort(apt_pkg.version_compare) # pylint: disable=no-member
                version = pkg.version_list[0]
                print("Multiple versions returned for %s - using newest: %s" % (pkg_name, pkg.version_list[0]))
            else:
                version = pkg.versions[0]
            if not version.uri:
                continue
            os.makedirs(pkg_dir)
            try:
                version.fetch_binary(destdir=pkg_dir)
            except TypeError as exc:
                continue
            except apt.package.FetchError as exc:
                raise cliapp.AppException('Unable to fetch %s: %s' % (pkg_name, exc))
        # FIXME: still need a Packages file and Release.
        # Horribe hardcoded mess --------------------------------------
        packages = check_output(['apt-ftparchive', '-o', 'Packages::Extensions=.udeb', 'packages', os.path.join(self.destdir, '..', 'pool', 'main')])
	meta_dir = os.path.normpath(os.path.join(self.destdir, '..', 'dists',
						 self.codename,
                                                 'main',
                                                 'debian-installer',
                                                 'binary-%s' % (self.architecture,)
                                                ))
        if not os.path.exists(meta_dir):
            os.makedirs(meta_dir)
        packages = re.sub(r"/tmp.*pool", "pool", packages)
        with open(os.path.join(meta_dir, 'Packages'), 'w') as pkgout:
            pkgout.write(packages)
        # More mess, this time for debs
        packages = check_output(['apt-ftparchive', '-o', 'Packages::Extensions=.deb', 'packages', os.path.join(self.destdir, '..', 'pool', 'main')])
        meta_dir = os.path.normpath(os.path.join(self.destdir, '..', 'dists', self.codename, 'main', 'binary-%s' % (self.architecture,)))
        if not os.path.exists(meta_dir):
            os.makedirs(meta_dir)
        packages = re.sub(r"/tmp.*pool", "pool", packages)
        with open(os.path.join(meta_dir, 'Packages'), 'w') as pkgout:
            pkgout.write(packages)
        release = check_output([
                'apt-ftparchive',
                '-o', 'APT::FTPArchive::Release::Origin=Debian',
                '-o', 'APT::FTPArchive::Release::Label=Debian',
                '-o', 'APT::FTPArchive::Release::Suite=%s' % (self.suite,),
                '-o', 'APT::FTPArchive::Release::Codename=%s' % (self.codename,),
                '-o', 'APT::FTPArchive::Release::Architectures=%s' % (self.architecture,),
                '-o', 'APT::FTPArchive::Release::Components=main',
	        'release', os.path.abspath(os.path.join(self.destdir, '..', 'dists', self.codename))])
        with open(os.path.join(self.destdir, '..', 'dists', self.codename, 'Release'), 'w') as relout: 
            relout.write(release)
        logging.info("Release file generated for CD-ROM pool.")
        # End mess ----------------------------------------------------

    def clean_up_apt(self):
        for clean in self.dirlist:
            if os.path.exists(clean):
                shutil.rmtree(clean)


def get_apt_handler(destdir, mirror, codename, architecture):
    apt_handler = AptUdebDownloader(destdir)
    apt_handler.mirror = mirror
    apt_handler.architecture = architecture
    apt_handler.codename = codename
    apt_handler.components = ['main', 'contrib', 'non-free']
    apt_handler.prepare_apt()
    return apt_handler
