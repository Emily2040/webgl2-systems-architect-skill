#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "webgl2-systems-architect"
AUTHOR = "Iamemily2050"
GITHUB_USER = "Emily2040"
REPO_URL = f"https://github.com/{GITHUB_USER}/webgl2-systems-architect-skill"
WEBSITE_URL = "https://Iamemily2050.com"
X_URL = "https://x.com/iamemily2050"
INSTAGRAM_URL = "https://instagram.com/iamemily2050"
NOREPLY_EMAIL = "191656017+Emily2040@users.noreply.github.com"

REQUIRED_FILES = [
    "SKILL.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "LICENSE",
    ".gitignore",
    "docs/index.html",
    "docs/assets/architecture.svg",
    "references/00-orchestrator.md",
    "references/01-redesign-rationale.md",
    "skills/core/01-triage.md",
    "skills/core/02-hardware-budget.md",
    "skills/core/03-pipeline-and-concurrency.md",
    "skills/core/04-subject-audit.md",
    "skills/core/05-shader-rules.md",
    "skills/core/06-runtime-ops.md",
    "skills/core/07-validation-and-ci.md",
    "registry/forbidden-slop.json",
    "registry/module-map.json",
    "schemas/authoring-base.json",
    "schemas/runtime-compact.json",
    "examples/face-raymarch.input.md",
    "examples/face-raymarch.output.json",
    "examples/terrain-midrange.input.md",
    "examples/terrain-midrange.output.json",
    "scripts/validate_repo.py",
    ".github/workflows/validate.yml",
]

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "metadata"}
PLACEHOLDER_PATTERNS = [
    r"your-org",
    r"your-repo",
    r"example\.com",
    r"your-username",
    r"openai",
]
TEXT_FILE_GLOBS = ["*.md", "*.json", "*.html", "*.yml", "*.yaml", "*.py"]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
      fail("SKILL.md is missing YAML frontmatter.")
    raw = match.group(1)
    data: dict[str, object] = {}
    current_parent = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if re.match(r"^\S", line):
            if ":" not in line:
                fail(f"Invalid frontmatter line: {line}")
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key not in ALLOWED_FRONTMATTER_KEYS:
                fail(f"Unsupported frontmatter key: {key}")
            if value == "":
                current_parent = key
                data[key] = {}
            else:
                data[key] = value.strip().strip('"')
                current_parent = None
        else:
            if current_parent != "metadata":
                fail(f"Unexpected indentation in frontmatter: {line}")
            sub = line.strip()
            if ":" not in sub:
                fail(f"Invalid metadata line: {line}")
            subkey, subvalue = sub.split(":", 1)
            cast = data.setdefault("metadata", {})
            assert isinstance(cast, dict)
            cast[subkey.strip()] = subvalue.strip().strip('"')
    return data


def walk_text_files() -> list[Path]:
    files: list[Path] = []
    for pattern in TEXT_FILE_GLOBS:
        files.extend(ROOT.rglob(pattern))
    files.extend(path for path in [ROOT / "LICENSE", ROOT / ".gitignore"] if path.exists())
    return sorted(set(files))


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def check_required_files() -> None:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))
    ok("Required files exist")


def check_no_shim_files() -> None:
    bad = [p.name for p in ROOT.iterdir() if p.is_file() and p.name.lower() == "skill.md" and p.name != "SKILL.md"]
    if bad:
        fail("Confusing duplicate entrypoints found: " + ", ".join(sorted(bad)))
    ok("No duplicate SKILL.md shim files found")


def check_skill() -> None:
    text = read("SKILL.md")
    if len(text) > 500:
        fail(f"SKILL.md must stay under 500 characters, got {len(text)}")
    meta = parse_frontmatter(text)
    for key in ("name", "description", "license", "metadata"):
        if key not in meta:
            fail(f"SKILL.md frontmatter missing key: {key}")
    if meta["name"] != SKILL_NAME:
        fail(f"metadata.name must be {SKILL_NAME!r}")
    metadata = meta["metadata"]
    if not isinstance(metadata, dict):
        fail("metadata must be a mapping")
    for key in ("version", "author", "repo"):
        if key not in metadata:
            fail(f"SKILL.md metadata missing key: {key}")
    if metadata["author"] != AUTHOR:
        fail(f"metadata.author must be {AUTHOR}")
    if metadata["repo"] != REPO_URL:
        fail(f"metadata.repo must be {REPO_URL}")
    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    if "references/00-orchestrator.md" not in body:
        fail("SKILL.md body must route to references/00-orchestrator.md")
    ok("SKILL.md frontmatter, routing, and size are valid")


def check_wrappers() -> None:
    for wrapper in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        text = read(wrapper)
        if "SKILL.md" not in text:
            fail(f"{wrapper} must point to SKILL.md")
        if "references/00-orchestrator.md" not in text:
            fail(f"{wrapper} must point to references/00-orchestrator.md")
    ok("Wrapper files point to the canonical source")


def check_no_extraneous_readmes() -> None:
    offenders = []
    for hidden_root in (ROOT / ".agents", ROOT / ".claude", ROOT / ".gemini"):
        if hidden_root.exists():
            offenders.extend(hidden_root.rglob("README.md"))
    if offenders:
        rels = ", ".join(str(p.relative_to(ROOT)) for p in offenders)
        fail("Extraneous README files found inside mirrored skill directories: " + rels)
    ok("No extraneous README files found in mirrored skill directories")


