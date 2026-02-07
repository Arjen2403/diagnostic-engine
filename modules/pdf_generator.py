import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_diagnostic_report(filename, user_id, machine_id, plot_image_path):
    """
    SRS Section 5: Automated PDF Generation.
    Includes metadata (Timestamp, Machine ID, and User) for audit trails.
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # 1. Header & Metadata
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Technology Implementation Program: Diagnostic Report")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, height - 85, f"Operator/Analyst: {user_id}")
    c.drawString(50, height - 100, f"Machine Identifier: {machine_id}")
    
    c.line(50, height - 110, width - 50, height - 110)

    # 2. Embed Diagnostic Plot (Snapshot)
    if os.path.exists(plot_image_path):
        c.drawString(50, height - 130, "Correlation Analysis Snapshot:")
        # Positioning the image (x, y, width, height)
        c.drawImage(plot_image_path, 50, height - 450, width=500, preserveAspectRatio=True)
    else:
        c.drawString(50, height - 130, "[Error: Plot image not found for export]")

    # 3. Footer / XPDS Standard
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 30, "Confidential - XPDS Diagnostic Engine Baseline v1.4")
    
    c.showPage()
    c.save()
    return filename
