# NUN Mesh integration — SAMBU

SAMBU is the language and developer-tooling layer. It supplies a Python-hosted language, CLI, Tkinter IDE, Duck Studio and declarative workflow descriptions. It is not a mandatory runtime dependency of the embedded C libraries.

## Existing graphical applications

- **SAMBU IDE:** a lightweight Tkinter editor with file operations, syntax checking, F5 execution, output and diagnostics.
- **SAMBU Duck Studio:** a separate Tkinter workspace for local, read-only Magento/Adobe Commerce XML inspection. It uses a worker queue for inspection results and keeps Tk widget updates on the UI thread.
- The screenshot set in docs/DUCK_STUDIO.md is captured from the current application with a labelled demo workspace. The existing screenshot evidence should remain clearly distinguished from synthetic portal illustrations.

## Mesh connections

- **ToolNG:** the Windows application embeds a portable policy/workflow core from this project family. It does not embed the Python interpreter, the language IDE or creative-text modules.
- **ReaperCripple:** SAMBU workflows can describe bounded station recipes, policy inputs and report layouts. A host/fixture adapter must produce its own execution evidence.
- **Klipot:** the portal lists the tools and provides repository navigation. Its labs are simulations, not SAMBU interpreter sessions.

## UI and compatibility

Keep IDE, Duck Studio and the .sambu runtime as separate surfaces with explicit responsibilities. Preserve read-only inspection, source-linked findings and asynchronous worker isolation. UI animation should never obscure diagnostic status or imply that a long-running task has completed.

See [Duck Studio screenshots and architecture](DUCK_STUDIO.md), [ToolNG integration](https://github.com/bboroski/ToolNG/blob/main/docs/ECOSYSTEM_INTEGRATION.md), and the [NUN Mesh protocol](https://github.com/bboroski/Klipot/blob/main/docs/INTEGRATION_PROTOCOL.md).
