"""Create one polished PDF report per lab practical using ReportLab."""
from pathlib import Path
from html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Preformatted, Image, PageBreak, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
NAME, ROLL, EMAIL = "Kartik Kumar", "2301730205", "kartikjangra5366@gmail.com"
NAVY, BLUE, PALE, TEXT, MUTED = colors.HexColor("#17365D"), colors.HexColor("#1769AA"), colors.HexColor("#EEF4FA"), colors.HexColor("#243447"), colors.HexColor("#5B6878")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontSize=10, leading=15, textColor=MUTED, spaceAfter=10))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=BLUE, spaceBefore=9, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=9.2, leading=13, textColor=TEXT, spaceAfter=5))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.2, leading=11, textColor=TEXT, spaceAfter=3))
styles.add(ParagraphStyle(name="Code2", fontName="Courier", fontSize=7.3, leading=9.5, textColor=colors.HexColor("#18314F"), backColor=colors.HexColor("#F3F6FA"), borderColor=colors.HexColor("#D8E1EC"), borderWidth=.5, borderPadding=7, leftIndent=3, rightIndent=3, spaceBefore=3, spaceAfter=7, wordWrap="CJK"))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=8.8, leading=12.5, textColor=TEXT, backColor=PALE, borderColor=colors.HexColor("#AFC5DB"), borderWidth=.7, borderPadding=8, spaceBefore=4, spaceAfter=7))

def P(text, style="Body2"):
    return Paragraph(text, styles[style])

def code(text):
    return Paragraph("<font name='Courier'>" + "<br/>".join(escape(line) or " " for line in text.strip("\n").splitlines()) + "</font>", styles["Code2"])

def bullets(items):
    return [P("- " + item, "Small") for item in items]

def footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor("#D5DFEA"))
    canvas.line(0.65*inch, 0.55*inch, w-0.65*inch, 0.55*inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.68*inch, 0.36*inch, f"DEVOPS LAB 2  |  {NAME}  |  {ROLL}")
    canvas.drawRightString(w-0.68*inch, 0.36*inch, f"Page {doc.page}")
    canvas.restoreState()

common_tools = "Windows PowerShell; Python 3 (standard library); Docker CLI / Docker Desktop; kubectl; Minikube; GitHub Actions (self-hosted runner)."
student_line = f"<b>{NAME}</b> &nbsp; | &nbsp; Roll no. <b>{ROLL}</b> &nbsp; | &nbsp; {EMAIL}"

