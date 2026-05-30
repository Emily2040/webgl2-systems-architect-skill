#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "webgl2-systems-architect-skill"
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
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    ".gitignore",
    "agents/openai.yaml",
    "docs/index.html",
    "docs/assets/architecture.svg",
    "docs/assets/skill-infographic.svg",
    "docs/assets/webgl2-systems-hero.png",
    "docs/assets/webgl2-systems-infographic.png",
    "references/00-orchestrator.md",
    "references/01-redesign-rationale.md",
    "references/02-webgl2-source-table.md",
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
    "fixtures/webgl2-smoke/index.html",
    "scripts/validate_repo.py",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/validate.yml",
]

CORE_MODULES = {
    "skills/core/01-triage.md",
    "skills/core/02-hardware-budget.md",
    "skills/core/03-pipeline-and-concurrency.md",
    "skills/core/04-subject-audit.md",
    "skills/core/05-shader-rules.md",
    "skills/core/06-runtime-ops.md",
    "skills/core/07-validation-and-ci.md",
}

EXPECTED_INTENTS = {
    "architecture",
    "implementation",
    "debug",
    "optimize",
    "review",
    "migration",
}

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "metadata"}
PLACEHOLDER_PATTERNS = [
    r"your-org",
    r"your-repo",
    r"example\.com",
    r"your-username",
]
TEXT_FILE_GLOBS = ["*.md", "*.json", "*.html", "*.yml", "*.yaml", "*.py", "*.svg"]
BIDI_CONTROL_PATTERN = re.compile("[\u202A-\u202E\u2066-\u2069]")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def rel_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_frontmatter(text: str) -> dict[str, Any]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md is missing YAML frontmatter.")

    raw = match.group(1)
    data: dict[str, Any] = {}
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
            if not isinstance(cast, dict):
                fail("metadata must be a mapping")
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


def load_json(rel: str) -> Any:
    try:
        return json.loads(read(rel))
    except Exception as exc:
        fail(f"Invalid JSON in {rel}: {exc}")


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
    if len(text) > 800:
        fail(f"SKILL.md must stay under 800 characters, got {len(text)}")

    meta = parse_frontmatter(text)
    for key in ("name", "description", "license", "metadata"):
        if key not in meta:
            fail(f"SKILL.md frontmatter missing key: {key}")
    if meta["name"] != SKILL_NAME:
        fail(f"metadata.name must be {SKILL_NAME!r}")
    if ROOT.name != SKILL_NAME:
        fail(f"Skill folder name must match SKILL.md name: expected {SKILL_NAME}, got {ROOT.name}")

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

    description = str(meta["description"])
    for trigger in ("WebGL2", "GLSL", "GPU", "context-loss", "DPR", "visual regression"):
        if trigger not in description:
            fail(f"SKILL.md description should include trigger term: {trigger}")

    body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    if "references/00-orchestrator.md" not in body:
        fail("SKILL.md body must route to references/00-orchestrator.md")
    ok("SKILL.md frontmatter, routing, trigger terms, and size are valid")


def check_openai_yaml() -> None:
    text = read("agents/openai.yaml")
    sections: dict[str, dict[str, str]] = {}
    current_section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            if not line.endswith(":"):
                fail(f"agents/openai.yaml top-level line must be a section: {line}")
            current_section = line[:-1]
            sections[current_section] = {}
            continue
        if current_section is None or not line.startswith("  ") or ":" not in line.strip():
            fail(f"Invalid agents/openai.yaml line: {line}")
        key, value = line.strip().split(":", 1)
        sections[current_section][key] = value.strip().strip('"')

    for section in ("interface", "policy"):
        if section not in sections:
            fail(f"agents/openai.yaml missing section: {section}")
    for key in ("display_name", "short_description", "default_prompt"):
        if not sections["interface"].get(key):
            fail(f"agents/openai.yaml missing interface field: {key}")
    for key in ("icon_small", "icon_large"):
        icon_path = sections["interface"].get(key)
        if icon_path and not (ROOT / icon_path.removeprefix("./")).exists():
            fail(f"agents/openai.yaml icon path does not exist: {icon_path}")
    if sections["policy"].get("allow_implicit_invocation") != "true":
        fail("agents/openai.yaml must keep allow_implicit_invocation: true")
    ok("Codex app metadata is present and structurally valid")


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
        rels = ", ".join(rel_posix(p) for p in offenders)
        fail("Extraneous README files found inside mirrored skill directories: " + rels)
    ok("No extraneous README files found in mirrored skill directories")


