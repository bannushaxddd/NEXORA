"""Public datasets collector for document collection"""
import time
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from src.config import settings
from src.logger import logger


def fetch_hackernews_posts(limit: int = 250) -> Dict[str, str]:
    """
    Fetch top stories from HackerNews API
    
    Args:
        limit: Maximum number of posts to fetch
        
    Returns:
        Dictionary of {doc_id: text}
    """
    docs = {}
    doc_id = 1
    
    try:
        # Get top story IDs
        logger.info("fetching_hackernews_top_stories")
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=settings.crawl_timeout,
        )
        top_story_ids = response.json()[:limit]
        
        # Fetch each story
        for story_id in top_story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=settings.crawl_timeout)
                story_data = story_response.json()
                
                if story_data and story_data.get("type") == "story":
                    title = story_data.get("title", "")
                    text = story_data.get("text", "")
                    url = story_data.get("url", "")
                    
                    # Combine title, text, and URL
                    content = f"{title}\n\n{text}"
                    if url:
                        content += f"\n\nURL: {url}"
                    
                    if content.strip():
                        docs[f"hn_{doc_id}"] = content[:settings.max_page_size]
                        doc_id += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning("hackernews_story_error", story_id=story_id, error=str(e))
                continue
        
        logger.info("hackernews_fetch_complete", count=len(docs))
        
    except Exception as e:
        logger.error("hackernews_fetch_error", error=str(e))
    
    return docs


def fetch_reddit_posts(subreddits: List[str] = None, limit_per_sub: int = 75) -> Dict[str, str]:
    """
    Fetch posts from Reddit programming subreddits
    
    Args:
        subreddits: List of subreddit names (without r/)
        limit_per_sub: Maximum posts per subreddit
        
    Returns:
        Dictionary of {doc_id: text}
    """
    if subreddits is None:
        subreddits = ["programming", "Python", "MachineLearning", "webdev", "compsci", "learnprogramming", "javascript", "rust"]
    
    docs = {}
    doc_id = 1
    
    headers = {
        "User-Agent": settings.user_agent,
    }
    
    for subreddit in subreddits:
        try:
            logger.info("fetching_reddit_posts", subreddit=subreddit)
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit_per_sub}"
            response = requests.get(url, headers=headers, timeout=settings.crawl_timeout)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", {}).get("children", [])
                
                for post in posts:
                    post_data = post.get("data", {})
                    title = post_data.get("title", "")
                    selftext = post_data.get("selftext", "")
                    url = post_data.get("url", "")
                    
                    # Combine title and selftext
                    content = f"{title}\n\n{selftext}"
                    if url and not url.startswith("https://www.reddit.com"):
                        content += f"\n\nURL: {url}"
                    
                    if content.strip() and len(content) > 50:  # Filter out very short posts
                        docs[f"reddit_{doc_id}"] = content[:settings.max_page_size]
                        doc_id += 1
                
                logger.info("reddit_fetch_success", subreddit=subreddit, count=len(posts))
            else:
                logger.warning("reddit_fetch_failed", subreddit=subreddit, status=response.status_code)
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error("reddit_fetch_error", subreddit=subreddit, error=str(e))
            continue
    
    logger.info("reddit_fetch_complete", total_count=len(docs))
    return docs


def fetch_arxiv_abstracts(categories: List[str] = None, max_results: int = 250) -> Dict[str, str]:
    """
    Fetch paper abstracts from ArXiv
    
    Args:
        categories: List of ArXiv categories (e.g., ['cs.AI', 'cs.LG'])
        max_results: Maximum number of papers to fetch
        
    Returns:
        Dictionary of {doc_id: text}
    """
    if categories is None:
        categories = ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.SE", "cs.PL", "cs.NE", "cs.DS"]
    
    docs = {}
    doc_id = 1
    
    try:
        # Build query
        query = " OR ".join([f"cat:{cat}" for cat in categories])
        
        logger.info("fetching_arxiv_papers", query=query, max_results=max_results)
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        
        response = requests.get(url, params=params, timeout=settings.crawl_timeout)
        
        if response.status_code == 200:
            # Parse XML response
            soup = BeautifulSoup(response.text, "xml")
            entries = soup.find_all("entry")
            
            for entry in entries:
                title = entry.find("title")
                summary = entry.find("summary")
                authors = entry.find_all("author")
                
                title_text = title.get_text(strip=True) if title else ""
                summary_text = summary.get_text(strip=True) if summary else ""
                author_names = [author.find("name").get_text() for author in authors if author.find("name")]
                
                # Combine title, authors, and abstract
                content = f"Title: {title_text}\n\n"
                if author_names:
                    content += f"Authors: {', '.join(author_names[:5])}\n\n"
                content += f"Abstract: {summary_text}"
                
                if content.strip():
                    docs[f"arxiv_{doc_id}"] = content[:settings.max_page_size]
                    doc_id += 1
            
            logger.info("arxiv_fetch_success", count=len(docs))
        else:
            logger.warning("arxiv_fetch_failed", status=response.status_code)
        
    except Exception as e:
        logger.error("arxiv_fetch_error", error=str(e))
    
    return docs