experiments = [
{
 "file":"Experiment_1_Docker_Image_Container_Workflow.pdf", "number":"EXPERIMENT 01",
 "title":"Docker Image and Container Workflow", "objective":"Create a reproducible application image, run it as an isolated container, inspect its health and logs, and stop it cleanly.",
 "status":"Executed successfully in Docker Desktop using Windows PowerShell.",
 "theory":"A Docker image packages an application and its runtime into a versioned, immutable template. A container is a running instance of that image with an isolated process and mapped network port. Health checks provide a basic signal that an instance is responding. This project uses a small Python standard-library HTTP service and a non-root image user.",
 "tools":["Windows 11 / PowerShell 7.6.5", "Python 3 standard library", "Docker CLI and Docker Desktop Linux engine 29.8.1", "Dockerfile and local HTTP client Invoke-RestMethod"],
 "steps":["Inspect the app and Dockerfile; the image copies only `app/server.py` and runs it as UID 10001.","Build the image and inspect its tag/size.","Run the container with host port 8080 mapped to container port 8080.","Check `/healthz`, `/readyz`, `/api/info`, and container logs; then stop the container."],
 "commands":"docker build -t devops-lab2:1.0.0 .\ndocker image ls devops-lab2\ndocker run --rm -d --name devops-lab2 -p 8080:8080 devops-lab2:1.0.0\nInvoke-RestMethod http://127.0.0.1:8080/healthz\nInvoke-RestMethod http://127.0.0.1:8080/api/info\ndocker logs devops-lab2\ndocker stop devops-lab2",
 "output":"Executed successfully: Docker CLI client and server reported version 29.8.1, `docker build` created image `devops-lab2:1.0.0`, and a container started with the image. PowerShell Invoke-RestMethod returned the healthy `/healthz` JSON and `/api/info` reported version 1.0.0 with Kartik Kumar's identity. `docker ps` showed the container healthy after 13 seconds; `docker stop` exited with code 0.",
 "images":[("powershell-docker-attempt.png", "Actual PowerShell terminal: Docker Desktop version and successful image build (exit code 0)."), ("powershell-docker-run.png", "Actual PowerShell terminal: container lifecycle, HTTP health and student metadata responses, healthy container status, and stop (exit code 0).")],
 "conclusion":"The container image was built and run successfully. Both HTTP endpoints returned the expected responses, the Docker health check reached healthy, and the container stopped cleanly."
},
{
 "file":"Experiment_2_Kubernetes_Deployment_Scaling.pdf", "number":"EXPERIMENT 02",
 "title":"Kubernetes Deployment and Scaling", "objective":"Deploy the containerized app to Minikube, expose it through a Service, verify replica health, and scale the Deployment horizontally.",
 "status":"Executed successfully on Minikube v1.39.0 / Kubernetes v1.37.0.",
 "theory":"A Kubernetes Deployment maintains the requested number of Pods and replaces unhealthy instances. A Service provides a stable endpoint for matching Pods. Horizontal scaling changes the desired replica count; the controller creates or removes Pods to converge on that count. Readiness and liveness probes connect the app's HTTP health endpoints to Kubernetes health management.",
 "tools":["Windows PowerShell", "Docker Desktop Linux engine", "Minikube with Docker driver", "kubectl", "Kubernetes Deployment/Service manifests in `k8s/`"],
 "steps":["Start Minikube with the Docker driver.","Build and load the image into Minikube's image cache.","Apply the namespace and Deployment/Service manifests; wait for rollout.","Inspect Pods and Service, open the Minikube service URL, and scale replicas from two to four."],
 "commands":"minikube start --driver=docker\ndocker build -t devops-lab2:1.0.0 .\nminikube image load devops-lab2:1.0.0\nkubectl apply -f .\\k8s\\namespace.yaml\nkubectl apply -f .\\k8s\\deployment.yaml\nkubectl -n devops-lab2 rollout status deployment/devops-lab2\nkubectl -n devops-lab2 get pods,svc\nkubectl -n devops-lab2 scale deployment/devops-lab2 --replicas=4\nkubectl -n devops-lab2 get deployment,pods",
 "output":"Executed on the live Minikube cluster. `minikube image load` completed; the namespace, Deployment and Service were applied; rollout status succeeded; `kubectl get deployment` reported 2/2 Ready and the NodePort Service was present. The Deployment was then scaled from two to four replicas; rollout completed with 4/4 replicas Ready.",
 "images":[("powershell-kubernetes-attempt.png", "Actual PowerShell session showing manifest apply, successful rollout, 2/2 Ready Deployment, and NodePort Service."), ("powershell-kubernetes-scale.png", "Actual PowerShell session showing scale to four, successful rollout, and four Ready Pods.")],
 "conclusion":"The Minikube deployment, NodePort Service, health probes and horizontal scaling all worked. The four-replica Deployment converged to 4/4 Ready Pods."
},
{
 "file":"Experiment_3_Kubernetes_Rolling_Update_Rollback.pdf", "number":"EXPERIMENT 03",
 "title":"Rolling Update and Rollback Strategy", "objective":"Release a new app version without planned downtime, observe rollout progress, and restore the previous Deployment revision if verification fails.",
 "status":"Executed successfully on Minikube with a rolling image/version update and rollback.",
 "theory":"A rolling update replaces old Pods gradually according to `maxSurge` and `maxUnavailable`. With one extra Pod allowed and zero unavailable replicas, Kubernetes can wait for a new Pod to become ready before removing an old one. Deployment revision history enables a rollback to the prior Pod template. Readiness probes gate traffic during replacement.",
 "tools":["PowerShell", "Docker and Minikube", "kubectl rollout / set image", "Kubernetes Deployment strategy and readiness probe"],
 "steps":["Build and load a second image tag.","Update the Deployment image and application version.","Wait for rollout, inspect revision history and Pod readiness.","If validation fails, undo the latest rollout and wait for the previous revision."],
 "commands":"docker build -t devops-lab2:1.1.0 .\nminikube image load devops-lab2:1.1.0\nkubectl -n devops-lab2 set image deployment/devops-lab2 web=devops-lab2:1.1.0\nkubectl -n devops-lab2 set env deployment/devops-lab2 APP_VERSION=1.1.0\nkubectl -n devops-lab2 rollout status deployment/devops-lab2\nkubectl -n devops-lab2 rollout history deployment/devops-lab2\n# Recovery if verification fails\nkubectl -n devops-lab2 rollout undo deployment/devops-lab2\nkubectl -n devops-lab2 rollout undo deployment/devops-lab2\nkubectl -n devops-lab2 rollout status deployment/devops-lab2",
 "output":"Executed on Minikube. Image `devops-lab2:1.1.0` was built and loaded; the Deployment image and APP_VERSION were updated. Kubernetes reported the rolling update successfully rolled out and recorded successive revisions in rollout history. Two `rollout undo` commands reverted the image and environment changes to the prior Deployment state; the restored Deployment rollout succeeded. Kubernetes emitted a warning that undo does not update the last-applied annotation because the Deployment was originally applied with `kubectl apply`.",
 "images":[("powershell-rollout-attempt.png", "Actual PowerShell output for the image build/load, version update, successful rollout, and revision history."), ("powershell-rollout-rollback.png", "Actual PowerShell output showing both rollback commands and a successful restored rollout. Kubernetes' apply annotation warning is visible in the terminal capture.")],
 "conclusion":"The rolling update and recovery worked on the live cluster. The new version became Ready before old replicas were removed, and the prior Deployment revision was restored by undoing both recorded changes."
},
{
 "file":"Experiment_4_Continuous_Deployment_to_Minikube.pdf", "number":"EXPERIMENT 04",
 "title":"Continuous Deployment to Minikube", "objective":"Automate build, local image delivery, manifest application, version update, and rollout verification for commits to the main branch.",
 "status":"Local Minikube deployment script executed; GitHub Actions runner is not attached to this workspace.",
 "theory":"Continuous deployment connects a source change to a repeatable release pipeline. This project's reusable PowerShell script builds an immutable tag, loads the image into Minikube, applies manifests, updates the Deployment image and APP_VERSION, and blocks completion until rollout succeeds. The GitHub Actions workflow invokes the same script with the commit SHA. A self-hosted runner is necessary because a GitHub-hosted runner cannot access a cluster bound to a student's workstation.",
 "tools":["Windows PowerShell 7", "Docker Desktop", "Minikube and kubectl", "GitHub Actions workflow `.github/workflows/deploy.yml`", "Reusable deployment script `scripts/deploy.ps1`"],
 "steps":["Start the Minikube cluster and provide an immutable image tag.","Build the container image and load it into Minikube.","Apply the namespace and app manifests, update the image and APP_VERSION, then wait for rollout status.","In GitHub Actions, a self-hosted runner checks out the commit and passes its SHA to the same deployment script."],
 "commands":"# Local deployment demonstration\npwsh -NoLogo -NoProfile -File .\\scripts\\deploy.ps1 -ImageTag lab2-local-20261105\n\n# GitHub Actions invocation (.github/workflows/deploy.yml)\n./scripts/deploy.ps1 -ImageTag \"${{ github.sha }}\"",
 "output":"Executed locally on Minikube with a unique immutable tag. The script built and loaded the image, applied the manifests, updated the Deployment image and version, and waited for a successful rollout. The GitHub Actions job itself was not run: this workspace has no Git repository/remote or registered self-hosted runner. The workflow is configured to call the exact same tested script with the commit SHA.",
 "images":[("powershell-cd-deploy.png", "Actual PowerShell execution of the reusable local continuous-deployment script on Minikube."), ("powershell-cd-config.png", "Actual PowerShell inspection showing the workflow file and the absence of a connected Git remote.")],
 "conclusion":"The deployment automation is exercised successfully against the local cluster, and the GitHub Actions workflow is wired to reuse the tested script. A remote Actions run remains pending until the project is connected to GitHub and a self-hosted runner is registered."
}
]

