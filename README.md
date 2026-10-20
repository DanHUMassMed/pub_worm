# pub_worm

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Package Manager: uv](https://img.shields.io/badge/managed%20by-uv-DE5FE9.svg?logo=python&logoColor=white)](https://github.com/astral-sh/uv)
[![Typing: Mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://mypy-lang.org/)

**A unified, high-performance Python toolkit for biological data mining, literature retrieval, and genomic sequence extraction across major scientific web services.**

`pub_worm` streamlines access to key biological databases, with specialized integrations for ***Caenorhabditis elegans*** genomics and general biomedical literature workflows:

* **[WormBase](https://wormbase.org)**: Direct REST API querying for genes, papers, and widgets; automated C. elegans gene ID resolution and sequence alias mapping.
* **[NCBI Entrez & PubMed](https://eutils.ncbi.nlm.nih.gov/entrez/eutils)**: E-utilities wrapper (`esearch`, `epost`, `esummary`, `efetch`, `elink`) with automated batching and PMC full-text harvesting.
* **[bioRxiv](https://www.biorxiv.org)**: Real-time RSS feed parsing, date-range REST searches, and strictly validated Pydantic v2 metadata models.
* **[Ensembl](https://rest.ensembl.org)**: Synchronous and asynchronous genomic sequence region extraction, promoter window calculations, and FASTA file generation.
* **[ORCID](https://pub.orcid.org)**: Public v3.0 researcher profile and record retrieval.
* **Journal Impact Factor Lookup**: Fast, pre-indexed ISSN/eISSN mapping to Clarivate Journal Citation Reports (JCR) impact metrics.

---

## Table of Contents

- [Key Features](#key-features)
- [Module Architecture](#module-architecture)
- [Installation](#installation)
- [Configuration & Environment Variables](#configuration--environment-variables)
- [Quickstart & Examples](#quickstart--examples)
  - [1. WormBase REST & Gene ID Mapping](#1-wormbase-rest--gene-id-mapping)
  - [2. NCBI Entrez & PubMed Extraction](#2-ncbi-entrez--pubmed-extraction)
  - [3. bioRxiv Search & Preprint Monitoring](#3-biorxiv-search--preprint-monitoring)
  - [4. Ensembl Sequence Retrieval & FASTA Export](#4-ensembl-sequence-retrieval--fasta-export)
  - [5. ORCID Author Lookup](#5-orcid-author-lookup)
  - [6. Journal Impact Factor Lookup](#6-journal-impact-factor-lookup)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
- [Development Workflow](#development-workflow)
- [Testing & Quality Gates](#testing--quality-gates)
- [Contributing](#contributing)
- [License](#license)

---

## Key Features

* **Dual Sync / Async APIs:** High-throughput `aiohttp` and `asyncio` routines alongside straightforward synchronous methods.
* **Data Validation via Pydantic v2:** Strongly-typed schemas for reliable handling of complex nested JSON payloads.
* **Resilient Networking:** Built-in configurable exponential backoff and rate-limit handling for high-volume API requests.
* **Automated Data Wrangling:** Helpers to flatten nested biomedical JSON directly into clean `pandas.DataFrame` tables and CSV files.
* **Zero Boilerplate Environment:** Fully configured for Python 3.12+ using `uv` and `make`.

---

## Module Architecture

| Module | Core Classes / Functions | Primary Data Source | Typical Use Cases |
| :--- | :--- | :--- | :--- |
| `pub_worm.wormbase` | `WormbaseAPI`, `map_wormbase_ids` | `rest.wormbase.org`, `downloads.wormbase.org` | Gene summaries, GO terms, sequence ID normalization |
| `pub_worm.ncbi` | `EntrezAPI` | `eutils.ncbi.nlm.nih.gov` | PubMed searches, XML metadata parsing, author & citation extraction |
| `pub_worm.biorxiv` | `biorxiv_search`, `biorxiv_recent_posts_filtered` | `api.biorxiv.org`, `connect.biorxiv.org` | Tracking preprint releases, automated keyword monitoring |
| `pub_worm.ensembl` | `get_sequence_region`, `async_get_sequence_region`, `create_fasta` | `rest.ensembl.org` | Genomic DNA extraction, promoter windows (2kb upstream) |
| `pub_worm.orcid` | `OrcidAPI` | `pub.orcid.org/v3.0` | Researcher affiliation resolution, verified paper attribution |
| `pub_worm.impact_factor`| `get_impact_factor` | Bundled JCR Index | Annotating publication lists with journal impact factors |

---

## Installation

### Recommended: Using `uv`

```bash
uv pip install pub-worm
```

Or add it directly to your project dependencies:

```bash
uv add pub-worm
```

### Standard `pip`

```bash
pip install pub-worm
```

---

## Configuration & Environment Variables

While many endpoints (such as bioRxiv and Ensembl) require no credentials, certain services benefit from higher rate limits or require access keys:

| Variable | Target Service | Purpose | Default |
| :--- | :--- | :--- | :--- |
| `NCBI_API_KEY` | NCBI Entrez | Increases rate limit from 3 req/sec to 10 req/sec | `None` (standard rate limits) |
| `ORCID_ACCESS_TOKEN` | ORCID API | Required for authenticated ORCID v3.0 member API requests | `None` (public endpoint) |

You can export these in your shell or define them in a `.env` file:

```bash
export NCBI_API_KEY="your-ncbi-api-key-here"
export ORCID_ACCESS_TOKEN="your-orcid-bearer-token"
```

---

## Quickstart & Examples

### 1. WormBase REST & Gene ID Mapping

#### Querying Gene Overview and Gene Ontology Summaries

```python
from pub_worm.wormbase.wormbase_api import WormbaseAPI

# Instantiate an API client for a specific endpoint schema:
# WormbaseAPI(call_type, call_class, data_request)
gene_client = WormbaseAPI("widget", "gene", "overview")

# Retrieve structured overview data for daf-16 (WBGene00000912)
result = gene_client.get_wormbase_data("WBGene00000912")
print(f"Gene Name: {result.get('wb_gene_name')}")

# Query Gene Ontology annotations
go_client = WormbaseAPI("field", "gene", "gene_ontology_summary")
go_data = go_client.get_wormbase_data("WBGene00000912")
print("GO Summary:", go_data)
```

#### Batch Mapping Experimental Sequence IDs to WormBase Genes

Normalize experimental sequence tags, isoforms, and legacy names to canonical `WBGene` identifiers:

```python
from pathlib import Path
from pub_worm.wormbase.wormbase_util import map_wormbase_ids

# Map IDs from an input CSV containing a column named 'ID'
found_df, not_found_df = map_wormbase_ids(
    sequence_ids_file_path=Path("my_experiment_ids.csv"),
    column_name="ID",
    working_dir_path=Path("./output")
)

print(f"Successfully matched {len(found_df)} genes.")
print(found_df[["Initial_Alias", "Wormbase_Id", "Gene_name"]].head())
```

---

### 2. NCBI Entrez & PubMed Extraction

Execute structured queries, store UID history on the NCBI server (`WebEnv`), and extract rich metadata, affiliations, and citation networks:

```python
from pub_worm.ncbi.entreze_api import EntrezAPI

ncbi = EntrezAPI()

# 1. Search PubMed and store results in history
search_query = "caenorhabditis elegans[Organism] AND daf-16[Title/Abstract] AND 2024[PDAT]"
search_results = ncbi.entreze_esearch({"term": search_query})

print(f"Total matching articles: {search_results.get('count')}")

# 2. Fetch full article metadata and citation records using WebEnv
if "WebEnv" in search_results:
    data = ncbi.entreze_efetch(search_results)
    
    # Process structured article summaries
    for article in data.get("articles", []):
        print(f"PMID: {article.get('pmid')} | {article.get('title')}")
        print(f"Journal: {article.get('pub_abbr')} | Impact Factor: {article.get('impact_factor')}\n")
```

---

### 3. bioRxiv Search & Preprint Monitoring

Filter recent preprints from the RSS feed or execute parameterized date-range REST queries:

```python
from pub_worm.biorxiv.biorxiv_api import biorxiv_search, biorxiv_recent_posts_filtered

# Scan the latest 30 preprints from the RSS feed for C. elegans keywords
recent_worm_papers = biorxiv_recent_posts_filtered(keywords=["elegans", "nematode"])
for paper in recent_worm_papers:
    print(f"[{paper['date']}] {paper['title']}")
    print(f"DOI: {paper['doi']}\n")

# Query the REST API for papers matching criteria in the last 7 days
preprints = biorxiv_search(
    search_criteria="aging lifespan",
    days=7,
    verbose=True
)
print(f"Found {len(preprints)} matching preprints.")
```

---

### 4. Ensembl Sequence Retrieval & FASTA Export

Retrieve genomic regions directly from Ensembl and write formatted FASTA records:

#### Synchronous Sequence Fetch

```python
from pub_worm.ensembl.ensembl_api import get_sequence_region, create_fasta

# Fetch genomic coordinates: Chromosome III, 1,000,000 to 1,002,000
seq = get_sequence_region(
    start_position=1000000,
    end_position=1002000,
    chromosome="III",
    species="caenorhabditis_elegans"
)

# Export formatted FASTA wrapped at 60 characters
create_fasta(
    gene_nm="daf-16_region",
    chromosome="III",
    sequence=seq,
    path="./output"
)
```

#### Asynchronous Sequence Fetching for Batch Pipelines

```python
import asyncio
from pub_worm.ensembl.ensembl_api import async_get_sequence_region

async def fetch_promoters():
    coords = [
        (100000, 102000, "I"),
        (200000, 202000, "II"),
        (300000, 302000, "X"),
    ]
    tasks = [
        async_get_sequence_region(start, end, chrom)
        for start, end, chrom in coords
    ]
    sequences = await asyncio.gather(*tasks)
    return sequences

sequences = asyncio.run(fetch_promoters())
print(f"Retrieved {len(sequences)} genomic regions.")
```

---

### 5. ORCID Author Lookup

Retrieve verified author records and disambiguate scientific contributors:

```python
from pub_worm.orcid.orcid_api import OrcidAPI

orcid_client = OrcidAPI()

# Query by ORCID identifier
profile = orcid_client.get_orcid_data("0000-0002-2403-8551")

person = profile.get("person", {})
names = person.get("name", {})
family_name = names.get("family-name", {}).get("value")
given_names = names.get("given-names", {}).get("value")

print(f"Researcher: {given_names} {family_name}")
```

---

### 6. Journal Impact Factor Lookup

Fast lookup of Journal Citation Reports (JCR) metrics using standard ISSN or electronic eISSN:

```python
from pub_worm.impact_factor.impact_factor_lookup import get_impact_factor

# Query Nature Genetics (ISSN: 1061-4036)
jif = get_impact_factor("1061-4036")
print(f"Journal Impact Factor: {jif}")
```

---

## Command-Line Interface (CLI)

`pub_worm` provides a convenient entry point for bulk WormBase ID resolution:

```bash
# General syntax:
uv run python run_map_wormbase_ids.py <input_csv_path> [id_column_name] [output_directory]

# Example:
uv run python run_map_wormbase_ids.py experiment_data.csv Gene_ID ./mapped_results
```

This will automatically:
1. Determine the latest WormBase release version via the REST API.
2. Download and unpack the corresponding `geneIDs.txt.gz` annotation table.
3. Perform fuzzy matching on sequence names, pseudogenes, and isoforms.
4. Output `{filename}_found.csv` and `{filename}_not_found.csv`.

---

## Development Workflow

This project adheres to strict Python standards (Python 3.12+, strict type hinting, and fast builds). All common development operations are managed through the local `Makefile`.

### Prerequisites

* Python `3.12+`
* [`uv`](https://docs.astral.sh/uv/) package manager

### Standard Targets

| Command | Action | Description |
| :--- | :--- | :--- |
| `make install` | `uv sync --all-groups` | Install runtime and developer dependencies in isolated virtualenv |
| `make test` | `uv run pytest` | Execute the test suite |
| `make lint` | `uv run ruff check .` | Run Ruff linter across all source modules |
| `make format` | `uv run ruff format .` | Reformat codebase according to style rules |
| `make dev` | `uv run python run_map_wormbase_ids.py` | Run local CLI development entry point |
| `make clean` | `rm -rf ...` | Remove build artifacts, caches, and test outputs |

---

## Testing & Quality Gates

The test suite is powered by `pytest` and `pytest-asyncio`. Run all tests locally:

```bash
make test
```

To run a specific test suite:

```bash
uv run pytest tests/wormbase/test_wormbase_api.py -v
uv run pytest tests/ncbi/test_entreze_api.py -k test_entreze_esearch -v
```

> [!NOTE]
> Tests in `tests/` currently perform live integration queries to external web endpoints. Ensure an active Internet connection is available when running the suite. For an exhaustive architectural audit and roadmap, refer to [REVIEW.md](file:///Users/dan/Code/Python/pub_worm/REVIEW.md).

---

## Contributing

Contributions, bug reports, and pull requests are welcome!

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Ensure all changes conform to linting and formatting standards:
   ```bash
   make lint && make format
   ```
3. Run the test suite:
   ```bash
   make test
   ```
4. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat(ensembl): add retry backoff parameter"
   ```
5. Submit a Pull Request.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.

Developed and maintained by **Dan Higgins** ([daniel.higgins@yahoo.com](mailto:daniel.higgins@yahoo.com)).
