from greenlet import greenlet


"""
This module contains a few ways to transform the block-push paradigm used by the DirMetaDataProvider into more familiar ones.
"""




def _general_push_pull_adaptor(func, coroutine_pull_builder):
    """Adapts a function which accepts a generator to a reader.
    A reader is a function which can be called multiple times with
    a nonempty block of data, and once with None, or an empty block of data.

    """

    grnlt_access = [False]    # Ugliness as Python 2.x lacks 'nonlocal'

    def reader(block):
        grnlt = grnlt_access[0]

        if grnlt is None:
            return False

        if grnlt is False:
            grnlt = grnlt_access[0] = greenlet(func)
            grnlt.switch(coroutine_pull_builder())

            if grnlt.dead:
                grnlt_access[0] = None
                return False


        grnlt.switch(block)

        if grnlt.dead:
            grnlt_access[0] = None
            return False

        # After feeding an empty block, the greenlet should finish processing, and return (i.e: become dead).
        # If this does not occur, there is a serious flaw in the greenlet switching logic.
        assert block, "At this point, we must have a nonempty block"

        return True


    return reader


def _greenlet_block_generator():
    block = greenlet.getcurrent().parent.switch()

    try:
        while block:
            yield block
            block = greenlet.getcurrent().parent.switch()

    finally:
        block = None


def reader_from_generator_accepting_function(func):
    """Adapts a function which accepts a generator which yields blocks of data
    to a reader. A reader is a function which can be called multiple times with
    a nonempty block of data, and once with None, or an empty block of data.

    """

    return _general_push_pull_adaptor(func, _greenlet_block_generator)



def _greenlet_byte_generator():
    block = greenlet.getcurrent().parent.switch()

    try:
        while block:
            for byte in block:
                yield byte

            block = greenlet.getcurrent().parent.switch()

    finally:
        block = None


def reader_from_byte_generator_accepting_function(func):
    """Adapts a function which accepts a generator which yields single bytes
    to a reader. A reader is a function which can be called multiple times with
    a nonempty block of data, and once with None, or an empty block of data.

    """

    return _general_push_pull_adaptor(func, _greenlet_byte_generator)


def block_to_byte_generator_wrapper(block_generator):
    try:
        for block in block_generator:
            for byte in block:
                yield byte

    except GeneratorExit:
        block_generator.close()






class _FileLikeBLockReader(object):

    def __init__(self):
        self._closed = False
        self._current_block = None
        self._next_byte_index = None
        self._sum_previous_blocksizes = 0


    def read(self, requested):
        """ Reads *exactly* 'requested' bytes from the stream,
        unless there are not enough bytes in the stream. After
        the stream is exhausted, the stream will close automatically.
        After a stream is closed, only '' (empty strings)
        will be returned.

        @param requested: The number of requested bytes. Must be > 0.
        """

        assert requested > 0

        if self._closed:
            return ''

        if self._current_block is None:
            self._read_next_block()

            if self._closed:
                return ''

        elif self._next_byte_index >= len(self._current_block):
            self._read_next_block()

            if self._closed:
                return ''


        if self._next_byte_index + requested < len(self._current_block):
            new_index = self._next_byte_index + requested
            result = self._current_block[self._next_byte_index:new_index]
            self._next_byte_index = new_index
            return result


        block = self._current_block[self._next_byte_index:]
        requested -= len(block)

        result = [block]
        while True:
            self._read_next_block()

            if self._closed:
                break

            if len(self._current_block) >= requested:
                self._next_byte_index = requested
                result.append(self._current_block[:requested])
                break

            requested -= len(self._current_block)
            result.append(self._current_block)


        return ''.join(result)



    def close(self):
        self._closed = True
        self._current_block = None


    @property
    def closed(self):
        return self._closed


    def __del__(self):
        self.close()


    def tell(self):
        return self._sum_previous_blocksizes + self._next_byte_index


    def seek(self, offset, whence=None):
        raise NotImplementedError()


    def _read_next_block(self):
        if self._closed:
            raise EOFError()

        previous_block_size = len(self._current_block) if self._current_block is not None else 0
        self._sum_previous_blocksizes += previous_block_size

        block = greenlet.getcurrent().parent.switch()
        if block:
            self._current_block = block
            self._next_byte_index = 0

        else:
            self.close()



class StreamReaderException(Exception):
    pass


class PrematureEndOfStream(StreamReaderException):
    pass


def reader_from_file_like_object_accepting_function(func):
    """Adapts a function which accepts a file-like object to a reader.
    A reader is a function which can be called multiple times with
    a nonempty block of data, and once with None, or an empty block of data.
    """

    return _general_push_pull_adaptor(func, _FileLikeBLockReader)
