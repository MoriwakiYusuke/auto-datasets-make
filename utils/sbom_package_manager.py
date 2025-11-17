import os
import json
from datetime import datetime, timezone
# ★★★ 1. `get_purl_from_package` をインポート ★★★
from .sbom_utils import get_purl_from_package

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
    (PURLベースで重複チェックを行う)
    """
    
    new_packages_added = 0
    new_relationships_added = 0
    
    if 'packages' not in source_data:
        return 0, 0

    main_package_spdx_id = _get_main_package_spdx_id(base_data)
    
    if not main_package_spdx_id:
        print("⚠️ Warning: Could not find the main package ID. Cannot add new relationships.")
    
    # ★★★ 2. `base_pkg_names` の代わりに `base_pkg_purls` を作成 ★★★
    base_pkg_purls = set()
    for pkg in base_data.get('packages', []):
        purl = get_purl_from_package(pkg)
        if purl:
            base_pkg_purls.add(purl)
    
    for source_pkg in source_data.get('packages', []):
        # ★★★ 3. `name` ではなく `purl` で判定する ★★★
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
            base_pkg_purls.add(source_purl) # 追加したpurlをセットにも追加
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