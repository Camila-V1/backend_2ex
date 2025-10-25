#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para exportar el schema OpenAPI en formatos legibles por copilots
Genera: JSON, YAML, y Markdown
"""
import os
import sys
import django
import json
import yaml

# Fix para encoding en Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from drf_spectacular.generators import SchemaGenerator


def generate_schema():
    """Genera el schema OpenAPI"""
    print("🔧 Generando schema OpenAPI...")
    generator = SchemaGenerator()
    schema = generator.get_schema(request=None, public=True)
    print(f"✅ Schema generado: {len(schema.get('paths', {}))} rutas")
    return schema


def export_json(schema, filename='API_SCHEMA.json'):
    """Exporta el schema a JSON formateado"""
    print(f"📄 Exportando a JSON: {filename}")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON exportado: {filename}")


def export_yaml(schema, filename='API_SCHEMA.yaml'):
    """Exporta el schema a YAML"""
    print(f"📄 Exportando a YAML: {filename}")
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(schema, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"✅ YAML exportado: {filename}")


def export_markdown(schema, filename='API_SCHEMA.md'):
    """Exporta el schema a Markdown legible"""
    print(f"📄 Exportando a Markdown: {filename}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        info = schema.get('info', {})
        f.write(f"# {info.get('title', 'API Documentation')}\n\n")
        f.write(f"**Versión:** {info.get('version', '1.0.0')}\n\n")
        f.write(f"**Descripción:** {info.get('description', 'API REST')}\n\n")
        
        # Servers
        servers = schema.get('servers', [])
        if servers:
            f.write("## 🌐 Servidores\n\n")
            for server in servers:
                f.write(f"- **{server.get('description', 'Servidor')}:** `{server.get('url', '')}`\n")
            f.write("\n")
        
        # Estadísticas
        paths = schema.get('paths', {})
        total_endpoints = sum(len([m for m in methods.keys() if m in ['get', 'post', 'put', 'patch', 'delete']]) 
                             for methods in paths.values())
        
        f.write("## 📊 Estadísticas\n\n")
        f.write(f"- **Total de Rutas:** {len(paths)}\n")
        f.write(f"- **Total de Endpoints:** {total_endpoints}\n")
        f.write(f"- **Componentes (Schemas):** {len(schema.get('components', {}).get('schemas', {}))}\n\n")
        
        # Organizar por tags
        f.write("## 📑 Tabla de Contenidos\n\n")
        
        tags_dict = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'patch', 'delete']:
                    tags = details.get('tags', ['Sin categoría'])
                    tag = tags[0] if tags else 'Sin categoría'
                    
                    if tag not in tags_dict:
                        tags_dict[tag] = []
                    
                    tags_dict[tag].append({
                        'method': method.upper(),
                        'path': path,
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'operationId': details.get('operationId', ''),
                        'parameters': details.get('parameters', []),
                        'requestBody': details.get('requestBody', {}),
                        'responses': details.get('responses', {}),
                        'security': details.get('security', [])
                    })
        
        # TOC
        for tag in sorted(tags_dict.keys()):
            f.write(f"- [{tag}](#{tag.lower().replace(' ', '-')}) ({len(tags_dict[tag])} endpoints)\n")
        f.write("\n---\n\n")
        
        # Endpoints detallados
        for tag in sorted(tags_dict.keys()):
            f.write(f"## {tag}\n\n")
            
            for endpoint in tags_dict[tag]:
                # Título del endpoint
                method = endpoint['method']
                path = endpoint['path']
                summary = endpoint['summary']
                
                # Badge de método
                method_badges = {
                    'GET': '🔵',
                    'POST': '🟢',
                    'PUT': '🟠',
                    'PATCH': '🟣',
                    'DELETE': '🔴'
                }
                badge = method_badges.get(method, '⚪')
                
                f.write(f"### {badge} {method} `{path}`\n\n")
                
                if summary:
                    f.write(f"**Resumen:** {summary}\n\n")
                
                if endpoint['description']:
                    f.write(f"**Descripción:**\n\n{endpoint['description']}\n\n")
                
                # Operation ID
                if endpoint['operationId']:
                    f.write(f"**Operation ID:** `{endpoint['operationId']}`\n\n")
                
                # Security
                if endpoint['security']:
                    f.write("**Autenticación:** Requerida\n\n")
                    for sec in endpoint['security']:
                        for sec_name, scopes in sec.items():
                            f.write(f"- `{sec_name}`")
                            if scopes:
                                f.write(f": {', '.join(scopes)}")
                            f.write("\n")
                    f.write("\n")
                
                # Parámetros
                if endpoint['parameters']:
                    f.write("**Parámetros:**\n\n")
                    f.write("| Nombre | Ubicación | Tipo | Requerido | Descripción |\n")
                    f.write("|--------|-----------|------|-----------|-------------|\n")
                    
                    for param in endpoint['parameters']:
                        name = param.get('name', '')
                        location = param.get('in', '')
                        required = '✅ Sí' if param.get('required', False) else '❌ No'
                        description = param.get('description', '').replace('\n', ' ')
                        
                        # Tipo del parámetro
                        schema_info = param.get('schema', {})
                        param_type = schema_info.get('type', 'string')
                        if schema_info.get('format'):
                            param_type += f" ({schema_info.get('format')})"
                        
                        f.write(f"| `{name}` | {location} | {param_type} | {required} | {description} |\n")
                    
                    f.write("\n")
                
                # Request Body
                if endpoint['requestBody']:
                    f.write("**Cuerpo de Solicitud:**\n\n")
                    content = endpoint['requestBody'].get('content', {})
                    required = endpoint['requestBody'].get('required', False)
                    
                    if required:
                        f.write("⚠️ **Requerido**\n\n")
                    
                    for content_type, schema_info in content.items():
                        f.write(f"**Content-Type:** `{content_type}`\n\n")
                        
                        # Schema reference
                        schema_ref = schema_info.get('schema', {})
                        if '$ref' in schema_ref:
                            ref_name = schema_ref['$ref'].split('/')[-1]
                            f.write(f"**Schema:** [`{ref_name}`](#schema-{ref_name.lower()})\n\n")
                        elif 'properties' in schema_ref:
                            f.write("**Campos:**\n\n")
                            f.write("```json\n")
                            f.write(json.dumps(schema_ref.get('properties', {}), indent=2))
                            f.write("\n```\n\n")
                
                # Responses
                if endpoint['responses']:
                    f.write("**Respuestas:**\n\n")
                    
                    for status_code, resp_info in sorted(endpoint['responses'].items()):
                        description = resp_info.get('description', 'Sin descripción')
                        f.write(f"**{status_code}** - {description}\n\n")
                        
                        content = resp_info.get('content', {})
                        for content_type, schema_info in content.items():
                            schema_ref = schema_info.get('schema', {})
                            if '$ref' in schema_ref:
                                ref_name = schema_ref['$ref'].split('/')[-1]
                                f.write(f"- Content-Type: `{content_type}`\n")
                                f.write(f"- Schema: [`{ref_name}`](#schema-{ref_name.lower()})\n\n")
                    
                    f.write("\n")
                
                f.write("---\n\n")
        
        # Schemas/Components
        schemas = schema.get('components', {}).get('schemas', {})
        if schemas:
            f.write("## 🗂️ Modelos de Datos (Schemas)\n\n")
            
            for schema_name, schema_def in sorted(schemas.items()):
                f.write(f"### Schema: `{schema_name}`\n\n")
                
                if schema_def.get('description'):
                    f.write(f"{schema_def.get('description')}\n\n")
                
                properties = schema_def.get('properties', {})
                required_fields = schema_def.get('required', [])
                
                if properties:
                    f.write("**Propiedades:**\n\n")
                    f.write("| Campo | Tipo | Requerido | Descripción |\n")
                    f.write("|-------|------|-----------|-------------|\n")
                    
                    for prop_name, prop_def in properties.items():
                        prop_type = prop_def.get('type', 'object')
                        if prop_def.get('format'):
                            prop_type += f" ({prop_def.get('format')})"
                        
                        is_required = '✅ Sí' if prop_name in required_fields else '❌ No'
                        description = prop_def.get('description', '').replace('\n', ' ')
                        
                        # Si es un array, mostrar el tipo de items
                        if prop_type == 'array':
                            items = prop_def.get('items', {})
                            if '$ref' in items:
                                ref_name = items['$ref'].split('/')[-1]
                                prop_type += f"\\<[{ref_name}](#schema-{ref_name.lower()})\\>"
                            elif items.get('type'):
                                prop_type += f"\\<{items.get('type')}\\>"
                        
                        f.write(f"| `{prop_name}` | {prop_type} | {is_required} | {description} |\n")
                    
                    f.write("\n")
                
                f.write("---\n\n")
        
        # Security Schemes
        security_schemes = schema.get('components', {}).get('securitySchemes', {})
        if security_schemes:
            f.write("## 🔒 Esquemas de Seguridad\n\n")
            
            for scheme_name, scheme_def in security_schemes.items():
                f.write(f"### `{scheme_name}`\n\n")
                f.write(f"- **Tipo:** {scheme_def.get('type', 'unknown')}\n")
                
                if scheme_def.get('scheme'):
                    f.write(f"- **Esquema:** {scheme_def.get('scheme')}\n")
                
                if scheme_def.get('bearerFormat'):
                    f.write(f"- **Formato:** {scheme_def.get('bearerFormat')}\n")
                
                if scheme_def.get('description'):
                    f.write(f"- **Descripción:** {scheme_def.get('description')}\n")
                
                f.write("\n")
    
    print(f"✅ Markdown exportado: {filename}")


if __name__ == '__main__':
    try:
        # Generar schema
        schema = generate_schema()
        
        # Exportar a múltiples formatos
        export_json(schema)
        export_yaml(schema)
        export_markdown(schema)
        
        print("\n🎉 ¡Exportación completada!")
        print("\n📄 Archivos generados:")
        print("  - API_SCHEMA.json  (JSON completo - ideal para procesamiento)")
        print("  - API_SCHEMA.yaml  (YAML - fácil de leer)")
        print("  - API_SCHEMA.md    (Markdown - perfecto para copilots)")
        print("\n💡 Estos archivos pueden ser leídos por cualquier copilot/IA")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
