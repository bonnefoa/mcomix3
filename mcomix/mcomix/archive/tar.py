# -*- coding: utf-8 -*-

''' Unicode-aware wrapper for tarfile.TarFile. '''

import os
import tarfile
from mcomix.archive import archive_base

class TarArchive(archive_base.NonUnicodeArchive):
    def __init__(self, archive):
        super(TarArchive, self).__init__(archive)
        # Track if archive contents have been listed at least one time: this
        # must be done before attempting to extract contents.
        self._contents_listed = False
        self._contents = []
        self.tar = None

    def is_solid(self):
        return True

    def iter_contents(self):
        if not self._contents_listed:
            if not self.tar:
                # Make sure we start back at the beginning of the tar.
                self.tar = tarfile.open(self.archive, 'r:*')
            self._contents.clear()
            self._contents.extend((self._unicode_filename(name)
                                   for name in self.tar.getnames()))
            self._contents_listed = True
        yield from self._contents

    def list_contents(self):
        return [filename for filename in self.iter_contents()]

    def extract(self, filename, destination_dir):
        if not self._contents_listed:
            self.list_contents()
        destination_path = os.path.join(destination_dir, filename)
        with self._create_file(destination_path) as new, \
             self.tar.extractfile(self._original_filename(filename)) as file_object:
            new.write(file_object.read())
        return destination_path

    def iter_extract(self, entries, destination_dir):
        if not self._contents_listed:
            self.list_contents()
        for f in super(TarArchive, self).iter_extract(entries, destination_dir):
            yield f

    def close(self):
        if self.tar is not None:
            self.tar.close()
            self.tar = None

# vim: expandtab:sw=4:ts=4