def check_cache_files() -> None:
    offenders = list(ROOT.rglob("__pycache__")) + list(ROOT.rglob(".DS_Store"))
    if offenders:
        rels = ", ".join(rel_posix(p) for p in offenders)
        fail("Cache files or directories must not be committed: " + rels)
    ok("No cache files or directories found")


def check_placeholders() -> None:
    pattern = re.compile("|".join(PLACEHOLDER_PATTERNS), flags=re.IGNORECASE)
    hits = []
    ignored = {"scripts/validate_repo.py"}
    for path in walk_text_files():
        rel = rel_posix(path)
        if rel in ignored:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            hits.append(rel)
    if hits:
        fail("Placeholder content found in: " + ", ".join(hits))
    ok("No placeholder content detected")


def check_internal_links() -> None:
    markdown_files = sorted(ROOT.rglob("*.md"))
    broken: list[str] = []
    link_pattern = re.compile(r"\]\(([^)]+)\)")
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for link in link_pattern.findall(text):
            target = link.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / target).exists():
                broken.append(f"{rel_posix(path)}: {target}")
    if broken:
        fail("Broken internal markdown links: " + ", ".join(broken))
    ok("Internal markdown links resolve")


def check_identity() -> None:
    skill_meta = parse_frontmatter(read("SKILL.md"))["metadata"]
    if not isinstance(skill_meta, dict):
        fail("SKILL.md metadata is not a mapping")
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
        SKILL_NAME,
    ]
    for bit in required_readme_bits:
        if bit not in readme_text:
            fail(f"README.md is missing required author/repo content: {bit}")

    docs_text = read("docs/index.html")
    if f"https://github.com/{GITHUB_USER}" not in docs_text:
        fail("docs/index.html footer must link to the GitHub profile")
    ok("Author identity and package name are consistent across key files")


def check_gitignore() -> None:
    text = read(".gitignore")
    for required in ("__pycache__/", ".DS_Store", "node_modules/", "test-results/", "playwright-report/"):
        if required not in text:
            fail(f".gitignore must contain {required}")
    ok(".gitignore contains required exclusions")


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return False


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    schema_type = schema.get("type")
    if schema_type is not None:
        types = schema_type if isinstance(schema_type, list) else [schema_type]
        if not any(type_matches(instance, expected) for expected in types):
            errors.append(f"{path}: expected type {types}, got {type(instance).__name__}")
            return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']!r}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required key {key!r}")

        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(validate_instance(instance[key], subschema, f"{path}.{key}"))

        additional = schema.get("additionalProperties", True)
        extra_keys = set(instance) - set(properties)
        if additional is False:
            for key in sorted(extra_keys):
                errors.append(f"{path}: unexpected key {key!r}")
        elif isinstance(additional, dict):
            for key in sorted(extra_keys):
                errors.extend(validate_instance(instance[key], additional, f"{path}.{key}"))

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(instance)}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{index}]"))

    return errors


def check_json() -> None:
    json_files = [
        "registry/forbidden-slop.json",
        "registry/module-map.json",
        "schemas/authoring-base.json",
        "schemas/runtime-compact.json",
        "examples/face-raymarch.output.json",
        "examples/terrain-midrange.output.json",
    ]
    parsed = {rel: load_json(rel) for rel in json_files}

    for schema_rel in ("schemas/authoring-base.json", "schemas/runtime-compact.json"):
        schema = parsed[schema_rel]
        for key in ("$schema", "type", "properties", "required"):
            if key not in schema:
                fail(f"{schema_rel} missing schema key: {key}")

    example_pairs = [
        ("examples/face-raymarch.output.json", "schemas/authoring-base.json"),
        ("examples/terrain-midrange.output.json", "schemas/runtime-compact.json"),
    ]
    validation_errors: list[str] = []
    for example_rel, schema_rel in example_pairs:
        for error in validate_instance(parsed[example_rel], parsed[schema_rel]):
            validation_errors.append(f"{example_rel} against {schema_rel}: {error}")
    if validation_errors:
        fail("Schema validation failed: " + "; ".join(validation_errors))

    skill = parse_frontmatter(read("SKILL.md"))
    metadata = skill["metadata"]
    assert isinstance(metadata, dict)
    authoring_skill = parsed["examples/face-raymarch.output.json"]["skill"]
    if authoring_skill["name"] != skill["name"] or authoring_skill["version"] != metadata["version"]:
        fail("Authoring example skill name/version must match SKILL.md")

    module_map = parsed["registry/module-map.json"]
    for example_rel in ("examples/face-raymarch.output.json", "examples/terrain-midrange.output.json"):
        example = parsed[example_rel]
        intent = example.get("task", example).get("intent")
        expected_modules = set(module_map[intent])
        actual_modules = set(example["modules"])
        missing = sorted(expected_modules - actual_modules)
        if missing:
            fail(f"{example_rel} is missing canonical modules for {intent}: " + ", ".join(missing))

    ok("JSON files parse and examples validate against schemas")


