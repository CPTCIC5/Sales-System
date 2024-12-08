
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	password VARCHAR(255) NOT NULL, 
	joined_at DATETIME, 
	is_active BOOLEAN, 
	email VARCHAR(255) NOT NULL, 
	phone_number VARCHAR(20), 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
)

;

CREATE TABLE categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE groups (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	PRIMARY KEY (id)
)

;

CREATE TABLE profiles (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	avatar VARCHAR(255), 
	country VARCHAR(100), 
	PRIMARY KEY (id), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)

;

CREATE TABLE organizations (
	id INTEGER NOT NULL, 
	root_user_id INTEGER NOT NULL, 
	business_name VARCHAR(255) NOT NULL, 
	"business_webURL" VARCHAR(255) NOT NULL, 
	industry_type VARCHAR(100), 
	vspace_id VARCHAR(100) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (root_user_id), 
	FOREIGN KEY(root_user_id) REFERENCES users (id), 
	UNIQUE ("business_webURL"), 
	UNIQUE (vspace_id)
)

;

CREATE TABLE organization_members (
	user_id INTEGER, 
	organization_id INTEGER, 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id)
)

;

CREATE TABLE organization_keys (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	whatsapp_business_token VARCHAR(255), 
	PRIMARY KEY (id), 
	UNIQUE (organization_id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id), 
	UNIQUE (whatsapp_business_token)
)

;

CREATE TABLE products (
	id INTEGER NOT NULL, 
	org_id INTEGER NOT NULL, 
	user VARCHAR(255), 
	title VARCHAR(255) NOT NULL, 
	description TEXT, 
	image VARCHAR(255), 
	product_type_id INTEGER, 
	category_id INTEGER, 
	price_per_quantity FLOAT, 
	status VARCHAR(50), 
	created_at DATETIME, 
	last_updated DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(org_id) REFERENCES organizations (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id)
)

;

CREATE TABLE organization_filesystem (
	id INTEGER NOT NULL, 
	org_id INTEGER NOT NULL, 
	file_upload VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(org_id) REFERENCES organizations (id)
)

;

CREATE TABLE organization_invites (
	id INTEGER NOT NULL, 
	invite_code VARCHAR(100) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	accepted BOOLEAN, 
	created_at DATETIME, 
	organization_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (invite_code), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id)
)

;

CREATE TABLE contacts (
	id INTEGER NOT NULL, 
	org_id INTEGER NOT NULL, 
	utm_campaign VARCHAR(255), 
	utm_source VARCHAR(255), 
	utm_medium VARCHAR(255), 
	name VARCHAR(255) NOT NULL, 
	avatar VARCHAR(255), 
	phone_number VARCHAR(20), 
	industry VARCHAR(100), 
	is_favorite BOOLEAN, 
	thread_id VARCHAR(100), 
	created_at DATETIME, 
	website_url VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(org_id) REFERENCES organizations (id), 
	UNIQUE (phone_number), 
	UNIQUE (thread_id), 
	UNIQUE (website_url)
)

;

CREATE TABLE tags (
	id INTEGER NOT NULL, 
	tag_name VARCHAR(100) NOT NULL, 
	org_id INTEGER NOT NULL, 
	color_code VARCHAR(7), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(org_id) REFERENCES organizations (id)
)

;

CREATE TABLE contact_groups (
	contact_id INTEGER, 
	group_id INTEGER, 
	FOREIGN KEY(contact_id) REFERENCES contacts (id), 
	FOREIGN KEY(group_id) REFERENCES groups (id)
)

;

CREATE TABLE prompts (
	id INTEGER NOT NULL, 
	thread_id VARCHAR(100) NOT NULL, 
	input_text TEXT, 
	response_text TEXT, 
	response_image VARCHAR(255), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(thread_id) REFERENCES contacts (thread_id)
)

;
