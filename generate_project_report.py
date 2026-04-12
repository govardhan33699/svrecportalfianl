"""
SVREC College ERP Portal - Project Report Generator
Generates a comprehensive PDF report using ReportLab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus.flowables import Flowable
from datetime import datetime
import os

# ──────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────
PRIMARY       = colors.HexColor('#1a237e')   # Deep Navy Blue
SECONDARY     = colors.HexColor('#0d47a1')   # Medium Blue
ACCENT        = colors.HexColor('#1565c0')   # Bright Blue
LIGHT_BLUE    = colors.HexColor('#e3f2fd')   # Very Light Blue
GREEN         = colors.HexColor('#2e7d32')   # Dark Green
GREEN_LIGHT   = colors.HexColor('#e8f5e9')   # Light Green
ORANGE        = colors.HexColor('#e65100')   # Deep Orange
ORANGE_LIGHT  = colors.HexColor('#fff3e0')   # Light Orange
PURPLE        = colors.HexColor('#4a148c')   # Deep Purple
PURPLE_LIGHT  = colors.HexColor('#f3e5f5')   # Light Purple
TEAL          = colors.HexColor('#00695c')   # Teal
TEAL_LIGHT    = colors.HexColor('#e0f2f1')   # Light Teal
DARK_GREY     = colors.HexColor('#212121')
MID_GREY      = colors.HexColor('#616161')
LIGHT_GREY    = colors.HexColor('#f5f5f5')
WHITE         = colors.white
BLACK         = colors.black
BORDER_COLOR  = colors.HexColor('#90caf9')

PAGE_WIDTH, PAGE_HEIGHT = A4


# ──────────────────────────────────────────────
# Custom Page Template with Header/Footer
# ──────────────────────────────────────────────
def draw_page_bg(canvas, doc):
    canvas.saveState()

    # Top Banner
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, PAGE_HEIGHT - 1.6*cm, PAGE_WIDTH, 1.6*cm, fill=1, stroke=0)

    # Banner text
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    if doc.page > 1:
        canvas.drawString(1.5*cm, PAGE_HEIGHT - 1.1*cm,
                          "SVREC College ERP Portal — Project Report")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(PAGE_WIDTH - 1.5*cm, PAGE_HEIGHT - 1.1*cm,
                               f"Page {doc.page}")

    # Thin accent line below banner
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(2)
    canvas.line(0, PAGE_HEIGHT - 1.7*cm, PAGE_WIDTH, PAGE_HEIGHT - 1.7*cm)

    # Footer
    canvas.setFillColor(LIGHT_GREY)
    canvas.rect(0, 0, PAGE_WIDTH, 1.2*cm, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(0, 1.2*cm, PAGE_WIDTH, 1.2*cm)
    canvas.setFillColor(MID_GREY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(1.5*cm, 0.45*cm,
                      "Sri Venkateswara Rajya Laksmi Engineering College (Autonomous) | ERP Portal")
    canvas.drawRightString(PAGE_WIDTH - 1.5*cm, 0.45*cm,
                           f"Generated: {datetime.now().strftime('%d %B %Y')}")
    canvas.restoreState()


# ──────────────────────────────────────────────
# Styles
# ──────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    styles = {
        'cover_college': ParagraphStyle(
            'cover_college', fontSize=11, fontName='Helvetica-Bold',
            textColor=SECONDARY, alignment=TA_CENTER, spaceAfter=4
        ),
        'cover_title': ParagraphStyle(
            'cover_title', fontSize=28, fontName='Helvetica-Bold',
            textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=8, leading=34
        ),
        'cover_subtitle': ParagraphStyle(
            'cover_subtitle', fontSize=14, fontName='Helvetica',
            textColor=SECONDARY, alignment=TA_CENTER, spaceAfter=6
        ),
        'cover_tag': ParagraphStyle(
            'cover_tag', fontSize=10, fontName='Helvetica',
            textColor=MID_GREY, alignment=TA_CENTER, spaceAfter=4
        ),
        'cover_meta': ParagraphStyle(
            'cover_meta', fontSize=10, fontName='Helvetica',
            textColor=DARK_GREY, alignment=TA_CENTER
        ),
        'chapter_title': ParagraphStyle(
            'chapter_title', fontSize=17, fontName='Helvetica-Bold',
            textColor=WHITE, alignment=TA_LEFT, spaceAfter=2,
            leftIndent=0, leading=22
        ),
        'section_head': ParagraphStyle(
            'section_head', fontSize=13, fontName='Helvetica-Bold',
            textColor=SECONDARY, spaceBefore=12, spaceAfter=6,
            borderPad=4, leftIndent=0
        ),
        'subsection_head': ParagraphStyle(
            'subsection_head', fontSize=11, fontName='Helvetica-Bold',
            textColor=ACCENT, spaceBefore=8, spaceAfter=4
        ),
        'body': ParagraphStyle(
            'body', fontSize=9.5, fontName='Helvetica',
            textColor=DARK_GREY, leading=14.5, spaceAfter=6,
            alignment=TA_JUSTIFY
        ),
        'bullet': ParagraphStyle(
            'bullet', fontSize=9.5, fontName='Helvetica',
            textColor=DARK_GREY, leading=14, leftIndent=16,
            spaceAfter=3, bulletIndent=6
        ),
        'label': ParagraphStyle(
            'label', fontSize=9, fontName='Helvetica-Bold',
            textColor=MID_GREY, spaceAfter=1
        ),
        'table_header': ParagraphStyle(
            'table_header', fontSize=9, fontName='Helvetica-Bold',
            textColor=WHITE, alignment=TA_CENTER
        ),
        'table_cell': ParagraphStyle(
            'table_cell', fontSize=9, fontName='Helvetica',
            textColor=DARK_GREY
        ),
        'caption': ParagraphStyle(
            'caption', fontSize=8, fontName='Helvetica',
            textColor=MID_GREY, alignment=TA_CENTER, spaceAfter=6
        ),
        'note': ParagraphStyle(
            'note', fontSize=8.5, fontName='Helvetica',
            textColor=MID_GREY, leftIndent=12, spaceAfter=4,
            alignment=TA_JUSTIFY
        ),
    }
    return styles


# ──────────────────────────────────────────────
# Helper Flowables
# ──────────────────────────────────────────────
def chapter_header(title, styles, color=PRIMARY):
    """Generates a coloured banner heading for a chapter."""
    data = [[Paragraph(title, styles['chapter_title'])]]
    tbl = Table(data, colWidths=[PAGE_WIDTH - 4*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('ROUNDEDCORNERS', [8]),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
    ]))
    return [Spacer(1, 0.4*cm), tbl, Spacer(1, 0.3*cm)]


def section_divider(color=BORDER_COLOR):
    return HRFlowable(width="100%", thickness=1, color=color,
                      spaceAfter=6, spaceBefore=6)


def info_box(items, styles, bg=LIGHT_BLUE, border=BORDER_COLOR):
    """Coloured information box, items = list of (label, value) or strings."""
    rows = []
    for item in items:
        if isinstance(item, tuple):
            rows.append([
                Paragraph(f"<b>{item[0]}</b>", styles['table_cell']),
                Paragraph(str(item[1]), styles['table_cell'])
            ])
        else:
            rows.append([Paragraph(item, styles['body']), ''])
    tbl = Table(rows, colWidths=[5*cm, PAGE_WIDTH - 4*cm - 5*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('BOX', (0,0), (-1,-1), 0.5, border),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [bg, WHITE]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return tbl


def colored_table(headers, rows, styles, col_widths=None, header_bg=PRIMARY):
    data = [[Paragraph(h, styles['table_header']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles['table_cell']) for c in row])
    if col_widths is None:
        available = PAGE_WIDTH - 4*cm
        col_widths = [available / len(headers)] * len(headers)
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    row_count = len(data)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), header_bg),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#cfd8dc')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    return tbl


def bullet_list(items, styles):
    out = []
    for item in items:
        out.append(Paragraph(f"• {item}", styles['bullet']))
    return out


def tag_table(items, styles, cols=3):
    """Creates a row of coloured tag-style cells."""
    row = []
    for item in items:
        row.append(Paragraph(item, ParagraphStyle('tag', fontSize=8,
            fontName='Helvetica-Bold', textColor=SECONDARY, alignment=TA_CENTER)))
    # Pad to fill cols
    while len(row) % cols:
        row.append(Paragraph('', styles['body']))
    rows = [row[i:i+cols] for i in range(0, len(row), cols)]
    tbl = Table(rows, colWidths=[(PAGE_WIDTH - 4*cm) / cols] * cols)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BLUE),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.25, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return tbl


# ══════════════════════════════════════════════
# PDF Builder
# ══════════════════════════════════════════════
def generate_report(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2.2*cm,
        bottomMargin=2*cm,
    )
    styles = build_styles()
    story = []

    # ═══════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════
    story.append(Spacer(1, 1.5*cm))

    # Top decorative bar (simulation via table)
    cover_bar_data = [['']]
    cover_bar = Table(cover_bar_data, colWidths=[PAGE_WIDTH - 4*cm], rowHeights=[0.6*cm])
    cover_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
    ]))
    story.append(cover_bar)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("SRI VENKATESWARA RAJYA LAKSMI ENGINEERING COLLEGE", styles['cover_college']))
    story.append(Paragraph("(Autonomous) — Affiliated to JNTUK", styles['cover_tag']))
    story.append(Spacer(1, 0.4*cm))

    # Divider
    story.append(HRFlowable(width="60%", thickness=2, color=ACCENT,
                             hAlign='CENTER', spaceBefore=4, spaceAfter=14))

    story.append(Paragraph("SVREC ERP Portal", styles['cover_title']))
    story.append(Paragraph("Enterprise Resource Planning System", styles['cover_subtitle']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Comprehensive Project Report", styles['cover_tag']))
    story.append(Spacer(1, 1*cm))

    # Cover info card
    cover_info = [
        ["Project Name",     "SVREC ERP Portal"],
        ["Institution",      "Sri Venkateswara Rajya Laksmi Engineering College"],
        ["Framework",        "Django 4.2 (Python)"],
        ["Database",         "SQLite (Dev) / PostgreSQL (Production)"],
        ["Report Date",      datetime.now().strftime("%d %B %Y")],
        ["Version",          "v3.0 — Production Release"],
    ]
    tbl = Table([[Paragraph(f"<b>{r[0]}</b>", styles['table_cell']),
                  Paragraph(r[1], styles['table_cell'])] for r in cover_info],
                colWidths=[5*cm, PAGE_WIDTH - 4*cm - 5*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BLUE),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.25, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.8*cm))

    # Bottom bar
    bottom_bar = Table([['']], colWidths=[PAGE_WIDTH - 4*cm], rowHeights=[0.6*cm])
    bottom_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
    ]))
    story.append(Spacer(1, 1.5*cm))
    story.append(bottom_bar)

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════
    story += chapter_header("TABLE OF CONTENTS", styles)

    toc_data = [
        ("1", "Project Overview", "3"),
        ("2", "System Architecture", "4"),
        ("3", "Technology Stack", "5"),
        ("4", "Data Models & Database Design", "6"),
        ("5", "Module 1 — Admin / HOD Portal", "8"),
        ("6", "Module 2 — Staff Faculty Portal", "10"),
        ("7", "Module 3 — Student Portal", "12"),
        ("8", "Key Advanced Features", "14"),
        ("9", "Security & Access Control", "15"),
        ("10", "Deployment & Configuration", "16"),
        ("11", "URL Route Map", "17"),
        ("12", "Conclusion & Future Scope", "18"),
    ]
    toc_table = Table(
        [[Paragraph(f"<b>{r[0]}.</b>", styles['table_cell']),
          Paragraph(r[1], styles['table_cell']),
          Paragraph(r[2], ParagraphStyle('toc_pg', fontSize=9, fontName='Helvetica',
                                          textColor=MID_GREY, alignment=TA_RIGHT))]
         for r in toc_data],
        colWidths=[1.2*cm, PAGE_WIDTH - 4*cm - 2.2*cm, 1*cm]
    )
    toc_table.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, LIGHT_GREY]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 1: PROJECT OVERVIEW
    # ═══════════════════════════════════════════
    story += chapter_header("1. Project Overview", styles)

    story.append(Paragraph("1.1 Introduction", styles['section_head']))
    story.append(Paragraph(
        "The <b>SVREC ERP Portal</b> is a full-featured, web-based Enterprise Resource Planning "
        "system purpose-built for Sri Venkateswara Rajya Laksmi Engineering College (Autonomous). "
        "Developed using the Django framework (Python), this platform replaces manual and paper-based "
        "academic processes with a unified, role-based digital environment accessible from any device.",
        styles['body']
    ))
    story.append(Paragraph(
        "The system caters to three primary user roles — <b>HOD/Admin</b>, <b>Faculty/Staff</b>, and "
        "<b>Students</b> — each with a dedicated, feature-rich portal. The ERP covers the full academic "
        "lifecycle: student enrollment, attendance tracking, marks management, timetable scheduling, "
        "assignments, announcements, certificates, cloud storage, and advanced workflow automation.",
        styles['body']
    ))

    story.append(Paragraph("1.2 Objectives", styles['section_head']))
    story += bullet_list([
        "Digitize all academic and administrative workflows of the institution.",
        "Provide role-based interfaces for Administrators, Faculty, and Students.",
        "Enable real-time attendance tracking, marks entry, and result computation.",
        "Support automated email notifications via a configurable workflow engine.",
        "Offer Excel import/export for student data and marks sheets.",
        "Provide a student cloud storage system for academic documents.",
        "Implement a certificate management system for student achievements.",
        "Generate academic calendars, timetables, and announcements.",
    ], styles)

    story.append(Paragraph("1.3 Scope", styles['section_head']))
    story.append(Paragraph(
        "This ERP is designed for a single college with multiple departments (branches), "
        "degree programs, academic regulations, and session years. The system supports "
        "multiple semesters (1-1 through 4-2) and sections (A, B, C). It is production-ready, "
        "deployed on PythonAnywhere and accessible at <b>syncx.pythonanywhere.com</b>.",
        styles['body']
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 2: SYSTEM ARCHITECTURE
    # ═══════════════════════════════════════════
    story += chapter_header("2. System Architecture", styles, color=SECONDARY)

    story.append(Paragraph("2.1 Architectural Pattern", styles['section_head']))
    story.append(Paragraph(
        "The application follows the <b>Model-View-Template (MVT)</b> architectural pattern "
        "— Django's adaptation of MVC. Business logic resides in Views (Python functions), "
        "data schemas are defined in Models (Django ORM), and presentation is handled by "
        "HTML Templates with Django template tags.",
        styles['body']
    ))

    arch_rows = [
        ["Layer", "Technology", "Responsibility"],
        ["Presentation", "HTML5, CSS3, Bootstrap 4, JS", "User Interface & UX"],
        ["Application", "Django 4.2 (Python)", "Business Logic, URL Routing, Views"],
        ["ORM", "Django ORM", "Database Abstraction, Model Signals"],
        ["Database", "SQLite / PostgreSQL", "Data Persistence"],
        ["Authentication", "Django Auth (AbstractUser)", "Login, Role-Based Access"],
        ["File Storage", "Django FileField + Pillow", "Profile Pics, Assignments, Cloud Files"],
        ["Static Files", "WhiteNoise", "Serving CSS/JS in Production"],
        ["Email", "Django SMTP", "Notifications & Workflow Emails"],
        ["Excel", "Pandas + OpenPyXL", "Import/Export of Marks & Student Data"],
    ]
    story.append(colored_table(
        arch_rows[0], arch_rows[1:], styles,
        col_widths=[4*cm, 6*cm, PAGE_WIDTH - 4*cm - 10*cm]
    ))

    story.append(Paragraph("2.2 Application Structure", styles['section_head']))
    story += bullet_list([
        "college_management_system/ — Django project root (settings, URLs, WSGI/ASGI)",
        "main_app/ — Core Django application with all models, views, forms and templates",
        "main_app/views.py — Shared views: Login, Logout, Attendance API",
        "main_app/hod_views.py — Admin/HOD module (103 KB, ~2,500 lines)",
        "main_app/staff_views.py — Staff module (45 KB, ~1,200 lines)",
        "main_app/student_views.py — Student module (47 KB, ~1,300 lines)",
        "main_app/models.py — 25 data models defining the full relational schema",
        "main_app/forms.py — 30+ Django forms for all data-entry operations",
        "main_app/workflow_engine.py — Custom workflow automation engine",
        "static/ & staticfiles/ — CSS, JS, images (WhiteNoise served)",
        "media/ — User-uploaded files (profile pics, assignments, certificates)",
    ], styles)

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 3: TECHNOLOGY STACK
    # ═══════════════════════════════════════════
    story += chapter_header("3. Technology Stack", styles, color=GREEN)

    story.append(Paragraph("3.1 Backend", styles['section_head']))
    tech_backend = [
        ["Component", "Technology", "Version / Notes"],
        ["Web Framework", "Django", "≥ 4.2.0"],
        ["Language", "Python", "3.x"],
        ["WSGI Server", "Gunicorn", "≥ 20.1.0"],
        ["Database ORM", "Django ORM", "Built-in"],
        ["Database Driver", "mysql-connector-python", "≥ 8.0.0 (MySQL support)"],
        ["URL Config", "dj-database-url", "≥ 0.5.0"],
        ["Static Files", "WhiteNoise", "≥ 6.2.0"],
        ["Image Processing", "Pillow", "Latest"],
        ["HTTP Requests", "requests", "Latest"],
        ["Data Processing", "pandas", "Latest"],
        ["Excel I/O", "openpyxl", "Latest"],
    ]
    story.append(colored_table(
        tech_backend[0], tech_backend[1:], styles,
        col_widths=[4.5*cm, 5*cm, PAGE_WIDTH - 4*cm - 9.5*cm],
        header_bg=GREEN
    ))

    story.append(Paragraph("3.2 Frontend", styles['section_head']))
    story += bullet_list([
        "HTML5 — Semantic markup for all 60+ templates",
        "CSS3 — Custom dark/glassmorphism design with transitions and animations",
        "Bootstrap 4.x — Responsive grid layout, modal dialogs, form controls",
        "JavaScript (ES6) — Dynamic interactions, AJAX calls, chart rendering",
        "Chart.js — Analytics dashboards with doughnut, bar, and line charts",
        "Drawflow.js — Visual drag-and-drop workflow builder canvas",
        "Select2 — Enhanced select dropdowns with search functionality",
        "Google Fonts (Inter) — Modern typography",
    ], styles)

    story.append(Paragraph("3.3 Deployment", styles['section_head']))
    dep_info = [
        ("Hosting", "PythonAnywhere (primary) | Local development: Django runserver"),
        ("Live URL", "https://syncx.pythonanywhere.com"),
        ("Static Files", "WhiteNoise middleware for production static serving"),
        ("Database", "SQLite for development, PostgreSQL-ready for production"),
        ("Version Control", "Git + GitHub (govardhan33699/svrecportalfianl)"),
        ("Procfile", "web: gunicorn college_management_system.wsgi"),
    ]
    story.append(info_box(dep_info, styles, bg=GREEN_LIGHT,
                          border=colors.HexColor('#a5d6a7')))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 4: DATABASE DESIGN
    # ═══════════════════════════════════════════
    story += chapter_header("4. Data Models & Database Design", styles, color=PURPLE)

    story.append(Paragraph(
        "The ERP uses <b>25 relational models</b> managed through Django ORM. "
        "All models include timestamped audit fields (created_at, updated_at) and are linked "
        "via ForeignKey and OneToOneField relationships for referential integrity.",
        styles['body']
    ))

    story.append(Paragraph("4.1 Core Models Summary", styles['section_head']))
    model_rows = [
        ["Model", "Key Fields", "Purpose"],
        ["CustomUser", "email, user_type, gender, profile_pic, address", "Central user entity (HOD/Staff/Student)"],
        ["Admin", "admin (→ CustomUser)", "HOD/Administrator profile extension"],
        ["Staff", "admin, course, designation, qualification, blood_group", "Faculty profile with detailed attributes"],
        ["Student", "admin, course, roll_number, section, regulation, semester", "Student profile with full academic details"],
        ["Course", "name, degree", "Department / Branch (e.g., CSE, ECE)"],
        ["Degree", "name", "Degree program (e.g., B.Tech, M.Tech)"],
        ["AcademicLevel", "name", "Year level (1st Year, 2nd Year…)"],
        ["AcademicSemester", "name, academic_level", "Semester within a year"],
        ["Regulation", "name, course, session", "Academic regulation (e.g., R20, R23)"],
        ["Session", "start_year, end_year", "Academic Year session"],
        ["Subject", "name, code, staff, course, semester, credits, max_marks", "Subject / paper linked to staff & course"],
        ["Attendance", "subject, date, semester, session, period", "Attendance session record"],
        ["AttendanceReport", "student, attendance, status", "Per-student attendance entry"],
        ["StudentResult", "student, subject, objective, descriptive, assignment, internal, external, total", "Marks entry per exam"],
        ["Assignment", "subject, staff, title, due_date, file", "Assignment created by staff"],
        ["AssignmentSubmission", "assignment, student, file, status, marks", "Student submission with grade"],
        ["StudyMaterial", "title, subject, file, description", "Study materials uploaded by staff"],
        ["Announcement", "title, content, category, audience", "Notices for all/staff/students"],
        ["AcademicCalendar", "session, semester, regulation, dates", "Semester calendar framework"],
        ["CalendarEvent", "calendar, event_type, start_date, end_date", "Specific events in academic calendar"],
        ["Timetable", "course, section, subject, day, period, staff, semester", "Weekly class timetable slots"],
        ["Period", "number, start_time, end_time", "Daily period timing definitions"],
        ["StudentCloudFile", "student, title, file, category", "Cloud file storage per student"],
        ["StudentCertificate", "student, title, type, issued_by, issue_date, file", "Achievement certificates"],
        ["Workflow / EmailTemplate", "name, trigger_type, graph_data, body", "Workflow automation engine"],
    ]
    story.append(colored_table(
        model_rows[0], model_rows[1:], styles,
        col_widths=[3.8*cm, 6.5*cm, PAGE_WIDTH - 4*cm - 10.3*cm],
        header_bg=PURPLE
    ))

    story.append(Paragraph("4.2 Database Relationships", styles['section_head']))
    story += bullet_list([
        "CustomUser ↔ Admin / Staff / Student : OneToOne — each user maps to exactly one role profile",
        "Student → Course / Session / Regulation / AcademicLevel / AcademicSemester : ForeignKey",
        "Subject → Course / Regulation / Staff : ForeignKey (subject belongs to a department & regulation)",
        "Attendance → Subject / Session / Period : ForeignKey (session of attendance)",
        "AttendanceReport → Student / Attendance : ForeignKey (individual student record)",
        "StudentResult → Student / Subject : ForeignKey with unique constraint per exam",
        "Assignment → Subject / Staff : ForeignKey; AssignmentSubmission → Assignment / Student",
        "Timetable → Course / Subject / Period / Staff : ForeignKey with unique_together constraint",
        "StudentCloudFile / StudentCertificate → Student : ForeignKey (per-student documents)",
        "Workflow → WorkflowExecutionLog → Student : audit trail for automation runs",
    ], styles)

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 5: ADMIN / HOD PORTAL
    # ═══════════════════════════════════════════
    story += chapter_header("5. Module 1 — Admin / HOD Portal", styles, color=SECONDARY)

    story.append(Paragraph(
        "The HOD/Admin portal is the management control centre of the ERP. It provides "
        "comprehensive CRUD operations for all entities and advanced analytics through "
        "interactive charts. The admin dashboard is implemented in <code>hod_views.py</code> "
        "(103 KB) with 60+ URL routes.",
        styles['body']
    ))

    story.append(Paragraph("5.1 Dashboard & Analytics", styles['section_head']))
    story += bullet_list([
        "Live statistics cards: Total Students, Staff, Courses, and Subjects",
        "Interactive Chart.js visualizations: Subject-wise attendance doughnut chart",
        "Staff performance analytics with course-wise student count breakdowns",
        "Recent activity log on the home dashboard",
        "Quick action shortcuts to all major management sections",
    ], styles)

    story.append(Paragraph("5.2 Academic Structure Management", styles['section_head']))
    academic_features = [
        ["Feature", "Description"],
        ["Degree Management", "Create/Edit/Delete B.Tech, M.Tech, and other degree programs"],
        ["Branch (Course)", "Manage departments: CSE, ECE, EEE, ME, CE etc."],
        ["Academic Level", "Year levels: 1st Year, 2nd Year, 3rd Year, 4th Year"],
        ["Academic Semester", "Semesters within each academic year (e.g., Sem 1, Sem 2)"],
        ["Session / Academic Year", "Annual sessions, e.g., 2023–2024, 2024–2025"],
        ["Regulation", "Syllabus regulations per course (R16, R20, R23 etc.)"],
        ["Subject Management", "Add subjects with code, credits, max marks, staff assignment, ordering"],
        ["Timetable Builder", "Visual weekly timetable with day/period/section/semester"],
        ["Academic Calendar", "Semester-wise calendars with mid-exam, end-exam, and lab exam events"],
    ]
    story.append(colored_table(
        academic_features[0], academic_features[1:], styles,
        col_widths=[4.5*cm, PAGE_WIDTH - 4*cm - 4.5*cm]
    ))

    story.append(Paragraph("5.3 People Management", styles['section_head']))
    story += bullet_list([
        "Staff Management — Add, edit, delete staff with full academic and personal profiles "
        "(designation, qualification, DOB, Aadhaar, PAN, blood group, experience)",
        "Staff Qualifications — Multi-entry qualification history per staff member",
        "Student Management — Comprehensive student profiles with 25+ fields including "
        "roll number, section, admission type, blood group, APAAR ID, parent details",
        "Student Import — Bulk upload via Excel (pandas + openpyxl) with validation",
        "Student Detail View — 360° student view with marks, attendance, certificates",
    ], styles)

    story.append(Paragraph("5.4 Marks & Results", styles['section_head']))
    story += bullet_list([
        "View consolidated marks report with subject-wise tabulation",
        "Student Marks Memo — Official formatted marks card per student per semester",
        "Edit Marks Memo — Admin correction of marks memo before printing",
        "Add Memo Subject — Add custom subjects to a student's marks memo",
        "Calculate Final Internal — Auto-compute final internal marks from components",
        "Export Final Internal Report — Download formatted Excel report per batch",
    ], styles)

    story.append(Paragraph("5.5 Communication & Announcements", styles['section_head']))
    story += bullet_list([
        "Create/Edit/Delete announcements with categories: News, Mid Exams, Semester Exams, "
        "Placements, Holidays, Other",
        "Audience targeting: All users, Staff only, or Students only",
        "Push notification support via Firebase Cloud Messaging (FCM tokens)",
        "Feedback review system: Read and reply to student and staff feedback",
        "Leave approval workflow: Approve/Reject leave applications from staff and students",
    ], styles)

    story.append(Paragraph("5.6 Certificate Management", styles['section_head']))
    story += bullet_list([
        "Add certificates to individual student profiles (Workshop, Sports, Technical, Others)",
        "View all certificates per student in the student detail page",
        "Edit or delete certificates with file attachment management",
    ], styles)

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 6: STAFF PORTAL
    # ═══════════════════════════════════════════
    story += chapter_header("6. Module 2 — Staff / Faculty Portal", styles, color=TEAL)

    story.append(Paragraph(
        "The staff portal provides faculty with tools to manage attendance, enter marks, "
        "create assignments, upload study materials, and communicate with administration. "
        "All operations are scoped to the subjects assigned to the logged-in staff member.",
        styles['body']
    ))

    staff_features = [
        ["Feature", "Details"],
        ["Staff Dashboard", "Personal analytics: subject-wise student count, attendance statistics"],
        ["Attendance Management", "Take attendance per subject/section/period with section filter; "
                                  "update previously entered attendance; grid view by date range"],
        ["Marks Entry", "Add student results: Objective (Quiz), Descriptive, Assignment, "
                        "Internal, External, and Total marks per subject per exam"],
        ["Excel Marks Import", "Download subject-specific Excel template, fill marks offline, "
                               "upload for bulk import; download generic template"],
        ["Export Final Internal", "Generate formatted Excel workbook with all marks for reporting"],
        ["Assignment Management", "Create assignments with due date and file attachment; "
                                   "view student submissions; grade and add remarks"],
        ["Study Materials", "Upload PDFs, notes, and documents per subject for student access"],
        ["Timetable View", "View personal class timetable with period-wise schedule"],
        ["Announcement View", "View all announcements published by the HOD"],
        ["Leave Application", "Apply for personal leave with date and reason"],
        ["Feedback", "Send feedback/suggestions to HOD/Admin"],
        ["Profile Management", "View and update personal profile including photo"],
        ["Notifications", "Receive and view admin notifications pushed via FCM"],
    ]
    story.append(colored_table(
        staff_features[0], staff_features[1:], styles,
        col_widths=[4.5*cm, PAGE_WIDTH - 4*cm - 4.5*cm],
        header_bg=TEAL
    ))

    story.append(Paragraph("6.1 Attendance System Detail", styles['section_head']))
    story.append(Paragraph(
        "The attendance module is one of the core features. Staff can take attendance for "
        "any subject they are assigned to, selecting the section, semester, date, and period "
        "(Period 1–7, Plus period). The system stores attendance per-student per-class and "
        "provides a grid view showing daily attendance across a date range with color-coded "
        "present (✓) and absent (✗) indicators.",
        styles['body']
    ))

    story.append(Paragraph("6.2 Marks Entry System", styles['section_head']))
    story.append(Paragraph(
        "Results are stored in the <code>StudentResult</code> model with separate columns for "
        "objective (quiz), descriptive, assignment, internal, and external marks. Staff can enter "
        "marks for multiple students at once. The system supports multiple exam entries (Mid-1, Mid-2, etc.) "
        "and computes totals automatically. Excel templates can be generated per subject for "
        "offline data entry and then imported back.",
        styles['body']
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 7: STUDENT PORTAL
    # ═══════════════════════════════════════════
    story += chapter_header("7. Module 3 — Student Portal", styles, color=ORANGE)

    story.append(Paragraph(
        "The student portal provides learners with a comprehensive personal academic dashboard. "
        "Students can monitor their attendance, access marks and results, view timetables, "
        "submit assignments, access study materials, store files in personal cloud storage, "
        "and manage their certificates.",
        styles['body']
    ))

    student_features = [
        ["Feature", "Description"],
        ["Student Dashboard", "Personalized home with attendance summary, quick links, "
                              "and announcement feed showing latest college notices"],
        ["Attendance Tracking", "View subject-wise attendance summary with percentage; "
                                "detailed date-wise attendance report with bar/chart visualization"],
        ["Marks / Results", "View marks per exam per subject with component-wise breakdown; "
                            "consolidated marks table across all semesters"],
        ["Traditional Results View", "Formatted result card with grade and status per subject"],
        ["Timetable", "Personal weekly timetable based on course, section, and semester"],
        ["Assignments", "View active assignments with due dates; submit files for each assignment; "
                        "track submission status and grades"],
        ["Study Materials", "Access uploaded PDFs and notes from faculty per subject"],
        ["Cloud Storage", "Personal cloud storage with categories: Notes, PDF, "
                           "Question Paper, Important File; upload/delete files"],
        ["Certificates", "View all uploaded achievement certificates (Workshop, Sports, Technical)"],
        ["Announcement Board", "Browse all active announcements with category filters"],
        ["Leave Application", "Apply for leave with date and reason; track approval status"],
        ["Feedback", "Submit written feedback to HOD/administration"],
        ["Profile", "View personal profile with academic info, contact details"],
        ["Change Password", "Secure password change with current password verification"],
        ["Notifications", "Receive and view admin push notifications"],
    ]
    story.append(colored_table(
        student_features[0], student_features[1:], styles,
        col_widths=[4.5*cm, PAGE_WIDTH - 4*cm - 4.5*cm],
        header_bg=ORANGE
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 8: KEY ADVANCED FEATURES
    # ═══════════════════════════════════════════
    story += chapter_header("8. Key Advanced Features", styles, color=colors.HexColor('#6a1b9a'))

    story.append(Paragraph("8.1 Workflow Automation Engine", styles['section_head']))
    story.append(Paragraph(
        "A custom <b>visual workflow builder</b> (powered by <b>Drawflow.js</b>) enables the HOD "
        "to create automated email and notification workflows triggered by system events. "
        "Workflows are defined as JSON graph data (nodes and connections) and executed by "
        "<code>workflow_engine.py</code>.",
        styles['body']
    ))
    story += bullet_list([
        "Trigger events: New Announcement, Marks Uploaded, Assignment Created, Attendance Alert, Manual Trigger",
        "Actions: Send email using customizable HTML email templates",
        "Email templates managed separately with subject and HTML body",
        "Execution logs stored in WorkflowExecutionLog with success/error status",
        "Full CRUD for workflows and email templates via admin interface",
    ], styles)

    story.append(Paragraph("8.2 Academic Calendar System", styles['section_head']))
    story.append(Paragraph(
        "Administrators can create detailed academic calendars per session and semester. "
        "Each calendar contains structured events with types: Mid-term exams, End-term exams, "
        "Lab exams, Branch workshops, Result declarations, and Next semester commencement. "
        "Custom events can also be added with free-form naming.",
        styles['body']
    ))

    story.append(Paragraph("8.3 Excel Import / Export", styles['section_head']))
    story += bullet_list([
        "Student bulk import from formatted Excel files via pandas",
        "Subject-specific marks template generation (Excel) for offline entry",
        "Generic marks template download for new data entry",
        "Final internal marks workbook export per batch/section",
        "Excel-based institutional reporting with multi-sheet workbooks",
    ], styles)

    story.append(Paragraph("8.4 Cloud Storage for Students", styles['section_head']))
    story.append(Paragraph(
        "Each student has a personal cloud storage area within the portal. They can upload "
        "files of up to any size, categorized as Notes, PDF, Question Paper, or Important File. "
        "Files are stored using Django's file storage backend in the <code>student_cloud/</code> "
        "directory under <code>media/</code>.",
        styles['body']
    ))

    story.append(Paragraph("8.5 Certificate Management", styles['section_head']))
    story.append(Paragraph(
        "HOD/Admin can add, edit, and delete achievement certificates for individual students. "
        "Each certificate record includes: title, type (Workshop, Sports, Technical, Others), "
        "issuing authority, issue date, and file attachment. Students can view all their "
        "certificates from the student portal.",
        styles['body']
    ))

    story.append(Paragraph("8.6 Timetable Management", styles['section_head']))
    story.append(Paragraph(
        "The timetable system supports weekly scheduling per course, section, and semester. "
        "Seven periods per day plus additional periods are supported. The system enforces "
        "unique constraints (no double-booking of a period for a course/section) and provides "
        "both staff and student views of the timetable.",
        styles['body']
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 9: SECURITY
    # ═══════════════════════════════════════════
    story += chapter_header("9. Security & Access Control", styles, color=colors.HexColor('#b71c1c'))

    story.append(Paragraph("9.1 Authentication System", styles['section_head']))
    story += bullet_list([
        "Custom AbstractUser with email as the primary identifier (username removed)",
        "Email-based login with hashed passwords (Django's PBKDF2-SHA256)",
        "Session-based authentication with CSRF protection on all forms",
        "Email validation backend (EmailBackend.py) for authentication",
        "Password change functionality available for students",
        "Admin-only creation of user accounts (no public registration)",
    ], styles)

    story.append(Paragraph("9.2 Role-Based Access Control (RBAC)", styles['section_head']))
    rbac = [
        ["Role", "user_type", "Access Scope"],
        ["HOD / Admin", "1", "Full system access: all CRUD, reports, settings, workflow"],
        ["Staff / Faculty", "2", "Own subjects & students: attendance, marks, assignments"],
        ["Student", "3", "Own data only: results, attendance, timetable, cloud, certs"],
    ]
    story.append(colored_table(
        rbac[0], rbac[1:], styles,
        col_widths=[3.5*cm, 2.5*cm, PAGE_WIDTH - 4*cm - 6*cm],
        header_bg=colors.HexColor('#b71c1c')
    ))

    story.append(Paragraph("9.3 Additional Security Measures", styles['section_head']))
    story += bullet_list([
        "Right-click context menu disabled across the portal to protect content",
        "All views protected with @login_required decorator",
        "Role checks in every view function to prevent horizontal privilege escalation",
        "CSRF tokens on all POST forms",
        "Middleware for session management and request authentication",
        "Media files served through Django (not directly, to allow access control)",
        "ALLOWED_HOSTS restricted in production settings",
    ], styles)

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 10: DEPLOYMENT
    # ═══════════════════════════════════════════
    story += chapter_header("10. Deployment & Configuration", styles, color=colors.HexColor('#004d40'))

    story.append(Paragraph("10.1 Local Development Setup", styles['section_head']))
    steps = [
        ("Step 1 — Clone", "git clone https://github.com/govardhan33699/svrecportalfianl"),
        ("Step 2 — Virtual Env", "python -m venv venv  |  venv\\scripts\\activate"),
        ("Step 3 — Dependencies", "pip install -r requirements.txt"),
        ("Step 4 — Settings", "Configure ALLOWED_HOSTS, SECRET_KEY, and database in settings.py"),
        ("Step 5 — Migrate", "python manage.py migrate"),
        ("Step 6 — Superuser", "python manage.py createsuperuser"),
        ("Step 7 — Run Server", "python manage.py runserver → http://127.0.0.1:8000"),
    ]
    story.append(info_box(steps, styles, bg=TEAL_LIGHT, border=colors.HexColor('#80cbc4')))

    story.append(Paragraph("10.2 Production Deployment (PythonAnywhere)", styles['section_head']))
    story += bullet_list([
        "WSGI configured via Gunicorn: web: gunicorn college_management_system.wsgi",
        "WhiteNoise middleware serves all static files in production",
        "SQLite database file (db.sqlite3) for persistence on PythonAnywhere",
        "Media files stored in /media/ directory (profile pics, assignments, cloud files)",
        "Environment variables for SECRET_KEY and database credentials",
        "runtime.txt specifies Python version for deployment",
    ], styles)

    story.append(Paragraph("10.3 Key Configuration Files", styles['section_head']))
    config_rows = [
        ["File", "Purpose"],
        ["college_management_system/settings.py", "Django settings: DB, auth, static, media, installed apps"],
        ["Procfile", "Gunicorn WSGI entry point for production"],
        ["requirements.txt", "All Python package dependencies"],
        ["runtime.txt", "Python runtime version specification"],
        ["college-erp.yml", "Conda environment specification"],
        ["manage.py", "Django management command entry point"],
        ["db.sqlite3", "SQLite database file (1 MB, development)"],
    ]
    story.append(colored_table(
        config_rows[0], config_rows[1:], styles,
        col_widths=[7*cm, PAGE_WIDTH - 4*cm - 7*cm],
        header_bg=colors.HexColor('#004d40')
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 11: URL ROUTE MAP
    # ═══════════════════════════════════════════
    story += chapter_header("11. URL Route Map (Summary)", styles, color=colors.HexColor('#37474f'))

    story.append(Paragraph(
        "The application has <b>80+ URL routes</b> organized by module. Below is a categorized summary.",
        styles['body']
    ))

    story.append(Paragraph("Common Routes", styles['subsection_head']))
    common_routes = [
        ["URL", "View", "Description"],
        ["/", "login_page", "Login page (landing)"],
        ["/doLogin/", "doLogin", "Login POST handler"],
        ["/logout_user/", "logout_user", "Logout"],
        ["/get_attendance", "get_attendance", "Attendance AJAX API"],
    ]
    story.append(colored_table(common_routes[0], common_routes[1:], styles,
                               col_widths=[5*cm, 4*cm, PAGE_WIDTH-4*cm-9*cm],
                               header_bg=colors.HexColor('#37474f')))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Admin / HOD Routes (Selected)", styles['subsection_head']))
    admin_routes = [
        ["URL", "Feature"],
        ["/admin/home/", "Admin Dashboard"],
        ["/student/add/", "Add Student"],
        ["/student/manage/", "Manage Students"],
        ["/student/view/<id>/", "Student Detail View"],
        ["/student/view/<id>/marks-memo/", "Student Marks Memo"],
        ["/student/import/", "Bulk Student Import (Excel)"],
        ["/course_management/", "Unified Academic Structure Management"],
        ["/attendance/view/", "Admin View Attendance"],
        ["/marks/view/", "Admin Marks Report"],
        ["/announcement/manage/", "Manage Announcements"],
        ["/calendar/manage/", "Academic Calendar"],
        ["/timetable/manage/", "Timetable Management"],
        ["/regulation/manage/", "Regulation / Syllabus Management"],
        ["/manage_workflows/", "Workflow Automation"],
        ["/workflow_builder/", "Visual Workflow Builder"],
    ]
    story.append(colored_table(admin_routes[0], admin_routes[1:], styles,
                               col_widths=[7*cm, PAGE_WIDTH-4*cm-7*cm],
                               header_bg=SECONDARY))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Staff Routes (Selected)", styles['subsection_head']))
    staff_routes = [
        ["URL", "Feature"],
        ["/staff/home/", "Staff Dashboard"],
        ["/staff/attendance/take/", "Take Attendance"],
        ["/staff/attendance/update/", "Update Attendance"],
        ["/staff/result/add/", "Add Marks"],
        ["/staff/result/import-excel/", "Import Marks Excel"],
        ["/staff/result/export-final-internal/", "Export Final Internal Excel"],
        ["/staff/assignment/create/", "Create Assignment"],
        ["/staff/materials/add/", "Upload Study Material"],
        ["/staff/timetable/manage/", "View Timetable"],
    ]
    story.append(colored_table(staff_routes[0], staff_routes[1:], styles,
                               col_widths=[7*cm, PAGE_WIDTH-4*cm-7*cm],
                               header_bg=TEAL))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Student Routes (Selected)", styles['subsection_head']))
    student_routes = [
        ["URL", "Feature"],
        ["/student/home/", "Student Dashboard"],
        ["/student/view/attendance/", "View Attendance"],
        ["/student/view/result/", "View Marks/Results"],
        ["/student/consolidated-marks/", "All-semester Consolidated Marks"],
        ["/student/timetable/", "View Timetable"],
        ["/student/assignments/", "View & Submit Assignments"],
        ["/student/cloud/", "Personal Cloud Storage"],
        ["/student/my-certificates/", "View Certificates"],
        ["/student/announcement/view/", "View Announcements"],
        ["/student/change-password/", "Change Password"],
    ]
    story.append(colored_table(student_routes[0], student_routes[1:], styles,
                               col_widths=[7*cm, PAGE_WIDTH-4*cm-7*cm],
                               header_bg=ORANGE))

    story.append(PageBreak())

    # ═══════════════════════════════════════════
    # CHAPTER 12: CONCLUSION
    # ═══════════════════════════════════════════
    story += chapter_header("12. Conclusion & Future Scope", styles, color=PRIMARY)

    story.append(Paragraph("12.1 Conclusion", styles['section_head']))
    story.append(Paragraph(
        "The <b>SVREC ERP Portal</b> is a comprehensive, production-ready college management system "
        "that successfully digitizes the entire academic workflow of Sri Venkateswara Rajya Laksmi "
        "Engineering College. Built entirely with open-source technologies (Python, Django, SQLite), "
        "it provides a robust, secure, and user-friendly platform for Administrators, Faculty, and "
        "Students.",
        styles['body']
    ))
    story.append(Paragraph(
        "The system handles 25+ data models, 80+ URL routes, three distinct user portals, "
        "advanced features like visual workflow automation, Excel integration, cloud storage, "
        "and a certificate management system. The glassmorphism-inspired dark-mode UI ensures "
        "a modern, engaging user experience across all devices.",
        styles['body']
    ))

    story.append(Paragraph("12.2 Key Achievements", styles['section_head']))
    story += bullet_list([
        "Full role-based ERP with HOD, Staff, and Student portals in a single Django application",
        "Advanced attendance system with period-wise tracking and grid visualization",
        "Flexible marks entry with multi-component grading and Excel import/export",
        "Visual workflow automation engine with email notification support",
        "Student cloud storage system with category-wise file organization",
        "Certificate and achievement management per student",
        "Academic calendar system with structured event types",
        "Bulk student data import with Excel template generation",
        "Deployed to production at PythonAnywhere with WhiteNoise static serving",
        "GitHub repository for version control and collaboration",
    ], styles)

    story.append(Paragraph("12.3 Future Scope", styles['section_head']))
    future = [
        ["Enhancement", "Description"],
        ["Mobile App", "React Native / Flutter mobile app consuming Django REST API"],
        ["REST API", "Full Django REST Framework API for third-party integrations"],
        ["Biometric Integration", "Link hardware fingerprint devices to the attendance system"],
        ["Fee Management", "Student fee tracking, payment gateway integration"],
        ["Library System", "Full library management (existing Book model to be expanded)"],
        ["Parent Portal", "Dedicated parent login to view ward's attendance and marks"],
        ["SMS Notifications", "Twilio or local SMS gateway integration for attendance alerts"],
        ["AI Grade Prediction", "Machine learning model to predict student performance"],
        ["Multi-College", "Multi-tenant architecture to serve multiple institutions"],
        ["PostgreSQL Production", "Migrate from SQLite to full PostgreSQL in production"],
        ["Docker", "Containerize the application for easier deployment"],
    ]
    story.append(colored_table(
        future[0], future[1:], styles,
        col_widths=[4.5*cm, PAGE_WIDTH - 4*cm - 4.5*cm]
    ))

    story.append(Spacer(1, 0.5*cm))
    story.append(section_divider(PRIMARY))

    story.append(Paragraph(
        "This report was auto-generated by the SVREC ERP Portal Report Generator on "
        f"{datetime.now().strftime('%d %B %Y at %I:%M %p')}. "
        "All information is derived from the live project source code.",
        styles['note']
    ))

    # ── Build PDF ──
    doc.build(story, onFirstPage=draw_page_bg, onLaterPages=draw_page_bg)
    print(f"\n✅ PDF Report generated successfully!\n   → {output_path}\n")


if __name__ == "__main__":
    output = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "SVREC_ERP_Portal_Project_Report.pdf"
    )
    generate_report(output)
