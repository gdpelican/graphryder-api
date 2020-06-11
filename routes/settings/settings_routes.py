from routes.settings.settings_update import Info, Status, GetContentNotTagged

def add_settings_routes(api):
    api.add_resource(Info, '/info')
    api.add_resource(Status, '/status')
    api.add_resource(GetContentNotTagged, '/content/nottagged')
