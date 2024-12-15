from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, Float
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import datetime
from sqlalchemy import create_engine
from passlib.context import CryptContext

# Database connection
engine = create_engine("sqlite:///test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Association table for Organization-User many-to-many relationship
organization_members = Table(
    'organization_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('organization_id', Integer, ForeignKey('organizations.id'))
)

# Add this association table for Contact-Group many-to-many relationship
contact_groups = Table(
    'contact_groups',
    Base.metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

# Add this near the top of the file with your other association tables
contact_tags = Table(
    'contact_tags',
    Base.metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__= 'users'

    id= Column(Integer, primary_key=True)
    username= Column(String(50), unique=True, nullable=False)
    password= Column(String(255), nullable=False)
    joined_at= Column(DateTime, default=datetime.now())
    is_active= Column(Boolean, default=True)
    email= Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20))

    # Relationships
    profile= relationship("Profile", back_populates="user", uselist=False)
    organizations= relationship("Organization", secondary=organization_members, back_populates="members")

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)

    def set_password(self, password):
        self.password = pwd_context.hash(password)

class Profile(Base):
    __tablename__= 'profiles'

    id= Column(Integer, primary_key=True)
    user_id= Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    avatar= Column(String(255))
    country= Column(String(100))

    # Relationship
    user = relationship("User", back_populates="profile")

class Organization(Base):
    __tablename__= 'organizations'

    id= Column(Integer, primary_key=True)
    root_user_id= Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    business_name= Column(String(255), nullable=False)
    business_webURL= Column(String(255), unique=True, nullable=False)
    industry_type= Column(String(100), nullable=True)
    vspace_id= Column(String(100), unique=True, nullable=True)
    created_at= Column(DateTime, default=datetime.now())

    # Relationships
    root_user= relationship("User", foreign_keys=[root_user_id])
    members= relationship("User", secondary=organization_members, back_populates="organizations")
    organization_keys= relationship("OrganizationKeys", back_populates="organization", uselist=False)
    filesystem= relationship("OrganizationFileSystem", back_populates="organization")
    invites = relationship("OrganizationInvite", back_populates="organization")

class OrganizationKeys(Base):
    __tablename__= 'organization_keys'

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), unique=True, nullable=False)
    whatsapp_business_token = Column(String(255), unique=True)

    # Relationship
    organization = relationship("Organization", back_populates="organization_keys")

class Category(Base):
    __tablename__= 'categories'

    id= Column(Integer, primary_key=True)
    name= Column(String(100), nullable=False)

class Product(Base):
    __tablename__= 'products'

    id= Column(Integer, primary_key=True)
    org_id= Column(Integer, ForeignKey('organizations.id'), nullable=False)
    user_id= Column(Integer, ForeignKey('users.id'), nullable=False)
    title= Column(String(255), nullable=False)
    description= Column(Text)
    image= Column(String(255))
    product_type= Column(Integer)
    category_id= Column(Integer, ForeignKey('categories.id'))
    price_per_quantity= Column(Float)
    is_available= Column(Boolean, default=True)
    created_at= Column(DateTime, default=datetime.now())
    last_updated= Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    filesystem_id = Column(Integer, ForeignKey('organization_filesystem.id'))

    # Relationships
    user= relationship("User")
    organization= relationship("Organization")
    category= relationship("Category")
    filesystem = relationship("OrganizationFileSystem", back_populates="products")

class OrganizationFileSystem(Base):
    __tablename__ = 'organization_filesystem'

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'), nullable=False, unique=True)
    api= Column(String(500), nullable=True)

    # Relationships
    products = relationship("Product", back_populates="filesystem")
    organization = relationship("Organization", back_populates="filesystem")
    files = relationship("OrganizationFile", back_populates="filesystem")

class OrganizationFile(Base):
    __tablename__ = 'organization_files'

    id = Column(Integer, primary_key=True)
    filesystem_id = Column(Integer, ForeignKey('organization_filesystem.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)  # Store S3 URL
    uploaded_at = Column(DateTime, default=datetime.now())
    
    # Relationship
    filesystem = relationship("OrganizationFileSystem", back_populates="files")

class OrganizationInvite(Base):
    __tablename__ = "organization_invites"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    email = Column(String)
    invite_code = Column(String)
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="invites")

class Contact(Base):
    __tablename__= 'contacts'

    id= Column(Integer, primary_key=True)
    org_id= Column(Integer, ForeignKey('organizations.id'), nullable=False)
    utm_campaign= Column(String(255))
    utm_source= Column(String(255))
    utm_medium= Column(String(255))
    name= Column(String(255), nullable=False)
    avatar= Column(String(255))  # Store image URL/path
    phone_number= Column(String(20), unique=True)
    industry= Column(String(100), nullable=True)
    is_favorite= Column(Boolean, default=False)
    thread_id= Column(String(100), unique=True, nullable=True)
    created_at= Column(DateTime, default=datetime.now())
    website_url= Column(String(255), unique=True)

    # Relationships
    organization= relationship("Organization")
    tags= relationship("Tag", secondary=contact_tags, back_populates="contacts")
    groups= relationship("Group", secondary=contact_groups, back_populates="contacts")
    prompts= relationship("Prompt", back_populates="contact")

class Tag(Base):
    __tablename__= 'tags'

    id= Column(Integer, primary_key=True)
    tag_name= Column(String(100), nullable=False)
    color_code= Column(String(7))  # Hex color code
    created_at= Column(DateTime, default=datetime.now())

    # Relationships
    contacts = relationship("Contact", secondary=contact_tags, back_populates="tags")

class Group(Base):
    __tablename__= 'groups'

    id= Column(Integer, primary_key=True)
    name= Column(String(255), nullable=False)
    
    # Relationships
    contacts = relationship("Contact", secondary=contact_groups, back_populates="groups")

class Prompt(Base):
    __tablename__= 'prompts'

    id= Column(Integer, primary_key=True)
    thread_id= Column(String(100), ForeignKey('contacts.thread_id'), nullable=False)
    input_text= Column(Text)
    response_text= Column(Text)
    response_image= Column(String(255))  # Store image URL/path
    created_at= Column(DateTime, default=datetime.now())

    # Relationship
    contact= relationship("Contact", back_populates="prompts")