# Guild Electrical AI | 0.0.1 development prototype
Windows desktop source project, not an installer or production estimator.

## Windows setup
Install Python 3.12 (64-bit). Extract the archive to a writable local folder. Open PowerShell in that folder and run `powershell -ExecutionPolicy RemoteSigned -File .\setup.ps1` (subject to company IT policy). Double-click run.bat to launch. Open a new empty project folder, import a PDF, select a page, right-click to add a typed count, and use the buttons to delete or export. Scroll to zoom and drag to pan. Exports are under the project's exports folder. Counts CSV opens in Excel.

## Codex
Open this folder as a Codex workspace. Ask it to read AGENTS.md and documentation, run tests, then implement the next gate. Use Git locally and do not commit customer drawings or credentials. Install the separate developer Skill in ChatGPT if desired; direct local app integration is not needed for this version.

## Status
Implemented: original copy and SHA256 deduplication, individual PDF pages, provisional drawing number detection, SQLite project persistence, manual count marks, standard editable PDF circle annotations, CSV counts, draft Qt interface. Core test covers two pages (0 and 90 degree rotation), duplicate import, source integrity, add/delete, export and reopen. GUI has not been executed in this environment (PySide6 unavailable); Windows setup and GUI need testing. No AI detection, rule extraction, routing, scale calibration, revision management, xlsx export, or MCP integration yet. No Bluebeam testing. Prototype uses PyMuPDF and PySide6; review licenses before proprietary distribution. No cloud transfer included.
