import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import io
from typing import List, Dict, Any
from datetime import datetime

# Optional imports for advanced features
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class DataExporter:
    def __init__(self):
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
        else:
            self.styles = None
    
    def export_to_json(self, data: List[Dict], pretty: bool = True) -> str:
        """Export data to JSON format"""
        try:
            if pretty:
                return json.dumps(data, indent=2, default=str, ensure_ascii=False)
            else:
                return json.dumps(data, default=str, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Error exporting to JSON: {str(e)}")
    
    def export_to_xml(self, data: List[Dict], root_name: str = "weather_data") -> str:
        """Export data to XML format"""
        try:
            root = ET.Element(root_name)
            
            for i, record in enumerate(data):
                record_elem = ET.SubElement(root, "record", id=str(i + 1))
                
                for key, value in record.items():
                    if value is not None:
                        elem = ET.SubElement(record_elem, key)
                        elem.text = str(value)
            
            # Pretty print XML
            rough_string = ET.tostring(root, 'unicode')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")
            
        except Exception as e:
            raise Exception(f"Error exporting to XML: {str(e)}")
    
    def export_to_csv(self, data: List[Dict]) -> str:
        """Export data to CSV format"""
        try:
            if not data:
                return ""
            
            output = io.StringIO()
            
            # Get all unique keys from all records
            fieldnames = set()
            for record in data:
                fieldnames.update(record.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in data:
                # Convert None values to empty strings
                clean_record = {k: (v if v is not None else '') for k, v in record.items()}
                writer.writerow(clean_record)
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Error exporting to CSV: {str(e)}")
    
    def export_to_markdown(self, data: List[Dict]) -> str:
        """Export data to Markdown format"""
        try:
            if not data:
                return "# Weather Data Export\n\nNo data available."
            
            md_content = []
            md_content.append("# Weather Data Export")
            md_content.append(f"\n*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            md_content.append(f"**Total Records:** {len(data)}\n")
            
            for i, record in enumerate(data, 1):
                md_content.append(f"## Record {i}")
                md_content.append("")
                
                for key, value in record.items():
                    if value is not None:
                        # Format key as title case
                        formatted_key = key.replace('_', ' ').title()
                        
                        # Special formatting for weather data
                        if key == 'weather_data' and isinstance(value, str):
                            md_content.append(f"**{formatted_key}:**")
                            md_content.append("```")
                            md_content.append(value)
                            md_content.append("```")
                        else:
                            md_content.append(f"**{formatted_key}:** {value}")
                
                md_content.append("")
                md_content.append("---")
                md_content.append("")
            
            return "\n".join(md_content)
            
        except Exception as e:
            raise Exception(f"Error exporting to Markdown: {str(e)}")
    
    def export_to_pdf(self, data: List[Dict]) -> bytes:
        """Export data to PDF format"""
        if not REPORTLAB_AVAILABLE:
            raise ValueError("PDF export requires 'reportlab' package. Install with: pip install reportlab")
            
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            title = Paragraph("Weather Data Export Report", title_style)
            elements.append(title)
            
            # Metadata
            meta_style = ParagraphStyle(
                'Meta',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=20,
                alignment=1
            )
            
            meta_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>Total Records: {len(data)}"
            meta = Paragraph(meta_text, meta_style)
            elements.append(meta)
            elements.append(Spacer(1, 20))
            
            if not data:
                no_data = Paragraph("No data available.", self.styles['Normal'])
                elements.append(no_data)
            else:
                # Create summary table
                summary_data = [
                    ['Field', 'Description'],
                    ['ID', 'Unique identifier'],
                    ['Location', 'Requested location'],
                    ['Date Range', 'Start and end dates'],
                    ['Created At', 'Request timestamp'],
                    ['Weather Data', 'Forecast information']
                ]
                
                summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(Paragraph("Data Structure", self.styles['Heading2']))
                elements.append(summary_table)
                elements.append(Spacer(1, 30))
                
                # Add individual records
                for i, record in enumerate(data, 1):
                    elements.append(Paragraph(f"Record {i}", self.styles['Heading2']))
                    
                    # Create table for record data
                    record_data = [['Field', 'Value']]
                    
                    for key, value in record.items():
                        if value is not None:
                            formatted_key = key.replace('_', ' ').title()
                            
                            # Truncate long values
                            if isinstance(value, str) and len(value) > 100:
                                display_value = value[:100] + "..."
                            else:
                                display_value = str(value)
                            
                            record_data.append([formatted_key, display_value])
                    
                    record_table = Table(record_data, colWidths=[2*inch, 4*inch])
                    record_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    
                    elements.append(record_table)
                    elements.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(elements)
            
            # Get the value of the BytesIO buffer
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            raise Exception(f"Error exporting to PDF: {str(e)}")
    
    def export_data(self, data: List[Dict], format_type: str, **kwargs) -> Dict[str, Any]:
        """Export data in the specified format"""
        try:
            format_type = format_type.lower()
            
            if format_type == 'json':
                content = self.export_to_json(data, kwargs.get('pretty', True))
                return {
                    'success': True,
                    'content': content,
                    'content_type': 'application/json',
                    'filename': f'weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                }
            
            elif format_type == 'xml':
                content = self.export_to_xml(data, kwargs.get('root_name', 'weather_data'))
                return {
                    'success': True,
                    'content': content,
                    'content_type': 'application/xml',
                    'filename': f'weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
                }
            
            elif format_type == 'csv':
                content = self.export_to_csv(data)
                return {
                    'success': True,
                    'content': content,
                    'content_type': 'text/csv',
                    'filename': f'weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                }
            
            elif format_type == 'markdown' or format_type == 'md':
                content = self.export_to_markdown(data)
                return {
                    'success': True,
                    'content': content,
                    'content_type': 'text/markdown',
                    'filename': f'weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
                }
            
            elif format_type == 'pdf':
                content = self.export_to_pdf(data)
                return {
                    'success': True,
                    'content': content,
                    'content_type': 'application/pdf',
                    'filename': f'weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                    'is_binary': True
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported format: {format_type}. Supported formats: json, xml, csv, markdown, pdf'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}'
            } 