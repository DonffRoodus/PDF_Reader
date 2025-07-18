#!/usr/bin/env python3
"""
DEPRECATED: Legacy single-file PDF Reader

This file contains the original single-file implementation of the PDF Reader.
For the improved modular structure, please use app.py instead.

Run: python app.py
"""

import sys
import warnings

# Show deprecation warning
warnings.warn(
    "main.py is deprecated. Please use 'python app.py' for the improved modular version.",
    DeprecationWarning,
    stacklevel=2
)

print("=" * 60)
print("DEPRECATED: This is the legacy single-file version")
print("For the improved modular structure, please run:")
print("  python app.py")
print("=" * 60)
print()

# Original imports and code below this line
import sys
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QTabWidget,
    QPushButton,
    QHBoxLayout,
    QToolBar,
    QToolButton,
    QLabel,
    QLineEdit,
    QListView,
    QDockWidget,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QStackedWidget,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtGui import (
    QAction,
    QIcon,
    QPixmap,
    QPainter,
    QColor,
    QActionGroup,
    QImage,
)  # Added QImage
from PyQt6.QtCore import Qt, QSize, QUrl, pyqtSignal
import fitz  # PyMuPDF
import os


class ViewMode(Enum):
    SINGLE_PAGE = 1  # Default, respects manual zoom_factor
    FIT_PAGE = 2  # Zooms to fit entire page in view
    FIT_WIDTH = 3  # Zooms to fit page width in view
    DOUBLE_PAGE = 4  # Shows two pages side-by-side
    CONTINUOUS_SCROLL = 5  # All pages in a long scrollable view
    # Future: CONTINUOUS_DOUBLE_PAGE


