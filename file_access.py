import os
import re
from pathlib import Path
from difflib import SequenceMatcher


MAX_FILE_BYTES = 250_000
MAX_FILE_CHARS = 40_000
MAX_RELATED_FILES = 4
MAX_RELATED_CHARS = 8_000

TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".scss",
    ".json", ".toml", ".yaml", ".yml", ".md", ".txt", ".ini", ".cfg",
    ".rs", ".java", ".c", ".cpp", ".h", ".hpp", ".sql", ".xml",
    ".sh", ".ps1", ".bat", ".cmd"
}

IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    "target", "dist", "build", ".idea", ".vs"
}


def _roots():
    home = Path.home()
    roots = [
        Path(__file__).resolve().parent,
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
    ]

    extra = os.environ.get("DRAX_FILE_ROOTS", "")
    for raw in extra.split(os.pathsep):
        raw = raw.strip()
        if raw:
            roots.append(Path(os.path.expandvars(raw)).expanduser())

    unique = []
    seen = set()
    for root in roots:
        try:
            root = root.resolve()
        except OSError:
            continue
        key = str(root).lower()
        if key not in seen and root.exists():
            seen.add(key)
            unique.append(root)
    return unique


def _clean_query(query):
    return re.sub(r"\s+", " ", str(query or "").strip())


def _is_current_file_query(query):
    q = _clean_query(query).lower()
    return q in {
        "this file", "the file", "current file",
        "this document", "the current file"
    }


def _current_window_filename():
    try:
        from brain.context import context
        title = str(getattr(context, "current_window", "") or "").strip()
    except Exception:
        title = ""

    if not title:
        return None

    # Prefer a filename-like token with a known text extension.
    match = re.search(
        r"([A-Za-z0-9_.()\- ]+\.(?:py|ts|tsx|js|jsx|html|css|json|rs|md|txt|sql|java|cpp|h|hpp))\b",
        title,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def _iter_files():
    for root in _roots():
        if root.is_file():
            yield root
            continue

        try:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if any(part.lower() in IGNORED_DIRS for part in path.parts):
                    continue
                yield path
        except (OSError, PermissionError):
            continue


def _score(query, path):
    q = query.lower().strip()
    name = path.name.lower()
    stem = path.stem.lower()
    full = str(path).lower()

    if q == name or q == stem:
        return 1.0

    score = max(
        SequenceMatcher(None, q, name).ratio(),
        SequenceMatcher(None, q, stem).ratio(),
    )

    q_words = set(re.findall(r"[a-z0-9]+", q))
    name_words = set(re.findall(r"[a-z0-9]+", name))
    if q_words and name_words:
        score = max(score, len(q_words & name_words) / len(q_words))

    if q in full:
        score = max(score, 0.9)

    return score


def find_files(query, limit=8):
    query = _clean_query(query)
    if not query:
        return []

    if _is_current_file_query(query):
        current = _current_window_filename()
        if current:
            query = current
        else:
            return []

    direct = Path(os.path.expandvars(query)).expanduser()
    if direct.exists() and direct.is_file():
        return [{"path": str(direct.resolve()), "score": 1.0}]

    candidates = []
    seen = set()

    # Fast exact filename pass.
    q_lower = query.lower()
    for path in _iter_files():
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)

        if path.name.lower() == q_lower or path.stem.lower() == q_lower:
            candidates.append({
                "path": str(path),
                "score": 1.0,
            })

    if candidates:
        return candidates[:limit]

    # Fuzzy fallback.
    for path in _iter_files():
        key = str(path).lower()
        if key in seen:
            continue
        score = _score(query, path)
        if score >= 0.55:
            candidates.append({
                "path": str(path),
                "score": round(score, 4),
            })

    candidates.sort(key=lambda item: (-item["score"], item["path"].lower()))
    return candidates[:limit]


def _read_text(path):
    path = Path(path)

    if path.stat().st_size > MAX_FILE_BYTES:
        return None, f"File is larger than {MAX_FILE_BYTES:,} bytes."

    try:
        data = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            data = path.read_text(encoding="utf-8-sig")
        except Exception:
            return None, "File is not readable as UTF-8 text."
    except Exception as error:
        return None, str(error)

    return data[:MAX_FILE_CHARS], None


def _related_files(primary_path, query):
    primary = Path(primary_path)
    siblings = []

    try:
        for path in primary.parent.iterdir():
            if not path.is_file() or path == primary:
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if any(part.lower() in IGNORED_DIRS for part in path.parts):
                continue

            score = _score(query, path)

            # Files sharing the same project/module family are useful.
            if path.stem.lower() in primary.stem.lower() or primary.stem.lower() in path.stem.lower():
                score = max(score, 0.72)

            if score >= 0.55:
                siblings.append((score, path))
    except (OSError, PermissionError):
        return []

    siblings.sort(key=lambda item: (-item[0], str(item[1]).lower()))
    return siblings[:MAX_RELATED_FILES]


def inspect(query, include_related=True):
    matches = find_files(query, limit=8)

    if not matches:
        return {
            "success": False,
            "kind": "file",
            "query": query,
            "message": f"I couldn't find a local file matching '{query}'.",
        }

    best = matches[0]

    if len(matches) > 1 and best["score"] < 0.95:
        return {
            "success": False,
            "kind": "file_ambiguous",
            "query": query,
            "message": "I found multiple possible files.",
            "matches": matches[:5],
        }

    content, error = _read_text(best["path"])
    if error:
        return {
            "success": False,
            "kind": "file",
            "query": query,
            "path": best["path"],
            "message": f"I found '{best['path']}', but couldn't read it: {error}",
        }

    related = []
    if include_related:
        for score, path in _related_files(Path(best["path"]), query):
            text, read_error = _read_text(path)
            if read_error or text is None:
                continue
            related.append({
                "path": str(path),
                "score": round(score, 4),
                "content": text[:MAX_RELATED_CHARS],
            })

    return {
        "success": True,
        "kind": "file_inspection",
        "query": query,
        "path": best["path"],
        "score": best["score"],
        "content": content,
        "related_files": related,
        "matches": matches[:5],
    }


def search(query):
    matches = find_files(query, limit=10)
    return {
        "success": bool(matches),
        "kind": "file_search",
        "query": query,
        "matches": matches,
        "message": (
            f"Found {len(matches)} matching file(s)."
            if matches
            else f"I couldn't find a local file matching '{query}'."
        ),
    }
