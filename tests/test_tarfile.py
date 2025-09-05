#!/usr/bin/python3
#
# Copyright (C) 2025 Canonical Ltd.
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.
"""Unit tests for verifying the correctness of tarfile management used in apt.debfile."""
import os
import resource
import sys
import unittest

from test_all import get_library_dir

libdir = get_library_dir()
if libdir:
    sys.path.insert(0, libdir)

import apt_inst
import testcommon


class TestTarfile(testcommon.TestCase):
    """test the tarfile"""

    # Large tarfile with single member called 'large_member'
    TEST_LARGE_TARFILE: str = "./data/misc/large_tar.zst"
    TEST_LARGE_TARFILE_MEMBER: str = "large_member"
    tarfile = apt_inst.TarFile(TEST_LARGE_TARFILE, comp="zstd")

    # Setting resource limit to trigger MemoryError for large files
    VR_MEM_LIMIT_HARD: int = 2**31
    VR_MEM_LIMIT_SOFT: int = VR_MEM_LIMIT_HARD
    resource.setrlimit(resource.RLIMIT_AS, (VR_MEM_LIMIT_SOFT, VR_MEM_LIMIT_HARD))

    def test_go_extract_data_large_file_oom(self):
        files = []
        with self.assertRaises(MemoryError):
            self.tarfile.go(
                (lambda item, data: files.append(item.name)),
                self.TEST_LARGE_TARFILE_MEMBER,
                True,
            )
        self.assertEqual(files, [])

    def test_go_extract_false_large_file_no_oom(self):
        files = []
        try:
            self.tarfile.go(
                (lambda item, data: files.append(item.name)),
                self.TEST_LARGE_TARFILE_MEMBER,
                False,
            )
        except MemoryError:
            self.fail(
                "tarfile.go(...) raised MemoryError with extract_data set to False!"
            )
        self.assertEqual(files, [self.TEST_LARGE_TARFILE_MEMBER])

    def test_go_skip_extract_large_file_if_not_specified(self):
        files = []
        try:
            self.tarfile.go((lambda item, data: files.append(item.name)), "", True)
        except MemoryError:
            self.fail(
                "tarfile.go(...) raised MemoryError when no member was specified!"
            )
        self.assertEqual(files, [self.TEST_LARGE_TARFILE_MEMBER])


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    os.chdir(os.path.dirname(__file__))
    _ = unittest.main()
