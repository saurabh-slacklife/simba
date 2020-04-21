from src.app.manage import ManageApp

manage_app = ManageApp()

simba_flask_app = manage_app.get_simba_app


@simba_flask_app.errorhandler(500)
def handle_500(error):
    return "It's Okay! Life is funny at time"
