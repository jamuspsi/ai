from handy.ice import Ice

class Reloader(Ice):
    def __init__(self):
        pass


    def reload_stuff(self):

        import reloader
        reload(reloader)

        self.reload_more_stuff()

    def reload_more_stuff(self):
        import ai_app
        reload(ai_app)