def fetch_github_readmes(repos: List[str] = None, limit: int = 150) -> Dict[str, str]:
    """
    Fetch README files from popular GitHub repositories
    
    Args:
        repos: List of repository names in format "owner/repo"
        limit: Maximum number of READMEs to fetch
        
    Returns:
        Dictionary of {doc_id: text}
    """
    if repos is None:
        # Popular programming repositories (150+ diverse repos)
        repos = [
            # Core Languages & Runtimes
            "golang/go",
            "rust-lang/rust",
            "python/cpython",
            "nodejs/node",
            "dotnet/core",
            "apple/swift",
            "microsoft/TypeScript",
            "oracle/graal",
            "ruby/ruby",
            "php/php-src",
            "juliaLang/julia",
            "scala/scala",
            "clojure/clojure",
            "erlang/otp",
            "elixir-lang/elixir",
            # Web Frameworks
            "facebook/react",
            "vuejs/vue",
            "angular/angular",
            "vercel/next.js",
            "rails/rails",
            "django/django",
            "spring-projects/spring-boot",
            "expressjs/express",
            "fastify/fastify",
            "nestjs/nest",
            "gin-gonic/gin",
            "flask/flask",
            "laravel/laravel",
            "symfony/symfony",
            # Mobile
            "flutter/flutter",
            "facebook/react-native",
            "ionic-team/ionic",
            "NativeScript/NativeScript",
            # ML/AI
            "tensorflow/tensorflow",
            "pytorch/pytorch",
            "scikit-learn/scikit-learn",
            "pandas-dev/pandas",
            "numpy/numpy",
            "apache/spark",
            "apache/flink",
            # Infrastructure & DevOps
            "kubernetes/kubernetes",
            "docker/docker",
            "hashicorp/terraform",
            "ansible/ansible",
            "prometheus/prometheus",
            "grafana/grafana",
            "istio/istio",
            "envoyproxy/envoy",
            "containerd/containerd",
            "gohugoio/hugo",
            # Databases
            "mongodb/mongo",
            "redis/redis",
            "postgres/postgres",
            "mysql/mysql-server",
            "mariadb/server",
            "apache/cassandra",
            "couchbase/couchbase",
            "neo4j/neo4j",
            "influxdata/influxdb",
            "elastic/elasticsearch",
            # Big Data
            "apache/hadoop",
            "apache/kafka",
            "apache/airflow",
            "apache/storm",
            "apache/druid",
            # Web Servers
            "apache/httpd",
            "nginx/nginx",
            "caddyserver/caddy",
            "traefik/traefik",
            # Editors & IDEs
            "microsoft/vscode",
            "atom/atom",
            "sublimehq/sublime_text",
            "neovim/neovim",
            "microsoft/monaco-editor",
            # Build Tools
            "maven/maven",
            "gradle/gradle",
            "bazelbuild/bazel",
            "webpack/webpack",
            "rollup/rollup",
            "vitejs/vite",
            # Testing
            "facebook/jest",
            "mochajs/mocha",
            "jasmine/jasmine",
            "pytest-dev/pytest",
            "junit-team/junit5",
            "testcontainers/testcontainers-java",
            # Security
            "OWASP/owasp-mastg",
            "OWASP/CheatSheetSeries",
            "hashicorp/vault",
            "aquasecurity/trivy",
            # Monitoring & Logging
            "elastic/kibana",
            "elastic/logstash",
            "grafana/loki",
            "prometheus/node_exporter",
            "jaegertracing/jaeger",
            # CI/CD
            "jenkinsci/jenkins",
            "gitlabhq/gitlabhq",
            "drone/drone",
            "argoproj/argo-cd",
            "tektoncd/pipeline",
            # Cloud Platforms
            "hashicorp/consul",
            "hashicorp/nomad",
            "apache/openwhisk",
            "serverless/serverless",
            # Game Engines
            "godotengine/godot",
            "Unity-Technologies/UnityCsReference",
            "unrealengine/unrealengine",
            # Graphics & Visualization
            "threejs/three.js",
            "d3/d3",
            "plotly/plotly.js",
            "apache/echarts",
            # Documentation
            "gitbookio/gitbook",
            "mkdocs/mkdocs",
            "sphinx-doc/sphinx",
            # Utilities
            "microsoft/PowerToys",
            "microsoft/terminal",
            "microsoft/WSL",
            "microsoft/calculator",
            "torvalds/linux",
            "mozilla/firefox",
            "mozilla/pdf.js",
            # Libraries & Tools
            "lodash/lodash",
            "moment/moment",
            "axios/axios",
            "request/request",
            "facebook/create-react-app",
            "facebook/flow",
            "microsoft/playwright",
            "cypress-io/cypress",
            "seleniumhq/selenium",
        ]
    
    docs = {}
    doc_id = 1
    
    headers = {
        "Accept": "application/vnd.github.v3.raw",
        "User-Agent": settings.user_agent,
    }
    
    for repo in repos[:limit]:
        try:
            logger.info("fetching_github_readme", repo=repo)
            readme_url = f"https://api.github.com/repos/{repo}/readme"
            
            response = requests.get(readme_url, headers=headers, timeout=settings.crawl_timeout)
            
            if response.status_code == 200:
                # Try to get raw content
                download_url = response.json().get("download_url")
                if download_url:
                    readme_response = requests.get(download_url, timeout=settings.crawl_timeout)
                    if readme_response.status_code == 200:
                        content = readme_response.text
                        if content.strip():
                            # Add repo info
                            full_content = f"Repository: {repo}\n\n{content}"
                            docs[f"github_{doc_id}"] = full_content[:settings.max_page_size]
                            doc_id += 1
                            logger.info("github_readme_success", repo=repo)
            
            # Rate limiting (GitHub allows 60 requests/hour without auth, but we'll be conservative)
            time.sleep(1)
            
        except Exception as e:
            logger.warning("github_readme_error", repo=repo, error=str(e))
            continue
    
    logger.info("github_fetch_complete", total_count=len(docs))
    return docs


