#!/usr/bin/env python3
"""Render a prompt template with variables and localized contract strings."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import runpy
import sys

CONTRACT = runpy.run_path(str(Path(__file__).with_name("_strings.py")))
TOKEN = re.compile(r"\{([^\W\d][\w.-]*)\}")


def body_of(text):
    lines = text.splitlines()
    marks = [i for i, line in enumerate(lines) if line.strip() == "---"]
    if not marks:
        raise ValueError("Template has no --- body delimiter")
    start = marks[0] + 1
    if marks[0] == 0:
        if len(marks) < 2:
            raise ValueError("YAML frontmatter has no closing ---")
        start = marks[1] + 1
    end = next((i for i in marks if i >= start), len(lines))
    return "\n".join(lines[start:end]).strip() + "\n"


def read_fields(path, lang="en"):
    fields, header = {}, None
    required = ("slug", "field(en)", "field(ko)", "extraclause(en)")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            header = None
            continue
        cells = [x.strip().strip("`") for x in line.strip().strip("|").split("|")]
        names = [re.sub(r"\s+", "", x).lower() for x in cells]
        if all(x in names for x in required):
            header = names
            continue
        if header is None or all(re.fullmatch(r":?-+:?", x) for x in cells):
            continue
        if len(cells) != len(header):
            raise ValueError(f"Table column count mismatch: {line}")
        row = dict(zip(header, cells))
        slug = row["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Invalid slug: {slug}")
        if slug in fields:
            raise ValueError(f"Duplicate slug: {slug}")
        extra = row["extraclause(en)"]
        fields[slug] = {"slug": slug, "field": row[f"field({lang})"],
                        "extra_clause": "" if extra.lower() in ("", "none", "-", "없음", "(없음)") else extra}
    if not fields:
        raise ValueError("No field (en), field (ko), slug, extra clause (en) table found")
    return fields


def substitute(text, values):
    return TOKEN.sub(lambda m: str(values.get(m[1], m[0])), text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("--lang", choices=("en", "ko"), default="en", help="Prompt language (default: en)")
    parser.add_argument("--vars", "--variables", dest="variables", type=Path)
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--out", "-o", required=True)
    parser.add_argument("--fields", help="Comma-separated slugs")
    parser.add_argument("--list", dest="field_list", type=Path)
    args = parser.parse_args()
    try:
        values = json.loads(args.variables.read_text(encoding="utf-8")) if args.variables else {}
        if not isinstance(values, dict):
            raise ValueError("Variables JSON must be an object")
        values = {"date": date.today().isoformat(), **values}
        for item in args.set:
            key, sep, value = item.partition("=")
            if not sep or not key:
                raise ValueError(f"--set requires KEY=VALUE: {item}")
            values[key] = value
        values.update(CONTRACT["flatten_strings"](CONTRACT["STRINGS"][args.lang]))
        values["lang"] = args.lang
        template = body_of(args.template.read_text(encoding="utf-8"))
        if bool(args.fields) != bool(args.field_list):
            raise ValueError("Use --fields and --list together")
        rows = [values]
        if args.fields:
            fields = read_fields(args.field_list, args.lang)
            slugs = args.fields.split(",")
            if len(set(slugs)) != len(slugs):
                raise ValueError("Duplicate slug in --fields")
            rows = []
            for slug in slugs:
                if slug not in fields:
                    raise ValueError(f"Slug not in table: {slug}")
                rows.append({**values, **fields[slug]})
        pending = []
        for row in rows:
            for _ in range(10):
                expanded = {k: substitute(str(v), row) for k, v in row.items()}
                if expanded == row:
                    break
                row = expanded
            rendered = substitute(template, row)
            output = substitute(args.out, row)
            leftovers = sorted(set(TOKEN.findall(rendered) + TOKEN.findall(output)))
            if leftovers:
                raise ValueError("Unresolved placeholders: " + ", ".join(leftovers))
            target = Path(output)
            if args.fields and "{slug}" not in args.out:
                target = target / f"{row['slug']}.txt"
            pending.append((target, rendered))
        if len({p.resolve() for p, _ in pending}) != len(pending):
            raise ValueError("Multiple fields share an output path")
        if any(p.resolve() == args.template.resolve() for p, _ in pending):
            raise ValueError("Cannot overwrite the template")
        for path, rendered in pending:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
            print(f"{path}: {len(rendered.encode('utf-8'))} bytes, 0 unresolved placeholders")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
