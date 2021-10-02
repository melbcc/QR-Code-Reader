from rest_framework.permissions import DjangoModelPermissions
from copy import deepcopy


class MyModelPermission(DjangoModelPermissions):
    pass
    # ref: https://stackoverflow.com/questions/46584653#46585240
    def __init__(self):
        self.perms_map = deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

