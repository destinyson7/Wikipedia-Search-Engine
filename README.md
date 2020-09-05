# Wikipedia Search Engine

A search engine for searching Wikipedia XML dumps.

## Requirements

python3 and PyStemmer library is required to run the search engine.

## Creation of Inverted Index

To create the inverted index, run the following command.

```bash
./index.sh <path_to_wiki_dump_file> <path_to_index_folder>
```

The arguments are the paths to the Wikipedia XML dump file and the folder where the inverted index is to be created and stored.

## Querying

To search, run the following command.

```bash
./search.sh <path_to_index_folder> <query_string>
```

It will output the postings lists of every word in the query that is present in the index that matches the given field (if given any).

### Submission for Phase 1
#### Tanish Lad (2018114005)