# ProPres and RTPR: A Dataset and Framework for Real-Time Proactive Information Retrieval

## Abstract

Real-time proactive information retrieval is where user information needs are anticipated and resolved with minimal user effort in real-time. This direction is an attractive new IR application, but it not yet been well studied partly because of the lack of test collections for evaluating such a task. To address this, we create the ProPres (Proactive retrieval during Presentation) dataset, which is designed for studying real-time proactive retrieval during conference presentations. The dataset consists of 356,657 extracted segments (e.g., sentences, references, tables, figure descriptions, etc.) from 1,000 AI-related academic papers, along with their corresponding conference presentation transcripts. Each paper's segments are aligned to the relevant points in the corresponding transcript, resulting in 32,970 transcript alignment points across 92,273 segments. We also propose the RTPR (Real-Time Proactive Retrieval) framework, which defines nine evaluation metrics designed to measure both the information discovery abilities and the end-user utility of real-time proactive retrieval models. Finally, we use the RTPR framework to evaluate various retrieval models on the ProPres dataset. We find that existing out-of-the-box retrieval models perform poorly for proactive retrieval, and that models generally struggle with knowing when to make predictions. Our findings provide a concrete path towards applications designed to support real-time proactive information retrieval with minimal user effort.

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