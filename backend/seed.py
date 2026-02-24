"""
Database Seeder
Creates sample data for testing
"""

from app.db.database import SessionLocal, engine, Base
from app.models.models import User, Job, UserRole, ContractType
from app.core.security import get_password_hash


def seed_database():
    """Seed the database with sample data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # Create users
        users = [
            User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN.value
            ),
            User(
                email="recruiter@example.com",
                hashed_password=get_password_hash("recruiter123"),
                full_name="Sarah Recruiter",
                role=UserRole.RECRUITER.value
            ),
            User(
                email="john@example.com",
                hashed_password=get_password_hash("john123"),
                full_name="John Doe",
                role=UserRole.CANDIDATE.value
            ),
            User(
                email="alice@example.com",
                hashed_password=get_password_hash("alice123"),
                full_name="Alice Smith",
                role=UserRole.CANDIDATE.value
            ),
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        
        # Get recruiter for job postings
        recruiter = db.query(User).filter(User.email == "recruiter@example.com").first()
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        
        # Create jobs
        jobs = [
            Job(
                title="Senior Python Developer",
                description="We are looking for an experienced Python developer to join our team. You will work on building scalable web applications using FastAPI and Django. Requirements: 5+ years of Python experience, knowledge of SQL databases, and familiarity with Docker.",
                company="TechCorp Algeria",
                location="Algiers",
                salary_min=80000,
                salary_max=120000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Python, FastAPI, Django, PostgreSQL, Docker",
                recruiter_id=recruiter.id
            ),
            Job(
                title="Frontend React Developer",
                description="Join our frontend team to build modern user interfaces using React.js. You will collaborate with designers and backend developers to create seamless user experiences.",
                company="WebSolutions",
                location="Oran",
                salary_min=60000,
                salary_max=90000,
                contract_type=ContractType.FULL_TIME.value,
                skills="React, JavaScript, TypeScript, Tailwind CSS, Redux",
                recruiter_id=recruiter.id
            ),
            Job(
                title="Data Science Intern",
                description="Exciting internship opportunity for students passionate about data science and machine learning. You will work on real-world projects and learn from experienced data scientists.",
                company="AI Innovations",
                location="Algiers",
                salary_min=20000,
                salary_max=30000,
                contract_type=ContractType.INTERNSHIP.value,
                skills="Python, Machine Learning, Pandas, NumPy, Scikit-learn",
                recruiter_id=admin.id
            ),
            Job(
                title="DevOps Engineer",
                description="Looking for a DevOps engineer to manage our cloud infrastructure and CI/CD pipelines. Experience with AWS, Kubernetes, and Terraform required.",
                company="CloudFirst",
                location="Constantine",
                salary_min=90000,
                salary_max=130000,
                contract_type=ContractType.FULL_TIME.value,
                skills="AWS, Kubernetes, Docker, Terraform, Jenkins, Linux",
                recruiter_id=recruiter.id
            ),
            Job(
                title="Full Stack JavaScript Developer",
                description="We need a full-stack developer proficient in both Node.js and React. You will build end-to-end features for our e-commerce platform.",
                company="ShopOnline",
                location="Algiers",
                salary_min=70000,
                salary_max=100000,
                contract_type=ContractType.FULL_TIME.value,
                skills="JavaScript, Node.js, React, MongoDB, Express",
                recruiter_id=recruiter.id
            ),
            Job(
                title="Mobile App Developer (React Native)",
                description="Part-time position for a React Native developer to help us build our mobile application. Flexible hours, remote-friendly.",
                company="MobileFirst",
                location="Remote",
                salary_min=40000,
                salary_max=60000,
                contract_type=ContractType.PART_TIME.value,
                skills="React Native, JavaScript, TypeScript, Mobile Development",
                recruiter_id=admin.id
            ),
            Job(
                title="Backend Java Developer",
                description="Join our enterprise team building robust Java applications. Experience with Spring Boot and microservices architecture required.",
                company="EnterpriseSoft",
                location="Blida",
                salary_min=75000,
                salary_max=110000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Java, Spring Boot, Microservices, PostgreSQL, Kafka",
                recruiter_id=recruiter.id
            ),
            Job(
                title="UI/UX Designer & Frontend Developer",
                description="Hybrid role for someone who can both design and implement beautiful user interfaces. Figma expertise and React skills required.",
                company="DesignTech",
                location="Oran",
                salary_min=55000,
                salary_max=85000,
                contract_type=ContractType.CONTRACT.value,
                skills="Figma, React, CSS, JavaScript, UI/UX Design",
                recruiter_id=admin.id
            ),
        ]
        
        for job in jobs:
            db.add(job)
        db.commit()
        
        print(f"✅ Created {len(users)} users")
        print(f"✅ Created {len(jobs)} jobs")
        print("\n📋 Demo Accounts:")
        print("=" * 40)
        print("Admin:     admin@example.com / admin123")
        print("Recruiter: recruiter@example.com / recruiter123")
        print("Candidate: john@example.com / john123")
        print("Candidate: alice@example.com / alice123")
        print("=" * 40)
        print("\n✨ Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
