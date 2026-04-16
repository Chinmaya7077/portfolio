import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

from projects.models import Project
from blog.models import Post

# Clear existing
Project.objects.all().delete()
Post.objects.all().delete()

# Projects
Project.objects.create(
    title="EZWallet",
    slug="ezwallet",
    subtitle="Autonomous Solana Trading System",
    description="An autonomous trading system that manages Solana token positions end to end on PumpFun and PumpSwap, executing buys and sells in the same on-chain slot as the trigger. Features rug protection, trailing stop-loss, parallel RPC submission, and flexible order placement with GTC/IOC/GTT time-in-force options.",
    role="Sole backend developer responsible for designing the trading engine, writing all FastAPI services, setting up gRPC integrations, and managing Redis/ClickHouse/PostgreSQL data layers.",
    tech_stack="Python, FastAPI, Solana, gRPC, Redis, ClickHouse, PostgreSQL",
    highlights="Same-slot execution via direct gRPC validator streams\nUnlimited take-profit and stop-loss levels with trailing stop-loss\nReal-time rug protection by monitoring pool liquidity\nParallel RPC submission with smart retry (3x buy, 10x sell)\nEncrypted wallet storage in PostgreSQL\nClickHouse for trade analytics and settlement price extraction\nREST endpoints with AND/ANY trigger logic and GTC/IOC/GTT options",
    order=1,
)

Project.objects.create(
    title="WhatsApp AI Chatbot",
    slug="whatsapp-ai-chatbot",
    subtitle="GPT-4o + LangChain Powered",
    description="An AI-powered WhatsApp chatbot that runs customer support and business workflows end to end with 90-95% intent recognition accuracy and under 1.2s response time. Resolves 80% of queries without human handoff.",
    role="Backend developer owning the chatbot API layer, NLP pipeline integration, Vector Database setup, and webhook/session management.",
    tech_stack="FastAPI, LangChain, GPT-4o, Vector Database, Redis, PostgreSQL",
    highlights="90-95% intent recognition accuracy across multi-turn conversations\nRAG with Vector Database, cutting hallucinations by 60%\n80% of queries resolved without human handoff\n500+ concurrent sessions with 99.9% delivery reliability\nSecure webhook APIs with Redis-backed message queueing",
    order=2,
)

Project.objects.create(
    title="Training & Ops Management",
    slug="training-ops-management",
    subtitle="Operations Platform",
    description="A Django platform managing 200+ training programs, 50+ trainers, and 1,000+ trainees with role-based access control, real-time dashboards, and automated scheduling. Reduced manual operational effort by 65%.",
    role="Full-stack backend developer handling Django models, REST APIs, role-based access control, dashboard queries, and Redis caching layer.",
    tech_stack="Django, Django REST Framework, PostgreSQL, Redis",
    highlights="200+ programs, 50+ trainers, 1,000+ trainees managed end to end\nRBAC with JWT across Admin, Trainer, and Trainee roles (15+ endpoints)\n65% reduction in manual operational effort\n55% faster dashboard load times with Redis caching\n3x concurrent user growth supported after optimization",
    order=3,
)

# Sample Blog Posts
Post.objects.create(
    title="How I Built a Same-Slot Trading Engine on Solana",
    slug="same-slot-trading-engine-solana",
    excerpt="A deep dive into building EZWallet, an autonomous trading system that executes in the same Solana slot as the trigger event.",
    content="""When I started building EZWallet, the goal was simple: execute trades **in the same slot** as the trigger event. No delays, no missed opportunities.

## The Problem

Most trading bots on Solana poll for price changes at fixed intervals — every second, every block. By the time they detect a signal, the opportunity is gone. We needed something faster.

## The Solution: gRPC Validator Streams

Instead of polling, I connected directly to Solana validators via gRPC. Every on-chain trade is streamed in real-time:

```python
async def stream_trades(client):
    async for event in client.subscribe_transactions():
        token = extract_token(event)
        price = calculate_price(event)
        await evaluate_triggers(token, price)
```

This means we evaluate user triggers on **every single transaction**, not every second.

## Same-Slot Execution

When a trigger fires, the buy/sell transaction lands in the same Solana slot (~400ms). I achieved this with:

- **Parallel RPC submission** to multiple endpoints
- **Smart retry** with 3x buy attempts, 10x sell attempts
- **Pre-signed transactions** ready to fire instantly

## Results

- Sub-second trigger-to-execution time
- 99.8% same-slot landing rate
- Zero missed exits during rug events

The key insight: **don't poll, stream.** Direct gRPC beats REST polling by orders of magnitude for latency-critical applications.
""",
)

Post.objects.create(
    title="Why I Use ClickHouse for Trade Analytics",
    slug="clickhouse-trade-analytics",
    excerpt="PostgreSQL is great for OLTP, but when you need to aggregate billions of rows in under 2 seconds, ClickHouse is the answer.",
    content="""After building EZWallet's trading engine, I needed to analyze millions of trades for patterns, P&L, and settlement prices.

## PostgreSQL Hit a Wall

PostgreSQL handled our OLTP workload perfectly — orders, wallets, user state. But when I tried running analytical queries over trade history:

```sql
SELECT token, AVG(price), COUNT(*)
FROM trades
WHERE timestamp > now() - interval '24 hours'
GROUP BY token
ORDER BY COUNT(*) DESC;
```

This query took **45 seconds** on 10M rows. Unacceptable for a real-time dashboard.

## Enter ClickHouse

ClickHouse is a columnar OLAP database designed for exactly this use case. The same query runs in **0.8 seconds** on the same data.

Why it's faster:
- **Columnar storage**: only reads the columns you need
- **Vectorized execution**: processes data in CPU-cache-friendly batches
- **Compression**: 10x smaller on disk than PostgreSQL for the same data

## How I Set It Up

I use PostgreSQL for writes (orders, wallets) and replicate trade events to ClickHouse via Kafka:

```
FastAPI -> PostgreSQL (orders)
       -> Kafka -> ClickHouse (analytics)
```

This gives me ACID for writes and blazing-fast analytics for reads. Best of both worlds.
""",
)

Post.objects.create(
    title="Building a RAG Pipeline for WhatsApp",
    slug="rag-pipeline-whatsapp",
    excerpt="How I used LangChain, GPT-4o, and a Vector Database to build a chatbot that actually gives accurate answers.",
    content="""Most chatbots either hallucinate or give generic responses. I needed one that answers accurately from a specific knowledge base.

## The RAG Architecture

RAG (Retrieval-Augmented Generation) works in two steps:

1. **Retrieve** relevant documents from a Vector Database
2. **Generate** an answer using those documents as context

```python
from langchain.chains import RetrievalQA

chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o"),
    retriever=vectorstore.as_retriever(k=4),
    chain_type="stuff",
)
answer = chain.run(user_question)
```

## Why Vector Databases Matter

Traditional keyword search misses semantic meaning. A user asking "how do I reset my password" should match a document titled "Account Recovery Steps" even though the words don't overlap.

Vector databases (I used Qdrant) store document embeddings and find semantically similar content in milliseconds.

## Results

- **90-95% intent recognition accuracy**
- **60% fewer hallucinations** compared to raw GPT-4o
- **1.2s average response time** including retrieval + generation

The key: always give the LLM context. A well-retrieved document beats a larger model every time.
""",
)

print(f"Seeded {Project.objects.count()} projects, {Post.objects.count()} posts")