def check_cache_files() -> None:
    offenders = list(ROOT.rglob("__pycache__")) + list(ROOT.rglob(".DS_Store"))
    if offenders:
        rels = ", ".join(str(p.relative_to(ROOT)) for p in offenders)
        fail("Cache files or directories must not be committed: " + rels)
    ok("No cache files or directories found")


def check_placeholders() -> None:
    pattern = re.compile("|".join(PLACEHOLDER_PATTERNS), flags=re.IGNORECASE)
    hits = []
    ignored = {"scripts/validate_repo.py"}
    for path in walk_text_files():
        rel = str(path.relative_to(ROOT))
        if rel in ignored:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            hits.append(rel)
    if hits:
        fail("Placeholder content found in: " + ", ".join(hits))
    ok("No placeholder content detected")


def check_internal_links() -> None:
    markdown_files = [ROOT / "README.md", ROOT / "SKILL.md"]
    broken: list[str] = []
    link_pattern = re.compile(r"\]\(([^)]+)\)")
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for link in link_pattern.findall(text):
            target = link.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).exists():
                broken.append(f"{path.name}: {target}")
    if broken:
        fail("Broken internal markdown links: " + ", ".join(broken))
    ok("Internal markdown links resolve")


def check_identity() -> None:
    skill_meta = parse_frontmatter(read("SKILL.md"))["metadata"]
    assert isinstance(skill_meta, dict)
    if skill_meta["author"] != AUTHOR or skill_meta["repo"] != REPO_URL:
        fail("SKILL.md author metadata is inconsistent")

    license_text = read("LICENSE")
    if f"Copyright (c) 2026 {AUTHOR}" not in license_text:
        fail("LICENSE copyright line is missing or incorrect")

    readme_text = read("README.md")
    required_readme_bits = [
        f"Created by **{AUTHOR}**",
        f"https://github.com/{GITHUB_USER}",
        WEBSITE_URL,
        X_URL,
        INSTAGRAM_URL,
        REPO_URL,
    ]
    for bit in required_readme_bits:
        if bit not in readme_text:
            fail(f"README.md is missing required author/repo content: {bit}")

    docs_text = read("docs/index.html")
    if f"https://github.com/{GITHUB_USER}" not in docs_text:
        fail("docs/index.html footer must link to the GitHub profile")
    ok("Author identity is consistent across key files")


def check_gitignore() -> None:
    text = read(".gitignore")
    for required in ("__pycache__/", ".DS_Store"):
        if required not in text:
            fail(f".gitignore must contain {required}")
    ok(".gitignore contains required exclusions")


def check_json() -> None:
    json_files = [
        "registry/forbidden-slop.json",
        "registry/module-map.json",
        "schemas/authoring-base.json",
        "schemas/runtime-compact.json",
        "examples/face-raymarch.output.json",
        "examples/terrain-midrange.output.json",
    ]
    parsed = {}
    for rel in json_files:
        try:
            parsed[rel] = json.loads(read(rel))
        except Exception as exc:
            fail(f"Invalid JSON in {rel}: {exc}")

    for schema_rel in ("schemas/authoring-base.json", "schemas/runtime-compact.json"):
        schema = parsed[schema_rel]
        for key in ("$schema", "type", "properties", "required"):
            if key not in schema:
                fail(f"{schema_rel} missing schema key: {key}")

    authoring = parsed["examples/face-raymarch.output.json"]
    for key in ("skill", "task", "inputs", "modules", "assumptions", "decisions", "derivations", "parallel_plan", "deliverables", "risks"):
        if key not in authoring:
            fail(f"face-raymarch.output.json missing key: {key}")

    compact = parsed["examples/terrain-midrange.output.json"]
    for key in ("intent", "project_class", "modules", "key_decisions", "parallel_tasks", "risks", "next_steps"):
        if key not in compact:
            fail(f"terrain-midrange.output.json missing key: {key}")
    ok("JSON files parse and example outputs match expected shape")


def check_yaml_surrogates() -> None:
    pattern = re.compile(r"\\ud[89ab]", flags=re.IGNORECASE)
    hits: list[str] = []
    ignored = {"scripts/validate_repo.py"}
    for path in walk_text_files():
        rel = str(path.relative_to(ROOT))
        if rel in ignored:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            hits.append(rel)
    if hits:
        fail("Unicode surrogate escape sequences found in: " + ", ".join(hits))
    ok("No surrogate escape sequences detected")


def check_mirror_sync() -> None:
    canonical = read("SKILL.md")
    mirrors = []
    for pattern in (
        ".agents/skills/**/SKILL.md",
        ".claude/skills/**/SKILL.md",
        ".gemini/skills/**/SKILL.md",
    ):
        mirrors.extend(ROOT.glob(pattern))
    mismatched = []
    for path in mirrors:
        if path.read_text(encoding="utf-8") != canonical:
            mismatched.append(str(path.relative_to(ROOT)))
    if mismatched:
        fail("Mirrored SKILL.md files are out of sync: " + ", ".join(mismatched))
    ok("Mirrored SKILL.md files are synchronized or not used")


def main() -> None:
    check_required_files()
    check_no_shim_files()
    check_skill()
    check_wrappers()
    check_no_extraneous_readmes()
    check_cache_files()
    check_placeholders()
    check_internal_links()
    check_identity()
    check_gitignore()
    check_json()
    check_yaml_surrogates()
    check_mirror_sync()
    ok("Repository validation succeeded")
    print()
    print("Suggested commit attribution:")
    print(
        'git -c user.name="Iamemily2050" \\\n    -c user.email="191656017+Emily2040@users.noreply.github.com" \\\n    commit -m "Your commit message"'
    )


if __name__ == "__main__":
    main()
