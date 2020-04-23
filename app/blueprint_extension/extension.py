from flask import Blueprint, request


class BlueprintExtension(Blueprint):

    def before_auth_request(self, f):
        super(BlueprintExtension, self).before_request(f)
