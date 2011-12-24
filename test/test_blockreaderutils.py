from dirmetadata.blockreaderutils import (
    reader_from_generator_accepting_function)
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



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()