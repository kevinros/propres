# ProPres and RTPR: A Dataset and Framework for Real-Time Proactive Information Retrieval

## Data

The dataset for this paper is available [here](https://uofi.box.com/s/jbka7k7y10mcfeule6yoe2ahl18d4ggy).

The "Alignment" folder contains JSON files, each corresponding to a paper/transcript pair. Each file contains the following keys:

1. "raw_transcript": the transcription of the paper presentation
2. "modified_segments": a list of extracted segments from the paper
3. "annotations": a mapping between the transcript chunks and the aligned segments
4. "summary": a short summary of the paper

The "retrieval_*" folders contain the formatted data for training retrieval models. It contains the following files:

1. "collection.tsv": all paper segments (i.e., the retrieval targets) formatted as ``document_id \t document segment``
2. "queries_*.tsv": all queries (transcript of every word or skipping five words) formatted as ``query_id \t transcript chunk``
3. "top_k_ranking": relevance labels formatted as ``query_id \t document_id``
4. "mappings.json": metadata file used for mapping the above samples back to the Alignment folder data