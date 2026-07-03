# finsight-ai

Multi-agent system for financial document intelligence (BFSI). Built for intent handling, tool orchestration, retrieval, and guardrails.

## What it does
- routes a user question to the right handling path (intent)
- retrieves relevant context from financial documents (RAG)
- orchestrates tools/agents to answer, grounded on the source
- guardrails so it doesn't answer beyond what the documents support

## Stack
Python, Anthropic Claude API (messages, tool use), RAG pipeline, vector database

## Status
Active development.
