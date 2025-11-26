from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
import pandas as pd
import io
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from .database import get_db

app = FastAPI(title="Reports Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# SCHEMAS
# ============================================

class ReportRequest(BaseModel):
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    status: Optional[str] = None

# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def read_root():
    return {"service": "Reports Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ============================================
# EQUIPMENT REPORTS
# ============================================

@app.get("/equipment/excel")
def export_equipment_excel(
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Exportar inventario de equipos a Excel"""
    query = """
        SELECT
            e.id,
            e.asset_code,
            e.name,
            e.brand,
            e.model,
            e.serial_number,
            c.name as category,
            e.status,
            CONCAT(l.building, ' - ', l.room) as location,
            e.assigned_to,
            e.purchase_date,
            e.purchase_price,
            e.warranty_end_date
        FROM equipment e
        LEFT JOIN equipment_categories c ON e.category_id = c.id
        LEFT JOIN locations l ON e.current_location_id = l.id
        WHERE 1=1
    """

    params = {}
    if category_id:
        query += " AND e.category_id = :category_id"
        params['category_id'] = category_id
    if location_id:
        query += " AND e.current_location_id = :location_id"
        params['location_id'] = location_id
    if status:
        query += " AND e.status = :status"
        params['status'] = status

    df = pd.read_sql(text(query), db.bind, params=params)

    # Crear archivo Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Equipment Inventory', index=False)

        # Obtener worksheet para formatear
        worksheet = writer.sheets['Equipment Inventory']

        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)

    filename = f"equipment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/equipment/pdf")
def export_equipment_pdf(
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Exportar inventario de equipos a PDF"""
    query = """
        SELECT
            e.asset_code,
            e.name,
            e.brand,
            e.model,
            c.name as category,
            e.status,
            CONCAT(l.building, ' - ', l.room) as location
        FROM equipment e
        LEFT JOIN equipment_categories c ON e.category_id = c.id
        LEFT JOIN locations l ON e.current_location_id = l.id
        WHERE 1=1
    """

    params = {}
    if category_id:
        query += " AND e.category_id = :category_id"
        params['category_id'] = category_id
    if location_id:
        query += " AND e.current_location_id = :location_id"
        params['location_id'] = location_id
    if status:
        query += " AND e.status = :status"
        params['status'] = status

    df = pd.read_sql(text(query), db.bind, params=params)

    # Crear PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # Center
    )

    # Título
    title = Paragraph("Reporte de Inventario de Equipos", title_style)
    elements.append(title)

    # Fecha de generación
    date_text = Paragraph(
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles['Normal']
    )
    elements.append(date_text)
    elements.append(Spacer(1, 20))

    # Tabla de datos
    data = [df.columns.tolist()] + df.values.tolist()

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    filename = f"equipment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ============================================
# MAINTENANCE REPORTS
# ============================================

@app.get("/maintenance/excel")
def export_maintenance_excel(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    equipment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Exportar historial de mantenimiento a Excel"""
    query = """
        SELECT
            m.id,
            e.asset_code,
            e.name as equipment_name,
            m.type,
            m.scheduled_date,
            m.performed_date,
            m.technician,
            m.description,
            m.diagnosis,
            m.solution,
            m.cost,
            m.status,
            mt.name as maintenance_type
        FROM maintenance m
        LEFT JOIN equipment e ON m.equipment_id = e.id
        LEFT JOIN maintenance_types mt ON m.maintenance_type_id = mt.id
        WHERE 1=1
    """

    params = {}
    if from_date:
        query += " AND m.performed_date >= :from_date"
        params['from_date'] = from_date
    if to_date:
        query += " AND m.performed_date <= :to_date"
        params['to_date'] = to_date
    if equipment_id:
        query += " AND m.equipment_id = :equipment_id"
        params['equipment_id'] = equipment_id

    query += " ORDER BY m.performed_date DESC"

    df = pd.read_sql(text(query), db.bind, params=params)

    # Crear archivo Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Maintenance History', index=False)

        worksheet = writer.sheets['Maintenance History']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)

    filename = f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/maintenance/pdf")
def export_maintenance_pdf(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Exportar historial de mantenimiento a PDF"""
    query = """
        SELECT
            e.asset_code,
            e.name as equipment,
            m.type,
            m.performed_date,
            m.technician,
            m.cost,
            m.status
        FROM maintenance m
        LEFT JOIN equipment e ON m.equipment_id = e.id
        WHERE 1=1
    """

    params = {}
    if from_date:
        query += " AND m.performed_date >= :from_date"
        params['from_date'] = from_date
    if to_date:
        query += " AND m.performed_date <= :to_date"
        params['to_date'] = to_date

    query += " ORDER BY m.performed_date DESC"

    df = pd.read_sql(text(query), db.bind, params=params)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Reporte de Mantenimientos", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    filename = f"maintenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ============================================
# DASHBOARD STATISTICS
# ============================================

@app.get("/dashboard/statistics")
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """Obtener estadísticas para el dashboard"""
    stats = {}

    # Total de equipos
    result = db.execute(text("SELECT COUNT(*) as total FROM equipment"))
    stats['total_equipment'] = result.fetchone()[0]

    # Equipos por estado
    result = db.execute(text("""
        SELECT status, COUNT(*) as count
        FROM equipment
        GROUP BY status
    """))
    stats['equipment_by_status'] = [
        {"status": row[0], "count": row[1]} for row in result.fetchall()
    ]

    # Equipos por categoría
    result = db.execute(text("""
        SELECT c.name, COUNT(e.id) as count
        FROM equipment_categories c
        LEFT JOIN equipment e ON e.category_id = c.id
        GROUP BY c.name
        ORDER BY count DESC
        LIMIT 10
    """))
    stats['equipment_by_category'] = [
        {"category": row[0], "count": row[1]} for row in result.fetchall()
    ]

    # Equipos por ubicación
    result = db.execute(text("""
        SELECT l.building, l.department, COUNT(e.id) as count
        FROM locations l
        LEFT JOIN equipment e ON e.current_location_id = l.id
        GROUP BY l.building, l.department
        ORDER BY count DESC
        LIMIT 10
    """))
    stats['equipment_by_location'] = [
        {"building": row[0], "department": row[1], "count": row[2]}
        for row in result.fetchall()
    ]

    # Costos de mantenimiento por mes (último año)
    result = db.execute(text("""
        SELECT
            DATE_FORMAT(performed_date, '%Y-%m') as month,
            SUM(cost) as total_cost,
            COUNT(*) as count
        FROM maintenance
        WHERE performed_date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
        AND status = 'completed'
        GROUP BY DATE_FORMAT(performed_date, '%Y-%m')
        ORDER BY month
    """))
    stats['maintenance_costs_by_month'] = [
        {"month": row[0], "total_cost": float(row[1] or 0), "count": row[2]}
        for row in result.fetchall()
    ]

    # Mantenimientos por tipo
    result = db.execute(text("""
        SELECT type, COUNT(*) as count, SUM(cost) as total_cost
        FROM maintenance
        GROUP BY type
    """))
    stats['maintenance_by_type'] = [
        {"type": row[0], "count": row[1], "total_cost": float(row[2] or 0)}
        for row in result.fetchall()
    ]

    # Próximos mantenimientos
    result = db.execute(text("""
        SELECT COUNT(*) as count
        FROM maintenance
        WHERE status = 'scheduled'
        AND scheduled_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    """))
    stats['upcoming_maintenance_30_days'] = result.fetchone()[0]

    # Mantenimientos vencidos
    result = db.execute(text("""
        SELECT COUNT(*) as count
        FROM maintenance
        WHERE status = 'scheduled'
        AND scheduled_date < CURDATE()
    """))
    stats['overdue_maintenance'] = result.fetchone()[0]

    # Top proveedores
    result = db.execute(text("""
        SELECT p.name, COUNT(c.id) as contracts, SUM(c.amount) as total_amount
        FROM providers p
        LEFT JOIN contracts c ON c.provider_id = p.id
        WHERE p.is_active = 1
        GROUP BY p.id, p.name
        ORDER BY contracts DESC
        LIMIT 5
    """))
    stats['top_providers'] = [
        {"name": row[0], "contracts": row[1], "total_amount": float(row[2] or 0)}
        for row in result.fetchall()
    ]

    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
