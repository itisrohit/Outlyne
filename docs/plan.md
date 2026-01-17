# Outlyne: AI-Powered Sketch-to-Image Meta Search
> **Project Blueprint**  
> *Real-time visual intelligence meets live internet recall.*

---

## Project Aim
Build a live, lightweight sketch-to-image meta search engine where a user draws a sketch, the system converts it into a visual embedding in real-time, fetches candidate images live from public image search engines, and re-ranks them locally.

**Core Philosophy:**
- **No Local Indexing:** Stay lightweight by leveraging existing search engines.
- **CPU-First:** High-performance inference on consumer hardware via OpenVINO optimization.
- **Sub-4-Second Latency:** Async architecture and minimal caching for fast iteration.

---

## Core Idea
> **"Do not own the index. Orchestrate the intelligence."**  
> Use existing image search engines for Recall, then apply sketch-aware visual intelligence locally for Precision.

---

## Scope & Constraints

### Included
- **Live Sketch → Embedding:** Instant conversion via SigLIP2 (92ms latency).
- **Dynamic Meta-Search:** Real-time fetching from DuckDuckGo (free, unlimited).
- **Local Re-ranking:** Dot product similarity on L2-normalized embeddings.
- **Minimal Caching:** In-memory LRU cache for sketch embeddings.
- **Proactive UI:** Modern, responsive canvas interface (Phase 4).

### Excluded
- Local image datasets or permanent indexing.
- Heavy web crawling or scraping.
- LLMs or RAG (focused on visual similarity only).
- GPU-only models (everything runs on CPU).

---

## Tech Stack (As Implemented)

### Vision & Inference
- **Vision Encoder:** SigLIP2-Base (`google/siglip-base-patch16-224`)
- **Inference Runtime:** OpenVINO 2025 (Intel CPU optimization)
- **Vector Math:** NumPy for vectorized dot product ranking

### Meta Search & Data
- **Search Engine:** DuckDuckGo (via `ddgs` library - 100% free, no limits)
- **Protocol:** HTTPX (Async Python) for concurrent thumbnail downloads
- **Concurrency:** asyncio.gather() with semaphore-limited parallelism (15 connections)

### Backend (The Orchestrator)
- **Framework:** FastAPI (Python 3.12+) — Asynchronous and type-safe
- **Caching:** async-lru for in-memory sketch embedding cache
- **Dependency Management:** uv (fast, reproducible)
- **Task Runner:** Bun (orchestrates dev/lint/docker commands)

### Frontend (The Experience)
- **Framework:** Vite + React (SPA) — Planned for Phase 4
- **Styling:** Vanilla CSS (Glassmorphism + Modern Gradients)
- **Canvas Engine:** Native Canvas + Perfect Freehand

---

## High-Level Architecture

```
User Sketch (224×224 RGB)
    ↓
[Vision Core] → SigLIP2 + OpenVINO → 768-dim embedding (92ms)
    ↓
[Cache Check] → async-lru (BLAKE3 hash key)
    ↓ (miss)
[Recall Engine] → DuckDuckGo search → 20 candidate URLs (1.8s)
    ↓
[Thumbnail Downloader] → Parallel fetch (15 concurrent) → Image bytes (0.5s)
    ↓
[Batch Encoder] → Encode all candidates → 20 embeddings (0.8s)
    ↓
[Precision Layer] → Dot product ranking → Sorted results (<10ms)
    ↓
Top-K Results (with similarity scores)
```

---

## Caching Strategy: MVP Approach

For the MVP, we implement **minimal in-memory caching** to optimize iterative sketching without infrastructure overhead.

### Sketch Embedding Cache (Manual Implementation)
- **Implementation:** Custom async-safe cache using `OrderedDict` + `asyncio.Lock`
- **Key:** BLAKE3 hash of sketch bytes (fast, collision-resistant)
- **Max Size:** 100 entries (LRU eviction via `OrderedDict.move_to_end()`)
- **TTL:** 10 minutes (timestamp-based expiration)
- **Purpose:** Instant response (<1ms) for repeated sketches during user iteration

**Why Manual Instead of async-lru:**
- `async-lru` couldn't hash numpy arrays (TypeError: unhashable type)
- Manual implementation gives us full control over cache keys
- `OrderedDict` provides built-in LRU behavior
- `asyncio.Lock` ensures thread-safety in async context