class PDFViewer(QWidget):
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

        self.scroll_area.verticalScrollBar().valueChanged.connect(
            self._update_visible_pages
        )
        # Also connect to resize events to update visible pages
        self.scroll_area.viewport().installEventFilter(self)

        if file_path:
            self.load_pdf(file_path)

    def eventFilter(self, source, event):
        if source == self.scroll_area.viewport() and event.type() == event.Type.Resize:
            self._update_visible_pages()
        return super().eventFilter(source, event)

    def load_pdf(self, file_path):
        self.file_path = file_path
        try:
            self.doc = fitz.open(file_path)
            self.set_view_mode(ViewMode.SINGLE_PAGE, force_setup=True)
        except Exception as e:
            print(f"Error opening PDF {file_path}: {e}")
            self.single_double_canvas.setText("Could not load PDF.")
            self.view_stack.setCurrentWidget(self.single_double_canvas)

    def _clear_continuous_view(self):
        while self.continuous_page_layout.count():
            item = self.continuous_page_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._page_widgets = []
        self._page_geometries = []

    def _update_visible_pages(self, value=None):
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
        """Replaces a spacer with a real, rendered page widget."""
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
        """Replaces a real widget with a lightweight spacer to save memory."""
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

    def render_page(self):  # Handles SINGLE and DOUBLE page modes
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
            # ... (rest of this method is unchanged)
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
        self.view_mode = mode

    def set_view_mode(self, mode: ViewMode, force_setup=False):
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
            # ... (rest of method is unchanged)
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
            # ... (rest of method is unchanged)
            if self.view_mode == ViewMode.DOUBLE_PAGE:
                if self.current_page % 2 != 0:
                    self.current_page = max(0, self.current_page - 1)
            self.render_page()

    def get_toc(self):
        if not self.doc:
            return []
        return self.doc.get_toc()

    def _handle_continuous_scroll(self, value):
        if (
            not self.doc
            or self.view_mode != ViewMode.CONTINUOUS_SCROLL
            or not self._page_labels_continuous
        ):
            return

        # Trigger lazy loading of visible pages
        self._render_visible_pages_continuous()

        best_page_idx = self.current_page
        min_abs_diff = float("inf")

        visible_top_y = self.scroll_area.verticalScrollBar().value()
        viewport_height = self.scroll_area.viewport().height()
        visible_bottom_y = visible_top_y + viewport_height

        # Try to find the page that occupies the most space in the viewport, or the topmost visible
        for i, label in enumerate(self._page_labels_continuous):
            label_y_pos = label.y()
            label_height = label.height()
            label_bottom_y_pos = label_y_pos + label_height

            # Check if this label is visible in the viewport
            if label_bottom_y_pos > visible_top_y and label_y_pos < visible_bottom_y:
                diff = abs(label_y_pos - visible_top_y)
                if (
                    label_y_pos >= visible_top_y
                ):  # Page starts at or below the viewport top
                    if diff < min_abs_diff:  # Closest to the top
                        min_abs_diff = diff
                        best_page_idx = i
                elif (
                    label_bottom_y_pos > visible_top_y + viewport_height / 4
                ):  # Or if a good chunk of it is showing from top
                    if (
                        best_page_idx == self.current_page
                    ):  # Prioritize if no better top page found yet
                        best_page_idx = i

            # More robust: if a page top is within the viewport, it's a strong candidate
            if label_y_pos >= visible_top_y and label_y_pos < visible_bottom_y:
                if (
                    abs(label_y_pos - visible_top_y) < min_abs_diff
                ):  # Check if it's the closest to top
                    min_abs_diff = abs(label_y_pos - visible_top_y)
                    best_page_idx = i
                    # Optimization: if a page starts exactly at or very near the top, it's likely the one.
                    if min_abs_diff < 20:  # Small threshold
                        break

        if self.current_page != best_page_idx:
            self.current_page = best_page_idx
            self.current_page_changed_in_continuous_scroll.emit(self.current_page)

    def _render_pages_around_current(self):
        """Render the current page and a few pages around it"""
        if not self.doc or not self._page_labels_continuous:
            return

        # Render current page ± 2 pages for better performance
        start_page = max(0, self.current_page - 2)
        end_page = min(self.doc.page_count, self.current_page + 3)

        for i in range(start_page, end_page):
            self._render_single_page_continuous(i)

    def _render_single_page_continuous(self, page_idx):
        """Render a single page in continuous view"""
        if (
            page_idx < 0
            or page_idx >= len(self._page_labels_continuous)
            or page_idx in self._rendered_pages
        ):
            return
        try:
            page = self.doc.load_page(page_idx)
            mat = fitz.Matrix(
                self._continuous_render_zoom, self._continuous_render_zoom
            )
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(img)

            page_label = self._page_labels_continuous[page_idx]

            # Adjust label size to match actual page dimensions if different from template
            page_rect = page.bound()
            actual_width = int(page_rect.width * self._continuous_render_zoom)
            actual_height = int(page_rect.height * self._continuous_render_zoom)
            if (
                page_label.width() != actual_width
                or page_label.height() != actual_height
            ):
                page_label.setFixedSize(actual_width, actual_height)

            page_label.setPixmap(pixmap)
            page_label.setText("")  # Clear placeholder text
            page_label.setStyleSheet("")  # Clear placeholder styling

            self._rendered_pages.add(page_idx)
        except Exception as e:
            print(f"Error rendering page {page_idx}: {e}")

    def _render_visible_pages_continuous(self):
        """Render pages that are currently visible in the viewport"""
        if not self.doc or not self._page_labels_continuous:
            return

        # Get visible area
        visible_top = self.scroll_area.verticalScrollBar().value()
        viewport_height = self.scroll_area.viewport().height()
        visible_bottom = visible_top + viewport_height

        # Add some buffer for smooth scrolling
        buffer = viewport_height // 2
        render_top = max(0, visible_top - buffer)
        render_bottom = visible_bottom + buffer

        for i, label in enumerate(self._page_labels_continuous):
            label_top = label.y()
            label_bottom = label_top + label.height()

            # Check if page intersects with render area
            if (
                label_bottom > render_top
                and label_top < render_bottom
                and i not in self._rendered_pages
            ):
                self._render_single_page_continuous(i)

    # ...existing code...


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Reader")
        self.setGeometry(100, 100, 1200, 800)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)  # Connect here
        self.setCentralWidget(self.tab_widget)

        self.create_menus_and_toolbar()
        self.create_dock_widgets()

        self.recent_files = []  # For simplicity, store in memory
        self.load_recent_files()
        self.update_view_menu_state()  # Initial state when no tabs might be open

    def change_view_mode(self, mode: ViewMode):
        current_viewer = self.tab_widget.currentWidget()
        if isinstance(current_viewer, PDFViewer):
            current_viewer.set_view_mode(mode)
            # The PDFViewer's set_view_mode emits view_mode_changed,
            # which should be connected to MainWindow's update_view_menu_state.

    def create_menus_and_toolbar(self):
        # File Menu
        file_menu = self.menuBar().addMenu("&File")
        open_action = QAction(QIcon.fromTheme("document-open"), "&Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        self.recent_files_menu = file_menu.addMenu("Recent Files")

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu for View Modes
        view_mode_menu = self.menuBar().addMenu(
            "&View Modes"
        )  # Renamed for clarity if "View" is used by docks
        self.view_mode_group = QActionGroup(self)
        self.view_mode_group.setExclusive(True)

        self.single_page_action = QAction("Single Page", self, checkable=True)
        self.single_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.SINGLE_PAGE)
        )
        view_mode_menu.addAction(self.single_page_action)
        self.view_mode_group.addAction(self.single_page_action)

        self.fit_page_action = QAction("Fit Page", self, checkable=True)
        self.fit_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.FIT_PAGE)
        )
        view_mode_menu.addAction(self.fit_page_action)
        self.view_mode_group.addAction(self.fit_page_action)

        self.fit_width_action = QAction("Fit Width", self, checkable=True)
        self.fit_width_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.FIT_WIDTH)
        )
        view_mode_menu.addAction(self.fit_width_action)
        self.view_mode_group.addAction(self.fit_width_action)

        self.double_page_action = QAction("Double Page", self, checkable=True)
        self.double_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.DOUBLE_PAGE)
        )
        view_mode_menu.addAction(self.double_page_action)
        self.view_mode_group.addAction(self.double_page_action)

        self.continuous_scroll_action = QAction(
            "Continuous Scroll", self, checkable=True
        )
        self.continuous_scroll_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.CONTINUOUS_SCROLL)
        )
        view_mode_menu.addAction(self.continuous_scroll_action)
        self.view_mode_group.addAction(self.continuous_scroll_action)

        self.single_page_action.setChecked(True)  # Default

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction(open_action)

        self.prev_page_action = QAction(
            QIcon.fromTheme("go-previous"), "Previous Page", self
        )
        self.prev_page_action.triggered.connect(self.prev_page)
        toolbar.addAction(self.prev_page_action)

        self.next_page_action = QAction(QIcon.fromTheme("go-next"), "Next Page", self)
        self.next_page_action.triggered.connect(self.next_page)
        toolbar.addAction(self.next_page_action)

        self.zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Zoom In", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(self.zoom_out_action)

        self.page_num_input = QLineEdit()
        self.page_num_input.setFixedWidth(50)
        self.page_num_input.returnPressed.connect(self.go_to_page_from_input)
        toolbar.addWidget(QLabel("Page:"))
        toolbar.addWidget(self.page_num_input)

        self.total_pages_label = QLabel("/ N/A")
        toolbar.addWidget(self.total_pages_label)

    def create_dock_widgets(self):
        # Panels Menu (was View Menu for docks)
        panels_menu = self.menuBar().addMenu("&Panels")  # Renamed from "View"

        # Table of Contents Dock
        self.toc_dock = QDockWidget("Table of Contents", self)
        self.toc_list_widget = QListWidget()
        self.toc_list_widget.itemClicked.connect(self.toc_navigate)
        self.toc_dock.setWidget(self.toc_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.toc_dock)
        self.toc_dock.setVisible(False)

        # Bookmarks Dock (Placeholder)
        self.bookmarks_dock = QDockWidget("Bookmarks", self)
        self.bookmarks_list_widget = QListWidget()
        self.bookmarks_dock.setWidget(self.bookmarks_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.bookmarks_dock)
        self.bookmarks_dock.setVisible(False)

        # Add toggle actions to the 'Panels' menu
        toggle_toc_action = QAction("Toggle Table of Contents", self)
        toggle_toc_action.setCheckable(True)
        toggle_toc_action.setChecked(False)
        toggle_toc_action.triggered.connect(
            self.toc_dock.setVisible
        )  # Connect directly
        self.toc_dock.visibilityChanged.connect(
            toggle_toc_action.setChecked
        )  # Sync check state
        panels_menu.addAction(toggle_toc_action)

        toggle_bookmarks_action = QAction("Toggle Bookmarks", self)
        toggle_bookmarks_action.setCheckable(True)
        toggle_bookmarks_action.setChecked(False)
        toggle_bookmarks_action.triggered.connect(
            self.bookmarks_dock.setVisible
        )  # Connect directly
        self.bookmarks_dock.visibilityChanged.connect(
            toggle_bookmarks_action.setChecked
        )  # Sync check state
        panels_menu.addAction(toggle_bookmarks_action)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.add_pdf_tab(file_path)
            self.add_to_recent_files(file_path)

    def add_pdf_tab(self, file_path):
        viewer = PDFViewer(file_path)
        viewer.view_mode_changed.connect(self.update_view_menu_state)
        viewer.current_page_changed_in_continuous_scroll.connect(
            self.update_page_info_from_signal
        )  # New connection

        tab_index = self.tab_widget.addTab(viewer, os.path.basename(file_path))
        self.tab_widget.setCurrentIndex(tab_index)
        # on_tab_changed will be called, which calls update_page_info, update_toc, update_view_menu_state

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            widget.deleteLater()
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.total_pages_label.setText("/ N/A")
            self.page_num_input.clear()
            self.toc_list_widget.clear()

    def current_viewer(self) -> PDFViewer | None:
        return self.tab_widget.currentWidget()

    def next_page(self):
        viewer = self.current_viewer()
        if viewer:
            viewer.next_page()
            self.update_page_info()

    def prev_page(self):
        viewer = self.current_viewer()
        if viewer:
            viewer.prev_page()
            self.update_page_info()

    def zoom_in(self):
        viewer = self.current_viewer()
        if viewer:
            viewer.zoom_in()

    def zoom_out(self):
        viewer = self.current_viewer()
        if viewer:
            viewer.zoom_out()

    def go_to_page_from_input(self):
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            try:
                page_num = int(self.page_num_input.text()) - 1  # User sees 1-based
                if 0 <= page_num < viewer.doc.page_count:
                    viewer.jump_to_page(page_num)
                    self.update_page_info()
                else:
                    self.page_num_input.setText(str(viewer.current_page + 1))
            except ValueError:
                self.page_num_input.setText(str(viewer.current_page + 1))

    def update_page_info(self):
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            current_display_page = viewer.current_page
            # For double page, current_page is the left page.
            # Display could be "L" or "L-R"
            page_text = str(current_display_page + 1)
            if (
                viewer.view_mode == ViewMode.DOUBLE_PAGE
                and current_display_page + 1 < viewer.doc.page_count
            ):
                page_text = f"{current_display_page + 1}-{current_display_page + 2}"

            self.page_num_input.setText(page_text)
            self.total_pages_label.setText(f"/ {viewer.doc.page_count}")
        else:
            self.page_num_input.clear()
            self.total_pages_label.setText("/ N/A")

    def update_toc(self):
        self.toc_list_widget.clear()
        viewer = self.current_viewer()
        if viewer:
            toc = viewer.get_toc()
            for level, title, page_num in toc:
                item = QListWidgetItem(f"{'  ' * (level-1)}{title} (Page {page_num})")
                item.setData(
                    Qt.ItemDataRole.UserRole, page_num - 1
                )  # Store 0-based page num
                self.toc_list_widget.addItem(item)

    def toc_navigate(self, item):
        viewer = self.current_viewer()
        if viewer:
            page_num = item.data(Qt.ItemDataRole.UserRole)
            viewer.jump_to_page(page_num)
            self.update_page_info()

    def add_to_recent_files(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep last 10
        self.update_recent_files_menu()
        # TODO: Persist recent files (e.g., to a settings file)

    def load_recent_files(self):
        # TODO: Load from a settings file
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        self.recent_files_menu.clear()
        for file_path in self.recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.triggered.connect(self.open_recent_file)
            self.recent_files_menu.addAction(action)

    def open_recent_file(self):
        action = self.sender()
        if action:
            file_path = action.data()
            self.add_pdf_tab(file_path)

    def on_tab_changed(self, index):  # Ensure this is connected in __init__
        self.update_page_info()  # Update based on viewer's current_page
        self.update_toc()
        current_viewer = self.current_viewer()
        if current_viewer:
            # Disconnect old signals if any robustly, or ensure fresh connections
            # For simplicity, assuming new viewer or re-connecting is fine
            try:  # viewer.view_mode_changed.disconnect(self.update_view_menu_state) # Example disconnect
                # viewer.current_page_changed_in_continuous_scroll.disconnect(self.update_page_info_from_signal)
                pass
            except TypeError:
                pass

            current_viewer.view_mode_changed.connect(self.update_view_menu_state)
            current_viewer.current_page_changed_in_continuous_scroll.connect(
                self.update_page_info_from_signal
            )
            self.update_view_menu_state(current_viewer.view_mode)  # Pass current mode
        else:
            self.update_view_menu_state()  # No viewer, update menu to disabled/default state
            self.update_page_info()  # Clear page info

    def update_page_info_from_signal(self, page_num):
        # This is specifically for updates from continuous scroll where current_page is set internally
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            self.page_num_input.setText(str(page_num + 1))  # page_num is 0-indexed
            # total_pages_label is usually static per doc, updated in update_page_info
        elif not viewer:
            self.page_num_input.clear()
            self.total_pages_label.setText("/ N/A")

    def update_view_menu_state(self, active_mode: ViewMode | None = None):
        # ... (logic for enabling/disabling and checking menu items)
        viewer = self.current_viewer()
        if active_mode is None:  # If not directly passed, get from viewer
            if viewer:
                active_mode = viewer.view_mode
            else:  # No active viewer
                self.single_page_action.setChecked(True)  # Default
                for act in [
                    self.single_page_action,
                    self.fit_page_action,
                    self.fit_width_action,
                    self.double_page_action,
                    self.continuous_scroll_action,
                ]:
                    act.setEnabled(False)
                return

        for act in [
            self.single_page_action,
            self.fit_page_action,
            self.fit_width_action,
            self.double_page_action,
            self.continuous_scroll_action,
        ]:
            act.setEnabled(
                True if viewer and viewer.doc else False
            )  # Enable only if doc loaded

        if not (viewer and viewer.doc):  # If no doc, set default and return
            self.single_page_action.setChecked(True)
            return

        actions_map = {
            ViewMode.SINGLE_PAGE: self.single_page_action,
            ViewMode.FIT_PAGE: self.fit_page_action,
            ViewMode.FIT_WIDTH: self.fit_width_action,
            ViewMode.DOUBLE_PAGE: self.double_page_action,
            ViewMode.CONTINUOUS_SCROLL: self.continuous_scroll_action,
        }

        checked_action = actions_map.get(active_mode, self.single_page_action)
        checked_action.setChecked(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        viewer = self.current_viewer()
        if viewer and viewer.doc:  # Check if doc is loaded
            if (
                viewer.view_mode in [ViewMode.FIT_PAGE, ViewMode.FIT_WIDTH]
                and viewer.view_mode != ViewMode.CONTINUOUS_SCROLL
            ):
                viewer.render_page()  # Re-apply fit for single/double
            elif (
                viewer.view_mode == ViewMode.CONTINUOUS_SCROLL
                and viewer.view_mode == ViewMode.FIT_WIDTH
            ):  # Or just FIT_WIDTH for continuous
                # For continuous FIT_WIDTH, a full rebuild is needed as zoom_factor for all pages changes
                # We need to recalculate the base zoom_factor for FIT_WIDTH
                vp_width = viewer.scroll_area.viewport().width()
                # A representative page (e.g. current) for width calculation
                page_rect = viewer.doc.load_page(viewer.current_page).bound()
                if vp_width > 0 and page_rect.width > 0:
                    viewer.zoom_factor = (
                        vp_width - viewer.scroll_area.verticalScrollBar().width()
                    ) / page_rect.width
                else:
                    viewer.zoom_factor = 1.0
                viewer._setup_continuous_view()
            elif viewer.view_mode == ViewMode.CONTINUOUS_SCROLL:
                # For continuous scroll without explicit FIT_WIDTH, pages just reflow.
                # However, if any page was rendered with a fit-to-old-width, it might look odd.
                # A simple approach is to re-setup if width changed significantly.
                # For now, let's assume manual zoom in continuous is preserved unless FIT_WIDTH is active.
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply a simple, clean stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0; /* Light gray background */
        }
        QTabWidget::pane {
            border-top: 2px solid #C2C7CB;
            background: white;
        }
        QTabBar::tab {
            background: #e0e0e0; /* Lighter gray for inactive tabs */
            border: 1px solid #C2C7CB;
            border-bottom-color: #C2C7CB; /* Same as pane border color */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 8ex;
            padding: 5px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: white; /* White for active tab */
            border-color: #9B9B9B;
            border-bottom-color: white; /* Make it look like it's part of the pane */
        }
        QTabBar::tab:!selected:hover {
            background: #d0d0d0; /* Slightly darker on hover for inactive tabs */
        }
        QToolBar {
            background: #e8e8e8; /* Slightly darker toolbar */
            border: 1px solid #C2C7CB;
            spacing: 3px; /* Space between items */
        }
        QPushButton, QToolButton {
            background-color: #dcdcdc; /* Light silver */
            border: 1px solid #c0c0c0; /* Silver border */
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover, QToolButton:hover {
            background-color: #c8c8c8; /* Darker silver on hover */
        }
        QPushButton:pressed, QToolButton:pressed {
            background-color: #b0b0b0; /* Even darker when pressed */
        }
        QLabel, QLineEdit {
            padding: 2px;
        }
        QDockWidget {
            titlebar-close-icon: url(close.png); /* Placeholder for icons */
            titlebar-normal-icon: url(float.png); /* Placeholder for icons */
            font-weight: bold;
        }
        QDockWidget::title {
            text-align: left; /* Align the title to the left */
            background: #e0e0e0;
            padding: 5px;
            border: 1px solid #C2C7CB;
        }
        QListView, QListWidget {
            background-color: white;
            border: 1px solid #C2C7CB;
        }
    """)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
