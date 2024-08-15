"""Monad Stack layout for qtile."""

# pylint: disable=fixme,invalid-name,import-error,line-too-long
# pylint: disable=missing-module-docstring,missing-function-docstring
# pylint: disable=attribute-defined-outside-init,too-few-public-methods

from libqtile import layout
from libqtile.command.base import expose_command

class MonadStack(layout.MonadTall):
    """Monad like layout with i3-like stacking (kind of).

    This layout is based on the 'MonadTall' built-in layout, but can
    automatically maximize the focused windows in the secondary pane, creating
    an effect vaguely similar to the "stacked" window mode in the i3 window
    manager.

    Added parameters:

    - auto_maximize: Turn auto-maximization on/off. With this set to False,
      this is basically the same as the MonadTall layout.

    Suggested Bindings:

        Key([mod, "shift"], "s", lazy.layout.toggle_auto_maximize()),

    For all other features, please check the source code of MonadTall.
    """

    defaults = [
            ("auto_maximize", True, "Maximize secondary windows on focus."),
            ("min_secondary_size", 40, "Minimum secondary size."),
            ]

    def __init__(self, **config):
        super().__init__(**config)
        self.auto_maximize = True
        self.add_defaults(self.defaults)

    @expose_command()
    def toggle_auto_maximize(self):
        "Toggle auto maximize secondary window on focus."
        self.auto_maximize = not self.auto_maximize
        self.normalize(True)
        if self.focused != 0:
            self.maximize_focused_secondary()

    def focus(self, client):
        super().focus(client)
        # Only maximize the window in the secondary pane when focus is *not* in
        # the main pane. Doing so in the main pane causes the last secondary
        # window to always be in focus when switching from secondary -> main.
        if self.focused != 0:
            self.maximize_focused_secondary()

    def remove(self, client):
        p = super().remove(client)
        # When we close the first (topmost) secondary window, focus goes back
        # to the main window. In this case, we WANT to force redraw of the
        # windows in the secondary pane so we get a maximized topmost window
        # again.
        if self.focused == 0 and len(self.clients) > 2:
            # This will also trigger secondary maximization, if needed.
            self.focus(self.clients[1])
        return p

    def maximize_focused_secondary(self):
        "Maximize the 'non-maximized' focused secondary pane"

        # Return immediately if no self.group.screen
        # (this may happen when moving windows across screens)
        if self.group.screen is None:
            return

        # If auto_maximize is off, return immediately.
        if not self.auto_maximize:
            return

        # if we have 1 or 2 panes, do nothing.
        if len(self.clients) < 3:
            return

        # Recalculate relative_sizes
        self.normalize(redraw=False)
        if len(self.relative_sizes) == 0:
            return

        # If the focused window (self.focused) is 0 (main pane), adjust
        # focused to work directly on the secondary pane windows.
        focused = self.focused
        if self.focused == 0:
            focused = 1

        n = len(self.clients) - 2  # total shrinking clients
        # total size of collapsed secondaries
        collapsed_size = self.min_secondary_size * n
        nidx = max(0, focused - 1)  # focused size index
        # total height of maximized secondary
        maxed_size = self.group.screen.dheight - collapsed_size

        # Maximize if window is not already maximized.
        if (abs(
            self._get_absolute_size_from_relative(
                self.relative_sizes[nidx]) - maxed_size) >=
            self.change_size):
            self._grow_secondary(maxed_size)
            self.group.layout_all()

    @expose_command()
    def reset(self, ratio=None, redraw=True):
        "Reset Layout."
        self.ratio = ratio or self.default_ratio
        self.align = self._left
        self.auto_maximize = False
        self.normalize(redraw)


class MonadStackRight(MonadStack):
    "MonadStackRight MonadStack, with the main window on the right."
    defaults = [
            ("align", 1, "Right align main window"),
            ("min_secondary_size", 40, "Minimum secondary size."),
            ]

    def __init__(self, **config):
        super().__init__(**config)
        self.align = self._right
        self.ratio = self.default_ratio
        self.add_defaults(self.defaults)

    @expose_command()
    def reset(self, ratio=None, redraw=True):
        "Reset Layout, keeping main window on the right."
        self.ratio = ratio or self.default_ratio
        self.align = self._right
        self.auto_maximize = False
        self.normalize(redraw)
