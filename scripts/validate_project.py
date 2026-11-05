"""Offline structural checks for manifests, Python source, PDFs and evidence."""
from pathlib import Path
import ast
import yaml
from pypdf import PdfReader
from PIL import Image

root = Path(__file__).resolve().parents[1]
results = []
def check(label, condition):
    if not condition:
        raise AssertionError(label)
    results.append(f"PASS {label}")

for source in [root / "app/server.py", root / "scripts/smoke_test.py", root / "scripts/build_reports.py"]:
    ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
check("Python source parses", True)

namespace = yaml.safe_load((root / "k8s/namespace.yaml").read_text(encoding="utf-8"))
resources = list(yaml.safe_load_all((root / "k8s/deployment.yaml").read_text(encoding="utf-8")))
workflow = yaml.safe_load((root / ".github/workflows/deploy.yml").read_text(encoding="utf-8"))
check("Kubernetes namespace manifest parses", namespace["kind"] == "Namespace")
check("Deployment and Service manifests parse", [r["kind"] for r in resources] == ["Deployment", "Service"])
check("Deployment has two replicas and rolling update policy", resources[0]["spec"]["replicas"] == 2 and resources[0]["spec"]["strategy"]["type"] == "RollingUpdate")
check("GitHub Actions workflow parses and has deploy job", isinstance(workflow, dict) and "jobs" in workflow and "deploy" in workflow["jobs"])

pdfs = sorted((root / "reports").glob("*.pdf"))
check("Exactly four experiment PDFs exist", len(pdfs) == 4)
for pdf in pdfs:
    reader = PdfReader(str(pdf))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = ["objective", "theory and explanation", "required software and tools", "implementation steps", "commands and code", "output and observations", "result and conclusion", "kartik kumar", "2301730205"]
    check(f"{pdf.name} has {len(reader.pages)} readable pages and all report sections", len(reader.pages) >= 2 and all(word in text.casefold() for word in required))

for image in sorted((root / "evidence/screenshots").glob("*.png")):
    with Image.open(image) as im:
        check(f"Screenshot opens: {image.name} ({im.width}x{im.height})", im.width >= 800 and im.height >= 300)

log = root / "evidence/logs/project-validation.txt"
log.write_text("\n".join(results) + "\n", encoding="utf-8")
print("\n".join(results))
