"""
Export utilities for Web Scraper Price Comparison
Provides CSV and PDF export functionality for scraped product data
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie


class CSVExporter:
    """Handles CSV export functionality for product comparison results"""
    
    def __init__(self):
        self.default_fields = [
            'product_name',
            'price',
            'original_price',
            'discount_percentage',
            'rating',
            'reviews_count',
            'availability',
            'seller',
            'url',
            'scraped_at'
        ]
    
    def export_to_csv(self, 
                     results: List[Dict[str, Any]], 
                     filename: Optional[str] = None,
                     fields: Optional[List[str]] = None) -> str:
        """
        Export product results to CSV file
        
        Args:
            results: List of product dictionaries
            filename: Output filename (default: price_comparison_TIMESTAMP.csv)
            fields: List of fields to include (default: all standard fields)
            
        Returns:
            Path to the created CSV file
        """
        if not results:
            raise ValueError("No results to export")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"price_comparison_{timestamp}.csv"
        
        # Use provided fields or default fields
        export_fields = fields or self.default_fields
        
        # Filter fields to only include those present in results
        available_fields = set(results[0].keys())
        export_fields = [f for f in export_fields if f in available_fields]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=export_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        
        return filename
    
    def export_to_csv_string(self, 
                            results: List[Dict[str, Any]], 
                            fields: Optional[List[str]] = None) -> str:
        """
        Export product results to CSV string (useful for web downloads)
        
        Args:
            results: List of product dictionaries
            fields: List of fields to include
            
        Returns:
            CSV data as string
        """
        if not results:
            raise ValueError("No results to export")
        
        export_fields = fields or self.default_fields
        available_fields = set(results[0].keys())
        export_fields = [f for f in export_fields if f in available_fields]
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=export_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
        
        return output.getvalue()
    
    def export_selected_products(self, 
                                results: List[Dict[str, Any]], 
                                selected_indices: List[int],
                                filename: Optional[str] = None) -> str:
        """
        Export only selected products by index
        
        Args:
            results: Full list of product dictionaries
            selected_indices: List of indices to export
            filename: Output filename
            
        Returns:
            Path to the created CSV file
        """
        selected_results = [results[i] for i in selected_indices if i < len(results)]
        return self.export_to_csv(selected_results, filename)


class PDFExporter:
    """Handles PDF report generation for product comparison results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            fontSize=20,
            textColor=colors.HexColor('#1565c0'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, 
                       results: List[Dict[str, Any]], 
                       filename: Optional[str] = None,
                       title: str = "Price Comparison Report",
                       include_charts: bool = True) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            results: List of product dictionaries
            filename: Output filename (default: report_TIMESTAMP.pdf)
            title: Report title
            include_charts: Whether to include charts and visualizations
            
        Returns:
            Path to the created PDF file
        """
        if not results:
            raise ValueError("No results to export")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        story = []
        
        # Add title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Add metadata
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              self.styles['Normal']))
        story.append(Paragraph(f"Total Products: {len(results)}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a237e')))
        story.append(Spacer(1, 20))
        
        # Add summary statistics
        story.extend(self._create_summary_section(results))
        story.append(Spacer(1, 20))
        
        # Add charts if requested
        if include_charts and len(results) > 0:
            story.extend(self._create_charts_section(results))
            story.append(PageBreak())
        
        # Add product comparison table
        story.append(Paragraph("Product Comparison", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        story.extend(self._create_product_table(results))
        
        # Add best deals section
        story.append(PageBreak())
        story.extend(self._create_best_deals_section(results))
        
        # Build PDF
        doc.build(story)
        return filename
    
    def _create_summary_section(self, results: List[Dict[str, Any]]) -> List:
        """Create summary statistics section"""
        elements = []
        
        elements.append(Paragraph("Summary Statistics", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        # Calculate statistics
        prices = [float(r.get('price', 0)) for r in results if r.get('price')]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        # Calculate average rating
        ratings = [float(r.get('rating', 0)) for r in results if r.get('rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Calculate products with discounts
        discounted = sum(1 for r in results if r.get('discount_percentage', 0) > 0)
        
        # Create summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Average Price', f"₹{avg_price:.2f}"],
            ['Lowest Price', f"₹{min_price:.2f}"],
            ['Highest Price', f"₹{max_price:.2f}"],
            ['Average Rating', f"{avg_rating:.1f}/5.0"],
            ['Discounted Products', f"{discounted}/{len(results)}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(summary_table)
        return elements
    
    def _create_charts_section(self, results: List[Dict[str, Any]]) -> List:
        """Create charts and visualizations section"""
        elements = []
        
        elements.append(Paragraph("Price Analysis", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        # Create price distribution chart
        if len(results) > 1:
            chart = self._create_price_chart(results)
            if chart:
                elements.append(chart)
                elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_price_chart(self, results: List[Dict[str, Any]]) -> Optional[Drawing]:
        """Create a price comparison bar chart"""
        # Take top 10 products by price
        sorted_results = sorted(results, key=lambda x: float(x.get('price', 0)))[:10]
        
        if not sorted_results:
            return None
        
        drawing = Drawing(400, 200)
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        
        # Prepare data
        prices = [float(r.get('price', 0)) for r in sorted_results]
        chart.data = [prices]
        
        # Configure chart
        chart.categoryAxis.categoryNames = [f"P{i+1}" for i in range(len(sorted_results))]
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(prices) * 1.1
        chart.bars[0].fillColor = colors.HexColor('#1565c0')
        
        drawing.add(chart)
        return drawing
    
    def _create_product_table(self, results: List[Dict[str, Any]]) -> List:
        """Create detailed product comparison table"""
        elements = []
        
        # Prepare table data
        table_data = [['Product', 'Price', 'Discount', 'Rating', 'Seller']]
        
        for result in results[:20]:  # Limit to first 20 products
            product_name = result.get('product_name', 'N/A')[:40]  # Truncate long names
            price = f"₹{result.get('price', 0):.2f}"
            discount = f"{result.get('discount_percentage', 0)}%"
            rating = f"{result.get('rating', 'N/A')}"
            seller = result.get('seller', 'N/A')[:20]
            
            table_data.append([product_name, price, discount, rating, seller])
        
        # Create table
        product_table = Table(table_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 0.8*inch, 1.4*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(product_table)
        return elements
    
    def _create_best_deals_section(self, results: List[Dict[str, Any]]) -> List:
        """Create best deals section"""
        elements = []
        
        elements.append(Paragraph("Best Deals", self.styles['CustomHeading']))
        elements.append(Spacer(1, 12))
        
        # Find best deals (highest discount)
        discounted = [r for r in results if r.get('discount_percentage', 0) > 0]
        best_deals = sorted(discounted, 
                          key=lambda x: float(x.get('discount_percentage', 0)), 
                          reverse=True)[:5]
        
        if best_deals:
            for i, deal in enumerate(best_deals, 1):
                elements.append(Paragraph(
                    f"<b>{i}. {deal.get('product_name', 'N/A')}</b>",
                    self.styles['Normal']
                ))
                elements.append(Paragraph(
                    f"Price: ₹{deal.get('price', 0):.2f} | "
                    f"Discount: {deal.get('discount_percentage', 0)}% | "
                    f"Seller: {deal.get('seller', 'N/A')}",
                    self.styles['Normal']
                ))
                elements.append(Spacer(1, 8))
        else:
            elements.append(Paragraph("No discounted products found.", self.styles['Normal']))
        
        return elements
    
    def generate_comparison_report(self,
                                  results: List[Dict[str, Any]],
                                  selected_products: List[int],
                                  filename: Optional[str] = None) -> str:
        """
        Generate focused comparison report for selected products
        
        Args:
            results: Full list of products
            selected_products: Indices of products to compare
            filename: Output filename
            
        Returns:
            Path to created PDF
        """
        selected = [results[i] for i in selected_products if i < len(results)]
        return self.generate_report(selected, filename, 
                                   title="Selected Products Comparison Report")


# Factory function for easy usage
def create_exporter(format_type: str):
    """
    Factory function to create appropriate exporter
    
    Args:
        format_type: 'csv' or 'pdf'
        
    Returns:
        CSVExporter or PDFExporter instance
    """
    if format_type.lower() == 'csv':
        return CSVExporter()
    elif format_type.lower() == 'pdf':
        return PDFExporter()
    else:
        raise ValueError(f"Unsupported format: {format_type}")
