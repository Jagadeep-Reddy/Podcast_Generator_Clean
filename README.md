# Podcast_Generator

# 🎙️ Podcast Generator (Clean)

A clean, modular, and production-ready pipeline to automatically generate podcast-style content using NLP, LLMs, graph-based reasoning, and summarization workflows.

---

## 🚀 Overview  
Podcast Generator automates the creation of podcast-ready content by ingesting raw text, processing it with NLP + LLM components, generating summaries, building knowledge graphs, performing retrieval-augmented generation, and producing final structured outputs.

This repository is a **clean, modular, and scalable** version of the original project.

---

## ✨ Features  
- 🔤 **Text Ingestion & Processing** — Custom utilities for text cleaning and segmentation.  
- 🧠 **Entity Extraction** — Extracts key entities using NLP/LLM.  
- 🔗 **Graph RAG** — Graph-based Retrieval-Augmented Generation via `graph_rag.py` & `graph_models.py`.  
- 🧩 **Agents System** — Multiple agents for summarization, clustering, community detection.  
- 📝 **Dynamic Prompting** — Modular prompt templates for flexible LLM workflows.  
- 🔍 **Query Engine** — Query text/chunks intelligently for better reasoning.  
- ⚙️ **Orchestrator** — End-to-end pipeline management in `orchestrator.py`.  
- 🗂️ **Clean Output Structure** — All generated outputs stored inside `outputs/`.

---

## 📁 Project Structure  

```plaintext
Podcast_Generator_Clean/
│
├── agents/                 # Core agent files
├── logs/                   # Run logs
├── outputs/                # Final generated outputs
├── static/                 # Static files (images, icons, etc.)
├── templates/              # Markdown / HTML templates
│
├── app.py                  # Optional web interface
├── main.py                 # Main entrypoint
├── orchestrator.py         # Pipeline orchestrator
├── llm_client.py           # LLM API wrapper
├── text_utils.py           # Text preprocessing functions
├── entity_extractor.py     # Entity extraction logic
├── graph_models.py         # Graph definitions
├── graph_rag.py            # Graph RAG implementation
├── community_detector.py   # Community detection logic
├── community_summarizer.py # Summarization across communities

Raw Text
   ↓
Text Utils → Preprocessing
   ↓
Entity Extractor → Entities
   ↓
Graph Models → Knowledge Graph
   ↓
Graph RAG → Enhanced Context
   ↓
Community Detector → Clusters
   ↓
Summarizer → Episode-level summaries
   ↓
Final Podcast Output (Markdown/Audio-ready)

├── query_engine.py         # Query + retrieval logic
├── prompts.py              # Prompt templates
│
├── history.json            # History of runs
├── debug_key.py            # Local API key file (ignore in Git)
├── .gitignore
