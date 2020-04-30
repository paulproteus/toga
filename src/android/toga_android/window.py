class AndroidViewport:
    def __init__(self, native):
        self.native = native
        self.dpi = 96  # FIXME This is almost certainly wrong...

    @property
    def width(self):
        return self.native.getMeasuredWidth()

    @property
    def height(self):
        return self.native.getMeasuredHeight()


class Window:
    def __init__(self, interface):
        self.interface = interface
        self.interface._impl = self
        self.widget = None
        self.create()

    def create(self):
        pass

    def set_app(self, app):
        self.app = app

    def set_content(self, widget):
        self.widget = widget

    def set_title(self, title):
        pass

    def set_position(self, position):
        pass

    def set_size(self, size):
        pass

    def create_toolbar(self):
        pass

    def show(self):
        if not self.widget:
            print("[Android] Showing an empty window is not supported.")

        # Set the widget's viewport to be based on the window's content.
        widget.viewport = AndroidViewport(widget.native)

        # Set the app's entire contentView to this window: only one Window can
        # be displayed at a time.
        self.app.native.setContentView(self.widget.native)

        # Attach child widgets to the this window as their container.
        for child in self.widget.interface.children:
            child._impl.container = self.widget

    def set_full_screen(self, is_full_screen):
        self.interface.factory.not_implemented('Window.set_full_screen()')

    def info_dialog(self, title, message):
        self.interface.factory.not_implemented('Window.info_dialog()')

    def question_dialog(self, title, message):
        self.interface.factory.not_implemented('Window.question_dialog()')

    def confirm_dialog(self, title, message):
        self.interface.factory.not_implemented('Window.confirm_dialog()')

    def error_dialog(self, title, message):
        self.interface.factory.not_implemented('Window.error_dialog()')

    def stack_trace_dialog(self, title, message, content, retry=False):
        self.interface.factory.not_implemented('Window.stack_trace_dialog()')

    def save_file_dialog(self, title, suggested_filename, file_types):
        self.interface.factory.not_implemented('Window.save_file_dialog()')
