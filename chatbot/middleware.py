# chatbot/middleware.py
def check_permission(user, permission_name):
    try:
        role = UserRole.objects.get(user=user).role
        return getattr(role, f'can_{permission_name}', False)
    except UserRole.DoesNotExist:
        return False