# MCL MCL Workbench

MCL MCL Workbench is an optional Tkinter desktop interface for MCL Studio's local, read-only Magento / Adobe Commerce XML inspector. It provides a guided workspace for inspecting configuration files and reviewing source-linked findings. It complements the `mcl-studio` command-line tool; it is separate from the `.mcl` language editor.

## Launch

Install MCL from the repository and start the desktop application:

~~~bash
python -m pip install -e .
python -m mcl_studio.workbench_gui
~~~

The Python build must include Tk support. Minimal Linux distributions may require the operating-system Tk package (commonly `python3-tk` on Debian/Ubuntu).

The CLI remains available for terminal and automation workflows:

~~~bash
mcl-studio inspect /path/to/module
mcl-studio inspect /path/to/module --format json
~~~

## Current application screenshots

The following images are **screenshots captured from the current, running MCL MCL Workbench application**. They show the present Tkinter layout and navigation. Each view is captured at **1280 × 818 pixels** and displayed at its native proportions. For a reproducible capture, the application was opened with a local workspace explicitly labelled **DEMO WORKSPACE** and deterministic example XML findings. The interface is real; the example project and its diagnostics are illustrative and must not be interpreted as an inspection of a production Magento installation.

### 1. Overview

The overview brings the selected workspace, inspection totals, configuration inventory and high-level workspace status into one screen.

<div align="center">
<img src="images/workbench-studio-hq/overview-00.webp" width="25%" alt="MCL MCL Workbench Overview screenshot, upper-left segment" /><img src="images/workbench-studio-hq/overview-01.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/overview-02.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/overview-03.webp" width="25%" alt="" />
<br />
<img src="images/workbench-studio-hq/overview-10.webp" width="25%" alt="Overview screenshot, lower-left segment" /><img src="images/workbench-studio-hq/overview-11.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/overview-12.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/overview-13.webp" width="25%" alt="" />
</div>

### 2. XML Inspector

The inspector presents supported XML files and the structured configuration records extracted from the local workspace. Findings retain their source paths so the reviewer can return to the originating file.

<div align="center">
<img src="images/workbench-studio-hq/xml-inspector-00.webp" width="25%" alt="MCL MCL Workbench XML Inspector screenshot, upper-left segment" /><img src="images/workbench-studio-hq/xml-inspector-01.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/xml-inspector-02.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/xml-inspector-03.webp" width="25%" alt="" />
<br />
<img src="images/workbench-studio-hq/xml-inspector-10.webp" width="25%" alt="XML Inspector screenshot, lower-left segment" /><img src="images/workbench-studio-hq/xml-inspector-11.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/xml-inspector-12.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/xml-inspector-13.webp" width="25%" alt="" />
</div>

### 3. Reports & findings

The report view consolidates the review summary and diagnostic messages. Original finding severity, code, source path and message remain visible for follow-up.

<div align="center">
<img src="images/workbench-studio-hq/reports-findings-00.webp" width="25%" alt="MCL MCL Workbench Reports and findings screenshot, upper-left segment" /><img src="images/workbench-studio-hq/reports-findings-01.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/reports-findings-02.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/reports-findings-03.webp" width="25%" alt="" />
<br />
<img src="images/workbench-studio-hq/reports-findings-10.webp" width="25%" alt="Reports and findings screenshot, lower-left segment" /><img src="images/workbench-studio-hq/reports-findings-11.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/reports-findings-12.webp" width="25%" alt="" /><img src="images/workbench-studio-hq/reports-findings-13.webp" width="25%" alt="" />
</div>

## Safety and scope

- Inspection is local and read-only. The UI does not modify the selected project.
- The inspector does not start Magento, contact a Magento runtime, database, RabbitMQ broker or other network service, or use external credentials.
- JSON export is a separate, explicit user action and writes only to the destination selected by the user.
- The tool is a static XML inspection aid. It is not Magento XSD validation, dependency-injection compilation, PHP symbol resolution or a production-health verification system.
- MCL Workbench is a desktop inspection shell over the existing inspector, not a full Magento IDE or general-purpose source editor.
- Demo screenshots show synthetic workspace data only; they are not evidence about a user's own project.

## Architecture

The `MclWorkbenchApp` imports Tkinter when the application is instantiated, so summary helpers remain importable and testable in headless CI. XML inspection runs on a worker thread and sends its result through a queue; Tk widgets are updated on the main UI thread. The inspector's file-size, UTF-8, DTD/entity, generated-directory and symlink safeguards remain authoritative.

## Troubleshooting

- **Tk support is missing** — install a Python distribution that includes Tk. On Debian/Ubuntu, install the `python3-tk` package.
- **The file list is empty** — choose a Magento module or project containing supported `etc/*.xml` files, then run inspection.
- **A warning appears** — review its original diagnostic code and source path in Reports & findings. Cross-file references may legitimately be declared by another module outside the selected folder.
- **The window does not launch** — verify that the editable install completed and that `python -m mcl_studio.workbench_gui` is executed from the intended Python environment.
