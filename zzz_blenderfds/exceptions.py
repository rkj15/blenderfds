"""BlenderFDS, exceptions"""

class BFException(Exception):
    """Exception raised by all methods in case of an error."""

    def __init__(self, sender, *msgs):
        if not sender: raise Exception("No sender for BFException __init__")
        self.sender = sender
        if not msgs: raise Exception("No msgs for BFException __init__")
        self.msgs = msgs

    def __str__(self):
        return "\n".join(self.labels)

    @property
    def labels(self) -> "List":
        """Return a list of exception labels (sender: msg)."""
        return [": ".join((str(self.sender), msg)) for msg in self.msgs]

    @property
    def fds_labels(self) -> "List":
        """Return a list of exception labels (sender: msg) in FDS file format."""
        return ["# ERROR: {}".format(label) for label in self.labels]

    def draw(self, context, layout) -> "layout":
        """Draw self user interface."""
        for msg in self.msgs: layout.label(icon="ERROR", text=msg)
        
