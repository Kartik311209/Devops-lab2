"""Create the requested report bundle and complete source/evidence archive."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import hashlib

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
dist.mkdir(exist_ok=True)
report_zip = dist / "devops-lab2-reports.zip"
project_zip = dist / "devops-lab2-project.zip"
reports = sorted((root / "reports").glob("*.pdf"))
if len(reports) != 4:
    raise RuntimeError(f"Expected 4 experiment reports, found {len(reports)}")

with ZipFile(report_zip, "w", ZIP_DEFLATED, compresslevel=9) as archive:
    for report in reports:
        archive.write(report, f"reports/{report.name}")

skip_dirs = {".git", ".venv", "tmp", "__pycache__"}
skip_names = {"devops-lab2-project.zip"}
with ZipFile(project_zip, "w", ZIP_DEFLATED, compresslevel=7) as archive:
    for path in root.rglob("*"):
        if not path.is_file() or any(part in skip_dirs for part in path.relative_to(root).parts):
            continue
        if path.name in skip_names or path.suffix == ".pyc":
            continue
        if path == report_zip:
            # Keep the requested report-only archive inside the complete project package.
            arcname = f"DevOps_Lab2_Kartik_Kumar/dist/{path.name}"
        else:
            arcname = str(Path("DevOps_Lab2_Kartik_Kumar") / path.relative_to(root))
        archive.write(path, arcname)

for path in (report_zip, project_zip):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{path.name}: {path.stat().st_size} bytes SHA256 {digest}")
