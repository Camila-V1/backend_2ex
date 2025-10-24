#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para generar el schema OpenAPI en PDF extendido
Uso: python generate_schema_pdf.py
"""
import os
import sys
import django
import json
from io import BytesIO

# Fix para encoding en Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.core.management import call_command
from drf_spectacular.generators import SchemaGenerator


def generate_openapi_schema():
    """Genera el schema OpenAPI usando drf-spectacular"""
    print("🔧 Generando schema OpenAPI...")
    generator = SchemaGenerator()
    schema = generator.get_schema(request=None, public=True)
    print(f"✅ Schema generado: {len(schema.get('paths', {}))} endpoints")
    return schema


def create_pdf_schema(schema, output_filename='API_SCHEMA.pdf'):
    """Genera un PDF completo del schema OpenAPI"""
    print(f"📄 Generando PDF: {output_filename}...")
    
    # Configuración del documento
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para títulos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para endpoints
    endpoint_style = ParagraphStyle(
        'EndpointStyle',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#0d47a1'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para método HTTP
    method_style = ParagraphStyle(
        'MethodStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para descripciones
    desc_style = ParagraphStyle(
        'DescStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#424242'),
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )
    
    # Estilo para código
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontSize=9,
        textColor=colors.HexColor('#c7254e'),
        backColor=colors.HexColor('#f9f2f4'),
        borderPadding=5,
        fontName='Courier'
    )
    
    # Contenido del PDF
    story = []
    
    # === PORTADA ===
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("SmartSales365 API", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Documentación Técnica OpenAPI", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Información del proyecto
    info = schema.get('info', {})
    story.append(Paragraph(f"<b>Versión:</b> {info.get('version', '1.0.0')}", desc_style))
    story.append(Paragraph(f"<b>Descripción:</b> {info.get('description', 'API de E-commerce')}", desc_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Estadísticas
    paths = schema.get('paths', {})
    total_endpoints = sum(len(methods) for methods in paths.values())
    
    stats_data = [
        ['Métrica', 'Valor'],
        ['Total de Endpoints', str(total_endpoints)],
        ['Total de Rutas', str(len(paths))],
        ['Componentes', str(len(schema.get('components', {}).get('schemas', {})))],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(stats_table)
    story.append(PageBreak())
    
    # === TABLA DE CONTENIDOS ===
    story.append(Paragraph("Tabla de Contenidos", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Organizar endpoints por categoría
    categories = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'patch', 'delete']:
                tags = details.get('tags', ['Sin categoría'])
                tag = tags[0] if tags else 'Sin categoría'
                
                if tag not in categories:
                    categories[tag] = []
                
                categories[tag].append({
                    'path': path,
                    'method': method.upper(),
                    'summary': details.get('summary', 'Sin descripción'),
                    'description': details.get('description', ''),
                    'parameters': details.get('parameters', []),
                    'requestBody': details.get('requestBody', {}),
                    'responses': details.get('responses', {}),
                })
    
    # Generar tabla de contenidos
    toc_data = [['Categoría', 'Endpoints']]
    for category, endpoints in sorted(categories.items()):
        toc_data.append([category, str(len(endpoints))])
    
    toc_table = Table(toc_data, colWidths=[3*inch, 2*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(toc_table)
    story.append(PageBreak())
    
    # === ENDPOINTS DETALLADOS ===
    story.append(Paragraph("Endpoints Detallados", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Colores para métodos HTTP
    method_colors = {
        'GET': colors.HexColor('#61affe'),
        'POST': colors.HexColor('#49cc90'),
        'PUT': colors.HexColor('#fca130'),
        'PATCH': colors.HexColor('#50e3c2'),
        'DELETE': colors.HexColor('#f93e3e'),
    }
    
    for category, endpoints in sorted(categories.items()):
        # Título de categoría
        story.append(Paragraph(f"📦 {category}", subtitle_style))
        story.append(Spacer(1, 0.1*inch))
        
        for endpoint in endpoints:
            endpoint_content = []
            
            # Método y ruta
            method = endpoint['method']
            path = endpoint['path']
            
            # Tabla de método
            method_table = Table(
                [[Paragraph(method, method_style), path]],
                colWidths=[0.8*inch, 5*inch]
            )
            method_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), method_colors.get(method, colors.grey)),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (1, 0), (1, 0), 'Courier-Bold'),
                ('FONTSIZE', (1, 0), (1, 0), 11),
                ('LEFTPADDING', (1, 0), (1, 0), 10),
            ]))
            
            endpoint_content.append(method_table)
            endpoint_content.append(Spacer(1, 0.1*inch))
            
            # Resumen
            if endpoint['summary']:
                endpoint_content.append(Paragraph(f"<b>Resumen:</b> {endpoint['summary']}", desc_style))
            
            # Descripción
            if endpoint['description']:
                desc_text = endpoint['description'].replace('\n', '<br/>')
                endpoint_content.append(Paragraph(f"<b>Descripción:</b> {desc_text}", desc_style))
            
            # Parámetros
            if endpoint['parameters']:
                endpoint_content.append(Paragraph("<b>Parámetros:</b>", desc_style))
                
                param_data = [['Nombre', 'Tipo', 'Requerido', 'Descripción']]
                for param in endpoint['parameters']:
                    param_data.append([
                        param.get('name', ''),
                        param.get('in', ''),
                        'Sí' if param.get('required', False) else 'No',
                        param.get('description', '')[:40] + '...' if len(param.get('description', '')) > 40 else param.get('description', '')
                    ])
                
                param_table = Table(param_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 2.5*inch])
                param_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0d47a1')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                endpoint_content.append(param_table)
                endpoint_content.append(Spacer(1, 0.1*inch))
            
            # Request Body
            if endpoint['requestBody']:
                endpoint_content.append(Paragraph("<b>Cuerpo de Solicitud:</b>", desc_style))
                content = endpoint['requestBody'].get('content', {})
                
                for content_type, schema_info in content.items():
                    endpoint_content.append(Paragraph(f"Content-Type: <font color='#c7254e'>{content_type}</font>", code_style))
                
                endpoint_content.append(Spacer(1, 0.1*inch))
            
            # Responses
            if endpoint['responses']:
                endpoint_content.append(Paragraph("<b>Respuestas:</b>", desc_style))
                
                resp_data = [['Código', 'Descripción']]
                for status_code, resp_info in endpoint['responses'].items():
                    desc = resp_info.get('description', 'Sin descripción')
                    resp_data.append([status_code, desc])
                
                resp_table = Table(resp_data, colWidths=[1*inch, 4.5*inch])
                resp_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f5e9')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                endpoint_content.append(resp_table)
            
            # Agregar separador
            endpoint_content.append(Spacer(1, 0.2*inch))
            
            # Mantener endpoint junto
            story.append(KeepTogether(endpoint_content))
        
        # Separador de categoría
        story.append(PageBreak())
    
    # === COMPONENTES (SCHEMAS) ===
    schemas = schema.get('components', {}).get('schemas', {})
    if schemas:
        story.append(Paragraph("Modelos de Datos (Schemas)", subtitle_style))
        story.append(Spacer(1, 0.2*inch))
        
        for schema_name, schema_def in sorted(schemas.items())[:20]:  # Limitar a 20 schemas
            story.append(Paragraph(f"🔹 {schema_name}", endpoint_style))
            
            properties = schema_def.get('properties', {})
            if properties:
                prop_data = [['Campo', 'Tipo', 'Descripción']]
                
                for prop_name, prop_def in properties.items():
                    prop_type = prop_def.get('type', 'object')
                    prop_desc = prop_def.get('description', '')[:50] + '...' if len(prop_def.get('description', '')) > 50 else prop_def.get('description', '')
                    
                    prop_data.append([prop_name, prop_type, prop_desc])
                
                prop_table = Table(prop_data, colWidths=[1.5*inch, 1*inch, 3*inch])
                prop_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff3e0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#e65100')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(prop_table)
                story.append(Spacer(1, 0.2*inch))
    
    # === PIE DE PÁGINA ===
    story.append(PageBreak())
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("SmartSales365 API - Documentación Generada Automáticamente", 
                          ParagraphStyle('Footer', parent=styles['Normal'], 
                                        fontSize=10, textColor=colors.grey, alignment=TA_CENTER)))
    story.append(Paragraph(f"Fecha: {os.popen('date /t').read().strip() if os.name == 'nt' else os.popen('date +%Y-%m-%d').read().strip()}", 
                          ParagraphStyle('Date', parent=styles['Normal'], 
                                        fontSize=9, textColor=colors.grey, alignment=TA_CENTER)))
    
    # Construir PDF
    doc.build(story)
    print(f"✅ PDF generado exitosamente: {output_filename}")
    print(f"📊 Total de categorías: {len(categories)}")
    print(f"📊 Total de endpoints: {total_endpoints}")


if __name__ == '__main__':
    try:
        # Generar schema
        schema = generate_openapi_schema()
        
        # Crear PDF
        create_pdf_schema(schema)
        
        print("\n🎉 ¡Proceso completado!")
        print("📄 Archivo generado: API_SCHEMA.pdf")
        print("\nEste PDF puede ser compartido con el equipo de frontend para:")
        print("  - Entender todos los endpoints disponibles")
        print("  - Ver ejemplos de requests/responses")
        print("  - Conocer los modelos de datos")
        print("  - Implementar la integración con la API")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