**Rationale:**
- Zero external dependencies (stdlib only)
- Significant UX improvement for iterative sketching
- Negligible memory overhead (~77MB for 100 cached embeddings)

**Future Optimization:**
- Add Redis for multi-user shared cache
- Implement search result caching (query → URLs)
- Add content-addressable image embedding cache

---

## Implementation Phases

### Phase 1: The Vision Core [COMPLETED ✅]
- [x] Integrate SigLIP2 and optimize with OpenVINO
- [x] Implement `normalize_sketch()` for line-width and contrast stabilization
- [x] Containerize with Docker and OpenVINO "bakery" for 2s cold starts
- [x] Achieve 92.7ms inference latency (8% faster than 100ms target)
- **Deliverable:** ✅ VisualEmbedder module + Dockerized API

### Phase 2: The Recall Engine [COMPLETED ✅]
- [x] Research and select best free image search API (DuckDuckGo via `ddgs`)
- [x] Implement BaseSearchAdapter abstract class for extensibility
- [x] Build DuckDuckGoAdapter with 100% free, unlimited access
- [x] Create async thumbnail downloader with concurrency control (15 connections)
- [x] Verify end-to-end search → download pipeline (100% success rate)
- [x] Integrate into FastAPI via SearchOrchestrator
- **Deliverable:** ✅ Fetch 20 results in ~2.3s (search + download)

### Phase 3: The Precision Layer [COMPLETED ✅]
- [x] Build vectorized ranker using dot product (L2-normalized embeddings)
- [x] Implement batch encoding for incoming thumbnails
- [x] Create SearchOrchestrator to tie Vision Core + Recall + Precision
- [x] Add `/search` FastAPI endpoint accepting base64 sketches
- [x] Verify end-to-end pipeline with test (61.3% top similarity score)
- **Deliverable:** ✅ Ranked image results endpoint with similarity scores

### Phase 3.5: Performance Optimization [COMPLETED ✅]
- [x] Add manual async-safe caching for sketch embeddings
- [x] Implement LRU eviction with 100-entry limit
- [x] Add TTL support (10-minute expiration)
- [x] Use BLAKE3 for fast hash computation
- [x] Verify cache functionality with end-to-end test
- **Deliverable:** ✅ Sub-millisecond response for cached sketches

### Phase 4: Premium UI/UX
- Build Vite-based frontend with high-performance drawing canvas
- Implement "Search-as-you-draw" (debounced inference)
- Add result gallery with similarity scores
- **Deliverable:** Smooth, polished static web application

---

## Performance Metrics (Actual)

### End-to-End Latency
- **Vision Core (sketch encoding):** 92.7ms
- **Recall (DuckDuckGo search):** 1.8s
- **Download (20 thumbnails, parallel):** 0.5s
- **Precision (batch encoding + ranking):** 0.8s
- **Total (uncached):** ~3.2s
- **Total (cached sketch):** <1ms (memory lookup)

### Quality Metrics
- **Top-1 similarity:** 61.3% (real-world test)
- **Encoding success rate:** 100% (20/20 candidates)
- **Results relevance:** High (visual + semantic match)

### Resource Usage
- **Memory footprint:** 886MB (model + runtime)
- **CPU load:** <40% on Apple M1 (4 cores)
- **Docker cold start:** 2 seconds (pre-baked model)

---

## Final Deliverables

- [x] **Outlyne Core:** FastAPI backend with /search endpoint
- [x] **Vision Core:** SigLIP2 + OpenVINO (92.7ms latency)
- [x] **Recall Engine:** DuckDuckGo integration (free, unlimited)
- [x] **Precision Layer:** Dot product ranking (vectorized)
- [x] **Caching Layer:** Manual async-safe sketch cache (OrderedDict + BLAKE3)
- [x] **Docker Setup:** Multi-stage build with baked model
- [ ] **Outlyne Web:** Vite-based reactive dashboard (Phase 4)
- [ ] **Deployment Kit:** Complete Docker Compose setup

---

## Current Status

**Completed:** Phases 1, 2, 3, 3.5 (Backend fully functional with caching)  
**Next:** Phase 4 (Frontend UI/UX)

**Status:** Backend is complete with optimized caching. Frontend pending.
