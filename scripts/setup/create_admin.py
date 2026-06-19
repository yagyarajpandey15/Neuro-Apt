from neuroapt.app import create_app, db, bcrypt
from neuroapt.app.models import User

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@neuroapt.com"
ADMIN_PASSWORD = "Admin123!"

app = create_app()

with app.app_context():
    # Check if admin already exists
    existing_user = User.query.filter_by(email=ADMIN_EMAIL).first()
    
    if existing_user:
        # Update existing user to have admin privileges
        existing_user.is_admin = True
        db.session.commit()
        print(f"Existing user '{existing_user.username}' updated with admin privileges")
    else:
        # Create a new admin user
        hashed_password = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')
        admin_user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=hashed_password,
            is_admin=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{ADMIN_USERNAME}' created successfully")

print(f"\nYou can now log in with:")
print(f"Email: {ADMIN_EMAIL}")
print(f"Password: {ADMIN_PASSWORD}")
print("Make sure to select 'Administrator' when logging in") 