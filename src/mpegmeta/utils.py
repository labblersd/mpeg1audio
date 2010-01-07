"""Helpers used in package."""

# Pylint disable settings:
# ------------------------
# ToDos, DocStrings:
# pylint: disable-msg=W0511,W0105 
 
# Unused variable, argument:
# pylint: disable-msg=W0612,W0613

# Re-define built-in:
# pylint: disable-msg=W0622

DEFAULT_CHUNK_SIZE = 8192
"""Chunk size for chunked reader, if not given.
@type: int"""

def get_filesize(file):
    """Get file size from file object.
    
    @param file: File object, returned e.g. by L{open<open>}.
    @type file: file object
    
    @return: File size in bytes.
    @rtype: int
    
    """
    offset = file.tell()
    file.seek(0, 2)
    filesize = file.tell()
    file.seek(offset)
    return filesize
    
def chunked_reader(file, chunk_size=None, start_position= -1,
                    max_chunks= -1, reset_offset=True):
    """Reads file in chunks for performance in handling of big files.
    
    @param file: File to be read, e.g. returned by L{open<open>}.
    @type file: file object
    
    @keyword chunk_size: Read in this sized chunks, C{None} defaults to 
        L{DEFAULT_CHUNK_SIZE}.
    @type chunk_size: int
    
    @keyword start_position: Start position of the chunked reading, C{-1} means
        that the file is not being seeked to new position.
    @type start_position: int
    
    @keyword max_chunks: Maximum amount of chunks, C{-1} means I{infinity}.
    @type max_chunks: int
    
    @keyword reset_offset: Resets the offset of seeking between chunks. Used
        to correct the cursor position when file seeks / reads occurs inside 
        chunk iteration.
    @type reset_offset: bool
    
    @return: Generator of file chunks as tuples of chunk offset and chunk.
    @rtype: generator of (chunk_offset, chunk)
    
    """
    if start_position != -1:
        file.seek(start_position)
        
    offset = file.tell()
    chunk = ""
    chunk_size = chunk_size or DEFAULT_CHUNK_SIZE 
            
    i = 0
    while True:
        if 0 < max_chunks <= i:
            break
        
        if reset_offset:
            file.seek(offset + len(chunk))
        
        offset = file.tell()
        chunk = file.read(chunk_size)
        if not chunk:
            break
        yield (offset, chunk)
        i += 1

def find_all_overlapping(string, occurrence):
    """Find all overlapping occurrences.
    
    @param string: String to be searched.
    @type string: string
    
    @param occurrence: Occurrence to search.
    @type occurrence: string
    
    @return: generator yielding I{positions of occurence}
    @rtype: generator of int
    
    """
    found = 0
    
    while True:
        found = string.find(occurrence, found)
        if found != -1:
            yield found
        else:
            return
        
        found += 1

# TODO: HIGH: Wrap Open and Close.
def wrap_open_close(function, object, filename, mode='rb',
                    file_handle_name='_file'):
    """Wraps the objects file handle for execution of function.
    
    @param function: Function to be executed during file handle wrap.
    @type function: callable
    
    @param object: Object having the file handle.
    @type object: object
    
    @param filename: Filename opened.
    @type filename: string
    
    @keyword mode: Opening mode.
    @type mode: string
    
    @keyword file_handle_name: Name of the instance variable in object.
    @type file_handle_name: string
    
    @return: New function which being run acts as wrapped function call.
    @rtype: function
    
    """
    file_handle = getattr(object, file_handle_name)
    
    if (file_handle is not None) and (not file_handle.closed):
        function()
        return
    
    new_file_handle = open(filename, mode)
    setattr(object, file_handle_name, new_file_handle)
    function()
    new_file_handle.close()
        
def join_iterators(iterable1, iterable2):
    """Joins list and generator.
    
    @param iterable1: List to be appended.
    @type iterable1: Generator
    
    @param iterable2: Generator to be appended.
    @type iterable2: generator
    
    @return: Generator yielding first iterable1, and then following iterable2.
    @rtype: generator
    
    """
    for item1 in iterable1:
        yield item1
        
    for item2 in iterable2:
        yield item2
        
def genmin(generator, min):
    """Ensures that generator has min amount of items left.
    
    @param generator: Generator to be ensured.
    @type generator: generator
    
    @param min: Minimum amount of items in generator.
    @type min: int
    
    @raise ValueError: Raised when minimum is not met.
    
        >>> def yrange(n): # Note that xrange doesn't work, requires next()
        ...     for i in range(n):
        ...         yield i
        ... 
        >>> genmin(yrange(5), min=4) #doctest: +ELLIPSIS
        <generator object join_iterators at ...>
        >>> genmin(yrange(5), min=5) #doctest: +ELLIPSIS
        <generator object join_iterators at ...>
        >>> genmin(yrange(5), min=6)
        Traceback (most recent call last):
          ...
        ValueError: Minimum amount not met.
        >>> 
        
    """
    cache = []
    for index in range(min): #@UnusedVariable
        try:
            cache.append(generator.next())
        except StopIteration:
            raise ValueError('Minimum amount not met.')
        
    return join_iterators(cache, generator)

def genmax(generator, max):
    """Ensures that generator does not exceed given max when yielding.
    
    For example when you have generator that goes to infinity, you might want to
    instead only get 100 first instead.
    
    @param generator: Generator
    @type generator: generator

    @param max: Maximum amount of items yields.
    @type max: int
    
    @rtype: generator
    @return: Generator limited by max.
    
        >>> list(genmax(xrange(100), max=3))
        [0, 1, 2]
        
    """
    for index, item in enumerate(generator):
        yield item
        if index + 1 >= max:
            return
        
def genlimit(generator, min, max):
    """Limit generator I{item count} between min and max.
    
    @param generator: Generator
    @type generator: generator

    @param min: Minimum amount of items in generator.
    @type min: int, or None
    
    @param max: Maximum amount of items.
    @type max: int, or None
    
    @note: If both are C{None} this returns the same generator.
    @raise ValueError: Raised when minimum is not met.
    
    """
    if (min is None) and (max is None):
        return generator
    
    if min is not None:
        generator = genmin(generator, min)
        
    if max is not None:
        generator = genmax(generator, max)
        
    return generator