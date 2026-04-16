from django.shortcuts import render
from projects.models import Project
from blog.models import Post


RESUME = {
    "name": "Chinmaya Ranjan Sahu",
    "role": "Python Backend Developer",
    "tagline": "I build fast, reliable backend systems that handle millions of events and serve thousands of users.",
    "email": "Chinmayaranjansahu262@gmail.com",
    "phone": "+91 6366368424",
    "linkedin_url": "https://linkedin.com/in/chinmaya-984525243",
    "about": (
        "I'm a Python Backend Developer with 3+ years of experience building "
        "scalable server-side systems. I currently work at HCL Technologies in "
        "Bangalore, where I architect production services across real-time trading "
        "platforms, AI-powered chatbots, and operations management systems.\n\n"
        "I specialize in Django, FastAPI, PostgreSQL, Redis, Kafka, and ClickHouse. "
        "I integrate LangChain, GPT-4o, and Vector Databases to power AI and NLP "
        "automation.\n\n"
        "When I'm not writing code, I'm reading about distributed systems, "
        "exploring new tools, or debugging production incidents at 2am with too much "
        "coffee."
    ),
    "skills": [
        {"name": "Languages", "items": ["Python", "SQL"]},
        {"name": "Backend", "items": ["Django", "FastAPI", "Django REST Framework"]},
        {"name": "AI & NLP", "items": ["LangChain", "GPT-4o", "Vector Databases", "RAG"]},
        {"name": "Databases", "items": ["PostgreSQL", "MySQL", "Redis", "ClickHouse"]},
        {"name": "Messaging", "items": ["Apache Kafka", "Redpanda"]},
        {"name": "DevOps", "items": ["Git", "GitHub", "GitLab", "Docker", "Linux"]},
        {"name": "Architecture", "items": ["REST API", "Microservices", "Event-Driven", "WebSockets"]},
    ],
    "experience": {
        "role": "Python Backend Developer",
        "company": "HCL Technologies",
        "location": "Bangalore, India",
        "period": "April 2023 - Present",
        "bullets": [
            "Built and maintained production Python services across 3 active projects: an autonomous Solana trading bot, an AI-powered WhatsApp chatbot, and an operations management platform.",
            "Wrote and reviewed REST API contracts, PostgreSQL schemas, and Kafka event flows, keeping 30+ endpoints consistent across services.",
            "Wrote unit and integration tests for every feature branch, maintaining 85%+ coverage.",
            "Set up GitHub Actions and GitLab CI pipelines that run lint, tests, build, and deploy on every pull request.",
            "Debugged production incidents by tracing logs, profiling slow queries, and analyzing Redis and Kafka message backlogs.",
            "Participated in daily standups, sprint planning, and retrospectives, delivering 2-3 features per sprint.",
            "Worked closely with product managers and DevOps to translate requirements into technical specs and Docker deployments.",
        ],
    },
    "education": [
        {"degree": "Master of Computer Applications (MCA)", "school": "Trident Academy of Creative Technology", "year": "2024"},
        {"degree": "B.Sc. in Physics", "school": "Khaira College", "year": "2022"},
    ],
}


def home(request):
    recent_projects = Project.objects.all()[:3]
    recent_posts = Post.objects.filter(published=True)[:3]
    return render(request, 'core/home.html', {
        **RESUME,
        'recent_projects': recent_projects,
        'recent_posts': recent_posts,
    })


def about(request):
    return render(request, 'core/about.html', RESUME)


def contact(request):
    return render(request, 'core/contact.html', RESUME)
