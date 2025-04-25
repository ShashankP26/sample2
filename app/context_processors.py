from django.contrib.auth.models import Group

def user_role(request):
    if request.user.is_authenticated:
        user = request.user
        groups = user.groups.values_list('name', flat=True)  # Get the names of groups
        group_name = groups[0] if groups else "No Role"  # Assuming one role per user
        print(f"role : ",user_role)
        return {
            'username': user.username,
            'user_role': group_name
        }
    return {}  # Empty context if user is not authenticated


from django.contrib.auth.models import Group

def admin_groups(request):
    # Get all groups
    groups = Group.objects.all()
    return {'all_groups': groups}


from .models import GroupButton

def group_buttons(request):
    return {
        'group_buttons': GroupButton.objects.all()
    }

from .models import ModuleVisibility 

def modules_with_submodules(request):
    if not request.user.is_authenticated:
        return {}  # Return an empty context for unauthenticated users

    # Ensure ModuleVisibility exists for the logged-in user
    module_visibility, _ = ModuleVisibility.objects.get_or_create(user=request.user)
    enabled_modules = module_visibility.get_enabled_modules()

    # Prefetch SubmoduleVisibility for the user to avoid repeated queries
    submodule_visibility_map = {
        submodule.submodule_id: submodule.is_visible
        for submodule in request.user.submodule_visibility.all()
    }

    # Prepare modules and submodules based on visibility
    modules_with_submodules = {}

    for module in enabled_modules:
        visible_submodules = [
            submodule for submodule in module.submodules.all()
            if submodule.is_active and submodule_visibility_map.get(submodule.id, False)
        ]

        # Add the module to the dictionary regardless of submodule visibility
        modules_with_submodules[module] = visible_submodules

    return {
        'modules_with_submodules': modules_with_submodules,
    }


