import os
import json

def get_purl_from_package(pkg):
    """パッケージ情報からpurl（Package URL）を抽出する."""
    if 'externalRefs' in pkg:
        for ref in pkg['externalRefs']:
            if ref.get('referenceType') == 'purl':
                return ref.get('referenceLocator')
    return None