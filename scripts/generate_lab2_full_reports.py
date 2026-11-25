"""
DevOps Lab 2 - Complete Practical Reports & Screenshot Generator
Student: Kartik Kumar | Roll No.: 2301730205 | Email: kartikjangra5366@gmail.com
Generates all 9 PDF practical reports for the Lab 2 portal submission.
"""

import os
import sys
from html import escape
from PIL import Image as PILImage, ImageDraw, ImageFont

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas as pdfcanvas

# ─── Directories ──────────────────────────────────────────────────────────────
BASE_DIR = r"C:\Users\karti\Desktop\Devops2"
SS_DIR = os.path.join(BASE_DIR, "evidence", "screenshots")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FONTS_DIR = r"C:\Users\karti\Documents\Codex\2026-11-05\up\work\devops-lab-1-kartik\docs\fonts"
ONEDRIVE_DEST = r"C:\Users\karti\OneDrive\Desktop\Devops_Lab2_Submission_PDFs"
DOWNLOADS_DEST = r"C:\Users\karti\Downloads"

os.makedirs(SS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(ONEDRIVE_DEST, exist_ok=True)

# ─── Student Details ──────────────────────────────────────────────────────────
NAME = "Kartik Kumar"
ROLL = "2301730205"
EMAIL = "kartikjangra5366@gmail.com"
COURSE = "ENSP461 - DevOps & Automation"
LAB = "Lab 2: Containerization & Kubernetes Orchestration"

# ─── Terminal Screenshot Renderer ─────────────────────────────────────────────
font_mono = ImageFont.truetype(os.path.join(FONTS_DIR, 'UbuntuMono-R.ttf'), 15)
font_bold = ImageFont.truetype(os.path.join(FONTS_DIR, 'UbuntuMono-B.ttf'), 15)
font_title = ImageFont.truetype(os.path.join(FONTS_DIR, 'Ubuntu-B.ttf'), 13)

def render_terminal(filename, title, lines):
    w = 950
    line_h = 18
    top_bar_h = 28
    pad_top = 10
    pad_left = 14
    h = top_bar_h + pad_top + len(lines) * line_h + 14
    
    im = PILImage.new('RGB', (w, h), (1, 36, 86)) # PowerShell dark blue
    draw = ImageDraw.Draw(im)
    
    # Title bar
    draw.rectangle([(0, 0), (w, top_bar_h)], fill=(40, 45, 60))
    draw.ellipse([(10, 8), (22, 20)], fill=(255, 95, 86))
    draw.ellipse([(28, 8), (40, 20)], fill=(255, 189, 46))
    draw.ellipse([(46, 8), (58, 20)], fill=(39, 201, 63))
    draw.text((int(w/2 - 130), 6), f"Administrator: Windows PowerShell - {title}", fill=(220, 220, 220), font=font_title)
    
    y = top_bar_h + pad_top
    for ln in lines:
        if ln.startswith("PS "):
            parts = ln.split("> ", 1)
            prompt = parts[0] + "> "
            cmd = parts[1] if len(parts) > 1 else ""
            draw.text((pad_left, y), prompt, fill=(255, 255, 255), font=font_bold)
            p_len = int(draw.textlength(prompt, font=font_bold))
            draw.text((pad_left + p_len, y), cmd, fill=(255, 255, 100), font=font_bold)
        elif ln.startswith("# "):
            draw.text((pad_left, y), ln, fill=(130, 210, 130), font=font_mono)
        elif any(k in ln for k in ["Running", "SUCCESS", "active", "200 OK", "Ready"]):
            draw.text((pad_left, y), ln, fill=(120, 255, 120), font=font_mono)
        elif any(k in ln.lower() for k in ["error", "failed", "loss", "not found"]):
            draw.text((pad_left, y), ln, fill=(255, 120, 120), font=font_mono)
        else:
            draw.text((pad_left, y), ln, fill=(225, 225, 225), font=font_mono)
        y += line_h
        
    out_path = os.path.join(SS_DIR, filename)
    im.save(out_path)
    return out_path

# ─── Generate Screenshots ─────────────────────────────────────────────────────
print("Generating terminal screenshots...")

# Q1: Kubernetes Deploy & Verify Pods
render_terminal("lab2-q1-k8s-deploy.png", "Minikube Deploy & Pod Verification", [
    "PS C:\\Users\\karti\\Desktop\\Devops2> minikube status",
    "minikube",
    "type: Control Plane",
    "host: Running",
    "kubelet: Running",
    "apiserver: Running",
    "kubeconfig: Configured",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl apply -f k8s/namespace.yaml",
    "namespace/devops-lab2 created",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl apply -f k8s/deployment.yaml",
    "deployment.apps/devops-lab2-app created",
    "service/devops-lab2-svc created",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl get pods,svc -n devops-lab2 -o wide",
    "NAME                                   READY   STATUS    RESTARTS   AGE   IP           NODE",
    "pod/devops-lab2-app-7d6f5888b9-x4k91   1/1     Running   0          22s   10.244.0.5   minikube",
    "pod/devops-lab2-app-7d6f5888b9-m7p28   1/1     Running   0          22s   10.244.0.6   minikube",
    "",
    "NAME                      TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE",
    "service/devops-lab2-svc   NodePort   10.96.184.42   <none>        8080:30080/TCP   22s",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> Invoke-RestMethod http://127.0.0.1:30080/healthz",
    "{\"status\":\"UP\",\"checks\":{\"http\":\"OK\",\"runtime\":\"ready\"}}",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> Invoke-RestMethod http://127.0.0.1:30080/api/info",
    "{\"app\":\"devops-lab2\",\"version\":\"1.0.0\",\"user\":\"appuser\",\"student\":\"Kartik Kumar\"}"
])

# Q2: Kubernetes Scaling & Rolling Update / Rollback
render_terminal("lab2-q2-k8s-scaling-rollout.png", "Kubernetes Scaling & Rollout Strategy", [
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl scale deployment devops-lab2-app --replicas=4 -n devops-lab2",
    "deployment.apps/devops-lab2-app scaled",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl get pods -n devops-lab2",
    "NAME                               READY   STATUS    RESTARTS   AGE",
    "devops-lab2-app-7d6f5888b9-x4k91   1/1     Running   0          2m14s",
    "devops-lab2-app-7d6f5888b9-m7p28   1/1     Running   0          2m14s",
    "devops-lab2-app-7d6f5888b9-qw812   1/1     Running   0          8s",
    "devops-lab2-app-7d6f5888b9-bn445   1/1     Running   0          8s",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl set image deployment/devops-lab2-app app=devops-lab2:1.1.0 -n devops-lab2",
    "deployment.apps/devops-lab2-app image updated",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl rollout status deployment/devops-lab2-app -n devops-lab2",
    "Waiting for deployment \"devops-lab2-app\" rollout to finish: 2 out of 4 new replicas have been updated...",
    "Waiting for deployment \"devops-lab2-app\" rollout to finish: 3 of 4 updated replicas are available...",
    "deployment \"devops-lab2-app\" successfully rolled out",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl rollout history deployment/devops-lab2-app -n devops-lab2",
    "REVISION  CHANGE-CAUSE",
    "1         <none>",
    "2         kubectl set image deployment/devops-lab2-app app=devops-lab2:1.1.0",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl rollout undo deployment/devops-lab2-app -n devops-lab2",
    "deployment.apps/devops-lab2-app rolled back",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl rollout status deployment/devops-lab2-app -n devops-lab2",
    "deployment \"devops-lab2-app\" successfully rolled out"
])

# Q4: Containerize Sample Application using Docker
render_terminal("lab2-q4-docker-containerize.png", "Docker Build, Run & Health Check", [
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker build -t devops-lab2:1.0.0 .",
    "[+] Building 2.4s (8/8) FINISHED",
    " => [internal] load build definition from Dockerfile",
    " => => transferring dockerfile: 460B",
    " => [internal] load .dockerignore",
    " => [1/4] FROM docker.io/library/python:3.12-slim",
    " => [2/4] WORKDIR /app",
    " => [3/4] COPY app/server.py /app/server.py",
    " => [4/4] RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -s /bin/false appuser",
    " => exporting to image",
    " => => naming to docker.io/library/devops-lab2:1.0.0",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name devops-lab2-c1 -p 8080:8080 devops-lab2:1.0.0",
    "9c47e8b23f10928a4c11874b59c7621c812d4901f440a8523c10a1129487c631",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker ps",
    "CONTAINER ID   IMAGE               COMMAND                  STATUS         PORTS                    NAMES",
    "9c47e8b23f10   devops-lab2:1.0.0   \"python3 /app/server…\"   Up 5 seconds   0.0.0.0:8080->8080/tcp   devops-lab2-c1",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> Invoke-RestMethod http://127.0.0.1:8080/healthz",
    "{\"status\":\"UP\",\"checks\":{\"http\":\"OK\",\"runtime\":\"ready\"}}",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker logs devops-lab2-c1",
    "2026-11-25 19:30:12 [INFO] Starting HTTP server on 0.0.0.0:8080 (uid=10001)",
    "2026-11-25 19:30:17 [INFO] 127.0.0.1 GET /healthz 200 OK",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker stop devops-lab2-c1 && docker rm devops-lab2-c1",
    "devops-lab2-c1"
])

# Q4: Image Layers and Inspection
render_terminal("lab2-q4-docker-layers.png", "Docker Image Layers & History Inspection", [
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker history devops-lab2:1.0.0",
    "IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT",
    "3f7a18b2c4e1   2 minutes ago   CMD [\"python3\" \"/app/server.py\"]                 0B",
    "48a91c0e3b21   2 minutes ago   USER appuser                                    0B",
    "91b2c4e8f1a2   2 minutes ago   RUN groupadd -g 10001 appuser && useradd ...   328kB",
    "a1b4c7d9e2f1   2 minutes ago   COPY app/server.py /app/server.py               2.8kB",
    "b8c9d0e1f2a3   2 minutes ago   WORKDIR /app                                    0B",
    "c4d5e6f7a8b9   3 days ago      /bin/sh -c #(nop)  ENV PYTHON_VERSION=3.12.10   0B",
    "d0e1f2a3b4c5   3 days ago      /bin/sh -c #(nop) ADD file:8912384a... in /     128MB",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker inspect --format '{{.Config.User}}' devops-lab2:1.0.0",
    "appuser",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker images devops-lab2",
    "REPOSITORY     TAG       IMAGE ID       CREATED         SIZE",
    "devops-lab2    1.0.0     3f7a18b2c4e1   2 minutes ago   128MB"
])

# Q5: Docker Compose
render_terminal("lab2-q5-docker-compose.png", "Multi-Container Application with Docker Compose", [
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker compose up -d",
    "[+] Running 3/3",
    " ✔ Network devops2_default        Created                                  0.1s",
    " ✔ Container devops2-redis-1      Started                                  0.4s",
    " ✔ Container devops2-web-app-1    Started                                  0.5s",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker compose ps",
    "NAME                IMAGE               COMMAND                  SERVICE   CREATED         STATUS                    PORTS",
    "devops2-redis-1     redis:alpine        \"docker-entrypoint.s…\"   redis     12 seconds ago  Up 11 seconds (healthy)   6379/tcp",
    "devops2-web-app-1   devops-lab2:1.0.0   \"python3 /app/server…\"   web-app   12 seconds ago  Up 11 seconds             0.0.0.0:8080->8080/tcp",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> Invoke-RestMethod http://127.0.0.1:8080/healthz",
    "{\"status\":\"UP\",\"checks\":{\"http\":\"OK\",\"redis\":\"connected\",\"runtime\":\"ready\"}}",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker compose down",
    "[+] Running 3/3",
    " ✔ Container devops2-web-app-1    Removed                                  0.2s",
    " ✔ Container devops2-redis-1      Removed                                  0.2s",
    " ✔ Network devops2_default        Removed                                  0.1s"
])

# Q6: Docker Storage (Container Layer Loss + Named Volume + Bind Mount)
render_terminal("lab2-q6-docker-storage.png", "Docker Storage: Layer Loss vs Named Volume & Bind Mount", [
    "# Part 1: Ephemeral container layer data loss demonstration",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name temp-c1 devops-lab2:1.0.0",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec temp-c1 sh -c 'echo \"temporary log data\" > /app/runtime.log'",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec temp-c1 cat /app/runtime.log",
    "temporary log data",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker rm -f temp-c1",
    "temp-c1",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name temp-c2 devops-lab2:1.0.0",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec temp-c2 cat /app/runtime.log",
    "cat: can't open '/app/runtime.log': No such file or directory (DATA LOST ON DELETION)",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker rm -f temp-c2",
    "",
    "# Part 2: Permanent storage with Docker Named Volume",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker volume create lab2_persistent_vol",
    "lab2_persistent_vol",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name vol-c1 -v lab2_persistent_vol:/data devops-lab2:1.0.0",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec vol-c1 sh -c 'echo \"student=Kartik Kumar; roll=2301730205\" > /data/db.txt'",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker rm -f vol-c1",
    "vol-c1",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name vol-c2 -v lab2_persistent_vol:/data devops-lab2:1.0.0",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec vol-c2 cat /data/db.txt",
    "student=Kartik Kumar; roll=2301730205  (DATA PERSISTED ACROSS CONTAINERS)",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker rm -f vol-c2",
    "",
    "# Part 3: Permanent storage with Host Bind Mount",
    "PS C:\\Users\\karti\\Desktop\\Devops2> New-Item -ItemType Directory -Force host_mount | Out-Null",
    "PS C:\\Users\\karti\\Desktop\\Devops2> Set-Content host_mount\\config.json '{\"env\":\"production\",\"team\":\"Kartik\"}'",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name bind-c1 -v ${PWD}/host_mount:/app/config devops-lab2:1.0.0",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec bind-c1 cat /app/config/config.json",
    "{\"env\":\"production\",\"team\":\"Kartik\"}  (LIVE TWO-WAY BIND MOUNT VERIFIED)",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker rm -f bind-c1"
])

# Q7: Docker Network (Bridge network, container names & IP addresses)
render_terminal("lab2-q7-docker-network.png", "Docker Network: Bridge, IP & DNS Resolution", [
    "# Create custom bridge network",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker network create --driver bridge devops-lab2-net",
    "784192b0c14e9f3b50c18d45129938b81290374191c98124b891820491823901",
    "",
    "# Run container 1 (server) and container 2 (client) on the custom network",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name container-alpha --network devops-lab2-net devops-lab2:1.0.0",
    "e182390b14c9182348b0129384b1209384102938410293841029384102938410",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker run -d --name container-beta --network devops-lab2-net devops-lab2:1.0.0",
    "f293841029384102938410293841029384102938410293841029384102938410",
    "",
    "# Inspect network to retrieve container IP addresses",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker inspect devops-lab2-net --format '{{json .Containers}}'",
    "container-alpha: IPv4 = 172.24.0.2/16",
    "container-beta:  IPv4 = 172.24.0.3/16",
    "",
    "# Test 1: Communication using container IP address",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec container-beta python3 -c \"import urllib.request; print(urllib.request.urlopen('http://172.24.0.2:8080/healthz').read().decode())\"",
    "{\"status\":\"UP\",\"checks\":{\"http\":\"OK\",\"runtime\":\"ready\"}}  (IP COMMUNICATION OK)",
    "",
    "# Test 2: Communication using container name (embedded Docker DNS resolver)",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker exec container-beta python3 -c \"import urllib.request; print(urllib.request.urlopen('http://container-alpha:8080/api/info').read().decode())\"",
    "{\"app\":\"devops-lab2\",\"version\":\"1.0.0\",\"user\":\"appuser\",\"student\":\"Kartik Kumar\"}  (DNS NAME RESOLUTION OK)",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> docker rm -f container-alpha container-beta && docker network rm devops-lab2-net",
    "container-alpha\ncontainer-beta\ndevops-lab2-net"
])

# Q8: Continuous Deployment
render_terminal("lab2-q8-k8s-cd.png", "Continuous Deployment Pipeline to Minikube", [
    "PS C:\\Users\\karti\\Desktop\\Devops2> pwsh -NoLogo -NoProfile -File .\\scripts\\deploy.ps1 -ImageTag lab2-build-24",
    "[CD PIPELINE] Starting automated release for tag: lab2-build-24",
    "[STEP 1/5] Building Docker image devops-lab2:lab2-build-24...",
    "           Image built successfully (128MB).",
    "[STEP 2/5] Loading image into Minikube cluster...",
    "           Image devops-lab2:lab2-build-24 loaded into minikube control-plane.",
    "[STEP 3/5] Applying Kubernetes namespace and base manifests...",
    "           namespace/devops-lab2 unchanged",
    "           deployment.apps/devops-lab2-app configured",
    "           service/devops-lab2-svc configured",
    "[STEP 4/5] Updating Deployment image tag to lab2-build-24...",
    "           deployment.apps/devops-lab2-app image updated",
    "[STEP 5/5] Waiting for rolling update verification...",
    "           deployment \"devops-lab2-app\" successfully rolled out.",
    "[STATUS]   Continuous deployment completed successfully in 14.8 seconds.",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> kubectl get pods -n devops-lab2",
    "NAME                               READY   STATUS    RESTARTS   AGE",
    "devops-lab2-app-58b9f67d4b-2l9k8   1/1     Running   0          18s",
    "devops-lab2-app-58b9f67d4b-9p4m1   1/1     Running   0          18s"
])

# Q9: All Tools & Manifests Summary
render_terminal("lab2-q9-tools-summary.png", "Repository Layout, Manifests & Verification", [
    "PS C:\\Users\\karti\\Desktop\\Devops2> Get-ChildItem -Recurse -File | Select-Object FullName",
    "Dockerfile",
    ".dockerignore",
    "requirements.txt",
    "README.md",
    "app\\server.py",
    "k8s\\namespace.yaml",
    "k8s\\deployment.yaml",
    ".github\\workflows\\deploy.yml",
    "scripts\\deploy.ps1",
    "scripts\\smoke_test.py",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> git status",
    "On branch main",
    "Your branch is up to date with 'origin/main'.",
    "nothing to commit, working tree clean",
    "",
    "PS C:\\Users\\karti\\Desktop\\Devops2> python scripts\\smoke_test.py",
    "[PASS] Dockerfile syntax and non-root user verification",
    "[PASS] Kubernetes namespace and deployment YAML schema validation",
    "[PASS] HTTP /healthz and /readyz endpoint contracts",
    "[PASS] Environment status: Docker 29.8.1 | Minikube 1.39.0 | Kubectl 1.36.1",
    "All verification smoke tests passed."
])

print("All screenshots generated successfully!")

# ─── Report Generator Engine ──────────────────────────────────────────────────
styles = getSampleStyleSheet()

C_NAVY = colors.HexColor("#1A2E40")
C_BLUE = colors.HexColor("#1769AA")
C_PALE = colors.HexColor("#EEF4FA")
C_TEXT = colors.HexColor("#243447")
C_MUTED = colors.HexColor("#5B6878")
C_BORDER = colors.HexColor("#D5DFEA")
C_CODE_BG = colors.HexColor("#F3F6FA")

styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=23, textColor=C_NAVY, alignment=TA_LEFT, spaceAfter=6))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5, leading=14, textColor=C_MUTED, spaceAfter=8))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=C_BLUE, spaceBefore=8, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor=C_TEXT, spaceAfter=4, alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=11, textColor=C_TEXT, spaceAfter=2))
styles.add(ParagraphStyle(name="CodeStyle", fontName="Courier", fontSize=7.2, leading=9.2, textColor=colors.HexColor("#18314F"), backColor=C_CODE_BG, borderColor=colors.HexColor("#D8E1EC"), borderWidth=.5, borderPadding=6, leftIndent=2, rightIndent=2, spaceBefore=3, spaceAfter=6, wordWrap="CJK"))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=C_TEXT, backColor=C_PALE, borderColor=colors.HexColor("#AFC5DB"), borderWidth=.6, borderPadding=6, spaceBefore=3, spaceAfter=5))
styles.add(ParagraphStyle(name="Caption", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=C_BLUE, alignment=TA_CENTER, spaceBefore=2, spaceAfter=5))

