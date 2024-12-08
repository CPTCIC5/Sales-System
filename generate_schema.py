from sqlalchemy import create_engine
from models import Base

# Using SQLite database URL
DATABASE_URL = "sqlite:///test.db"

def generate_schema():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create the actual database and tables
    Base.metadata.create_all(engine)
    
    # Generate schema SQL file (optional, you can keep or remove this part)
    with open('schema.sql', 'w') as f:
        def dump(sql, *multiparams, **params):
            f.write(str(sql.compile(dialect=engine.dialect)) + ';\n')
        
        engine = create_engine('sqlite://', strategy='mock', executor=dump)
        Base.metadata.create_all(engine, checkfirst=False)

if __name__ == '__main__':
    generate_schema() 