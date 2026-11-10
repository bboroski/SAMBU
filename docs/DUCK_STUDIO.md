# SAMBU Duck Studio

SAMBU Duck Studio is an optional desktop interface for the existing SAMBU Studio static XML inspector. It is built with Python's standard-library Tkinter module and does not add a mandatory runtime dependency.

## Launch

Install SAMBU from the repository, then run:

~~~bash
python -m pip install -e .
sambu-duck-studio
~~~

Tkinter must be present in the Python build. Minimal Linux distributions may require their operating-system Tk package. The existing CLI remains available:

~~~bash
sambu-studio inspect /path/to/module
sambu-studio inspect /path/to/module --format json
~~~

## Screenshots

The images below are captures of the running desktop application using a clearly labelled demo workspace and deterministic sample findings. They are illustrative UI captures, not a claim that a production Magento project has been scanned.

### Project overview

![SAMBU Duck Studio project overview](images/sambu-duck-studio-overview.png)

### XML inspector

![SAMBU Duck Studio XML Inspector](images/sambu-duck-studio-xml-inspector.png)

### Reports and findings

![SAMBU Duck Studio reports](images/sambu-duck-studio-reports.png)

## Safety and scope

- Inspection is local and read-only. The UI does not alter the selected project.
- No Magento runtime, database, RabbitMQ broker, network service, or external credentials are contacted.
- JSON export is a separate, explicit user action and writes only the report path chosen by the user.
- The inspector is not Magento XSD validation, DI compilation, PHP symbol resolution, or production-health verification.
- The GUI is a desktop shell over the existing static inspector, not a full Magento IDE or general-purpose source editor.

## Architecture

The DuckStudioApp imports Tkinter only when the application is instantiated, so summary helpers remain importable and testable in headless CI. XML inspection runs on a worker thread; the result is sent back through a queue and Tk widgets are updated only by the main UI thread. The inspector's existing file-size, UTF-8, DTD/entity, generated-directory and symlink safeguards remain authoritative.

## Troubleshooting

- **Tk support is missing** — install a Python distribution that includes Tk. On Debian/Ubuntu, this is commonly provided by the python3-tk OS package.
- **The file list is empty** — choose a Magento module or project containing one or more supported etc/*.xml files, then run inspection.
- **A warning appears** — read the original diagnostic code and path in Reports & findings. Cross-file references can legitimately be declared by another module not included in the selected folder.
