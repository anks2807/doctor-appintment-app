from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url = 'mysql+pymysql://doctor_user:doctor_pass@mysql:3306/doctor_db'
engine = create_engine(db_url)

session = sessionmaker(autoflush=False, bind=engine)