# Rollback plan and evidence

## What this project includes

- `render.yaml` defines a repeatable Render web-service build, start command, and `/api/health` health check.
- `Procfile` defines the same start command for compatible Python hosting services.
- `tests/test_analysis.py` checks core statistics, population standard deviation, IQR outlier detection, and invalid input handling.

## Reproducible pre-deployment check

Run these commands from the project root in PowerShell or a terminal:

```text
python -m unittest discover -s tests -v
python app.py
```

With the server running, open `http://127.0.0.1:8000/api/health`. A healthy response includes `"status": "ok"` and the installed NumPy version. The app can be stopped with `Ctrl+C`.

## Deployment rollback procedure (Render)

1. Push a tested version to the connected public GitHub repository and deploy it through the Render service created from `render.yaml`.
2. Save the service URL, deployment timestamp, Git commit, and a screenshot of the working app and `/api/health` endpoint as the **pre-change evidence**.
3. If a later deployment fails, open the Render service's **Deploys** page, choose a recent successful deployment, and click **Rollback** to restore it. If instant rollback is not available for the service/plan, revert the faulty commit in Git and redeploy the previous known-good commit.
4. After rollback, revisit the app and `/api/health`, rerun the test suite, and save screenshots/logs as **post-rollback evidence**. Record the failed commit, restored commit, timestamps, and verification results below.

## Evidence status

No hosted service or Render account was provided with this task, so a real production deployment/rollback has **not** been claimed or fabricated. The repository contains deployment configuration and the above rollback runbook. The package build was locally verified (six unit tests passed, static/API smoke checks returned HTTP 200, and the health endpoint responded). Add actual before/after screenshots and deployment IDs after performing the rollback on your own service. Local verification is recorded in the project's README after the test run used to prepare this package.

| Evidence field | Fill in after hosting setup |
| --- | --- |
| Public deployment URL | Pending deployment |
| Known-good commit / deployment ID | Pending deployment |
| Failed commit / deployment ID | Pending rollback exercise |
| Restored commit / deployment ID | Pending rollback exercise |
| Post-rollback health endpoint | Pending verification |
| Screenshot filenames | Add to this folder after execution |
