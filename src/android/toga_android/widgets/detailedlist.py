from travertino.size import at_least

from rubicon.java.jni import cast, java

from ..libs import android_widgets
from .base import Widget


class DetailedListOnClickListener(android_widgets.OnClickListener):
    def __init__(self, impl, row_number):
        super().__init__()
        self._impl = impl
        self._row_number = row_number

    def onClick(self, _view):
        if self._impl.interface.on_select:
            self._impl.interface.on_select(widget=self._impl.interface, row=self._row_number)


class _SwipeDismissTouchListener(android_widgets.View__OnTouchListener):
    # Inspired directly by https://android.googlesource.com/platform/frameworks/base/+/ca6234e084a71e0c968cff404620298bcd971fcc/core/java/com/android/internal/widget/SwipeDismissLayout.java
    # which is copyright (C) 2014 The Android Open Source Project, Licensed under the Apache License, Version 2.0

    # Cached ViewConfiguration and system-wide constant values
    mSlop = 0
    mMinFlingVelocity = 0
    mMaxFlingVelocity = 0
    mAnimationTime = 0

    mView = None
    mCallbacks = None
    mViewWidth = 1.0  # 1 and not 0 to prevent dividing by zero

    # Transient properties
    mDownX = 0
    mDownY = 0
    mSwiping = False
    mSwipingSlop = 0
    mVelocityTracker = None
    mTranslationX = 0.0

    def __init__(self, view, on_dismiss_callback):
        super().__init__()
        vc = android_widgets.ViewConfiguration.get(view.getContext())
        self.mSlop = vc.getScaledTouchSlop()
        self.mMinFlingVelocity = vc.getScaledMinimumFlingVelocity() * 16
        self.mMaxFlingVelocity = vc.getScaledMaximumFlingVelocity()
        self.mAnimationTime = view.getContext().getResources().getInteger(
                android_widgets.R__integer.config_shortAnimTime)
        self.mView = view
        self._on_dismiss_callback = on_dismiss_callback

    def onTouch(self, view, motionEvent):
        # offset because the view is translated during swipe
        motionEvent.offsetLocation(self.mTranslationX, 0.0)

        if (self.mViewWidth < 2):
            self.mViewWidth = float(self.mView.getWidth())

        action_masked = motionEvent.getActionMasked()
        if action_masked == android_widgets.MotionEvent.ACTION_DOWN:
            # TODO: ensure this is a finger, and set a flag
            self.mDownX = motionEvent.getRawX()
            self.mDownY = motionEvent.getRawY()
            self.mVelocityTracker = android_widgets.VelocityTracker(
                __jni__=java.NewGlobalRef(android_widgets.VelocityTracker.obtain()))
            self.mVelocityTracker.addMovement(motionEvent)
            return False

        if action_masked == android_widgets.MotionEvent.ACTION_UP:
            if self.mVelocityTracker is not None:
                deltaX = motionEvent.getRawX() - self.mDownX
                self.mVelocityTracker.addMovement(motionEvent)
                self.mVelocityTracker.computeCurrentVelocity(1000)
                velocityX = self.mVelocityTracker.getXVelocity()
                absVelocityX = abs(velocityX)
                absVelocityY = abs(self.mVelocityTracker.getYVelocity())
                dismiss = False
                dismissRight = False
                if abs(deltaX) > self.mViewWidth / 2 and self.mSwiping:
                    dismissRight = deltaX > 0
                    dismiss = True
                elif (self.mMinFlingVelocity <= absVelocityX <= self.mMaxFlingVelocity and
                      absVelocityY < absVelocityX and
                      absVelocityY < absVelocityX and self.mSwiping):
                    # dismiss only if flinging in the same direction as dragging
                    dismissRight = self.mVelocityTracker.getXVelocity() > 0
                    dismiss = dismissRight
                if dismiss:
                    self.mView.animate(
                    ).translationX(self.mViewWidth if dismissRight else -self.mViewWidth
                                   ).alpha(0.0
                                           ).setDuration(self.mAnimationTime
                                                         ) # TODO: setListener(new AnimatorListenerAdapter() { @Override public void onAnimationEnd(Animator animation) {                                    performDismiss();                                 }
                    # PYTHON HACK, DELETE THE NEXT LINE SOON
                    self._performDismiss()
                elif self.mSwiping:
                    self.mView.animate(
                    ).translationX(0.0
                                   ).alpha(1.0
                                           ).setDuration(self.mAnimationTime) # .setListener(null)
                self.mVelocityTracker.recycle()
                self.mVelocityTracker = None
                self.mTranslationX = 0.0
                self.mDownX = 0
                self.mDownY = 0
                self.mSwiping = False
        elif action_masked == android_widgets.MotionEvent.ACTION_CANCEL:
            if self.mVelocityTracker is not None:
                self.mView.animate().translationX(0.0).alpha(1.0).setDuration(self.mAnimationTime) # .setListener(null);
                self.mVelocityTracker.recycle()
                self.mVelocityTracker = None
                self.mTranslationX = 0.0
                self.mDownX = 0
                self.mDownY = 0
                self.mSwiping = False
        elif action_masked == android_widgets.MotionEvent.ACTION_MOVE:
            if self.mVelocityTracker is not None:
                self.mVelocityTracker.addMovement(motionEvent)
                deltaX = float(motionEvent.getRawX() - self.mDownX)
                # Prevent a swipe to the left from moving us into swiping state.
                if deltaX < 0 and not self.mSwiping:
                    return True
            deltaY = motionEvent.getRawY() - self.mDownY
            if abs(deltaX) > self.mSlop and abs(deltaY) < abs(deltaX) / 2:
                self.mSwiping = True
                self.mSwipingSlop = (deltaX > 0 if self.mSlop else -self.mSlop) # TODO: wrong, just like the other ternary
                self.mView.getParent().requestDisallowInterceptTouchEvent(True)

            if self.mSwiping:
                self.mTranslationX = deltaX
                self.mView.setTranslationX(float(deltaX - self.mSwipingSlop))
        return False

    def _performDismiss(self):
        # Animate the dismissed view to zero-height and then fire the dismiss callback.
        # This triggers layout on each animation frame; in the future we may want to do something
        # smarter and more performant.
        layout_params = self.mView.getLayoutParams()
        originalHeight = self.mView.getHeight()

        animator = android_widgets.ValueAnimator.ofInt([originalHeight, 1]).setDuration(self.mAnimationTime)
        self._on_dismiss_callback()
        _unused = '''animator.addListener(new AnimatorListenerAdapter() {
            @Override
            public void onAnimationEnd(Animator animation) {
                mCallbacks.run();
                // Reset view presentation
                mView.setAlpha(1f);
                mView.setTranslationX(0);
                lp.height = originalHeight;
                mView.setLayoutParams(lp);
            }
        });'''

        _unused2 = '''animator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override
            public void onAnimationUpdate(ValueAnimator valueAnimator) {
                lp.height = (Integer) valueAnimator.getAnimatedValue();
                mView.setLayoutParams(lp);
            }
        });'''

        animator.start()


