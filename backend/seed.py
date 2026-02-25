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
        
        # Create jobs - Algerian job market
        jobs = [
            # IT & Tech Jobs
            Job(
                title="Développeur Python Senior",
                description="Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe. Vous travaillerez sur des applications web utilisant FastAPI et Django. Exigences: 5+ ans d'expérience Python, connaissance des bases de données SQL.",
                company="TechCorp Algérie",
                location="Alger",
                salary_min=80000,
                salary_max=120000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Python, FastAPI, Django, PostgreSQL, Docker",
                recruiter_id=recruiter.id
            ),
            Job(
                title="Développeur Frontend React",
                description="Rejoignez notre équipe frontend pour créer des interfaces utilisateur modernes avec React.js. Vous collaborerez avec les designers et les développeurs backend.",
                company="WebSolutions DZ",
                location="Oran",
                salary_min=60000,
                salary_max=90000,
                contract_type=ContractType.FULL_TIME.value,
                skills="React, JavaScript, TypeScript, Tailwind CSS, Redux",
                recruiter_id=recruiter.id
            ),
            Job(
                title="Stagiaire Data Science (DAIP)",
                description="Opportunité de stage pour étudiants passionnés par la science des données et le machine learning. Programme DAIP éligible. Formation par des data scientists expérimentés.",
                company="AI Innovations Algérie",
                location="Alger",
                salary_min=20000,
                salary_max=30000,
                contract_type=ContractType.INTERNSHIP.value,
                skills="Python, Machine Learning, Pandas, NumPy, Scikit-learn",
                recruiter_id=admin.id
            ),
            Job(
                title="Ingénieur DevOps",
                description="Recherche ingénieur DevOps pour gérer notre infrastructure cloud et pipelines CI/CD. Expérience AWS, Kubernetes et Terraform requise.",
                company="CloudFirst Maghreb",
                location="Constantine",
                salary_min=90000,
                salary_max=130000,
                contract_type=ContractType.FULL_TIME.value,
                skills="AWS, Kubernetes, Docker, Terraform, Jenkins, Linux",
                recruiter_id=recruiter.id
            ),
            
            # Banking & Finance
            Job(
                title="Agent Commercial Bancaire",
                description="Accueil et conseil clientèle, proposition de produits bancaires, gestion des opérations courantes. Formation assurée.",
                company="BEA - Banque Extérieure d'Algérie",
                location="Blida",
                salary_min=45000,
                salary_max=60000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Relation client, Vente, Comptabilité, Microsoft Office",
                recruiter_id=admin.id
            ),
            Job(
                title="Comptable",
                description="Tenue de la comptabilité générale, déclarations fiscales, préparation des bilans. Maîtrise du plan comptable national requis.",
                company="Groupe Cevital",
                location="Béjaïa",
                salary_min=50000,
                salary_max=75000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Comptabilité, Fiscalité algérienne, Sage, Excel",
                recruiter_id=recruiter.id
            ),
            
            # Healthcare
            Job(
                title="Infirmier(e) Diplômé(e)",
                description="Soins aux patients, surveillance des paramètres vitaux, administration des traitements. Diplôme d'État requis.",
                company="Clinique El Azhar",
                location="Sétif",
                salary_min=40000,
                salary_max=55000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Soins infirmiers, Urgences, Communication patient",
                recruiter_id=admin.id
            ),
            Job(
                title="Pharmacien(ne)",
                description="Gestion d'officine, délivrance de médicaments, conseil aux patients. Diplôme de pharmacie et inscription à l'Ordre requis.",
                company="Pharmacie Centrale",
                location="Tizi Ouzou",
                salary_min=60000,
                salary_max=85000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Pharmacologie, Gestion stock, Conseil patient",
                recruiter_id=recruiter.id
            ),
            
            # Oil & Gas
            Job(
                title="Technicien Maintenance Industrielle",
                description="Maintenance préventive et curative des équipements industriels. Rotation 28/28. Logé et nourri sur site.",
                company="Sonatrach",
                location="Hassi Messaoud",
                salary_min=100000,
                salary_max=150000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Maintenance industrielle, Électromécanique, HSE",
                recruiter_id=recruiter.id
            ),
            Job(
                title="Ingénieur HSE",
                description="Mise en place et suivi des procédures HSE, audits sécurité, formation du personnel. Expérience secteur pétrolier requise.",
                company="Schlumberger Algérie",
                location="Ouargla",
                salary_min=120000,
                salary_max=180000,
                contract_type=ContractType.FULL_TIME.value,
                skills="HSE, Audit sécurité, ISO 14001, Formation",
                recruiter_id=admin.id
            ),
            
            # Education
            Job(
                title="Enseignant(e) d'Anglais",
                description="Enseignement de l'anglais tous niveaux. Préparation aux examens internationaux (TOEFL, IELTS). Temps partiel possible.",
                company="British Council Algérie",
                location="Alger",
                salary_min=35000,
                salary_max=50000,
                contract_type=ContractType.PART_TIME.value,
                skills="Anglais natif, Pédagogie, TEFL/TESOL",
                recruiter_id=recruiter.id
            ),
            
            # Construction
            Job(
                title="Conducteur de Travaux BTP",
                description="Supervision des chantiers, coordination des équipes, suivi budgétaire et planning. Projets résidentiels et commerciaux.",
                company="COSIDER Construction",
                location="Tipaza",
                salary_min=80000,
                salary_max=110000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Gestion chantier, AutoCAD, MS Project, BTP",
                recruiter_id=admin.id
            ),
            Job(
                title="Architecte",
                description="Conception de projets architecturaux, suivi de chantier, relation client. Portfolio requis.",
                company="Cabinet d'Architecture Moderne",
                location="Annaba",
                salary_min=70000,
                salary_max=100000,
                contract_type=ContractType.CONTRACT.value,
                skills="AutoCAD, Revit, 3D Max, Conception architecturale",
                recruiter_id=recruiter.id
            ),
            
            # Telecom
            Job(
                title="Technicien Réseau Télécom",
                description="Installation et maintenance réseaux fibre optique et mobile. Astreintes possibles. Véhicule de service fourni.",
                company="Algérie Télécom",
                location="Médéa",
                salary_min=45000,
                salary_max=65000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Fibre optique, 4G/5G, Cisco, Huawei",
                recruiter_id=admin.id
            ),
            
            # Agriculture
            Job(
                title="Ingénieur Agronome",
                description="Développement de cultures céréalières, conseil technique aux agriculteurs. Déplacements fréquents dans la wilaya.",
                company="ITGC - Institut Technique des Grandes Cultures",
                location="Tiaret",
                salary_min=55000,
                salary_max=75000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Agronomie, Irrigation, Phytosanitaire",
                recruiter_id=recruiter.id
            ),
            
            # Retail & Commerce
            Job(
                title="Responsable Magasin",
                description="Gestion d'un point de vente, management d'équipe, atteinte des objectifs commerciaux. Expérience grande distribution souhaitée.",
                company="Carrefour Algérie",
                location="Oran",
                salary_min=50000,
                salary_max=70000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Management, Commerce, Gestion stocks, Relation client",
                recruiter_id=admin.id
            ),
            
            # Transport & Logistics
            Job(
                title="Chauffeur Poids Lourd",
                description="Transport de marchandises inter-wilayas. Permis C requis. Connaissance du réseau routier national.",
                company="SNTR - Société Nationale des Transports Routiers",
                location="Ghardaïa",
                salary_min=35000,
                salary_max=50000,
                contract_type=ContractType.FULL_TIME.value,
                skills="Permis C, Mécanique de base, GPS",
                recruiter_id=recruiter.id
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
