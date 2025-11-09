import os
import csv

# ★★★ 1. CSVヘッダーに 'merge_annotations_added' を追加 ★★★
# これが、全スクリプトが「出典として追加した注釈の総数」を記録する共通の列となります.
CSV_FIELDNAMES = [
    'repository', 'source_tool',
    'licenses_updated', 'copyrights_updated', 'comments_updated',
    'suppliers_updated', 'originators_updated', 'source_infos_added', 'external_refs_added',
    'purposes_updated', 'annotations_added', # (Trivyが元々持つ注釈の数)
    'file_types_added',
    'merge_annotations_added', # ★★★ この行を追加 ★★★
    'new_packages_added', 'new_relationships_added', 'creators_added',
    'total_changes'
]

def create_summary_dict(repo_name, source_tool, counts):
    """
    カウント結果の辞書を受け取り、CSV_FIELDNAMESに基づいた
    汎用的なサマリー辞書を作成して返す.
    """
    summary = {field: 0 for field in CSV_FIELDNAMES}
    summary['repository'] = repo_name
    summary['source_tool'] = source_tool
    summary.update(counts)
    return summary

def write_summary_to_csv(all_changes_data, csv_output_path):
    """
    変更サマリーの辞書リストを受け取り、指定されたCSVファイルに追記する.
    """
    if not all_changes_data:
        print("   No changes to write to CSV.")
        return

    file_exists = os.path.isfile(csv_output_path)
    
    print(f"\nWriting/Appending merge summary to '{csv_output_path}'...")
    try:
        with open(csv_output_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerows(all_changes_data)
        print("✅ CSV summary saved successfully.")
    except Exception as e:
        print(f"❌ Error writing CSV file: {e}")