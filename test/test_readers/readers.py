# -*- coding: utf-8 -*-

import datetime
import os.path

from dirmetadata.readers import FileSystemDirectoryReader


test_directory = os.path.abspath(os.path.join(__file__, '..', '..', 'testdata'))

def reader():
    return FileSystemDirectoryReader('test', None, test_directory)


def test_not_empty_files():
    expected = set(['Lyrical Ballads 1798.txt', 'pg19033-images.epub'])
    assert expected == set(reader().files())


def test_attributes():
    result = reader().get_file_info('Lyrical Ballads 1798.txt')
    print result
    assert 151549 == result['size']
    assert 0o100666 == result['mode']

    # 2012-09-16 09:10:17.168216000 +0200 Lyrical Ballads 1798.txt
    assert datetime.datetime(2012, 9, 16, 9, 10, 17) == datetime.datetime.fromtimestamp(result['created']).replace(microsecond=0)

    # ‎2012-05-26 10:42:27.471178200 +0200 Lyrical Ballads 1798.txt
    assert datetime.datetime(2012, 5, 26, 10, 42, 27) == datetime.datetime.fromtimestamp(result['modified']).replace(microsecond=0)

