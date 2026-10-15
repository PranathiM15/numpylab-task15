# NumPy Insight Lab — Task 15

A compact, responsive web application for **NumPy statistical analysis**. Add numerical observations, calculate descriptive statistics, compare mean and median, visualise observations, and flag unusual values using the interquartile range (IQR) rule.

## Task requirements covered

- Numerical datasets: built-in Student Performance and Monthly Sales samples, plus custom input.
- Statistical calculations: mean, median, population standard deviation, minimum, maximum, range, quartiles, and IQR.
- At least three observations are required; the app supports up to 500 values.
- Mean/median comparison with a plain-language interpretation.
- Unusually high/low values flagged using the 1.5 × IQR fence rule.
- Responsive custom UI, deployment configuration (`render.yaml`, `Procfile`), test suite, and rollback runbook.

## Technology

- Python 3.10+ recommended
- NumPy
- Python standard-library HTTP server
- HTML, CSS, and vanilla JavaScript

No Flask, Node.js, database, notebook, frontend package manager, or paid service is needed to run the app locally. NumPy performs the calculations in Python; the browser presents the results.

## Run on Windows using PowerShell (no notebook and no activation required)

1. Install Python from [python.org](https://www.python.org/downloads/) if it is not already installed. During installation, enable **Add Python to PATH**.
2. Extract the ZIP so the `numpylab-task15` folder contains `app.py`, `requirements.txt`, `static`, and the other project files.
3. Open that folder in File Explorer, click the address bar, type `powershell`, and press Enter. Confirm that the terminal is in the project root by running:

   ```powershell
   Get-ChildItem
   ```

4. Create an isolated environment:

   ```powershell
   py -m venv .venv
   ```

   If `py` is not recognised, use `python -m venv .venv` instead.

5. Install the one dependency (activation is deliberately not required, so PowerShell execution-policy errors are avoided):

   ```powershell
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

6. Start the application:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

7. Open **http://127.0.0.1:8000** in your browser. To stop the server, return to the terminal and press **Ctrl+C**.

If you prefer not to create a virtual environment, and NumPy is already installed for your Python interpreter, you can use `python app.py`. A virtual environment is recommended to avoid dependency conflicts.

## Test the project

With the environment created and dependency installed, run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The included tests check calculation results, population standard deviation, outlier detection, and invalid-data handling.

## Try these sample datasets

- **Student performance:** `72, 85, 91, 68, 88, 94, 76, 83, 79, 97, 42`
- **Monthly sales:** `120, 135, 128, 142, 138, 155, 149, 162, 157, 171, 410`
- **Custom sample:** `10, 12, 11, 13, 12, 14, 80`

Select a sample from the dropdown or paste your own values separated by commas, spaces, or new lines. Use at least three numerical values. Click **Run statistical analysis**. Try the custom sample above to see a high-value outlier highlighted.

## Calculation notes

- **Mean:** arithmetic average.
- **Median:** middle value after ordering.
- **Standard deviation:** population standard deviation (`numpy.std`, `ddof=0`), measuring spread around the mean.
- **IQR:** third quartile minus first quartile.
- **Outlier rule:** below Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR. The IQR rule is a screening technique; a flagged value is not automatically an error.

## GitHub upload (PowerShell)

1. Create a new empty public repository at **https://github.com/new**. Suggested name: `numpylab-task15`. Do not tick the options to add a README, `.gitignore`, or licence because this folder already contains project files.
2. In PowerShell, make sure you are inside the extracted `numpylab-task15` folder. Run these commands in order:

   ```powershell
   git init
   git add .
   git status
   git commit -m "Build NumPy statistical analysis web app"
   git branch -M main
   git remote add origin https://github.com/PranathiM15/numpylab-task15.git
   git push -u origin main
   ```

3. Confirm the project files appear at `https://github.com/PranathiM15/numpylab-task15`.

If Git says `remote origin already exists`, run `git remote -v`. If it points to the wrong repository, update it with:

```powershell
git remote set-url origin https://github.com/PranathiM15/numpylab-task15.git
git push -u origin main
```

If Git asks you to configure your identity, set the name/email you use for GitHub:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

Then repeat the commit command. Do not put passwords or access tokens in source files. If GitHub reports that the remote already contains commits, avoid force-pushing; because the repository should be created empty, check that you selected the intended repository and follow Git's suggested safe merge/rebase instructions if needed.

## Optional deployment using Render

The repo contains `render.yaml` and `Procfile` as deployment configuration. For a hosted URL, create a Render account, select **New → Blueprint** or create a Python web service connected to this GitHub repository, then deploy using the included config. The health check is `/api/health`. Hosting plans and interface options may change; review the current platform terms before deploying.

A hosted rollback has not been performed as part of creating this ZIP because no hosting account/service was provided. Follow [`docs/ROLLBACK_EVIDENCE.md`](docs/ROLLBACK_EVIDENCE.md) to deploy, exercise rollback, and record genuine before/after evidence rather than claiming a rollback that did not occur.

## Project layout

```text
numpylab-task15/
├── app.py
├── requirements.txt
├── README.md
├── Procfile
├── render.yaml
├── .env.example
├── .gitignore
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   └── test_analysis.py
└── docs/
    └── ROLLBACK_EVIDENCE.md
```

## Verification record (package build)

The following checks were run while preparing this project package:

- Environment: Python 3.13.5 and NumPy 2.3.5.
- Automated unit tests: **6 passed** (`python -m unittest discover -s tests -v`).
- Syntax check: `app.py` and the test module compiled successfully.
- HTTP smoke test: `/`, `/static/style.css`, `/static/app.js`, `/api/health`, and `/api/samples` returned HTTP 200.
- API check: a seven-value custom dataset returned mean `21.7143`, median `12`, and correctly flagged `80` as a high IQR outlier. A two-value dataset returned HTTP 400 with a helpful validation message.
- Sample check: Student Performance flags `42` as a low outlier; Monthly Sales flags `410` as a high outlier.

Repeat the test commands on your own computer and use your own terminal/browser screenshots as assignment evidence. The build checks do **not** claim that a public deployment or hosted rollback has taken place. Keep screenshots of a successful local app, GitHub repository, deployment, and any rollback exercise in your submission materials.
