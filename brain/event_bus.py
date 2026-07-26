class EventBus:

    def __init__(self):

        self.listeners = {}

    def subscribe(
        self,
        event,
        callback
    ):

        self.listeners.setdefault(
            event,
            []
        ).append(callback)

    def emit(
        self,
        event,
        data=None
    ):

        if event not in self.listeners:
            return

        for callback in self.listeners[event]:
            callback(data)


bus = EventBus()