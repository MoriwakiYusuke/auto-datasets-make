import os
import json
from datetime import datetime, timezone
from .sbom_utils import get_purl_from_package

def _get_main_package_spdx_id(sbom_data):
    """
    (内部ヘルパー関数) 親となるトップレベルパッケージのSPDXIDを特定する.
    """
    if 'relationships' in sbom_data:
        for rel in sbom_data['relationships']:
            if rel.get('relationshipType') == 'DESCRIBES' and rel.get('spdxElementId') == 'SPDXRef-DOCUMENT':
                return rel.get('relatedSpdxElement')
    return None

def merge_package_info(base_pkg, source_pkg, fields_to_check, source_tool_name):
    """
    既存パッケージの情報をソースからマージする.
    - 補完可能な場合は値を更新し、最後にまとめて注釈を記録する.
    - 値が競合する場合（BaseとSourceで異なる値を持つ場合）は更新せず、その都度警告注釈を記録する.
    
    Returns:
        dict: 更新されたフィールドとその状態のサマリー ({'licenseConcluded': 'updated', ...})
    """
    results = {}
    updated_fields = [] # ★追加: 更新されたフィールドを一時保存するリスト
    
    # 無効とみなす値のリスト
    invalid_values = [None, "", "NOASSERTION", "NONE"]
    
    for field in fields_to_check:
        base_val = base_pkg.get(field)
        source_val = source_pkg.get(field)
        
        # ソースに有効な値がない場合は何もしない
        if source_val in invalid_values:
            continue

        # ケース1: 補完 (Baseが空またはNOASSERTION)
        if base_val in invalid_values:
            base_pkg[field] = source_val
            results[field] = 'updated'
            updated_fields.append(field) # ★変更: ここではリストに追加するだけ

        # ケース2: 競合 (BaseとSourceが異なり、かつBaseも有効な値を持つ)
        elif base_val != source_val:
            results[field] = 'conflict'
            
            # 警告の注釈を追加 (これは個別の警告なので、都度追加するのが適切)
            annotation = {
                "annotationDate": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "annotationType": "OTHER", 
                "annotator": "Tool: sbom-merge-script",
                "comment": f"WARNING: Conflict in field '{field}'. Kept base value '{base_val}'. Ignored source value '{source_val}' from {source_tool_name}."
            }
            base_pkg.setdefault('annotations', []).append(annotation)

    # ★追加: ループ終了後、更新があった場合のみまとめて注釈を追加
    if updated_fields:
        annotation = {
            "annotationDate": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "annotationType": "OTHER",
            "annotator": "Tool: sbom-merge-script",
            # フィールド名をカンマ区切りで結合してコメントにする
            "comment": f"Fields ({', '.join(updated_fields)}) were supplemented by {source_tool_name}."
        }
        base_pkg.setdefault('annotations', []).append(annotation)

    return results

def add_missing_packages_and_relationships(base_data, source_data, source_tool_name):
    """
    ベースSBOMに存在しないパッケージと関連するRelationshipをソースSBOMから追加する.
    (PURLベースで重複チェックを行う)
    """
    
    new_packages_added = 0
    new_relationships_added = 0
    
    if 'packages' not in source_data:
        return 0, 0

    main_package_spdx_id = _get_main_package_spdx_id(base_data)
    
    if not main_package_spdx_id:
        print("⚠️ Warning: Could not find the main package ID. Cannot add new relationships.")
    
    base_pkg_purls = set()
    for pkg in base_data.get('packages', []):
        purl = get_purl_from_package(pkg)
        if purl:
            base_pkg_purls.add(purl)
    
    for source_pkg in source_data.get('packages', []):
        source_purl = get_purl_from_package(source_pkg)
        
        # PURLが存在し、かつそれがベースSBOMに存在しない場合のみ追加処理を行う.
        if source_purl and source_purl not in base_pkg_purls:
            
            # 1. パッケージに出典情報を注釈として記録する.
            annotation = {
                "annotationDate": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "annotationType": "OTHER",
                "annotator": "Tool: sbom-merge-script",
                "comment": f"Package (purl: {source_purl}) added from {source_tool_name}."
            }
            source_pkg.setdefault('annotations', []).append(annotation)

            # 2. SPDX必須項目が欠落している場合、'NOASSERTION'で補完する.
            source_pkg.setdefault('licenseConcluded', 'NOASSERTION')
            source_pkg.setdefault('licenseDeclared', 'NOASSERTION')
            source_pkg.setdefault('copyrightText', 'NOASSERTION')
            
            # 3. packagesリストに新しいパッケージを追加する.
            base_data.setdefault('packages', []).append(source_pkg)
            base_pkg_purls.add(source_purl)
            new_packages_added += 1
            print(f"   Added new package from {source_tool_name}: {source_pkg.get('name')} ({source_purl})")
            
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