def check_module_map() -> None:
    module_map = load_json("registry/module-map.json")
    if set(module_map) != EXPECTED_INTENTS:
        fail("registry/module-map.json intents do not match expected intents")

    orchestrator = read("references/00-orchestrator.md")
    bad: list[str] = []
    for intent, modules in module_map.items():
        if not isinstance(modules, list) or not modules:
            bad.append(f"{intent}: modules must be a non-empty list")
            continue
        if modules[0] != "skills/core/01-triage.md":
            bad.append(f"{intent}: first module must be skills/core/01-triage.md")
        for module in modules:
            if module not in CORE_MODULES:
                bad.append(f"{intent}: unexpected module path {module}")
            if not (ROOT / module).exists():
                bad.append(f"{intent}: missing module file {module}")
            if module not in orchestrator and Path(module).name not in orchestrator:
                bad.append(f"{intent}: module path not mentioned by orchestrator {module}")
    if bad:
        fail("Module map validation failed: " + "; ".join(bad))
    ok("Module map paths and intent routing are valid")


def check_versions() -> None:
    skill = parse_frontmatter(read("SKILL.md"))
    metadata = skill["metadata"]
    assert isinstance(metadata, dict)
    version = metadata["version"]
    readme = read("README.md")
    changelog = read("CHANGELOG.md")
    if f"version-{version}-" not in readme:
        fail("README version badge must match SKILL.md metadata.version")
    if f"## {version} -" not in changelog:
        fail("CHANGELOG.md must contain the current SKILL.md version")
    ok("Version references are synchronized")


def check_yaml_surrogates() -> None:
    pattern = re.compile(r"\\ud[89ab]", flags=re.IGNORECASE)
    hits: list[str] = []
    ignored = {"scripts/validate_repo.py"}
    for path in walk_text_files():
        rel = rel_posix(path)
        if rel in ignored:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            hits.append(rel)
    if hits:
        fail("Unicode surrogate escape sequences found in: " + ", ".join(hits))
    ok("No surrogate escape sequences detected")


def check_no_bidi_controls() -> None:
    hits: list[str] = []
    for path in walk_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        if BIDI_CONTROL_PATTERN.search(text):
            hits.append(rel_posix(path))
    if hits:
        fail("Bidirectional Unicode control characters found in: " + ", ".join(hits))
    ok("No bidirectional Unicode controls detected")


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
            mismatched.append(rel_posix(path))
    if mismatched:
        fail("Mirrored SKILL.md files are out of sync: " + ", ".join(mismatched))
    ok("Mirrored SKILL.md files are synchronized or not used")


def check_webgl_fixture() -> None:
    text = read("fixtures/webgl2-smoke/index.html")
    required = [
        'getContext("webgl2"',
        "window.__webgl2Smoke",
        "status.dataset.smoke",
        "#version 300 es",
        "gl.drawArrays",
        "gl.readPixels",
    ]
    for bit in required:
        if bit not in text:
            fail(f"WebGL2 smoke fixture missing expected code: {bit}")
    ok("WebGL2 smoke fixture is present")


def main() -> None:
    check_required_files()
    check_no_shim_files()
    check_skill()
    check_openai_yaml()
    check_wrappers()
    check_no_extraneous_readmes()
    check_cache_files()
    check_placeholders()
    check_internal_links()
    check_identity()
    check_gitignore()
    check_json()
    check_module_map()
    check_versions()
    check_yaml_surrogates()
    check_no_bidi_controls()
    check_mirror_sync()
    check_webgl_fixture()
    ok("Repository validation succeeded")
    print()
    print("Suggested commit attribution:")
    print(
        'git -c user.name="Iamemily2050" '
        '-c user.email="191656017+Emily2040@users.noreply.github.com" '
        'commit -m "Your commit message"'
    )


if __name__ == "__main__":
    main()