def collect_public_datasets() -> Dict[str, str]:
    """
    Collect documents from all public datasets
    
    Returns:
        Dictionary of {doc_id: text} with 500-1000+ documents
    """
    all_docs = {}
    
    logger.info("starting_public_datasets_collection")
    
    # Collect from each source to ensure 500-1000 documents
    logger.info("collecting_hackernews")
    hn_docs = fetch_hackernews_posts(limit=250)
    all_docs.update(hn_docs)
    logger.info("hackernews_collected", count=len(hn_docs), total=len(all_docs))
    
    logger.info("collecting_reddit")
    reddit_docs = fetch_reddit_posts(
        subreddits=["programming", "Python", "MachineLearning", "webdev", "compsci", 
                   "learnprogramming", "javascript", "rust", "golang", "cpp"],
        limit_per_sub=75
    )
    all_docs.update(reddit_docs)
    logger.info("reddit_collected", count=len(reddit_docs), total=len(all_docs))
    
    logger.info("collecting_arxiv")
    arxiv_docs = fetch_arxiv_abstracts(
        categories=["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.SE", "cs.PL", "cs.NE", "cs.DS"],
        max_results=250
    )
    all_docs.update(arxiv_docs)
    logger.info("arxiv_collected", count=len(arxiv_docs), total=len(all_docs))
    
    logger.info("collecting_github")
    github_docs = fetch_github_readmes(limit=150)
    all_docs.update(github_docs)
    logger.info("github_collected", count=len(github_docs), total=len(all_docs))
    
    logger.info("public_datasets_collection_complete", total_documents=len(all_docs))
    
    return all_docs
