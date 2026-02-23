"""
Database Seed Script
Populates the database with sample data for testing
"""

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.job import Job, ContractType
from app.core.security import get_password_hash

# Import all models to create tables
from app.models import user, job, application, conversation

def seed_database():
    """Seed the database with sample data"""
    
    # Create tables
    user.Base.metadata.create_all(bind=engine)
    job.Base.metadata.create_all(bind=engine)
    application.Base.metadata.create_all(bind=engine)
    conversation.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded!")
            return
        
        # Create sample users
        users = [
            User(
                name="Admin User",
                email="admin@example.com",
                password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            ),
            User(
                name="Recruiter ABC Corp",
                email="recruiter@example.com",
                password=get_password_hash("recruiter123"),
                role=UserRole.RECRUITER
            ),
            User(
                name="John Doe",
                email="john@example.com",
                password=get_password_hash("john123"),
                role=UserRole.CANDIDATE
            ),
            User(
                name="Alice Smith",
                email="alice@example.com",
                password=get_password_hash("alice123"),
                role=UserRole.CANDIDATE
            ),
        ]
        
        for u in users:
            db.add(u)
        
        db.commit()
        print(f"✅ Created {len(users)} users")
        
        # Create sample jobs
        jobs = [
            Job(
                title="Backend Developer (Python)",
                company="TechCorp Algeria",
                location="Algiers",
                description="We are looking for an experienced Python backend developer to join our team. You will work on building scalable APIs using FastAPI and PostgreSQL.",
                skills="Python, FastAPI, PostgreSQL, Docker, REST API",
                contract_type=ContractType.FULL_TIME,
                salary_min=80000,
                salary_max=120000
            ),
            Job(
                title="Frontend Developer (React)",
                company="WebStudio",
                location="Oran",
                description="Join our creative team to build beautiful user interfaces. Experience with React and modern CSS frameworks required.",
                skills="React, JavaScript, TypeScript, Tailwind CSS, HTML",
                contract_type=ContractType.FULL_TIME,
                salary_min=70000,
                salary_max=110000
            ),
            Job(
                title="Full Stack Developer Intern",
                company="StartupDZ",
                location="Algiers",
                description="6-month internship opportunity for students. Learn and grow with our experienced development team.",
                skills="JavaScript, Python, SQL, Git",
                contract_type=ContractType.INTERNSHIP,
                salary_min=20000,
                salary_max=30000
            ),
            Job(
                title="Data Scientist",
                company="DataMinds",
                location="Constantine",
                description="Looking for a data scientist to analyze large datasets and build machine learning models. PhD or Master's preferred.",
                skills="Python, Machine Learning, TensorFlow, SQL, Statistics",
                contract_type=ContractType.FULL_TIME,
                salary_min=100000,
                salary_max=150000
            ),
            Job(
                title="DevOps Engineer",
                company="CloudServices DZ",
                location="Remote",
                description="Manage our cloud infrastructure and CI/CD pipelines. AWS experience required.",
                skills="AWS, Docker, Kubernetes, Jenkins, Linux, Terraform",
                contract_type=ContractType.FULL_TIME,
                salary_min=90000,
                salary_max=140000
            ),
            Job(
                title="Mobile Developer (React Native)",
                company="AppFactory",
                location="Algiers",
                description="Build cross-platform mobile applications for our clients. 2+ years experience required.",
                skills="React Native, JavaScript, TypeScript, iOS, Android",
                contract_type=ContractType.FULL_TIME,
                salary_min=75000,
                salary_max=115000
            ),
            Job(
                title="Junior Python Developer",
                company="PyWorks",
                location="Oran",
                description="Entry-level position for Python enthusiasts. Great opportunity to grow your skills.",
                skills="Python, Django, SQL, Git",
                contract_type=ContractType.FULL_TIME,
                salary_min=50000,
                salary_max=70000
            ),
            Job(
                title="Backend Developer Intern",
                company="TechCorp Algeria",
                location="Algiers",
                description="3-month summer internship for backend development. Perfect for students.",
                skills="Python, JavaScript, API, Database",
                contract_type=ContractType.INTERNSHIP,
                salary_min=15000,
                salary_max=25000
            ),
            Job(
                title="UI/UX Designer",
                company="DesignHub",
                location="Algiers",
                description="Create beautiful and intuitive user experiences for web and mobile applications.",
                skills="Figma, Adobe XD, UI Design, User Research, Prototyping",
                contract_type=ContractType.FULL_TIME,
                salary_min=60000,
                salary_max=100000
            ),
            Job(
                title="Freelance Web Developer",
                company="Various Clients",
                location="Remote",
                description="Looking for freelance web developers for various projects. Flexible hours.",
                skills="HTML, CSS, JavaScript, WordPress, PHP",
                contract_type=ContractType.FREELANCE,
                salary_min=40000,
                salary_max=80000
            ),
        ]
        
        for j in jobs:
            db.add(j)
        
        db.commit()
        print(f"✅ Created {len(jobs)} jobs")
        
        print("\n🎉 Database seeded successfully!")
        print("\nTest accounts:")
        print("  - admin@example.com / admin123 (Admin)")
        print("  - recruiter@example.com / recruiter123 (Recruiter)")
        print("  - john@example.com / john123 (Candidate)")
        print("  - alice@example.com / alice123 (Candidate)")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
