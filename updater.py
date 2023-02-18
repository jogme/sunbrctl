class Updater:
    theMediator = None

    def __init__(self, mediator):
        self.theMediator = mediator
    def update(self):
        self.theMediator.notify(self)
