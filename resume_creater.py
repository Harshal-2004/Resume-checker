from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import Color, black, darkblue
from reportlab.lib.units import inch, mm
import os

# Create a custom stylesheet
def getCustomStyleSheet():
    styles = getSampleStyleSheet()
    
    # Add custom styles with unique names
    styles.add(ParagraphStyle(
        name='ResumeTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=darkblue
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeHeading',
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        textColor=darkblue
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeNormal',
        fontName='Helvetica',
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=6,
        textColor=black
    ))
    
    styles.add(ParagraphStyle(
        name='ResumeBullet',
        fontName='Helvetica',
        fontSize=11,
        alignment=TA_LEFT,
        leftIndent=10,
        spaceAfter=4,
        textColor=black
    ))
    
    return styles

# Resume contents
resumes = {
    "Python_Developer_Resume.pdf": {
        "name": "John Doe",
        "contact": "Email: john.doe@example.com | Phone: +91-9876543210 | LinkedIn: linkedin.com/in/johndoe",
        "summary": "Passionate Python Developer with 3+ years of experience in backend development, API design, and automation scripting. Strong problem-solving skills with focus on scalable and efficient code.",
        "skills": [
            "Programming: Python, Django, Flask, FastAPI, SQLAlchemy",
            "Databases: MySQL, PostgreSQL, MongoDB",
            "Tools: Git, Docker, AWS (EC2, S3), Linux",
            "Other: REST APIs, Microservices, Unit Testing"
        ],
        "experience": [
            {
                "title": "Software Developer | ABC Tech | Jan 2021 – Present",
                "details": [
                    "Designed and deployed REST APIs in Django used by 10,000+ daily users.",
                    "Automated data pipelines saving 20+ hours of manual work weekly.",
                    "Collaborated with frontend team for seamless API integrations."
                ]
            },
            {
                "title": "Junior Python Developer | XYZ Corp | Jul 2019 – Dec 2020",
                "details": [
                    "Built backend modules in Flask for internal tools.",
                    "Wrote unit tests and improved code coverage by 30%.",
                    "Migrated database from SQLite to PostgreSQL."
                ]
            }
        ],
        "projects": [
            "Employee Management System: Built using Django and PostgreSQL with role-based authentication.",
            "Automation Bot: Developed Python scripts to automate Excel data reporting, reducing effort by 50%."
        ],
        "education": "B.Tech in Computer Science, ABC University, 2019"
    },

    "C++_Expert_Resume.pdf": {
        "name": "Jane Smith",
        "contact": "Email: jane.smith@example.com | Phone: +91-9988776655 | LinkedIn: linkedin.com/in/janesmith",
        "summary": "Highly skilled C++ Developer with 4+ years of experience in system-level programming, performance optimization, and real-time applications. Adept at writing efficient, low-latency code.",
        "skills": [
            "Programming: C++, STL, Boost, Python (for scripting)",
            "OS: Linux, Windows, RTOS",
            "Tools: GDB, Valgrind, Git, CMake",
            "Other: Data Structures, Algorithms, Multithreading, Networking"
        ],
        "experience": [
            {
                "title": "C++ Developer | Tech Systems | Feb 2020 – Present",
                "details": [
                    "Developed high-performance modules in C++ for trading systems with <1ms latency.",
                    "Optimized legacy codebase improving performance by 40%.",
                    "Implemented multithreaded systems handling 100k+ requests/sec."
                ]
            },
            {
                "title": "Software Engineer | Innovatech | Jan 2018 – Jan 2020",
                "details": [
                    "Built C++ libraries for network packet processing.",
                    "Debugged and optimized memory usage in real-time applications."
                ]
            }
        ],
        "projects": [
            "Game Engine Module: Designed physics simulation module in C++.",
            "Trading Platform: Built order-matching engine in C++ with focus on speed."
        ],
        "education": "B.E. in Computer Engineering, XYZ Institute, 2017"
    },

    "ML_Engineer_Resume.pdf": {
        "name": "Rahul Verma",
        "contact": "Email: rahul.verma@example.com | Phone: +91-9123456789 | LinkedIn: linkedin.com/in/rahulverma",
        "summary": "Machine Learning Engineer with 3+ years of experience in building, training, and deploying ML models. Strong expertise in Python, TensorFlow, and PyTorch for AI-driven solutions.",
        "skills": [
            "Programming: Python, TensorFlow, PyTorch, Scikit-learn",
            "ML/DL: NLP, Computer Vision, Time Series Forecasting",
            "Tools: Git, Docker, MLflow, AWS SageMaker",
            "Databases: MySQL, MongoDB, PostgreSQL"
        ],
        "experience": [
            {
                "title": "ML Engineer | AI Labs | Jan 2021 – Present",
                "details": [
                    "Developed NLP pipeline improving chatbot accuracy by 35%.",
                    "Deployed ML models using Flask APIs serving 50k+ daily requests.",
                    "Implemented MLflow for experiment tracking and model versioning."
                ]
            },
            {
                "title": "Data Scientist | DataWorks | Jul 2019 – Dec 2020",
                "details": [
                    "Built predictive models for sales forecasting with 90% accuracy.",
                    "Designed anomaly detection system saving $200k annually."
                ]
            }
        ],
        "projects": [
            "Image Classification: Trained CNN on TensorFlow for product recognition.",
            "Recommender System: Built movie recommendation system using collaborative filtering."
        ],
        "education": "M.Tech in Artificial Intelligence, NIT, 2019"
    }
},

def create_resume_pdf(filename, data):
    """Create a PDF resume with the given data"""
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           leftMargin=20*mm, rightMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    story = []
    
    # Get custom styles
    styles = getCustomStyleSheet()
    
    # Name
    story.append(Paragraph(data["name"], styles["ResumeTitle"]))
    
    # Contact info
    story.append(Paragraph(data["contact"], styles["ResumeNormal"]))
    story.append(Spacer(1, 15))
    
    # Summary section
    story.append(Paragraph("SUMMARY", styles["ResumeHeading"]))
    story.append(Paragraph(data["summary"], styles["ResumeNormal"]))
    story.append(Spacer(1, 10))
    
    # Skills section
    story.append(Paragraph("SKILLS", styles["ResumeHeading"]))
    for skill in data["skills"]:
        story.append(Paragraph(f"• {skill}", styles["ResumeBullet"]))
    story.append(Spacer(1, 10))
    
    # Experience section
    story.append(Paragraph("EXPERIENCE", styles["ResumeHeading"]))
    for exp in data["experience"]:
        story.append(Paragraph(exp["title"], styles["ResumeNormal"]))
        for detail in exp["details"]:
            story.append(Paragraph(f"• {detail}", styles["ResumeBullet"]))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 5))
    
    # Projects section
    story.append(Paragraph("PROJECTS", styles["ResumeHeading"]))
    for project in data["projects"]:
        story.append(Paragraph(f"• {project}", styles["ResumeBullet"]))
    story.append(Spacer(1, 10))
    
    # Education section
    story.append(Paragraph("EDUCATION", styles["ResumeHeading"]))
    story.append(Paragraph(data["education"], styles["ResumeNormal"]))
    
    # Build PDF
    doc.build(story)
    return filename

# Create output directory if it doesn't exist
output_dir = "resumes"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generate all resumes
file_paths = []
for filename, data in resumes.items():
    filepath = os.path.join(output_dir, filename)
    created_file = create_resume_pdf(filepath, data)
    file_paths.append(created_file)
    print(f"Created: {created_file}")

print(f"\nGenerated {len(file_paths)} resumes in the '{output_dir}' directory")