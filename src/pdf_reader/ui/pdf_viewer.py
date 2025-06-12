"""PDF viewer widget component."""

import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QStackedWidget,
    QSpacerItem, QSizePolicy, QApplication
)
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt, QSize, pyqtSignal

from ..core.models import ViewMode


class PDFViewer(QWidget):
    """Main PDF viewing widget with support for multiple view modes."""
    
    view_mode_changed = pyqtSignal(ViewMode)
    current_page_changed_in_continuous_scroll = pyqtSignal(int)

    def __init__(self, file_path=None):
        super().__init__()
        self.doc = None
        self.file_path = None
        self.current_page = 0
        self.zoom_factor = 1.0
        self._last_auto_zoom_level = 1.0
        self.view_mode = ViewMode.SINGLE_PAGE

        # --- New attributes for virtualization ---
        self._page_widgets = []  # Will hold widgets or None
        self._page_geometries = []  # Store calculated page sizes
        self._continuous_render_zoom = 1.0

        self._setup_ui()
        
        if file_path:
            self.load_pdf(file_path)

    def _setup_ui(self):
        """Initialize the user interface components."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.single_double_canvas = QLabel("Single/Double Canvas")
        self.single_double_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.single_double_canvas.setStyleSheet("background-color: #e0e0e0;")

        self.continuous_page_container = QWidget()
        self.continuous_page_layout = QVBoxLayout(self.continuous_page_container)
        self.continuous_page_layout.setContentsMargins(5, 5, 5, 5)
        self.continuous_page_layout.setSpacing(10)
        self.continuous_page_layout.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self.continuous_page_container.setStyleSheet("background-color: #d0d0d0;")

        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self.single_double_canvas)
        self.view_stack.addWidget(self.continuous_page_container)
        self.scroll_area.setWidget(self.view_stack)
        self.layout.addWidget(self.scroll_area)

        # Connect scroll events
        self.scroll_area.verticalScrollBar().valueChanged.connect(
            self._update_visible_pages
        )
        self.scroll_area.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        """Handle viewport resize events."""
        if source == self.scroll_area.viewport() and event.type() == event.Type.Resize:
            self._update_visible_pages()
        return super().eventFilter(source, event)

    def load_pdf(self, file_path):
        """Load a PDF file for viewing."""
        self.file_path = file_path
        try:
            self.doc = fitz.open(file_path)
            self.set_view_mode(ViewMode.SINGLE_PAGE, force_setup=True)
        except Exception as e:
            print(f"Error opening PDF {file_path}: {e}")
            self.single_double_canvas.setText("Could not load PDF.")
            self.view_stack.setCurrentWidget(self.single_double_canvas)

    def _clear_continuous_view(self):
        """Clear all widgets from continuous view layout."""
        while self.continuous_page_layout.count():
            item = self.continuous_page_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._page_widgets = []
        self._page_geometries = []

    def _update_visible_pages(self, value=None):
        """Update visible pages in continuous scroll mode for performance."""
        if (
            not self.doc
            or self.view_mode != ViewMode.CONTINUOUS_SCROLL
            or not self._page_widgets
        ):
            return

        viewport_rect = self.scroll_area.viewport().rect()

        # Determine which pages are visible
        visible_pages = set()
        current_y = self.continuous_page_layout.contentsMargins().top()

        for i in range(self.doc.page_count):
            page_height = self._page_geometries[i].height()
            spacing = self.continuous_page_layout.spacing()

            page_top = current_y
            page_bottom = current_y + page_height

            # Check if this page is in the visible area (with a buffer)
            if (
                page_bottom
                >= self.scroll_area.verticalScrollBar().value() - viewport_rect.height()
                and page_top
                <= self.scroll_area.verticalScrollBar().value()
                + viewport_rect.height() * 2
            ):
                visible_pages.add(i)

            current_y += page_height + spacing

        # Inflate visible pages that don't have a widget yet
        for i in sorted(list(visible_pages)):
            if self._page_widgets[i] is None:
                self._inflate_page(i)

        # Deflate pages that are no longer visible
        for i in range(self.doc.page_count):
            if i not in visible_pages and self._page_widgets[i] is not None:
                self._deflate_page(i)

        self._update_current_page_in_scroll_view()

    def _inflate_page(self, i):
        """Replace a spacer with a real, rendered page widget."""
        if (
            not self.doc
            or not (0 <= i < len(self._page_widgets))
            or self._page_widgets[i] is not None
        ):
            return

        size = self._page_geometries[i]
        page_label = QLabel()
        page_label.setFixedSize(size)
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Render the pixmap
        page = self.doc.load_page(i)
        mat = fitz.Matrix(self._continuous_render_zoom, self._continuous_render_zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(
            pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(img)
        page_label.setPixmap(pixmap)

        # Replace the spacer item with our new widget
        item = self.continuous_page_layout.takeAt(i)
        del item
        self.continuous_page_layout.insertWidget(i, page_label)
        self._page_widgets[i] = page_label

    def _deflate_page(self, i):
        """Replace a real widget with a lightweight spacer to save memory."""
        if not (0 <= i < len(self._page_widgets)) or self._page_widgets[i] is None:
            return

        widget = self._page_widgets[i]

        # Replace the widget with a spacer item
        self.continuous_page_layout.removeWidget(widget)
        widget.deleteLater()

        size = self._page_geometries[i]
        spacer = QSpacerItem(
            size.width(),
            size.height(),
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed,
        )
        self.continuous_page_layout.insertItem(i, spacer)

        self._page_widgets[i] = None

    def _update_current_page_in_scroll_view(self):
        """Update current page based on scroll position in continuous mode."""
        if self.view_mode != ViewMode.CONTINUOUS_SCROLL:
            return

        viewport_center = (
            self.scroll_area.verticalScrollBar().value()
            + self.scroll_area.viewport().height() / 2
        )

        current_y = self.continuous_page_layout.contentsMargins().top()
        best_page_idx = 0

        for i in range(self.doc.page_count):
            page_height = self._page_geometries[i].height()
            if current_y + page_height / 2 > viewport_center:
                break
            best_page_idx = i
            current_y += page_height + self.continuous_page_layout.spacing()

        if self.current_page != best_page_idx:
            self.current_page = best_page_idx
            self.current_page_changed_in_continuous_scroll.emit(self.current_page)

    def _setup_continuous_view(self):
        """Set up the continuous scroll view with virtualized pages."""
        if not self.doc:
            return

        self._clear_continuous_view()

        # Default to a fit-width zoom for performance on initial load.
        QApplication.processEvents()  # Ensure viewport has a size
        vp_width = self.scroll_area.viewport().width()
        if vp_width > 20:
            sample_page_rect = self.doc.load_page(self.current_page).bound()
            if sample_page_rect.width > 0:
                margins = self.continuous_page_layout.contentsMargins()
                available_width = (
                    vp_width - margins.left() - margins.right() - 20
                )  # Buffer for scrollbar
                self.zoom_factor = available_width / sample_page_rect.width
        else:
            self.zoom_factor = 1.0
        self._continuous_render_zoom = self.zoom_factor

        # Pre-calculate all page geometries but don't create widgets
        for i in range(self.doc.page_count):
            page_rect = self.doc.load_page(i).bound()
            width = int(page_rect.width * self._continuous_render_zoom)
            height = int(page_rect.height * self._continuous_render_zoom)
            self._page_geometries.append(QSize(width, height))
            self._page_widgets.append(None)  # Placeholder for not-yet-created widget

            # Add a lightweight spacer to represent the page in the layout
            spacer = QSpacerItem(
                width, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
            )
            self.continuous_page_layout.addSpacerItem(spacer)

        self.jump_to_page(self.current_page)

    def render_page(self):
        """Render the current page(s) for single and double page modes."""
        if not self.doc:
            self.single_double_canvas.clear()
            self.single_double_canvas.setText("Could not load PDF.")
            return

        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            self.view_stack.setCurrentWidget(self.continuous_page_container)
            return

        self.view_stack.setCurrentWidget(self.single_double_canvas)
        page_left = self.doc.load_page(self.current_page)
        page_rect_left = page_left.bound()
        vp_width = self.scroll_area.viewport().width()
        vp_height = self.scroll_area.viewport().height()
        current_render_zoom = self.zoom_factor

        if self.view_mode == ViewMode.FIT_PAGE:
            target_width = page_rect_left.width
            target_height = page_rect_left.height
            if (
                self.view_mode == ViewMode.DOUBLE_PAGE
                and self.current_page + 1 < self.doc.page_count
            ):
                page_rect_right = self.doc.load_page(self.current_page + 1).bound()
                target_width = page_rect_left.width + page_rect_right.width
                target_height = max(page_rect_left.height, page_rect_right.height)

            if (
                vp_width > 0
                and vp_height > 0
                and target_width > 0
                and target_height > 0
            ):
                zoom_x = vp_width / target_width
                zoom_y = vp_height / target_height
                current_render_zoom = min(zoom_x, zoom_y)
            else:
                current_render_zoom = 1.0
            self._last_auto_zoom_level = current_render_zoom
        elif self.view_mode == ViewMode.FIT_WIDTH:
            target_width = page_rect_left.width
            if (
                self.view_mode == ViewMode.DOUBLE_PAGE
                and self.current_page + 1 < self.doc.page_count
            ):
                page_rect_right = self.doc.load_page(self.current_page + 1).bound()
                target_width = page_rect_left.width + page_rect_right.width

            if vp_width > 0 and target_width > 0:
                current_render_zoom = vp_width / target_width
            else:
                current_render_zoom = 1.0
            self._last_auto_zoom_level = current_render_zoom
            
        mat = fitz.Matrix(current_render_zoom, current_render_zoom)
        pix_left = self.doc.load_page(self.current_page).get_pixmap(
            matrix=mat, alpha=False
        )
        final_pixmap = QPixmap()
        
        if (
            self.view_mode == ViewMode.DOUBLE_PAGE
            and self.current_page + 1 < self.doc.page_count
        ):
            pix_right = self.doc.load_page(self.current_page + 1).get_pixmap(
                matrix=mat, alpha=False
            )
            img_left_q = QPixmap()
            img_left_q.loadFromData(pix_left.tobytes("ppm"))
            img_right_q = QPixmap()
            img_right_q.loadFromData(pix_right.tobytes("ppm"))
            final_pixmap = QPixmap(
                img_left_q.width() + img_right_q.width(),
                max(img_left_q.height(), img_right_q.height()),
            )
            final_pixmap.fill(Qt.GlobalColor.white)
            painter = QPainter(final_pixmap)
            painter.drawPixmap(0, 0, img_left_q)
            painter.drawPixmap(img_left_q.width(), 0, img_right_q)
            painter.end()
        else:
            final_pixmap.loadFromData(pix_left.tobytes("ppm"))
            
        self.single_double_canvas.setPixmap(final_pixmap)
        self.single_double_canvas.adjustSize()

    def _set_view_mode_internal(self, mode: ViewMode):
        """Internal method to set view mode."""
        self.view_mode = mode

    def set_view_mode(self, mode: ViewMode, force_setup=False):
        """Set the view mode for the PDF viewer."""
        if not self.doc:
            return
        if self.view_mode == mode and not force_setup:
            return
            
        previous_mode = self.view_mode
        self._set_view_mode_internal(mode)

        if mode == ViewMode.CONTINUOUS_SCROLL:
            self.view_stack.setCurrentWidget(self.continuous_page_container)
            if previous_mode != ViewMode.CONTINUOUS_SCROLL or force_setup:
                self._setup_continuous_view()
        else:
            if previous_mode == ViewMode.CONTINUOUS_SCROLL:
                self._clear_continuous_view()
            self.view_stack.setCurrentWidget(self.single_double_canvas)
            
            self.single_double_canvas.clear()
            self.single_double_canvas.setPixmap(QPixmap())
            self.single_double_canvas.setText("")
            self.single_double_canvas.setStyleSheet("background-color: #e0e0e0;")
            QApplication.processEvents()
            
            if (
                mode == ViewMode.DOUBLE_PAGE
                and self.current_page % 2 != 0
                and self.current_page > 0
            ):
                self.current_page -= 1
                
            self.single_double_canvas.setText("Loading page...")
            QApplication.processEvents()
            
            try:
                self.render_page()
            except Exception as e:
                print(f"Error rendering page in view mode change: {e}")
                self.single_double_canvas.setText(
                    f"Error: Could not render page {self.current_page + 1}"
                )
                
            self.single_double_canvas.update()
            self.view_stack.update()
            self.scroll_area.update()
            self.update()
            QApplication.processEvents()

        self.view_mode_changed.emit(self.view_mode)

    def zoom_in(self):
        """Zoom in on the PDF."""
        if not self.doc:
            return

        if self.view_mode in [ViewMode.FIT_PAGE, ViewMode.FIT_WIDTH]:
            self.zoom_factor = self._last_auto_zoom_level

        self.zoom_factor *= 1.2

        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            # Re-setup the virtualized view with the new zoom
            self._setup_continuous_view()
        else:
            self._set_view_mode_internal(
                ViewMode.SINGLE_PAGE
                if self.view_mode != ViewMode.DOUBLE_PAGE
                else ViewMode.DOUBLE_PAGE
            )
            self.render_page()
        self.view_mode_changed.emit(self.view_mode)

    def zoom_out(self):
        """Zoom out on the PDF."""
        if not self.doc:
            return

        if self.view_mode in [ViewMode.FIT_PAGE, ViewMode.FIT_WIDTH]:
            self.zoom_factor = self._last_auto_zoom_level

        self.zoom_factor /= 1.2

        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            # Re-setup the virtualized view with the new zoom
            self._setup_continuous_view()
        else:
            self._set_view_mode_internal(
                ViewMode.SINGLE_PAGE
                if self.view_mode != ViewMode.DOUBLE_PAGE
                else ViewMode.DOUBLE_PAGE
            )
            self.render_page()
        self.view_mode_changed.emit(self.view_mode)

    def next_page(self):
        """Navigate to the next page."""
        if not self.doc:
            return
            
        page_increment = 2 if self.view_mode == ViewMode.DOUBLE_PAGE else 1
        if self.current_page < self.doc.page_count - page_increment:
            self.current_page += page_increment
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self.jump_to_page(self.current_page, force_scroll_continuous=True)
                self.current_page_changed_in_continuous_scroll.emit(self.current_page)
            else:
                self.render_page()
        elif (
            self.view_mode == ViewMode.DOUBLE_PAGE
            and self.current_page == self.doc.page_count - 2
            and self.doc.page_count % 2 == 1
        ):
            # Special case for double page, if on second to last and total is odd, can go to last single page
            self.current_page += 1
            self.render_page()
        elif (
            self.view_mode != ViewMode.DOUBLE_PAGE
            and self.current_page < self.doc.page_count - 1
        ):
            self.current_page += 1
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self.jump_to_page(self.current_page, force_scroll_continuous=True)
                self.current_page_changed_in_continuous_scroll.emit(self.current_page)
            else:
                self.render_page()

    def prev_page(self):
        """Navigate to the previous page."""
        if not self.doc:
            return
            
        page_decrement = 2 if self.view_mode == ViewMode.DOUBLE_PAGE else 1
        if self.current_page > 0:
            self.current_page = max(0, self.current_page - page_decrement)
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self.jump_to_page(self.current_page, force_scroll_continuous=True)
                self.current_page_changed_in_continuous_scroll.emit(self.current_page)
            else:
                self.render_page()

    def jump_to_page(self, page_num, force_scroll_continuous=False):
        """Jump to a specific page number."""
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return

        self.current_page = page_num
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            # Calculate y position of the target page
            target_y = self.continuous_page_layout.contentsMargins().top()
            for i in range(page_num):
                target_y += (
                    self._page_geometries[i].height()
                    + self.continuous_page_layout.spacing()
                )

            self.scroll_area.verticalScrollBar().setValue(int(target_y))
            QApplication.processEvents()  # Ensure scroll happens before update
            self._update_visible_pages()
            self.current_page_changed_in_continuous_scroll.emit(self.current_page)
        else:
            if self.view_mode == ViewMode.DOUBLE_PAGE:
                if self.current_page % 2 != 0:
                    self.current_page = max(0, self.current_page - 1)
            self.render_page()

    def get_toc(self):
        """Get the table of contents for the PDF."""
        if not self.doc:
            return []
        return self.doc.get_toc()