def make_report(exp):
    path = REPORTS / exp["file"]
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=.7*inch, leftMargin=.7*inch, topMargin=.62*inch, bottomMargin=.76*inch, title=exp["title"], author=NAME, subject="DevOps Lab 2")
    story = []
    story += [P(exp["number"], "Subtitle"), P(exp["title"], "CoverTitle"), P(student_line, "Subtitle")]
    summary = [[P("OBJECTIVE", "Small"), P(exp["objective"], "Body2")], [P("EXECUTION STATUS", "Small"), P(exp["status"], "Body2")]]
    table = Table(summary, colWidths=[1.18*inch, 5.75*inch], hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),PALE),("VALIGN",(0,0),(-1,-1),"TOP"),("BOX",(0,0),(-1,-1),.5,colors.HexColor("#D5DFEA")),("INNERGRID",(0,0),(-1,-1),.35,colors.HexColor("#D5DFEA")),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [table, P("Theory and explanation", "Section"), P(exp["theory"]), P("Required software and tools", "Section")]
    story += bullets(exp["tools"])
    story += [P("Implementation steps", "Section")]
    story += [P(f"<b>{i}.</b> {escape(step)}", "Small") for i, step in enumerate(exp["steps"],1)]
    story += [P("Commands and code", "Section"), code(exp["commands"]), P("Output and observations", "Section")]
    story += [P(exp["output"], "Callout"), P("Execution evidence", "Section")]
    for screenshot, caption in exp["images"]:
        img = Image(str(ROOT / "evidence" / "screenshots" / screenshot))
        maxw, maxh = 6.9*inch, 4.0*inch
        scale = min(maxw/img.imageWidth, maxh/img.imageHeight)
        img.drawWidth, img.drawHeight = img.imageWidth*scale, img.imageHeight*scale
        story += [img, Spacer(1,3), P(escape(caption), "Small"), Spacer(1,4)]
    story += [P("Result and conclusion", "Section"), P(exp["conclusion"])]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Created {path}")

for experiment in experiments:
    make_report(experiment)




