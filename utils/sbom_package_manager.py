import os
import json
from datetime import datetime, timezone

def _get_main_package_spdx_id(sbom_data):
    """
    (内部ヘルパー関数)
    SBOMデータから 'DESCRIBES' 関係を辿り、
    親となるトップレベルパッケージのSPDXIDを特定する.
    """
    if 'relationships' in sbom_data:
        for rel in sbom_data['relationships']:
            if rel.get('relationshipType') == 'DESCRIBES' and rel.get('spdxElementId') == 'SPDXRef-DOCUMENT':
                return rel.get('relatedSpdxElement')
    return None

def add_missing_packages_and_relationships(base_data, source_data, source_tool_name):
    """
    ベースSBOMに存在しないパッケージと関連するRelationshipをソースSBOMから追加する.
    """
    
    new_packages_added = 0
    new_relationships_added = 0
    
    if 'packages' not in source_data:
        return 0, 0

    # 親となるトップレベルパッケージのSPDXIDを特定する (内部関数を呼び出す)
    main_package_spdx_id = _get_main_package_spdx_id(base_data)
    
    if not main_package_spdx_id:
        print("⚠️ Warning: Could not find the main package ID. Cannot add new relationships.")
    
    base_pkg_names = {pkg.get('name') for pkg in base_data.get('packages', []) if pkg.get('name')}
    
    for source_pkg in source_data.get('packages', []):
        pkg_name = source_pkg.get('name')
        
        if pkg_name and pkg_name not in base_pkg_names:
            
            # 1. パッケージに出典情報を注釈として記録する.
            annotation = {
                "annotationDate": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "annotationType": "OTHER",
                "annotator": "Tool: sbom-merge-script",
                "comment": f"Package added from {source_tool_name}."
            }
            source_pkg.setdefault('annotations', []).append(annotation)

            # 2. SPDX必須項目が欠落している場合、'NOASSERTION'で補完する.
            source_pkg.setdefault('licenseConcluded', 'NOASSERTION')
            source_pkg.setdefault('licenseDeclared', 'NOASSERTION')
            source_pkg.setdefault('copyrightText', 'NOASSERTION')
            
            # 3. packagesリストに新しいパッケージを追加する.
            base_data.setdefault('packages', []).append(source_pkg)
            base_pkg_names.add(pkg_name)
            new_packages_added += 1
            print(f"   Added new package from {source_tool_name}: {pkg_name}")
            
            # 4. 新しく追加したパッケージの親子関係をrelationshipsリストに追加する.
            new_pkg_spdx_id = source_pkg.get('SPDXID')
            if main_package_spdx_id and new_pkg_spdx_id:
                for source_rel in source_data.get('relationships', []):
                    if source_rel.get('relatedSpdxElement') == new_pkg_spdx_id:
                        
                        new_relationship = {
                            'spdxElementId': main_package_spdx_id,
                            'relatedSpdxElement': new_pkg_spdx_id,
                            'relationshipType': source_rel.get('relationshipType', 'CONTAINS'),
                            'comment': f'Relationship added from {source_tool_name}.'
                        }
                        
                        is_duplicate = any(
                            rel.get('spdxElementId') == new_relationship['spdxElementId'] and
                            rel.get('relatedSpdxElement') == new_relationship['relatedSpdxElement'] and
                            rel.get('relationshipType') == new_relationship['relationshipType']
                            for rel in base_data.get('relationships', [])
                        )
                        
                        if not is_duplicate:
                            base_data.setdefault('relationships', []).append(new_relationship)
                            new_relationships_added += 1
                            
    return new_packages_added, new_relationships_added