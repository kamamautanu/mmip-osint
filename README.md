# MMIP OSINT — Multi-Agent, Safety-Gated OSINT Workflow
> A compliance-first, human-supervised OSINT workflow for MMIP case investigations that turns **publicly available social signals** into an **evidence-backed ClaimsLedger** and a **traceable dossier draft**, with **two-agent integrity safety reviews** and **Human-in-the-Loop (HITL)** escalation checkpoints.

---

## Table of Contents
- [Overview](#overview)
- [Why this exists](#why-this-exists)
- [Key principles](#key-principles)
- [Architecture](#architecture)
  - [High-level workflow](#high-level-workflow)
  - [Agent graph](#agent-graph)
  - [Data plane vs control plane](#data-plane-vs-control-plane)
  - [State keys and output keys](#state-keys-and-output-keys)
- [Workflow details](#workflow-details)
  - [1) OSINT ingestion (parallel map)](#1-osint-ingestion-parallel-map)
  - [2) Artifact reduction (reduce)](#2-artifact-reduction-reduce)
  - [3) ClaimsLedger generation](#3-claimsledger-generation)
  - [4) Data safety: two-person integrity + judge + HITL](#4-data-safety-two-person-integrity--judge--hitl)
  - [5) Dossier writing cycle (author/critic loop)](#5-dossier-writing-cycle-authorcritic-loop)
  - [6) Presentation safety: two-person integrity + judge + HITL](#6-presentation-safety-two-person-integrity--judge--hitl)
- [How to use (MVP / Playground)](#how-to-use-mvp--playground)
- [Safety, ethics, and ToS compliance](#safety-ethics-and-tos-compliance)
- [Limitations](#limitations)
- [Roadmap / Next steps](#roadmap--next-steps)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This is an **agentic OSINT workflow** designed for **MMIP** investigations with a **TraceLabs-like structure** (case inputs may include explicit target social profiles). It emphasizes:
- **Evidence-first outputs** (artifacts → claims → dossier)
- **No overreach** (strict traceability and confidence-aligned language)
- **Safety gating** via independent safety reviewers and judge arbitration
- **HITL escalation** as a control-plane decision point before sensitive outputs proceed

The system is implemented using **Google ADK** with a root **SequentialAgent** orchestrating a staged pipeline.

---

## Why this exists

OSINT is powerful but risky. In missing persons/MMIP contexts, mistakes can cause real harm:
- misidentification and reputational damage
- privacy violations and doxxing
- unsafe public distribution of sensitive details
- overconfident narratives from incomplete evidence

This project aims to make OSINT **more structured, auditable, and safer-by-default** by separating:
- **data-plane work** (collection and transformation)
- **control-plane decisions** (gating, escalation, and human judgment)

---

## Key principles

- **Read-only ingestion:** Connectors do not bypass auth or access controls.
- **Evidence-first:** Claims must reference artifacts; the dossier must reference claims.
- **No speculation:** No inferred identity, motive, or intent beyond explicit sources.
- **Two-person integrity:** Parallel safety agents are intentionally *non-correlated*.
- **Control-plane separation:** HITL is used for non-deterministic, high-stakes decisions.
- **Structured interchange:** Agents communicate via **output keys** and **state keys**, not narrative message history.

---

## Architecture

### High-level workflow

1) **Ingest** public OSINT signals (parallel connectors)  
2) **Reduce** to a unified **ArtifactBundle** (dedupe + standardize)  
3) **Process** artifacts into a **ClaimsLedger** (explicit, cited claims only)  
4) **Data safety review** (two reviewers → judge → HITL gate if needed)  
5) **Write dossier** (author → critic, looped iterations)  
6) **Presentation safety review** (two reviewers → judge → HITL gate if needed)  

### Agent graph

```mermaid
flowchart TD
  A["Root Orchestrator\nSequentialAgent"] --> B["OSINT Ingestion MAP\nParallelAgent"]
  B --> B1[TikTok Connector]
  B --> B2[Facebook Connector]
  B --> B3[Instagram Connector]

  B --> C[Ingestion REDUCE<br/>ArtifactBundle Builder]
  C --> D[OSINT Processing<br/>ClaimsLedger Generator]

  D --> E[Data Safety<br/>Parallel A/B]
  E --> E1[Data Safety A<br/>Traceability/Overreach]
  E --> E2[Data Safety B<br/>Contradictions/Sensitivity]

  E --> F[Data Safety Judge]
  F --> G[HITL Data Gate<br/>Pause/Resume]

  G --> H[Writing Cycle<br/>LoopAgent max=2]
  H --> H1[Dossier Sequence<br/>Sequential]
  H1 --> H2[Dossier Author]
  H1 --> H3[Dossier Critic]

  H --> I[Presentation Safety<br/>Parallel A/B]
  I --> I1[Presentation Safety A<br/>Harm/Privacy/MisID]
  I --> I2[Presentation Safety B<br/>Misuse/Framing/Aggregation]

  I --> J[Presentation Safety Judge]
  J --> K[HITL Presentation Gate (planned/infra)]
