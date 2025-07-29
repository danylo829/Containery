from app.modules.user.models import Permissions, User, Role

def create_admin_role ():
    """Create the admin role if it doesn't exist."""
    if not Role.query.filter_by(name='admin').first():
        admin_role = Role.create_role('admin')
        if not admin_role:
            raise Exception("Failed to create admin role.")
        
        for permission in Permissions:
            try:
                admin_role.add_permission(permission.value)
            except ValueError as e:
                raise Exception(f"Failed to add permission {permission.value} to admin role: {str(e)}")
        return admin_role