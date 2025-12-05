
# AI Business Proposal Generator

## Overview

AI Business Proposal Generator is an intelligent system that creates customized business proposals by learning from your firm's unique style and industry best practices. Unlike generic AI-generated proposals, this tool leverages a Retrieval-Augmented Generation (RAG) architecture to blend reference materials from published proposals with your organization's historical documents, ensuring proposals sound authentic and maintain your firm's distinctive tone.

## Key Features

- **RAG-Based Generation**: Combines public business proposal references with your internal proposal history
- **Tone Preservation**: Generates proposals in your firm's authentic voice, not generic AI-speak
- **Best Practice Integration**: Incorporates industry standards from published successful proposals
- **Customizable Output**: Learns from your past proposals to maintain consistency

## Technology Stack

- **Language**: Python
- **Dependency Management**: Poetry
- **LLM Framework**: LangChain
- **Vector Database**: ChromaDB
- **Environment Config**: Python-dotenv

## Project Status

🔬 **POC & Research Level** - Currently in proof-of-concept and research phase

## Setup Instructions

### Prerequisites

- Python 3.10+
- Poetry

### Installation

1. **Clone the repository** and navigate to the project directory

2. **Configure environment variables**:
    ```bash
    cp env.sample .env
    ```
    Edit `.env` and add all required API keys and configuration variables

3. **Install dependencies**:
    ```bash
    cd proposal
    poetry install
    ```

4. **Activate the virtual environment**:
    ```bash
    poetry env activate
    ```