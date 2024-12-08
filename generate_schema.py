from sqlalchemy import create_engine
from models import Base

# Replace with your database URL
# Format: postgresql://username:password@localhost:5432/dbname
# or: mysql://username:password@localhost:3306/dbname
DATABASE_URL = "sqlite:///test.db"

def generate_schema():
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Generate schema
    with open('schema.sql', 'w') as f:
        def dump(sql, *multiparams, **params):
            f.write(str(sql.compile(dialect=engine.dialect)) + ';\n')
        
        engine = create_engine('postgresql://', strategy='mock', executor=dump)
        Base.metadata.create_all(engine, checkfirst=False)

if __name__ == '__main__':
    generate_schema() 