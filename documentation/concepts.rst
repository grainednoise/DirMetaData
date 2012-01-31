
Introduction & concepts
#######################

"So what's this project all about," you might ask, "and what can it do for
me?" Truth be said, that is a hard question to answer succinctly. I'll try
to anwer the first part of the question first:
 
 ..  pull-quote::
   ``Dirmetadata`` records and maintains metadata about every file in a
   particular directory on a file system. The metadata resides in a
   single file, ``.dirmetadata``, in the same directory as the files.

The term 'metadata' suggest that it concerns data about the individual files,
but it doesn't say anything about what kind of data that might be. It all
remains kind of vague. The problem here is, it *is* vague by nature. A lot of
it depends on the file type itself: an .mp3 file will yield different metadata
than a .jpg file, and some files don't really have any metadata themselves at
all.

Thus metadata comes in a few flavours:

#. Intrinsic metadata
   This type of data can be extracted form the file itself. Typically,
   different file types have different types of metadata.
  
#. Content metadata is a type of intrinsic metadata, but it's specific to the
   content of a file.
 
#. User metadata

#. Historical metadata