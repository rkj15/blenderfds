"""BlenderFDS, exceptions"""

class BFException(Exception):
    """Exception raised by all methods in case of an error."""

    def __init__(self, sender, *msgs):
        if not sender: raise Exception("No sender for BFException __init__")
        self.sender = sender
        if not msgs: raise Exception("No msgs for BFException __init__")
        self.msgs = msgs

    def __repr__(self):
        return "{__class__.__name__!s}(sender={sender!r}, {msgs!r})".format(
            __class__ = self.__class__,
            **self.__dict__
        )

    def __str__(self):
        return "; ".join(self.msgs)

    def draw(self, context, layout):
        """Draw self user interface"""
        for msg in self.msgs:
            layout.label(icon="ERROR", text=msg)

    @property
    def labels(self):
        label = self.sender.fds_label or self.sender.label or "Unknown"
        return [": ".join((label, msg)) for msg in self.msgs]

    @property
    def fds_labels(self):
        return ["! ERROR --- {}".format(label) for label in self.labels]

