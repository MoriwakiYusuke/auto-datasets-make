# SBOMデータセット自動生成ツール

このプロジェクトは、指定されたGitHubリポジトリのリストから、リッチなSBOM（Software Bill of Materials）データセットを自動的に生成するためのツールです。複数のツールとAPIを活用して、SBOM情報を収集、結合、補強します。

## 主な機能

- **リポジトリの自動クローン:** `url_list.txt`に記載されたURLのリストからGitリポジトリをクローンします。
- **マルチソースでのSBOM生成:** 以下のソースを利用してSBOMを生成します:
    - [Microsoft SBOM Tool](https://github.com/microsoft/sbom-tool)
    - [Syft](https://github.com/anchore/syft)
    - [Trivy](https://github.com/aquasecurity/trivy)
    - GitHub Dependency Graph API
- **SBOMの統合と拡充:** `sbom-tool`の出力をベースとして、他のソース（Syft, Trivy, GitHub API）からの情報（ライセンス、著作権、パッケージの依存関係など）を統合し、より完全なSBOMを生成します。

## ディレクトリ構成

- **`cloned_repositories/`**: `url_list.txt`からクローンされたGitリポジトリが保存されます。
- **`generated_sboms/`**: 生成されたSBOMが格納されます。各リポジトリは独自のサブディレクトリを持ち、その中には以下が含まれます:
    - `source/`: 各ツールから出力された生のSBOMファイル。
    - `combined_sbom.json`: 最終的に統合・拡充されたSBOMファイル。
- **`url_list.txt`**: 処理対象となるGitリポジトリのURLリスト。
- **`main.ipynb`**: クローン、生成、統合の全ワークフローを含むJupyter Notebook。

## 使い方

### 事前準備

以下のツールがインストールされ、PATHが通っていることを確認してください:

- Python 3
- Git
- [sbom-tool](https://github.com/microsoft/sbom-tool)
- [Syft](https://github.com/anchore/syft)
- [Trivy](https://github.com/aquasecurity/trivy)
- Jupyter Notebook または JupyterLab

### 手順

1.  **URLリストの編集:**
    `url_list.txt`に、処理したいGitHubリポジトリのURLを1行に1つずつ追加します。

    ```
    https://github.com/owner/repo1.git
    https://github.com/owner/repo2.git
    ```

2.  **Notebookの実行:**
    `main.ipynb`をJupyter NotebookまたはJupyterLabで開き、セルを上から順に実行します。

    ノートブックは以下のワークフローを実行します:
    1.  リポジトリをクローンします。
    2.  `sbom-tool`を使用してベースとなるSBOMを生成します。
    3.  `syft`を使用して依存関係のSBOMを生成します。
    4.  GitHub APIからSBOMを取得します。
    5.  `trivy`を使用してファイルシステムのSBOMを生成します。
    6.  `sbom-tool`の出力をコピーして`combined_sbom.json`を作成します。
    7.  `combined_sbom.json`にGitHub API、`syft`、`trivy`の情報を順次統合します。

3.  **出力の確認:**
    処理が完了すると、最終的に拡充されたSBOMが`generated_sboms/[リポジトリ名]/`ディレクトリに`combined_sbom.json`として保存されます。