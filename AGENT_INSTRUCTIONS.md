## Create a New Branch

Always start by creating a new branch for the task:
```bash
git switch -c fix/documents update
```

# Instructions for Agent: Changelog and Task Management

This document outlines the steps to be performed by an agent to update the changelog, migrate roadmap tasks to a 'todo' folder, and archive completed tasks. These instructions are designed to be reproducible in other repositories.

## 1. Update Changelog

The goal is to ensure `CHANGELOG.rst` is current with the git history and correctly formatted.

1.  **Read Current Changelog**:
    *   Read the content of `CHANGELOG.rst` to understand its current state and formatting.
    ```bash
    read_file(absolute_path = "/home/phi/PROJECTS/geometor/model/CHANGELOG.rst")
    ```

2.  **Retrieve Git History**:
    *   Fetch the git log to identify commits that might be missing from the changelog.
    ```bash
    run_shell_command(command = "git log --pretty=format:%h %ad | %s%d [%an]" --date=short", description = "Get the git log to identify missing changelog entries.")
    ```

3.  **Integrate Missing Entries**:
    *   Based on the git log, add new entries to `CHANGELOG.rst`.
    *   Ensure new entries are:
        *   Chronologically ordered by version number (newest first).
        *   Grouped by version.
        *   Contain a date and a brief description (fixed, added, changed).
        *   Follow the existing reStructuredText (`.rst`) formatting conventions.
    *   Use the `replace` tool to insert new sections or update existing ones. Example (adapt `old_string` and `new_string` precisely):
    ```python
    replace(
        file_path = "/home/phi/PROJECTS/geometor/model/CHANGELOG.rst",
        instruction = "Add a new changelog entry for version X.Y.Z detailing changes.",
        old_string = "Existing content before new entry, including surrounding lines.",
        new_string = "New entry content, including surrounding lines for context."
    )
    ```

4.  **Verify Documentation Symlink**:
    *   Confirm that `docsrc/changelog.rst` simply includes the main `CHANGELOG.rst`. If it's not a direct include, an additional update might be needed.
    ```bash
    read_file(absolute_path = "/home/phi/PROJECTS/geometor/model/docsrc/changelog.rst")
    ```

## 2. Update `GEMINI.md` for Architectural Changes

Ensure `GEMINI.md` reflects the current high-level architecture.

1.  **Review `__init__.py`**:
    *   Read `src/<namespace>/<repo_name>/__init__.py` to understand the current implementation of core classes (e.g., `Model` class no longer uses an event system but a synchronous analysis hook).
    ```bash
    read_file(absolute_path = "/home/phi/PROJECTS/geometor/model/src/geometor/model/__init__.py")
    ```

2.  **Update `GEMINI.md`**:
    *   Read `GEMINI.md`.
    ```bash
    read_file(absolute_path = "/home/phi/PROJECTS/geometor/model/GEMINI.md")
    ```
    *   Use the `replace` tool to update relevant sections to match the current architecture.
    ```python
    replace(
        file_path = "/home/phi/PROJECTS/geometor/model/GEMINI.md",
        instruction = "Update description of __init__.py to reflect synchronous analysis hook.",
        old_string = "-   `__init__.py`: Main `Model` class, a `dict` subclass with an event system.",
        new_string = "-   `__init__.py`: Main `Model` class, a `dict` subclass with a synchronous analysis hook."
    )
    ```

## 3. Migrate `ROADMAP.md` Tasks to `todo` and Archive Completed

This process moves active roadmap items to dedicated files in a `todo` directory and archives completed ones.

1.  **Create `todo` Directory**:
    *   Create a new directory named `todo` in the project root.
    ```bash
    run_shell_command(command = "mkdir -p todo", description = "Create a 'todo' directory to store task files.")
    ```

2.  **Read `ROADMAP.md`**:
    *   Read the content of `ROADMAP.md` to identify all planned features, improvements, and known issues.
    ```bash
    read_file(absolute_path = "/home/phi/PROJECTS/geometor/model/ROADMAP.md")
    ```

3.  **Process and Create `todo` Files**:
    *   For each *incomplete* task or feature listed in `ROADMAP.md`:
        *   Extract its objective and strategy.
        *   Create a new Markdown file in the `todo` directory.
        *   Use a numerical prefix for the filename (e.g., `1_task_name.md`), where lower numbers indicate higher priority.
        *   Ensure the content is clean and accurately reflects the task. Example:
    ```python
    write_file(
        file_path = "/home/phi/PROJECTS/geometor/model/todo/1_advanced_geometric_operations.md",
        content = "# 1. Advanced Geometric Operations\n\n-   **Objective:** [Objective text]\n-   **Strategy:** [Strategy text]"
    )
    ```

4.  **Create `docsrc/completed_tasks` Directory**:
    *   Create a dedicated directory within `docsrc` for archiving completed tasks.
    ```bash
    run_shell_command(command = "mkdir -p docsrc/completed_tasks", description = "Create the directory for completed tasks in docsrc.")
    ```

5.  **Archive Completed Tasks**:
    *   For each *completed* task identified in `ROADMAP.md` (and confirmed via `CHANGELOG.rst` or user input):
        *   Extract its original objective and strategy.
        *   Create a new Markdown file in `docsrc/completed_tasks/` (e.g., `1_enhanced_serialization.md`).
        *   Prefix the content with `# Completed:`. Example:
    ```python
    write_file(
        file_path = "/home/phi/PROJECTS/geometor/model/docsrc/completed_tasks/1_enhanced_serialization.md",
        content = "# Completed: Enhanced Serialization\n\n-   **Objective:** [Objective text]\n-   **Strategy:** [Strategy text]"
    )
    ```

6.  **Remove `ROADMAP.md`**:
    *   Once all tasks have been successfully migrated and archived, delete the original `ROADMAP.md` file.
    ```bash
    run_shell_command(command = "rm /home/phi/PROJECTS/geometor/model/ROADMAP.md", description = "Remove the old ROADMAP.md file after migration.")
    ```