class OnRefreshListener(android_widgets.SwipeRefreshLayout__OnRefreshListener):
    def __init__(self, interface):
        super().__init__()
        self._interface = interface

    def onRefresh(self):
        if self._interface.on_refresh:
            self._interface.on_refresh(self._interface)

    def __del__(self):
        print("lol would delete it but i cant")


class DetailedList(Widget):
    _android_swipe_refresh_layout = None

    def create(self):
        # DetailedList is not a specific widget on Android, so we build it out
        # of a few pieces.

        if self.native is None:
            self.native = android_widgets.LinearLayout(self._native_activity)
            self.native.setOrientation(android_widgets.LinearLayout.VERTICAL)
        else:
            # If create() is called a second time, clear the widget and regenerate it.
            self.native.removeAllViews()

        scroll_view = android_widgets.ScrollView(self._native_activity)
        scroll_view_layout_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT,
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT
        )
        scroll_view_layout_params.gravity = android_widgets.Gravity.TOP
        swipe_refresh_wrapper = android_widgets.SwipeRefreshLayout(self._native_activity)
        swipe_refresh_wrapper.setOnRefreshListener(OnRefreshListener(self.interface))
        self._android_swipe_refresh_layout = android_widgets.SwipeRefreshLayout(
            __jni__=java.NewGlobalRef(swipe_refresh_wrapper))
        swipe_refresh_wrapper.addView(scroll_view)
        self.native.addView(swipe_refresh_wrapper, scroll_view_layout_params)
        dismissable_container = android_widgets.LinearLayout(self._native_activity)
        dismissable_container.setOrientation(android_widgets.LinearLayout.VERTICAL)
        dismissable_container_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT,
                android_widgets.LinearLayout__LayoutParams.MATCH_PARENT
        )
        scroll_view.addView(
                dismissable_container, dismissable_container_params
        )
        for i in range(len((self.interface.data or []))):
            self._make_row(dismissable_container, i)

    def _make_row(self, container, i):
        # Create a frame such that the background is behind the foreground.
        entire_row = android_widgets.FrameLayout(self._native_activity)
        container.addView(entire_row)

        # Create a background, so that when a user swipes the row away, they see the word "Delete".
        row_background = android_widgets.LinearLayout(self._native_activity)
        entire_row.addView(row_background)
        # <orig>
        row_background.setBackgroundColor(0xFFFF2222)  # Transparent pink
        # </orig>
        background_text = android_widgets.TextView(self._native_activity)
        background_text.setText("Delete")
        background_text.setTextSize(20.0)
        background_text_layout_params = android_widgets.LinearLayout__LayoutParams(
            android_widgets.LinearLayout__LayoutParams.MATCH_PARENT,
            android_widgets.LinearLayout__LayoutParams.MATCH_PARENT,
        )
        background_text_layout_params.setMarginStart(15)
        background_text.setGravity(android_widgets.Gravity.CENTER_VERTICAL)
        row_background.addView(background_text, background_text_layout_params)

        # Create the foreground.
        row_foreground = android_widgets.RelativeLayout(self._native_activity)
        # <good>
        row_foreground.setBackgroundColor(self._native_activity.getResources().getColor(
            android_widgets.R__color.background_light))
        # </good>
        # <test>
        #print(self.native.getResources()) # OK then.getColor(value.resourceId)
        #primary_color_id = self._native_activity.getResources().getIdentifier("colorPrimary", "color", self._native_activity.getApplicationContext().getPackageName())
        #primary_color = self._native_activity.getResources().getInteger(primary_color_id)
        row_foreground.setBackgroundColor(-328966)  # Default Android app background color, specifically 0xFFFAFAFA as a signed 32-bit int
        # </test>
        entire_row.addView(row_foreground)

        # Add user-provided icon to layout.
        icon_image_view = android_widgets.ImageView(self._native_activity)
        icon = self.interface.data[i].icon
        if icon is not None:
            icon.bind(self.interface.factory)
            bitmap = android_widgets.BitmapFactory.decodeFile(str(icon._impl.path))
            icon_image_view.setImageBitmap(bitmap)
        icon_layout_params = android_widgets.RelativeLayout__LayoutParams(
            android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
            android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT)
        icon_layout_params.width = 150
        icon_layout_params.setMargins(25, 0, 25, 0)
        icon_layout_params.height = 250
        icon_image_view.setScaleType(android_widgets.ImageView__ScaleType.FIT_CENTER)
        row_foreground.addView(icon_image_view, icon_layout_params)

        # Create layout to show top_text and bottom_text.
        text_container = android_widgets.LinearLayout(self._native_activity)
        text_container_params = android_widgets.RelativeLayout__LayoutParams(
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT)
        text_container_params.height = 250
        text_container_params.setMargins(25 + 25 + 150, 0, 0, 0)
        row_foreground.addView(text_container, text_container_params)
        text_container.setOrientation(android_widgets.LinearLayout.VERTICAL)
        text_container.setWeightSum(2.0)

        # Create top & bottom text; add them to layout.
        top_text = android_widgets.TextView(self._native_activity)
        top_text.setText(str(getattr(self.interface.data[i], 'title', '')))
        top_text.setTextSize(20.0)
        top_text.setTextColor(self._native_activity.getResources().getColor(android_widgets.R__color.black))
        bottom_text = android_widgets.TextView(self._native_activity)
        bottom_text.setTextColor(self._native_activity.getResources().getColor(android_widgets.R__color.black))
        bottom_text.setText(str(getattr(self.interface.data[i], 'subtitle', '')))
        bottom_text.setTextSize(16.0)
        top_text_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
                android_widgets.RelativeLayout__LayoutParams.MATCH_PARENT)
        top_text_params.weight = 1.0
        top_text.setGravity(android_widgets.Gravity.BOTTOM)
        text_container.addView(top_text, top_text_params)
        bottom_text_params = android_widgets.LinearLayout__LayoutParams(
                android_widgets.RelativeLayout__LayoutParams.WRAP_CONTENT,
                android_widgets.RelativeLayout__LayoutParams.MATCH_PARENT)
        bottom_text_params.weight = 1.0
        bottom_text.setGravity(android_widgets.Gravity.TOP)
        bottom_text_params.gravity = android_widgets.Gravity.TOP
        text_container.addView(bottom_text, bottom_text_params)

        # Apply an onclick listener so that clicking anywhere on the row triggers Toga's on_select(row).
        row_foreground.setOnClickListener(DetailedListOnClickListener(self, i))
        row_foreground.setOnTouchListener(_SwipeDismissTouchListener(row_foreground, lambda *args: print(args)))

    def change_source(self, source):
        # If the source changes, re-build the widget.
        self.create()

    def set_on_refresh(self, handler):
        # No special handling needed.
        pass

    def after_on_refresh(self):
        if self._android_swipe_refresh_layout:
            self._android_swipe_refresh_layout.setRefreshing(False)

    def insert(self, index, item):
        # If the data changes, re-build the widget.
        self.create()

    def change(self, item):
        # If the data changes, re-build the widget.
        self.create()

    def remove(self, item):
        # If the data changes, re-build the widget. Brutally effective.
        self.create()

    def clear(self):
        # If the data changes, re-build the widget.
        self.create()

    def get_selection(self):
        return None

    def set_on_select(self, handler):
        # No special handling required.
        pass

    def set_on_delete(self, handler):
        # This widget currently does not implement event handlers for data change.
        self.interface.factory.not_implemented("DetailedList.set_on_delete()")

    def scroll_to_row(self, row):
        # This widget cannot currently scroll to a specific row.
        self.interface.factory.not_implemented("DetailedList.scroll_to_row()")

    def rehint(self):
        # Android can crash when rendering some widgets until they have their layout params set. Guard for that case.
        if self.native.getLayoutParams() is None:
            return
        self.native.measure(
            android_widgets.View__MeasureSpec.UNSPECIFIED,
            android_widgets.View__MeasureSpec.UNSPECIFIED,
        )
        self.interface.intrinsic.width = at_least(self.native.getMeasuredWidth())
        self.interface.intrinsic.height = self.native.getMeasuredHeight()
