from typing import Any

def resolve_capture_status(facade_manifest: dict | None, prod_manifest: dict | None) -> dict[str, Any]:
    """Resolve the canonical status of a capture from its dual manifests.
    
    Precedence:
    1. Explicit manual facade state ('accepted', 'rejected').
    2. Production manifest success state (True -> 'complete', False -> 'failed').
    3. Production manifest raw status if malformed.
    4. Facade state (normally 'created').
    """
    if not facade_manifest:
        return {'status': 'not_found', 'status_source': 'none'}
        
    facade_status = facade_manifest.get('status', 'created')
    result = {
        'capture_id': facade_manifest.get('capture_id', ''),
        'capture_name': facade_manifest.get('capture_name', ''),
        'status': facade_status,
        'created_at': facade_manifest.get('created_at', ''),
        'workflow_id': facade_manifest.get('workflow_id'),
        'raw_file_rel': facade_manifest.get('raw_file_rel'),
        'tags': facade_manifest.get('tags', []),
        'facade_status': facade_status,
        'production_status': None,
        'status_source': 'facade',
        'success': None
    }
    
    if facade_status in ('accepted', 'rejected'):
        return result
        
    if prod_manifest is not None:
        prod_status = prod_manifest.get('status')
        success = prod_manifest.get('success')
        
        result['production_status'] = prod_status
        result['success'] = success
        
        if success is True:
            result['status'] = 'complete'
            result['status_source'] = 'production'
        elif success is False:
            result['status'] = 'failed'
            result['status_source'] = 'production'
        else:
            # Malformed or contradictory
            result['status'] = prod_status if prod_status else 'unknown'
            result['status_source'] = 'production'
            
    return result
