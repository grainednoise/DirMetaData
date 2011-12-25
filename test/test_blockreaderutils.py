from dirmetadata.blockreaderutils import (
    reader_from_generator_accepting_function, reader_from_file_like_object_accepting_function)
import unittest



class TestGeneratorConsumer(object):
    def __init__(self):
        self.data =[]
    
    def consumer(self, generator):
        self.data.append('start')
        
        for block in generator:
            self.data.append(block)
        
        self.data.append('end')


    def limited_consumer(self, limit):
        
        def consumer(generator):
            self.data.append('start')
            
            for _ in range(limit):
                try:
                    self.data.append(generator.next())

                except StopIteration:
                    break
            
            self.data.append('end')
        
        return consumer    



class ReaderAdaptorTest(unittest.TestCase):

    def test_single_reader(self):
        testdata = ['block1', 'block2', 'block3']
        
        consumer = TestGeneratorConsumer()
        reader = reader_from_generator_accepting_function(consumer.consumer)
        
        
        self.assertEqual([], consumer.data)
        
        for d in testdata:
            self.assertTrue(reader(d))
        
        self.assertFalse(reader(''))
        
        self.assertEqual(['start'] + testdata + ['end'], consumer.data)


    def test_double_reader(self):
        testdata = ['block1', 'block2', 'block3']
        
        consumer1 = TestGeneratorConsumer()
        reader1 = reader_from_generator_accepting_function(consumer1.consumer)

        consumer2 = TestGeneratorConsumer()
        reader2 = reader_from_generator_accepting_function(consumer2.consumer)
        
        
        for d in testdata:
            self.assertTrue(reader1(d))
            self.assertTrue(reader2(d))
        
        self.assertFalse(reader1(''))
        self.assertFalse(reader2(''))
        
        expected = ['start'] + testdata + ['end']
        
        self.assertEqual(expected, consumer1.data)
        self.assertEqual(expected, consumer2.data)
        

    def test_single_reader_no_data(self):
        testdata = []
        
        consumer = TestGeneratorConsumer()
        reader = reader_from_generator_accepting_function(consumer.consumer)
        
        
        self.assertEqual([], consumer.data)
        
        for d in testdata:
            reader(d)
        
        reader('')
        
        self.assertEqual(['start'] + testdata + ['end'], consumer.data)     


    def test_single_reader_limited0(self):
        testdata = ['block1', 'block2', 'block3']
        
        consumer = TestGeneratorConsumer()
        reader = reader_from_generator_accepting_function(consumer.limited_consumer(0))
        
        
        self.assertEqual([], consumer.data)
        
        for d in testdata:
            reader(d)
        
        reader('')
        
        self.assertEqual(['start', 'end'], consumer.data)
        

    def test_single_reader_limited1(self):
        testdata = ['block1', 'block2', 'block3']
        
        consumer = TestGeneratorConsumer()
        reader = reader_from_generator_accepting_function(consumer.limited_consumer(1))
        
        
        self.assertEqual([], consumer.data)
        
        for d in testdata:
            reader(d)
        
        reader('')
        
        self.assertEqual(['start'] + testdata[:1] + ['end'], consumer.data)


    def test_single_reader_limited2(self):
        testdata = ['block1', 'block2', 'block3']
        
        consumer = TestGeneratorConsumer()
        reader = reader_from_generator_accepting_function(consumer.limited_consumer(2))
        
        
        self.assertEqual([], consumer.data)
        
        for d in testdata:
            reader(d)
        
        reader('')
        
        self.assertEqual(['start'] + testdata[:2] + ['end'], consumer.data)




testdata = "He had found a Nutri-Matic machine which had provided him with a plastic cup filled with a liquid that was almost, but not quite, entirely unlike tea."


class FileLikeAdaptorTest(unittest.TestCase):
    
    def test_read_all(self):
        called = [False]
        
        def read_all(stream):
            data = stream.read(100000)
            self.assertEqual(testdata, data)
            self.assertTrue(stream.closed)
            called[0] = True
        
        reader = reader_from_file_like_object_accepting_function(read_all)
        
        input_chunks = [testdata[start:start + 30] for start in range(0, len(testdata), 30)]
        for d in input_chunks:
            self.assertTrue(reader(d))
        
        self.assertFalse(reader(''))
        
        self.assertTrue(called[0])
        
        
    def read_per_chunk(self, testdata, input_chunk_size, request_sizes):
        total = sum(request_sizes)
        if total > len(testdata):
            raise ValueError("Total {0} exceeds {1}".format(total, len(testdata)))
        
        elif total < len(testdata):
            request_sizes.append(len(testdata) - total)
        
            
        called = [False]
        
        def read_all(stream):
            accumulated = []
            
            for request_size in request_sizes:
                self.assertFalse(stream.closed)
                data = stream.read(request_size)
                self.assertEqual(request_size, len(data), "Failure after {0} of {1} bytes".format(len(''.join(accumulated)), len(testdata)))
                accumulated.append(data)
                
            data = stream.read(1)
            self.assertEqual('', data)
            
            self.assertTrue(stream.closed)
            called[0] = True
            
            self.assertEqual(testdata, ''.join(accumulated))
        
        reader = reader_from_file_like_object_accepting_function(read_all)
        
        input_chunks = [testdata[start:start + input_chunk_size] for start in range(0, len(testdata), input_chunk_size)]
        for d in input_chunks:
            self.assertTrue(reader(d))
        
        self.assertFalse(reader(''))
        
        self.assertTrue(called[0])   
        
    
    def test_read_per_byte(self):
        self.read_per_chunk(testdata, 1, [1] * len(testdata))
        self.read_per_chunk(testdata, 20, [1] * len(testdata))
        self.read_per_chunk(testdata, 100, [1] * len(testdata))
        self.read_per_chunk(testdata, 200, [1] * len(testdata))
        

    def test_read_increasing(self):
        sizes = []
        size = 1
        while sum(sizes) + size < len(testdata):
            sizes.append(size)
            size += 1
            
        self.read_per_chunk(testdata, 20, sizes)
        self.read_per_chunk(testdata, 100, sizes)
        self.read_per_chunk(testdata, 200, sizes)


    def test_read_decreasing(self):
        sizes = []
        size = 1
        while sum(sizes) + size < len(testdata):
            sizes.append(size)
            size += 1
        
        rest = len(testdata) - sum(sizes)
        if rest > 0:
            sizes.append(rest)
        
        sizes.reverse()
        
        self.read_per_chunk(testdata, 20, sizes)
        self.read_per_chunk(testdata, 100, sizes)
        self.read_per_chunk(testdata, 200, sizes)

  

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()