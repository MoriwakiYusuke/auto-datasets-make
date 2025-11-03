import os
import csv

# 共通のヘッダーリスト (全てのスクリプトでこれを参照する)
CSV_FIELDNAMES = [
    'repository', 'source_tool',
    'licenses_updated', 'copyrights_updated', 'comments_updated',
    'suppliers_updated', 'originators_updated', 'source_infos_added', 'external_refs_added',
    'purposes_updated', 'annotations_added', 'file_types_added',
    'new_packages_added', 'new_relationships_added', 'creators_added',
    'total_changes'
]

def create_summary_dict(repo_name, source_tool, counts):
    """
    カウント結果の辞書を受け取り、CSV_FIELDNAMESに基づいた
    汎用的なサマリー辞書を作成して返す.
    """
    # まず、全てのキーを持つ辞書をデフォルト値0で初期化する
    summary = {field: 0 for field in CSV_FIELDNAMES}
    
    # 共通のキーを更新
    summary['repository'] = repo_name
    summary['source_tool'] = source_tool
    
    # counts辞書（例: {'suppliers_updated': 5, ...}）の内容で上書きする
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
            # ヘッダーはライブラリ内の定数を参照する
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            
            if not file_exists:
                writer.writeheader()
                
            writer.writerows(all_changes_data)
        print("✅ CSV summary saved successfully.")
    except Exception as e:
        print(f"❌ Error writing CSV file: {e}")