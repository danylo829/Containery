from app.lib.common import stable_hash

# List of all permission names used in the system.
# These will be hashed into stable values and added as class attributes.
permission_names = [
    'USER_ADD',
    'USER_DELETE',
    'USER_EDIT',
    'USER_VIEW_LIST',
    'USER_VIEW_PROFILE',

    'ROLE_ADD',
    'ROLE_VIEW',
    'ROLE_VIEW_LIST',
    'ROLE_EDIT',

    'CONTAINER_INFO',
    'CONTAINER_START',
    'CONTAINER_STOP',
    'CONTAINER_RESTART',
    'CONTAINER_DELETE',
    'CONTAINER_VIEW_LIST',
    'CONTAINER_EXEC',

    'IMAGE_INFO',
    'IMAGE_DELETE',
    'IMAGE_VIEW_LIST',

    'VOLUME_INFO',
    'VOLUME_DELETE',
    'VOLUME_VIEW_LIST',

    'NETWORK_INFO',
    'NETWORK_DELETE',
    'NETWORK_VIEW_LIST',

    'GLOBAL_SETTINGS_VIEW',
    'GLOBAL_SETTINGS_EDIT'
]

class PermissionsMeta(type):
    def __iter__(cls):
        """
        Makes the class itself iterable.

        Enables `for perm in Permissions:` to yield individual permission objects.
        Each yielded object has `.name` and `.value` attributes.

        Note: This only works *after* the class is fully defined.
        You CANNOT iterate over the class inside its own body,
        because the metaclass __iter__ is not active during class construction.
        """
        for name in permission_names:
            value = getattr(cls, name)
            yield type('Permission', (), {'name': name, 'value': value})()

class Permissions(metaclass=PermissionsMeta):
    # Dynamically assign each permission name to a stable hash value.
    # These become class-level constants, e.g. Permissions.USER_ADD
    for name in permission_names:
        locals()[name] = stable_hash(name)

    @classmethod
    def all(cls):
        """
        Returns all permission values (i.e., stable hashes) as a list.

        Equivalent to: [Permissions.USER_ADD, Permissions.USER_DELETE, ...]
        """
        return list(cls)  # Leverages the metaclass __iter__