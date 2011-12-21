from greenlet import greenlet

"""
This module contains a few ways to transform the block-push paradigm used by the DirMetaDataProvider into more familiar ones.
"""


def greenlet_generator():
    block = greenlet.getcurrent().parent.switch()
    
    try:
        while block:
            yield block
            block = greenlet.getcurrent().parent.switch()
    
    finally:
        block = None


def reader_from_generator_accepting_function(func):
    """Adapts a function which accepts a generator to a reader.
    A reader is a function which can be called multiple times with
    a nonempty block of data, and once with None, or an empty block of data.

    """
    
    grnlt_access = [None]    # Ugliness as Python 2.x lacks 'nonlocal'
    closed_access = [False]  # Ugliness as Python 2.x lacks 'nonlocal'
    
    def reader(block):
        if closed_access[0]:
            return
        
        grnlt = grnlt_access[0]
        if grnlt is None:
            grnlt = greenlet(func)
            grnlt_access[0] = grnlt
            grnlt.switch(greenlet_generator())
        
               
        grnlt.switch(block)
        
        if grnlt.dead:
            closed_access[0] = True
            grnlt_access[0] = None
            return
            
        assert block, "At this point, we must have a valid block"
    
    
    return reader



def block_to_byte_generator_wrapper(block_generator):
    try:
        for block in block_generator:
            for byte in block:
                yield byte 
                
    except GeneratorExit:
        block_generator.close()




class ReaderFromBlockGenerator(object):
    def __init__(self, block_generator):
        self._block_generator = block_generator
        self._current_block = None
        self._next_byte_index = None
        self._sum_previous_blocksizes = 0
    
        
    def read(self, requested):
        """ Reads /exactly/ 'requested' bytes from the stream,
        unless there are not enough bytes in the stream. After
        the stream is exhausted, only '' (empty strings)
        will be returned.
        """
        
        assert requested > 0
        
        if self._current_block is None:
            if self._block_generator is None:
                return ""
            
            self._read_next_block()
            if self._current_block is None:
                return ""
        
        elif self._next_byte_index >= len(self._current_block):
            self._read_next_block()
            if self._current_block is None:
                return ""
        
        
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
            
            if self._block_generator is None:
                break
            
            if len(self._current_block) >= requested:
                self._next_byte_index = requested
                result.append(self._current_block[:requested])
                break
            
            requested -= len(self._current_block)
            result.append(self._current_block)
        
        
        return ''.join(result)
    
    
    def close(self):
        if self._block_generator is not None:
            self._block_generator.close()
            self._block_generator = None
    
    
    
    def __del__(self):
        self.close()
    
    
    def tell(self):
        return self._sum_previous_blocksizes + self._next_byte_index
    
    
    def seek(self, offset, whence=None):
        raise NotImplementedError()
        
    
    def _read_next_block(self):
        if self._block_generator is None:
            raise EOFError()
            
        try:
            previous_block_size = len(self._current_block) if self._current_block is not None else 0
            self._current_block = self._block_generator.next()
            self._next_byte_index = 0
            self._sum_previous_blocksizes += previous_block_size
            
        except StopIteration:
            self._current_block = None
            self._block_generator = None
    
            

class StreamReaderException(Exception):
    pass


class PrematureEndOfStream(StreamReaderException):
    pass



