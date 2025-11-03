import os
import json

# SPDXドキュメントのトップレベルキーの標準的な順序を定義する
KEY_ORDER = [
    "SPDXID", "spdxVersion", "creationInfo", "name", "dataLicense", 
    "documentNamespace", "comment", "documentDescribes", "externalDocumentRefs", 
    "packages", "files", "relationships"
]

def save_sbom_json(sbom_data, file_path):
    """
    SBOMデータを、定義されたキーの順序で並び替えた上で、
    インデント付きのJSONファイルとして保存する.
    
    Args:
        sbom_data (dict): 保存するSBOMデータ.
        file_path (str): 保存先のファイルパス.
    """
    try:
        # 1. KEY_ORDERに基づいてキーを並び替える
        ordered_data = {key: sbom_data[key] for key in KEY_ORDER if key in sbom_data}
        # 2. KEY_ORDERにないカスタムキーなどを末尾に追加する
        ordered_data.update({key: value for key, value in sbom_data.items() if key not in ordered_data})

        # 3. 整形してファイルに書き出す
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ordered_data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Successfully saved and reordered '{os.path.basename(file_path)}'.")
        
    except Exception as e:
        print(f"❌ Error saving JSON file to {file_path}: {e}")