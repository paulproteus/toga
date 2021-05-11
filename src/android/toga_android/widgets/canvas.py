from rubicon.java.jni import java

from ..libs import activity
from ..libs import android_widgets
from .base import Widget

BIGGER = 5

class MicroCustomCanvasView(activity.IView):
    def __init__(self, interface):
        self.interface = interface
        super().__init__()

    def onDraw(self, canvas):
        # TODO: Maybe only draw if self.interface.redraw. Does that do anything?
        self.interface._draw(self.interface._impl, draw_context=canvas)
        print("About to drawPath")
        canvas.drawPath(self.interface._impl._path, self.interface._impl._draw_paint)
        print("Done with onDraw")


class Canvas(Widget):
    def create(self):
        self.native = activity.CustomView(self._native_activity.getApplicationContext())
        self._path = android_widgets.Path(__jni__=java.NewGlobalRef(android_widgets.Path()))
        self._draw_paint = android_widgets.Paint(__jni__=java.NewGlobalRef(android_widgets.Paint()))
        self.native.setView(MicroCustomCanvasView(self.interface))

        # self.native.interface = self.interface
        # self.native._impl = self
        # self.native.backgroundColor = UIColor.whiteColor

    def redraw(self):
        pass

    def set_on_press(self, handler):
        self.interface.factory.not_implemented('Canvas.set_on_press()')

    def set_on_release(self, handler):
        self.interface.factory.not_implemented('Canvas.set_on_release()')

    def set_on_drag(self, handler):
        self.interface.factory.not_implemented('Canvas.set_on_drag()')

    def set_on_alt_press(self, handler):
        self.interface.factory.not_implemented('Canvas.set_on_alt_press()')

    def set_on_alt_release(self, handler):
        self.interface.factory.not_implemented('Canvas.set_on_alt_release()')

    def set_on_alt_drag(self, handler):
        self.interface.factory.not_implemented('Canvas.set_on_alt_drag()')

    # Basic paths

    def new_path(self, draw_context, *args, **kwargs):
        self.interface.factory.not_implemented('Canvas.new_path()')

    def closed_path(self, x, y, draw_context, *args, **kwargs):
        draw_context.drawPath(self._path, self._draw_paint)
        # self.interface.factory.not_implemented('Canvas.closed_path()')

    def move_to(self, x, y, draw_context, *args, **kwargs):
        self._path.moveTo(float(x) * BIGGER, float(y) * BIGGER)
#        self.interface.factory.not_implemented('Canvas.move_to()')

    def line_to(self, x, y, draw_context, *args, **kwargs):
        self._path.lineTo(float(x) * BIGGER, float(y) * BIGGER)
    #        self.interface.factory.not_implemented('Canvas.line_to()')

    # Basic shapes

    def bezier_curve_to(
            self, cp1x, cp1y, cp2x, cp2y, x, y, draw_context, *args, **kwargs
    ):
        self.interface.factory.not_implemented('Canvas.bezier_curve_to()')

    def quadratic_curve_to(self, cpx, cpy, x, y, draw_context, *args, **kwargs):
        self.interface.factory.not_implemented('Canvas.quadratic_curve_to()')

    def arc(
            self,
            x,
            y,
            radius,
            startangle,
            endangle,
            anticlockwise,
            draw_context,
            *args,
            **kwargs
    ):
        self.interface.factory.not_implemented('Canvas.arc()')

    # Drawing Paths

    def fill(self, color, fill_rule, preserve, draw_context, *args, **kwargs):
        self.interface.factory.not_implemented('Canvas.fill()')

    def stroke(self, color, line_width, line_dash, draw_context, *args, **kwargs):
        self._draw_paint.setAntiAlias(True)
        self._draw_paint.setStrokeWidth(float(line_width) * BIGGER)
        self._draw_paint.setStyle(android_widgets.Paint__Style.STROKE)
        self._draw_paint.setStrokeJoin(android_widgets.Paint__Join.ROUND)
        self._draw_paint.setStrokeCap(android_widgets.Paint__Cap.ROUND)
        if color is None:
            a, r, g, b = 255, 0, 0, 0
        else:
            a, r, g, b = round(color.a * 255), int(color.r), int(color.g), int(color.b)
        self._draw_paint.setARGB(a, r, g, b)

        if line_dash is not None:
            self._draw_paint.setPathEffect(android_widgets.DashPathEffect([float(d) for d in line_dash], 0.0))

    # Rehint

    def set_on_resize(self, handler):
        self.interface.factory.not_implemented('Canvas.on_resize')
