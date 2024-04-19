# Entrez Programming Utilities Help 

Last Updated: April, 18 2024

Note: This document is an updated guide with a focus on Python programming.
The original guide is can be found at [books/NBK25501](https://www.ncbi.nlm.nih.gov/books/NBK25501)

The Entrez Programming Utilities (E-utilities) are a set of eight server-side programs that
provide a stable interface into the Entrez query and database system at the National Center
for Biotechnology Information (NCBI). The E-utilities use a fixed URL syntax that translates
a standard set of input parameters into the values necessary for various NCBI software
components to search for and retrieve the requested data. The E-utilities are therefore the
structured interface to the Entrez system, which currently includes 38 databases covering a
variety of biomedical data, including nucleotide and protein sequences, gene records, three-
dimensional molecular structures, and the biomedical literature.

---
## Table of Contents

- [E-utilities Quick Start](#E-utilities-Quick-Start)
- [A General Introduction to the E-utilities](#A-General-Introduction-to-the-E-utilities)
- [Sample Applications of the E-utilities](#Sample-Applications-of-the-E-utilities)
- [The E-utilities In-Depth: Parameters, Syntax and More](#The-E-utilities-In-Depth-Parameters-Syntax-and-More)
- [Entrez Direct: E-utilities on the Unix Command Line](#Entrez-Direct-E-utilities-on-the-Unix-Command-Line)

---
## E-utilities Quick Start {#E-utilities-Quick-Start}

### Introduction

This chapter provides a brief overview of basic E-utility functions along with examples of URL calls. 

Examples include live URLs that provide sample outputs.

All E-utility calls share the same base URL:

https://eutils.ncbi.nlm.nih.gov/entrez/eutils/

### Searching a Database
#### Basic Searching
esearch.fcgi?db=<database>&term=<query>

#### Storing Search Results
esearch.fcgi?db=<database>&term=<query>&usehistory=y

#### Associating Search Results with Existing Search Results
esearch.fcgi?db=<database>&term=<query1>&usehistory=y

#### Searching PubMed with Citation Data
ecitmatch.cgi?db=pubmed&rettype=xml&bdata=<citations>


### Uploading UIDs to Entrez
#### Basic Uploading
epost.fcgi?db=<database>&id=<uid_list>

#### Associating a Set of UIDs with Previously Posted Sets
epost.fcgi?db=<database1>&id=<uid_list1>


### Downloading Document Summaries
#### Basic Downloading
esummary.fcgi?db=<database>&id=<uid_list>

##### Downloading Data From a Previous Search
esearch.fcgi?db=<database>&term=<query>&usehistory=y

#### Finding Links to Data from a Previous Search
esearch.fcgi?db=<source_db>&term=<query>&usehistory=y

### Downloading Full Records
#### Basic Downloading
efetch.fcgi?db=<database>&id=<uid_list>&rettype=<retrieval_type>
&retmode=<retrieval_mode>

#### Downloading Data From a Previous Search
esearch.fcgi?db=<database>&term=<query>&usehistory=y



### Finding Related Data Through Entrez Links
#### Basic Linking Batch mode – finds only one set of linked UIDs
elink.fcgi?dbfrom=<source_db>&db=<destination_db>&id=<uid_list>

#### Finding Links to Data from a Previous Search
esearch.fcgi?db=<source_db>&term=<query>&usehistory=y

#### Finding Computational Neighbors Limited by an Entrez Search
elink.fcgi?dbfrom=<source_db>&db=<source_db>&id=<uid_list>&term=
<query>&cmd=neighbor_history



### Getting Database Statistics and Search Fields
#### Basic Stats
einfo.fcgi?db=<database>

### Performing a Global Entrez Search
#### Basic Global Search
egquery.fcgi?term=<query>

### Retrieving Spelling Suggestions
#### Basic Spelling retrieval
espell.fcgi?term=<query>&db=<database>




