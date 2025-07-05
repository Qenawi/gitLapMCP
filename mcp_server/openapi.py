from django.http import JsonResponse
from jsonrpc.site import jsonrpc_site


def openapi_schema(request):
    desc = jsonrpc_site.service_desc()
    paths = {}
    for proc in desc.get('procs', []):
        name = proc.get('name')
        params = proc.get('params', [])
        param_props = {}
        required = []
        for p in params:
            param_props[p['name']] = {'type': 'string'}
            required.append(p['name'])
        request_schema = {
            'type': 'object',
            'properties': {
                'jsonrpc': {'type': 'string', 'enum': ['2.0']},
                'method': {'type': 'string', 'enum': [name]},
                'params': {
                    'type': 'object',
                    'properties': param_props,
                    'required': required,
                },
                'id': {'type': 'integer'},
            },
            'required': ['jsonrpc', 'method', 'id'],
        }
        paths[f'/{name}'] = {
            'post': {
                'summary': proc.get('summary') or '',
                'requestBody': {
                    'content': {
                        'application/json': {'schema': request_schema}
                    }
                },
                'responses': {
                    '200': {'description': 'JSON-RPC response'}
                },
            }
        }
    schema = {
        'openapi': '3.0.0',
        'info': {
            'title': desc.get('name', 'GitLab MCP'),
            'version': desc.get('version', '1.0'),
        },
        'paths': paths,
    }
    return JsonResponse(schema)
