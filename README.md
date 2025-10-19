# SBOM Dataset Auto Generator

This project is a tool to automatically generate a rich Software Bill of Materials (SBOM) dataset from a list of specified GitHub repositories. It utilizes multiple tools and APIs to gather, combine, and supplement SBOM information.

## Features

- **Automatic Repository Cloning:** Clones Git repositories from a list of URLs provided in `url_list.txt`.
- **Multi-Source SBOM Generation:** Generates SBOMs using the following sources:
    - [Microsoft's SBOM Tool](https://github.com/microsoft/sbom-tool)
    - [Syft](https://github.com/anchore/syft)
    - GitHub Dependency Graph API
- **SBOM Enrichment:** Combines the generated SBOMs, using the output from `sbom-tool` as a base and enriching it with data (like license and copyright information) from other sources.

## Directory Structure

- **`cloned_repositories/`**: Stores the Git repositories cloned from the URLs in `url_list.txt`.
- **`generated_sboms/`**: Contains the generated SBOMs. Each repository has its own subdirectory, which includes:
    - `source/`: Raw SBOM files from each tool.
    - `combined_sbom.json`: The final, enriched SBOM file.
- **`url_list.txt`**: A text file containing the list of Git repository URLs to be processed.
- **`main.ipynb`**: A Jupyter Notebook that contains the entire workflow for cloning, generation, and enrichment.

## How to Use

### Prerequisites

Ensure you have the following tools installed and accessible in your PATH:

- Python 3
- Git
- [sbom-tool](https://github.com/microsoft/sbom-tool)
- [Syft](https://github.com/anchore/syft)
- Jupyter Notebook or JupyterLab

### Steps

1.  **Edit the URL List:**
    Add the GitHub repository URLs you want to process to `url_list.txt`, with one URL per line.

    ```
    https://github.com/owner/repo1.git
    https://github.com/owner/repo2.git
    ```

2.  **Run the Notebook:**
    Open `main.ipynb` in Jupyter Notebook or JupyterLab and run the cells in order from top to bottom.

    The notebook will execute the following workflow:
    1.  Clone repositories.
    2.  Generate SBOMs using `sbom-tool`.
    3.  Generate SBOMs using `syft`.
    4.  Fetch SBOMs from the GitHub API.
    5.  Create a base `combined_sbom.json` from the `sbom-tool` output.
    6.  Supplement `combined_sbom.json` with information from the GitHub API output.

3.  **Check the Output:**
    Once the process is complete, you can find the final enriched SBOMs in the `generated_sboms/[repository_name]/` directories.
