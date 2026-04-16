"""
Custom tools the LangChain agent can invoke.
Each tool provides structured information about the portfolio.
"""
from langchain_core.tools import tool


@tool
def get_github_projects() -> str:
    """Returns a list of Chinmaya's GitHub repositories and project links.
    Use this when the user asks about GitHub repos, source code, or project links."""
    return """
Chinmaya's GitHub: https://github.com/Chinmaya7077

Key Repositories:
1. portfolio - Personal portfolio website built with Django, exported as static HTML, deployed on Vercel.
   Link: https://github.com/Chinmaya7077/portfolio
   Tech: Django, Python, Vanilla JS, Vercel

2. EZWallet (Private) - Autonomous Solana trading system with same-slot execution.
   Tech: Python, FastAPI, Solana, gRPC, Redis, ClickHouse, PostgreSQL

3. WhatsApp AI Chatbot (Private) - AI-powered customer support chatbot using RAG.
   Tech: FastAPI, LangChain, GPT-4o, Qdrant, Redis, PostgreSQL

4. Training Ops Platform (Private) - Django-based operations management system.
   Tech: Django, DRF, PostgreSQL, Redis

Note: Some repositories are private due to client agreements. The portfolio repo is publicly available.
""".strip()


@tool
def generate_api_example(topic: str) -> str:
    """Generates a backend API code example for a given topic.
    Use this when the user asks for code examples, API patterns, or implementation samples.
    Input should be the topic like 'fastapi endpoint', 'authentication', 'websocket', etc."""

    examples = {
        "fastapi": '''
# FastAPI CRUD Endpoint Example
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

items_db = {}

@app.post("/items/", status_code=201)
async def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item.dict()
    return {"id": item_id, **item.dict()}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]
''',
        "authentication": '''
# JWT Authentication with FastAPI
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()
SECRET_KEY = "your-secret-key"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
async def protected_route(user=Depends(verify_token)):
    return {"message": f"Hello {user['sub']}"}
''',
        "websocket": '''
# WebSocket Streaming Example
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Process and stream response
        async for token in generate_response(data):
            await websocket.send_text(token)
''',
        "django": '''
# Django REST Framework ViewSet
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def recent(self, request):
        recent = self.queryset.order_by("-created")[:5]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
''',
    }

    # Match topic to closest example
    topic_lower = topic.lower()
    for key, code in examples.items():
        if key in topic_lower:
            return f"Here's a {key} example from Chinmaya's toolkit:\n{code}"

    # Default to FastAPI if no match
    return f"""Here's a general FastAPI example (Chinmaya's primary framework):
{examples['fastapi']}

Chinmaya works with FastAPI, Django, and Django REST Framework.
Ask for a specific topic like 'authentication', 'websocket', or 'django' for more examples."""


@tool
def explain_architecture(system_name: str) -> str:
    """Explains the system architecture of one of Chinmaya's projects.
    Use this when the user asks about system design, architecture, or how a project is built.
    Input should be the project name like 'ezwallet', 'whatsapp chatbot', or 'training platform'."""

    architectures = {
        "ezwallet": """
EZWallet - Autonomous Solana Trading System Architecture:

┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  FastAPI     │────>│  PostgreSQL  │────>│   Kafka     │
│  (Orders)   │     │  (OLTP)      │     │  (Stream)   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
┌─────────────┐     ┌──────────────┐     ┌──────▼──────┐
│  gRPC       │────>│  Redis       │     │ ClickHouse  │
│  (Solana    │     │  (State +    │     │ (Analytics) │
│  Validator) │     │   Triggers)  │     └─────────────┘
└─────────────┘     └──────────────┘

Flow:
1. gRPC streams real-time transactions from Solana validators
2. Each transaction is evaluated against user-defined triggers in Redis
3. When a trigger fires, FastAPI submits buy/sell via parallel RPC
4. Orders stored in PostgreSQL, replicated to ClickHouse via Kafka
5. Same-slot execution (~400ms) with 99.8% landing rate

Key Design Decisions:
- gRPC over REST polling for sub-second latency
- Redis for trigger evaluation (microsecond lookups)
- ClickHouse for analytics (columnar, 50x faster than PostgreSQL for aggregations)
- Parallel RPC submission for reliability (3x buy, 10x sell retries)
""",
        "whatsapp": """
WhatsApp AI Chatbot Architecture:

┌──────────┐     ┌──────────────┐     ┌─────────────┐
│ WhatsApp │────>│  FastAPI      │────>│  LangChain  │
│ Webhook  │     │  (Gateway)    │     │  (Agent)    │
└──────────┘     └──────────────┘     └──────┬──────┘
                                              │
                 ┌──────────────┐     ┌──────▼──────┐
                 │  Redis       │     │  Qdrant     │
                 │  (Queue +    │     │  (Vector DB)│
                 │   Sessions)  │     └─────────────┘
                 └──────────────┘              │
                                       ┌──────▼──────┐
                                       │   GPT-4o    │
                                       │   (LLM)     │
                                       └─────────────┘

Flow:
1. WhatsApp message arrives via webhook
2. FastAPI queues it in Redis for reliable processing
3. LangChain agent retrieves relevant docs from Qdrant (RAG)
4. GPT-4o generates response with retrieved context
5. Response sent back via WhatsApp API

Key Metrics:
- 90-95% intent recognition accuracy
- 60% fewer hallucinations with RAG
- 1.2s average response time
- 500+ concurrent sessions
""",
        "training": """
Training & Ops Management Platform Architecture:

┌──────────┐     ┌──────────────┐     ┌─────────────┐
│ Frontend │────>│  Django DRF  │────>│ PostgreSQL  │
│ (React)  │     │  (15+ APIs)  │     │ (Primary)   │
└──────────┘     └──────┬───────┘     └─────────────┘
                        │
                 ┌──────▼──────┐     ┌─────────────┐
                 │  JWT Auth   │     │   Redis     │
                 │  (RBAC)     │     │  (Cache)    │
                 └─────────────┘     └─────────────┘

Roles: Admin | Trainer | Trainee
- Admin: Full CRUD on programs, trainers, trainees
- Trainer: Manage assigned programs, mark attendance
- Trainee: View enrolled programs, track progress

Key Results:
- 65% reduction in manual effort
- 55% faster dashboards with Redis caching
- 3x concurrent user growth supported
""",
    }

    name_lower = system_name.lower()
    for key, arch in architectures.items():
        if key in name_lower:
            return arch.strip()

    return f"""Available architectures to explain:
1. EZWallet (Solana trading system)
2. WhatsApp Chatbot (AI customer support)
3. Training Platform (operations management)

Please specify which project you'd like me to explain."""
