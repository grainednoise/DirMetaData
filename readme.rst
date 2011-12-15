About this project
==================

The eventual aim of this project is to be able to store all kinds of metadata about files. Why then, you might ask, is the project called DirMetaData? Well, that is because it is more convenient to store the metatadata *per directory* rather than *per file*. 

There is a lot of different types of metadata that could be stored for a file., To name some:

* File hash
* Content hash. This differs from file hash in that it disregards certain data in the file. For example: a content hash for an MP3 files will *only* be calculated from frames which actally contain real MP3 data. Frames with ID3 tags, or spurious data will be disregarded. For document type files, a content hash can be created by hashing a generic text representation of the files (e.g. by stripping all style markup). In general, content hashed allow tracking of files even if some aspects of the data change.
* Key/value pairs. Some file formats contain data in the form of key/value pairs. For instance, many document files coutain an 'autor' field, and that data could be extracted as such. Other examples could be the EXIF data in JPG files, and the ID3 data in MP3 files.
* User tags/keywords
* User key/value pairs
* User notes (this might be modelled as a key/value pair with the key being 'notes'.)
* Thumbnails (for pictures)
* Versioning. When the file or content hash changes, the old values can be remembered. This allows you to determine if you have more than one version of the same file. 

Well, this list is probably far from exhaustive, but you get the picture. Currently, there are no plans to expand the scope of this project beyond the collection and maintenance of metadata, but the API will enable other projects or applications to leverage this data for a multitude of purposes. Examples sre:

* Finding duplicate files: the file hash will allow you to find exact duplicates, and the content hash will allow you to find effectively duplicate files.
* Finding files based on tags/keywords
* Finding files based key/value pairs
* Extending the (OS-dependent) file manager to display the metadata.
