# Wikipedia Search Engine

A search engine for searching Wikipedia XML dumps.

## Requirements

python3 and PyStemmer library is required to run the search engine.

## Creation of Inverted Index

To create the inverted index, run the following command.

```python
python3 wiki_indexer.py <path_to_wiki_dump_folder> <path_to_index_folder>
```

The arguments are the paths to the Wikipedia XML dump folder which contains all the wiki dump files and the folder where the inverted index is to be created and stored.

## Querying

To search, run the following command.

```python
python3 wiki_search.py <path_to_query_file>
```

## Conventions
1. Index is split into many files. Each file's name is a number starting from 0 up until 3076 and the file extension is .txt.

2. There is a titles folder. Each file's name is a number starting from 0 up until 4914 and the file extension is .txt.

### Submission for Phase 2
#### Tanish Lad (2018114005)