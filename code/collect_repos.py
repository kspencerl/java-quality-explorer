import os
import time
import pandas as pd
from dotenv import load_dotenv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from requests.exceptions import HTTPError, RequestException

# Config
MAX_REPOS = 1000
PAGE_SIZE = 25
MAX_RETRIES = 4
RETRY_BASE = 1.5

# .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise SystemExit("Erro: GITHUB_TOKEN não encontrado no .env")

transport = RequestsHTTPTransport(
    url="https://api.github.com/graphql",
    headers={"Authorization": f"bearer {GITHUB_TOKEN}"},
    use_json=True,
)
client = Client(transport=transport, fetch_schema_from_transport=False)

QUERY_PATH = os.path.join(os.path.dirname(__file__), "query.graphql")
with open(QUERY_PATH, "r", encoding="utf-8") as f:
    QUERY = f.read()

def fetch_page(cursor=None):
    variables = {"cursor": cursor}
    attempt = 0
    while True:
        try:
            return client.execute(gql(QUERY), variable_values=variables)
        except (HTTPError, RequestException, Exception) as e:
            attempt += 1
            if attempt > MAX_RETRIES:
                raise
            sleep_s = RETRY_BASE ** attempt
            print(f"Erro (tentativa {attempt}/{MAX_RETRIES}): {e}. Repetindo em {sleep_s:.1f}s…")
            time.sleep(sleep_s)

def collect_top_repos():
    all_edges = []
    cursor = None
    has_next = True
    while has_next and len(all_edges) < MAX_REPOS:
        data = fetch_page(cursor)
        search = data["search"]
        edges = search.get("edges", [])
        all_edges.extend(edges)
        page_info = search.get("pageInfo") or {}
        has_next = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")
        print(f"Coletados {len(all_edges)} repositórios...")
    return all_edges[:MAX_REPOS]

def save_to_csv(edges):
    rows = []
    for edge in edges:
        repo = edge["node"]
        rows.append({
            "name": repo["name"],
            "owner": repo["owner"]["login"],
            "url": repo["url"],
            "stars": repo["stargazerCount"],
            "createdAt": repo["createdAt"],
            "pushedAt": repo["pushedAt"],
            "defaultBranch": (repo.get("defaultBranchRef") or {}).get("name"),
            "releases": (repo.get("releases") or {}).get("totalCount", 0),
        })
    df = pd.DataFrame(rows)
    df.to_csv("repositories.csv", index=False)
    print(f"Arquivo repositories.csv salvo com {len(rows)} registros.")

if __name__ == "__main__":
    edges = collect_top_repos()
    save_to_csv(edges)