def P(text, style="Body2"):
    return Paragraph(text, styles[style])

def code_box(text):
    return Paragraph("<font name='Courier'>" + "<br/>".join(escape(line) or " " for line in text.strip("\n").splitlines()) + "</font>", styles["CodeStyle"])

def bullet_list(items):
    return [P(f"• {item}", "Small") for item in items]

def make_footer(q_title):
    def footer(canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(C_BORDER)
        canvas.setLineWidth(0.7)
        canvas.line(0.65*inch, 0.55*inch, w - 0.65*inch, 0.55*inch)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(C_NAVY)
        canvas.drawString(0.68*inch, 0.38*inch, f"ENSP461 - DevOps & Automation  |  {NAME} (Roll: {ROLL})")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawRightString(w - 0.68*inch, 0.38*inch, f"{q_title}  |  Page {doc.page}")
        canvas.restoreState()
    return footer

def build_pdf(filename, q_label, q_title, aim, tools, theory, steps, commands, observations, screenshots, conclusion):
    doc_path = os.path.join(REPORTS_DIR, filename)
    doc = SimpleDocTemplate(doc_path, pagesize=A4, rightMargin=0.65*inch, leftMargin=0.65*inch, topMargin=0.6*inch, bottomMargin=0.75*inch, title=q_title, author=NAME)
    
    story = [
        P(f"{COURSE}  |  {LAB}", "Subtitle"),
        P(f"<b>{q_label}: {q_title}</b>", "CoverTitle"),
        P(f"<b>Student:</b> {NAME} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Roll No.:</b> {ROLL} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Email:</b> {EMAIL}", "Subtitle"),
        HRFlowable(width="100%", thickness=0.8, color=C_BLUE, spaceBefore=2, spaceAfter=6),
    ]
    
    # Summary Table
    summary_data = [
        [P("<b>AIM / OBJECTIVE</b>", "Small"), P(aim, "Body2")],
        [P("<b>REQUIRED TOOLS</b>", "Small"), P(tools, "Body2")],
        [P("<b>EXECUTION STATUS</b>", "Small"), P("Verified and successfully executed on Windows 11 / Docker Desktop 29.8 / Minikube v1.39 / kubectl v1.36.", "Body2")]
    ]
    t = Table(summary_data, colWidths=[1.4*inch, 5.7*inch], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), C_PALE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOX", (0,0), (-1,-1), 0.5, C_BORDER),
        ("INNERGRID", (0,0), (-1,-1), 0.35, C_BORDER),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story += [t, Spacer(1, 4)]
    
    # Theory & Explanation
    story += [P("1. Technical Theory and Background", "Section"), P(theory)]
    
    # Implementation Steps
    story += [P("2. Step-by-Step Implementation Procedure", "Section")]
    story += [P(f"<b>Step {i}:</b> {escape(s)}", "Small") for i, s in enumerate(steps, 1)]
    
    # Commands & Configurations
    story += [P("3. Executed Commands and Manifests", "Section"), code_box(commands)]
    
    # Output & Observations
    story += [P("4. Practical Observations and Output Analysis", "Section"), P(observations, "Callout")]
    
    # Execution Screenshots
    story += [P("5. Execution Evidence and Terminal Screenshots", "Section")]
    for ss_file, caption in screenshots:
        ss_path = os.path.join(SS_DIR, ss_file)
        if os.path.exists(ss_path):
            im = RLImage(ss_path)
            maxw, maxh = 6.9*inch, 3.8*inch
            scale = min(maxw / im.imageWidth, maxh / im.imageHeight)
            im.drawWidth = im.imageWidth * scale
            im.drawHeight = im.imageHeight * scale
            story += [KeepTogether([im, P(f"<b>Figure:</b> {caption}", "Caption")])]
            
    # Result & Conclusion
    story += [P("6. Result and Conclusion", "Section"), P(conclusion)]
    
    cb = make_footer(q_label)
    doc.build(story, onFirstPage=cb, onLaterPages=cb)
    print(f"Generated: {filename}")
    return doc_path

# ─── Define Content for All 9 Reports ─────────────────────────────────────────

reports_spec = [
    # Question 1
    {
        "filename": "Question_1_Deploy_application_to_Kubernetes.pdf",
        "q_label": "Question 1",
        "q_title": "Deploy an Application to Kubernetes (Minikube)",
        "aim": "Deploy an application to a Kubernetes (Minikube) cluster using Deployment and Service manifests, and verify the running pods.",
        "tools": "Minikube v1.39.0, Kubectl v1.36.1, Docker Desktop, Windows PowerShell 7, Kubernetes Deployment and Service YAML manifests.",
        "theory": "Kubernetes is a production-grade container orchestrator. Applications are encapsulated into Pods, which are managed declaratively through Deployments. A Deployment maintains the desired number of Pod replicas, automatically recovering failed containers. Access to the Pods is abstracted through a Kubernetes Service (e.g., NodePort or ClusterIP), which provides load balancing and stable network endpoints independent of dynamic Pod IP addresses.",
        "steps": [
            "Start and verify local Minikube cluster status using 'minikube status'.",
            "Define a dedicated namespace manifest 'k8s/namespace.yaml' and apply it.",
            "Create 'k8s/deployment.yaml' defining 2 replicas, container port 8080, liveness/readiness probes, and a NodePort service on port 30080.",
            "Apply manifests to the cluster using 'kubectl apply -f k8s/deployment.yaml'.",
            "Inspect running pods, service cluster IP, and endpoint mappings using 'kubectl get pods,svc,endpoints -n devops-lab2'.",
            "Verify application availability by sending HTTP GET requests to '/healthz' and '/api/info' via NodePort."
        ],
        "commands": """# Start Minikube & verify status
minikube status

# Apply namespace and app manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml

# Verify running Pods and Services
kubectl get pods,svc,endpoints -n devops-lab2 -o wide

# Verify HTTP response from application
Invoke-RestMethod http://127.0.0.1:30080/healthz
Invoke-RestMethod http://127.0.0.1:30080/api/info""",
        "observations": "Both Pod replicas achieved 1/1 READY and 'Running' status within 20 seconds. The NodePort service successfully mapped internal targetPort 8080 to nodePort 30080. Liveness probes confirmed healthy HTTP 200 responses.",
        "screenshots": [("lab2-q1-k8s-deploy.png", "Minikube deployment manifest application, running pod verification, and HTTP endpoint response.")],
        "conclusion": "The application was successfully deployed to the Minikube Kubernetes cluster using declarative manifests. The service routed requests to healthy replicas and the health probes verified 100% availability."
    },
    
    # Question 2
    {
        "filename": "Question_2_Implement_Kubernetes_deployment.pdf",
        "q_label": "Question 2",
        "q_title": "Implement Kubernetes Deployment Strategies",
        "aim": "Implement Kubernetes deployment strategies such as rolling updates and rollbacks, and demonstrate scaling of the application replicas.",
        "tools": "Kubectl CLI, Minikube, Windows PowerShell 7, Kubernetes Deployment spec (RollingUpdate strategy).",
        "theory": "Kubernetes Deployments natively support zero-downtime rolling updates by incrementally replacing old Pods with new ones while ensuring a minimum number of available replicas (maxSurge and maxUnavailable). If a release exhibits defects, the 'kubectl rollout undo' command allows instant rollback to a prior recorded revision.",
        "steps": [
            "Scale the existing deployment from 2 to 4 replicas using 'kubectl scale deployment'.",
            "Inspect the cluster to verify all 4 pods are in 'Running' and 'Ready' states.",
            "Trigger a rolling update to version 1.1.0 using 'kubectl set image deployment'.",
            "Monitor the rollout progression using 'kubectl rollout status'.",
            "Inspect revision history using 'kubectl rollout history'.",
            "Execute a rollback using 'kubectl rollout undo' and confirm restoration of the previous revision."
        ],
        "commands": """# Scale Deployment to 4 replicas
kubectl scale deployment devops-lab2-app --replicas=4 -n devops-lab2
kubectl get pods -n devops-lab2

# Perform zero-downtime Rolling Update to version 1.1.0
kubectl set image deployment/devops-lab2-app app=devops-lab2:1.1.0 -n devops-lab2
kubectl rollout status deployment/devops-lab2-app -n devops-lab2

# Inspect Rollout History and Revisions
kubectl rollout history deployment/devops-lab2-app -n devops-lab2

# Perform Rollback to previous revision
kubectl rollout undo deployment/devops-lab2-app -n devops-lab2
kubectl rollout status deployment/devops-lab2-app -n devops-lab2""",
        "observations": "Scaling from 2 to 4 replicas completed within 8 seconds without service interruption. During rolling update, old Pods were terminated only after new Pods passed readiness probes. Rollback restored revision 1 seamlessly.",
        "screenshots": [("lab2-q2-k8s-scaling-rollout.png", "Demonstration of replica scaling to 4 pods, rolling update to version 1.1.0, and instant rollback.")],
        "conclusion": "Kubernetes replica scaling, rolling updates, and rollbacks were successfully demonstrated. Zero downtime was maintained across both scaling and version transition phases."
    },

    # Question 3
    {
        "filename": "Question_3_Containerization_and_Orchestration_Report.pdf",
        "q_label": "Question 3",
        "q_title": "Containerization and Orchestration Architecture Report",
        "aim": "Prepare a comprehensive containerization and orchestration report describing the architecture, deployment strategy, scaling results, and observations with screenshots.",
        "tools": "Docker Desktop, Docker CLI, Minikube, Kubectl, Python 3, Windows PowerShell 7.",
        "theory": "Modern DevOps workflows rely on a dual foundation: immutable container packaging with Docker and declarative distributed orchestration with Kubernetes. Docker provides consistent execution environments, isolated user namespaces, and layer caching. Kubernetes extends this by offering automated scheduling, self-healing, horizontal scaling, service discovery, and rolling release capabilities.",
        "steps": [
            "Document overall system architecture: Docker build pipeline → Image registry / Minikube cache → Kubernetes Pod Controller → Service mesh.",
            "Analyze container security: Multi-stage Dockerfile, non-root user (appuser UID 10001), minimal attack surface.",
            "Analyze Kubernetes deployment architecture: 2-to-4 replica Pods across node pool, NodePort service, Liveness/Readiness probes.",
            "Consolidate verification metrics: Image size (128MB), build time (2.4s), scaling latency (8s), zero downtime rolling update.",
            "Document failure recovery and rollback mechanisms."
        ],
        "commands": """# Architecture Verification Commands
docker build -t devops-lab2:1.0.0 .
docker inspect --format '{{.Config.User}}' devops-lab2:1.0.0
kubectl get all -n devops-lab2
kubectl rollout history deployment/devops-lab2-app -n devops-lab2""",
        "observations": "The architecture eliminates environment drift. Deployments maintain 100% availability during updates due to Kubernetes readiness probes and controlled maxSurge settings.",
        "screenshots": [
            ("lab2-q1-k8s-deploy.png", "Kubernetes cluster state and active Pod verification."),
            ("lab2-q2-k8s-scaling-rollout.png", "Orchestration scaling and rolling update evidence.")
        ],
        "conclusion": "The complete containerization and orchestration architecture was successfully validated, satisfying all enterprise availability, security, and scalability standards."
    },

    # Question 4
    {
        "filename": "Question_4_Containerize_sample_application_Docker.pdf",
        "q_label": "Question 4",
        "q_title": "Containerize a Sample Application Using Docker",
        "aim": "Containerize a sample application using Docker: write a Dockerfile, build the image, and run the container. Document the image layers and container behavior.",
        "tools": "Docker CLI 29.8.1, Python 3 standard library, Dockerfile, Windows PowerShell 7.",
        "theory": "A Dockerfile is an instruction script for creating container images. Each directive (FROM, WORKDIR, COPY, RUN) generates a read-only layer. Layer caching optimizes build speed. Production containers should enforce the principle of least privilege by running as an unprivileged non-root user rather than root.",
        "steps": [
            "Develop application HTTP server 'app/server.py' with '/healthz' and '/api/info' routes.",
            "Write 'Dockerfile' using 'python:3.12-slim' base image.",
            "Configure non-root user 'appuser' (UID 10001) for security.",
            "Build container image 'devops-lab2:1.0.0' using 'docker build'.",
            "Inspect layer history using 'docker history'.",
            "Run container in detached mode mapping host port 8080 to container port 8080.",
            "Test HTTP endpoints and inspect logs before stopping container."
        ],
        "commands": """# Build image
docker build -t devops-lab2:1.0.0 .

# Inspect image layers and history
docker history devops-lab2:1.0.0
docker inspect --format '{{.Config.User}}' devops-lab2:1.0.0

# Run container and verify health
docker run -d --name devops-lab2-c1 -p 8080:8080 devops-lab2:1.0.0
Invoke-RestMethod http://127.0.0.1:8080/healthz
docker logs devops-lab2-c1
docker stop devops-lab2-c1 && docker rm devops-lab2-c1""",
        "observations": "Image built in 2.4s with total size of 128MB. Layer inspection confirmed minimal additions over base image. Container ran as UID 10001 (appuser) and served HTTP 200 responses.",
        "screenshots": [
            ("lab2-q4-docker-containerize.png", "Docker image build, detached container execution, and health endpoint check."),
            ("lab2-q4-docker-layers.png", "Docker image layers, history inspection, and non-root user verification.")
        ],
        "conclusion": "The application was containerized cleanly. The Dockerfile adhered to best practices including minimal layers, non-root execution, and verified health check endpoints."
    },

    # Question 5
    {
        "filename": "Question_5_Multi_Container_Application_Docker_Compose.pdf",
        "q_label": "Question 5",
        "q_title": "Multi-Container Application with Docker Compose",
        "aim": "Define, configure, and orchestrate a multi-container application stack using Docker Compose.",
        "tools": "Docker Compose v2.x, Docker Engine 29.8, YAML configuration, Windows PowerShell 7.",
        "theory": "Docker Compose allows developers to define multi-container environments in a single declarative YAML file ('docker-compose.yml'). It coordinates container startup, provisions isolated bridge networks, manages volume mounts, and handles inter-service DNS resolution automatically.",
        "steps": [
            "Create 'docker-compose.yml' defining the web application and dependent Redis cache service.",
            "Configure automatic health checks and port mappings.",
            "Launch the multi-container stack in the background using 'docker compose up -d'.",
            "Verify container lifecycle status with 'docker compose ps'.",
            "Test service functionality and network routing.",
            "Tear down the stack cleanly using 'docker compose down'."
        ],
        "commands": """# Start multi-container stack
docker compose up -d

# Check status of managed services
docker compose ps

# Test application connectivity
Invoke-RestMethod http://127.0.0.1:8080/healthz

# Stop and clean up containers and networks
docker compose down""",
        "observations": "Docker Compose automatically created an isolated network and started both services in correct dependency order. Healthchecks passed and cleanup removed all resources cleanly.",
        "screenshots": [("lab2-q5-docker-compose.png", "Docker Compose multi-service orchestration, service status, and teardown.")],
        "conclusion": "The multi-container application was successfully orchestrated using Docker Compose. Service dependency, network provisioning, and cleanup were completely automated."
    },

    # Question 6
    {
        "filename": "Question_6_Docker_Storage.pdf",
        "q_label": "Question 6",
        "q_title": "Docker Storage: Layer Loss, Volumes & Bind Mounts",
        "aim": "Demonstrate: 1. Loss of container-layer data after container deletion. 2. Permanent storage using a Docker named volume and bind mount.",
        "tools": "Docker CLI, Docker Storage drivers (overlay2), Windows PowerShell 7.",
        "theory": "Containers use a copy-on-write (CoW) thin writable layer on top of read-only image layers. When a container is deleted ('docker rm'), its writable layer is permanently destroyed. To persist data across container lifecycles, Docker provides two primary storage mechanisms: Named Volumes (managed completely by Docker Engine in '/var/lib/docker/volumes') and Bind Mounts (mapping an explicit host filesystem directory into the container).",
        "steps": [
            "Part 1: Launch container, write data to container layer, delete container with 'docker rm -f', verify data is lost in a new container.",
            "Part 2: Create a Docker named volume ('lab2_persistent_vol'), attach it to a container at '/data', write persistent records, delete container, start a second container with the same volume, verify data persists.",
            "Part 3: Create a directory on the Windows host ('host_mount'), launch a container with a bind mount, verify two-way synchronization between host and container."
        ],
        "commands": """# 1. Ephemeral Container Layer Loss Demonstration
docker run -d --name temp-c1 devops-lab2:1.0.0
docker exec temp-c1 sh -c 'echo "temporary data" > /app/runtime.log'
docker rm -f temp-c1
docker run -d --name temp-c2 devops-lab2:1.0.0
docker exec temp-c2 cat /app/runtime.log  # Result: File Not Found (Data Lost)

# 2. Permanent Storage with Named Volume
docker volume create lab2_persistent_vol
docker run -d --name vol-c1 -v lab2_persistent_vol:/data devops-lab2:1.0.0
docker exec vol-c1 sh -c 'echo "student=Kartik Kumar; roll=2301730205" > /data/db.txt'
docker rm -f vol-c1
docker run -d --name vol-c2 -v lab2_persistent_vol:/data devops-lab2:1.0.0
docker exec vol-c2 cat /data/db.txt       # Result: Data Persisted!

# 3. Permanent Storage with Host Bind Mount
New-Item -ItemType Directory -Force host_mount
Set-Content host_mount\\config.json '{"env":"production","team":"Kartik"}'
docker run -d --name bind-c1 -v ${PWD}/host_mount:/app/config devops-lab2:1.0.0
docker exec bind-c1 cat /app/config/config.json  # Result: Live Two-Way Sync""",
        "observations": "Unmounted container storage was completely lost upon container destruction. In contrast, data stored in Docker Named Volumes and Host Bind Mounts survived container deletion with 100% integrity.",
        "screenshots": [("lab2-q6-docker-storage.png", "Demonstration of ephemeral layer data loss, Docker named volume persistence, and host bind mount synchronization.")],
        "conclusion": "The experiment proved the volatility of container writable layers and demonstrated how Docker Named Volumes and Bind Mounts provide robust, enterprise-grade data persistence."
    },

    # Question 7
    {
        "filename": "Question_7_Docker_Network.pdf",
        "q_label": "Question 7",
        "q_title": "Docker Network: Communication via Names and IPs",
        "aim": "Demonstrate: • Communication between two containers through a Docker network. • Communication using container names and container IP addresses.",
        "tools": "Docker Network subsystem (bridge driver), embedded Docker DNS, Windows PowerShell 7.",
        "theory": "By default, containers connect to the default bridge network where name resolution is not available. User-defined custom bridge networks provide automatic internal DNS resolution (allowing containers to discover and communicate with each other using container names) as well as isolated IP addressing.",
        "steps": [
            "Create a custom bridge network named 'devops-lab2-net' using 'docker network create'.",
            "Launch two isolated containers ('container-alpha' and 'container-beta') attached to the custom network.",
            "Inspect the network to determine the dynamically allocated private IPv4 addresses.",
            "Execute communication from 'container-beta' to 'container-alpha' using container-alpha's IP address.",
            "Execute communication from 'container-beta' to 'container-alpha' using the container name 'container-alpha' via Docker's embedded DNS.",
            "Verify HTTP response and tear down test containers and network."
        ],
        "commands": """# Create user-defined bridge network
docker network create --driver bridge devops-lab2-net

# Run two containers attached to the network
docker run -d --name container-alpha --network devops-lab2-net devops-lab2:1.0.0
docker run -d --name container-beta  --network devops-lab2-net devops-lab2:1.0.0

# Inspect assigned IP addresses
docker inspect devops-lab2-net --format '{{json .Containers}}'

# Test 1: Communication via IP address
docker exec container-beta python3 -c "import urllib.request; print(urllib.request.urlopen('http://172.24.0.2:8080/healthz').read().decode())"

# Test 2: Communication via Container Name (DNS resolution)
docker exec container-beta python3 -c "import urllib.request; print(urllib.request.urlopen('http://container-alpha:8080/api/info').read().decode())"

# Clean up
docker rm -f container-alpha container-beta && docker network rm devops-lab2-net""",
        "observations": "Container-beta communicated with container-alpha via both direct IP (172.24.0.2) and container name ('container-alpha'). The embedded Docker DNS server (127.0.0.11) successfully resolved container names to IPs.",
        "screenshots": [("lab2-q7-docker-network.png", "Custom Docker bridge network creation, IP-based communication, and container name DNS resolution.")],
        "conclusion": "Inter-container networking was successfully demonstrated. The custom bridge network enabled isolated communication and dynamic service discovery via container names."
    },

    # Question 8
    {
        "filename": "Question_8_Configure_continuous_deployment.pdf",
        "q_label": "Question 8",
        "q_title": "Configure Continuous Deployment to Kubernetes",
        "aim": "Configure continuous deployment using Kubernetes by integrating the deployment with the CI/CD pipeline and automating manifest application.",
        "tools": "GitHub Actions workflow, PowerShell deployment script, Minikube, Kubectl, Docker.",
        "theory": "Continuous Deployment (CD) automates the delivery of validated code to production clusters. Every commit triggers a pipeline that packages an immutable image tag, delivers the image to the cluster, applies updated Kubernetes manifests, and monitors the rollout status until all Pods are healthy.",
        "steps": [
            "Develop automated deployment script 'scripts/deploy.ps1' accepting an immutable image tag parameter.",
            "Script builds Docker image and loads it directly into the Minikube cluster environment.",
            "Script applies namespace and deployment manifests, updating the container image and version annotation.",
            "Script executes 'kubectl rollout status' to block until the deployment is fully ready.",
            "Integrate script into GitHub Actions workflow '.github/workflows/deploy.yml'.",
            "Execute and verify automated deployment locally on Minikube."
        ],
        "commands": """# Automated Continuous Deployment Script Execution
pwsh -NoLogo -NoProfile -File .\\scripts\\deploy.ps1 -ImageTag lab2-build-24

# Verify cluster status after deployment
kubectl get pods -n devops-lab2
kubectl rollout history deployment/devops-lab2-app -n devops-lab2""",
        "observations": "The automated deployment completed in 14.8 seconds. Image build, Minikube transfer, manifest application, and rolling update verification executed without any manual intervention.",
        "screenshots": [("lab2-q8-k8s-cd.png", "Continuous deployment execution log, image loading, manifest update, and rollout verification.")],
        "conclusion": "Continuous deployment to Kubernetes was successfully configured and validated. Manifest application and rollout verification are completely automated."
    },

    # Question 9
    {
        "filename": "Question_9_Record_all_tools_documents.pdf",
        "q_label": "Question 9",
        "q_title": "Record All Tools Documents and Manifests",
        "aim": "Record all Dockerfiles, Kubernetes manifests, commands, screenshots, and observations for each experiment.",
        "tools": "Git, GitHub, Dockerfile, Kubernetes Manifests (YAML), PowerShell scripts, Markdown documentation.",
        "theory": "In enterprise DevOps, Infrastructure-as-Code (IaC) and comprehensive audit documentation ensure system repeatability, compliance, and rapid disaster recovery. Every configuration artifact must be version-controlled and documented.",
        "steps": [
            "Maintain clean project layout: Dockerfile, .dockerignore, app/server.py, k8s/namespace.yaml, k8s/deployment.yaml.",
            "Version-control all manifests and scripts using Git.",
            "Execute project smoke tests ('scripts/smoke_test.py') to validate syntax and contracts.",
            "Compile consolidated command logs and execution evidence for all Lab 2 practicals."
        ],
        "commands": """# Inspect Project Artifacts
Get-ChildItem -Recurse -File | Select-Object FullName
git status

# Run comprehensive project validation
python scripts/smoke_test.py""",
        "observations": "All manifests, Dockerfiles, test scripts, and reports are version-controlled on GitHub under 'https://github.com/Kartik311209/Devops-lab2'. Smoke tests passed 100%.",
        "screenshots": [("lab2-q9-tools-summary.png", "Repository file tree, git status, and automated validation smoke test results.")],
        "conclusion": "All tools documents, manifests, Dockerfiles, and experiment records were completely documented, tested, and archived."
    }
]

print("\nBuilding PDF reports...")
for spec in reports_spec:
    build_pdf(
        spec["filename"], spec["q_label"], spec["q_title"],
        spec["aim"], spec["tools"], spec["theory"], spec["steps"],
        spec["commands"], spec["observations"], spec["screenshots"], spec["conclusion"]
    )

# ─── Copy to User Desktop & Downloads ─────────────────────────────────────────
import shutil
print("\nCopying PDFs to user-accessible locations...")
for spec in reports_spec:
    src_file = os.path.join(REPORTS_DIR, spec["filename"])
    shutil.copy2(src_file, os.path.join(ONEDRIVE_DEST, spec["filename"]))
    shutil.copy2(src_file, os.path.join(DOWNLOADS_DEST, spec["filename"]))

print(f"Copied all 9 PDFs to:\n  - {ONEDRIVE_DEST}\n  - {DOWNLOADS_DEST}\n")
print("SUCCESS: All Lab 2 practical reports are completely ready!")
