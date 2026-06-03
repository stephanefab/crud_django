"""Convertit des .md en PDF via markdown + Chrome headless.

Usage :
    python md_to_pdf.py              # tous les .md du dossier courant
    python md_to_pdf.py ./TEST.md    # un fichier précis
    python md_to_pdf.py ./docs       # tous les .md d'un dossier
"""
from pathlib import Path
import subprocess
import sys
import markdown

MD_DIR = Path.cwd()              # dossier courant (là où le script est lancé)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.55;
  color: #1f2328;
  max-width: 100%;
  margin: 0;
}
h1, h2, h3, h4 {
  color: #0b3d91;
  font-weight: 700;
  line-height: 1.25;
  margin-top: 1.6em;
  margin-bottom: 0.5em;
  page-break-after: avoid;
}
h1 { font-size: 28pt; border-bottom: 2px solid #0b3d91; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 20pt; border-bottom: 1px solid #d0d7de; padding-bottom: 4px; }
h3 { font-size: 14pt; color: #1f4ea1; }
h4 { font-size: 12pt; }
p  { margin: 0.5em 0; }
a  { color: #0969da; text-decoration: none; }
ul, ol { padding-left: 1.6em; margin: 0.5em 0; }
li { margin: 0.2em 0; }

blockquote {
  margin: 0.8em 0;
  padding: 0.4em 1em;
  border-left: 4px solid #0969da;
  background: #f0f7ff;
  color: #1f2328;
  page-break-inside: avoid;
}
blockquote p { margin: 0.2em 0; }

code {
  font-family: "JetBrains Mono", "Cascadia Code", Consolas, "Courier New", monospace;
  font-size: 9.5pt;
  background: #f3f4f6;
  padding: 1px 5px;
  border-radius: 3px;
  color: #b91c1c;
}
pre {
  background: #0d1117;
  color: #e6edf3;
  padding: 12px 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 9pt;
  line-height: 1.45;
  page-break-inside: avoid;
  margin: 0.6em 0;
}
pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.8em 0;
  font-size: 10pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid #d0d7de;
  padding: 6px 10px;
  text-align: left;
  vertical-align: top;
}
th {
  background: #0b3d91;
  color: white;
  font-weight: 600;
}
tr:nth-child(even) td { background: #f6f8fa; }

hr { border: 0; border-top: 1px solid #d0d7de; margin: 1.5em 0; }

/* Pygments code highlighting */
.codehilite { background: #0d1117; border-radius: 6px; }
.codehilite .k, .codehilite .kn, .codehilite .kc { color: #ff7b72; }    /* keyword */
.codehilite .s, .codehilite .s1, .codehilite .s2 { color: #a5d6ff; }    /* string */
.codehilite .c, .codehilite .c1, .codehilite .cm { color: #8b949e; font-style: italic; }
.codehilite .nb { color: #79c0ff; }                                      /* builtin */
.codehilite .nf { color: #d2a8ff; }                                      /* function */
.codehilite .nc { color: #ffa657; }                                      /* class */
.codehilite .mi, .codehilite .mf { color: #79c0ff; }                     /* number */
.codehilite .o { color: #ff7b72; }                                       /* operator */
.codehilite .nd { color: #d2a8ff; }                                      /* decorator */
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{content}
</body>
</html>
"""


def convert_one(md_file: Path) -> bool:
    """Convertit un .md en .pdf (même dossier, même nom). Renvoie True si succès."""
    html_file = md_file.with_suffix(".html")
    pdf_file = md_file.with_suffix(".pdf")

    md_text = md_file.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "fenced_code", "codehilite", "toc"],
        extension_configs={"codehilite": {"guess_lang": False, "css_class": "codehilite"}},
    )
    html_file.write_text(
        HTML_TEMPLATE.format(css=CSS, content=html_body, title=md_file.stem),
        encoding="utf-8",
    )

    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file}",
        html_file.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    html_file.unlink(missing_ok=True)   # nettoyage du HTML intermédiaire

    if result.returncode != 0 or not pdf_file.exists():
        print(f"[ECHEC] {md_file.name}", file=sys.stderr)
        print("   Chrome stderr:", result.stderr.strip(), file=sys.stderr)
        return False

    print(f"[OK] {md_file.name} -> {pdf_file.name}  ({pdf_file.stat().st_size // 1024} Ko)")
    return True


def collect_md_files(arg: str | None) -> list[Path]:
    """Détermine les .md à convertir selon l'argument (fichier, dossier, ou rien)."""
    if arg is None:                              # pas d'argument → tous les .md du dossier courant
        return sorted(MD_DIR.glob("*.md"))

    target = Path(arg).expanduser().resolve()
    if target.is_dir():                          # un dossier → tous ses .md
        return sorted(target.glob("*.md"))
    if target.is_file():                         # un fichier précis
        if target.suffix.lower() != ".md":
            print(f"Pas un fichier .md : {target}", file=sys.stderr)
            return []
        return [target]

    print(f"Chemin introuvable : {target}", file=sys.stderr)
    return []


def main() -> int:
    if not Path(CHROME).exists():
        print(f"Chrome introuvable : {CHROME}", file=sys.stderr)
        return 1

    arg = sys.argv[1] if len(sys.argv) > 1 else None
    md_files = collect_md_files(arg)
    if not md_files:
        if arg is None:
            print(f"Aucun .md trouvé dans {MD_DIR}", file=sys.stderr)
        return 1

    print(f"{len(md_files)} fichier(s) .md à convertir\n")
    ok = sum(convert_one(md) for md in md_files)
    failed = len(md_files) - ok

    print(f"\nTerminé : {ok} réussi(s), {failed} échec(s).")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
