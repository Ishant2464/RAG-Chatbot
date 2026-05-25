"""Generate LLM_CODEBASE.md — full source export for LLM context."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "LLM_CODEBASE.md"

SKIP_DIRS = {
    "node_modules", ".next", "__pycache__", ".git", "venv", ".venv", "env",
    "uploads", ".qdrant", ".cache", "huggingface", "mcps", ".cursor", "scripts",
}
SKIP_FILES = {
    "package-lock.json", "LLM_CODEBASE.md", "next-env.d.ts",
    ".env", ".env.local", ".env.prod", "build_llm_codebase.py",
}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".pyd"}


def should_include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(p in SKIP_DIRS for p in rel.parts):
        return False
    if path.name in SKIP_FILES:
        return False
    if path.suffix in SKIP_EXTENSIONS:
        return False
    if path.name.startswith(".env") and path.name != ".env.example":
        return False
    return True


def sort_key(p: Path) -> tuple:
    s = p.as_posix()
    if s.endswith("README.md") or s.endswith("SETUP.md"):
        return (0, s.lower())
    if s.startswith("app"):
        return (1, s.lower())
    if s.startswith("frontend"):
        return (2, s.lower())
    return (3, s.lower())


files = sorted(
    [p for p in ROOT.rglob("*") if p.is_file() and should_include(p)],
    key=sort_key,
)

LANG = {
    ".py": "python",
    ".tsx": "tsx",
    ".ts": "typescript",
    ".js": "javascript",
    ".css": "css",
    ".yml": "yaml",
    ".sh": "bash",
    ".md": "markdown",
    ".txt": "text",
}

lines = [
    "# RAG Chatbot — Full Codebase Export for LLM Context",
    "",
    "> Auto-generated snapshot. Excludes: node_modules, .next, __pycache__, venv, "
    "package-lock.json, .env secrets, uploads, build artifacts.",
    "",
    "## How to use",
    "Paste this entire file into an LLM when asking for code review, debugging, or modifications.",
    "",
    "## Architecture summary",
    "- **Backend** (`app/`): FastAPI — ingest PDFs to Supabase Storage, RQ worker embeds into Qdrant, Groq LLM for chat",
    "- **Frontend** (`frontend/`): Next.js 14 — Google OAuth via Supabase, streaming chat, document sidebar",
    "- **Infra**: Docker Compose (local), Render (API + Worker), Vercel (frontend)",
    "",
    "## File index",
]
for f in files:
    lines.append(f"- `{f.relative_to(ROOT).as_posix()}`")
lines.extend(["", "---", ""])

for f in files:
    rel = f.relative_to(ROOT).as_posix()
    try:
        content = f.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = f.read_text(encoding="utf-8", errors="replace")
    lang = LANG.get(f.suffix, f.suffix.lstrip(".") or "text")
    lines.append(f"## FILE: `{rel}`")
    lines.append("")
    lines.append(f"```{lang}")
    lines.append(content.rstrip())
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
size_kb = OUT.stat().st_size // 1024
print(f"Written {OUT} ({size_kb} KB, {len(files)} files)")
