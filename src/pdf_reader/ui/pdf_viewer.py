"""PDF viewer widget component."""

import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QStackedWidget,
    QSpacerItem, QSizePolicy, QApplication, QInputDialog
)
from PyQt6.QtGui import QPixmap, QPainter, QImage, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QRect

from ..core.models import ViewMode, Bookmark, AnnotationType, Annotation


class PDFViewer(QWidget):
    """Main PDF viewing widget with support for multiple view modes."""
    
    view_mode_changed = pyqtSignal(ViewMode)
    current_page_changed_in_continuous_scroll = pyqtSignal(int)
    bookmarks_changed = pyqtSignal()  # Emitted when bookmarks are added/removed
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
        
        # --- Bookmark management ---
        self._bookmarks = []  # List of Bookmark objects for this document
          # --- Annotation management ---
        self.active_annotation_type = None
        self.annotation_start_point = None
        self.annotations = []
        self.is_annotating = False
        self.annotation_mode_enabled = False  # New: require explicit mode activation
        self._current_annotation_page = 0
        self._page_labels_continuous = [None] * (self.doc.page_count if self.doc else 0)

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
        """Handle viewport resize events and annotation interactions."""
        # Handle resize events
        if source == self.scroll_area.viewport() and event.type() == event.Type.Resize:
            self._update_visible_pages()
            return super().eventFilter(source, event)
          # Handle annotation events
        if not self.doc:
            return super().eventFilter(source, event)
            
        if event.type() == event.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton and self.active_annotation_type and self.annotation_mode_enabled and not self.is_annotating:
                self.is_annotating = True
                # Get the correct position on the PDF page
                self.annotation_start_point = self._get_pdf_position(source, event.pos())
                if source != self.single_double_canvas and source != self.continuous_page_container:
                    page_idx = self._page_labels_continuous.index(source) if source in self._page_labels_continuous else self.current_page
                    self._current_annotation_page = page_idx
                else:
                    self._current_annotation_page = self.current_page
                return True
            elif event.button() == Qt.MouseButton.RightButton:
                # Handle right-click for annotation deletion
                self._handle_annotation_right_click(source, event.pos())
                return True
        elif event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton and self.is_annotating:
            # Get the correct end position using the same coordinate mapping
            end_point = self._get_pdf_position(source, event.pos())
            
            if self.active_annotation_type == AnnotationType.TEXT:
                text, ok = QInputDialog.getText(self, "Text Annotation", "Enter annotation text:")
                if ok and text:
                    self.annotations.append(Annotation(
                        AnnotationType.TEXT,
                        self._current_annotation_page,
                        self.annotation_start_point,
                        text=text
                    ))
            else:
                self.annotations.append(Annotation(
                    self.active_annotation_type,
                    self._current_annotation_page,
                    self.annotation_start_point,
                    end_point
                ))
            
            self.is_annotating = False
            self.annotation_start_point = None
            self._redraw_page(self._current_annotation_page)
            return True
            
        elif event.type() == event.Type.MouseMove and self.is_annotating and self.active_annotation_type != AnnotationType.TEXT:
            self._redraw_page(self._current_annotation_page, preview=True, preview_end=event.pos())
            return True
        return super().eventFilter(source, event)

    def load_pdf(self, file_path):
        """Load a PDF file for viewing."""
        self.file_path = file_path
        try:
            self.doc = fitz.open(file_path)
            self._page_labels_continuous = [None] * self.doc.page_count
            self._setup_annotation_event_filters()
            self.set_view_mode(ViewMode.SINGLE_PAGE, force_setup=True)
        except Exception as e:
            print(f"Error opening PDF {file_path}: {e}")
            self.single_double_canvas.setText("Could not load PDF.")
            self.view_stack.setCurrentWidget(self.single_double_canvas)
    
    def _setup_annotation_event_filters(self):
        """Set up event filters for annotation handling."""
        if self.doc:
            self.single_double_canvas.installEventFilter(self)
            self.continuous_page_container.installEventFilter(self)

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
        
        # Render the pixmap with annotations
        page = self.doc.load_page(i)
        mat = fitz.Matrix(self._continuous_render_zoom, self._continuous_render_zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(
            pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(img)
        
        # Draw annotations on the pixmap
        painter = QPainter(pixmap)
        self._draw_annotations(painter, i, False, None)
        painter.end()
        
        page_label.setPixmap(pixmap)

        # Replace the spacer item with our new widget
        item = self.continuous_page_layout.takeAt(i)
        del item
        self.continuous_page_layout.insertWidget(i, page_label)
        self._page_widgets[i] = page_label
        
        # Set up event filter for annotations and update tracking array
        page_label.installEventFilter(self)
        self._page_labels_continuous[i] = page_label
        
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
        # Also clear from the tracking array
        if i < len(self._page_labels_continuous):
            self._page_labels_continuous[i] = None

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
                self.render_page_with_annotations()
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
            # Use annotation-aware rendering
            self.render_page_with_annotations()
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
            # Use annotation-aware rendering
            self.render_page_with_annotations()
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
                self.render_page_with_annotations()
        elif (
            self.view_mode == ViewMode.DOUBLE_PAGE
            and self.current_page == self.doc.page_count - 2
            and self.doc.page_count % 2 == 1
        ):
            # Special case for double page, if on second to last and total is odd, can go to last single page
            self.current_page += 1
            self.render_page_with_annotations()
        elif (
            self.view_mode != ViewMode.DOUBLE_PAGE
            and self.current_page < self.doc.page_count - 1
        ):
            self.current_page += 1
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self.jump_to_page(self.current_page, force_scroll_continuous=True)
                self.current_page_changed_in_continuous_scroll.emit(self.current_page)
            else:
                self.render_page_with_annotations()

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
                self.render_page_with_annotations()

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
            self.render_page_with_annotations()

    def get_toc(self):
        """Get the table of contents for the PDF."""
        if not self.doc:
            return []
        return self.doc.get_toc()
    
    # Bookmark functionality
    def add_bookmark(self, title: str = None, page_number: int = None) -> bool:
        """Add a bookmark for the current or specified page."""
        if not self.doc or not self.file_path:
            return False
            
        page_num = page_number if page_number is not None else self.current_page
        
        # Validate page number
        if not (0 <= page_num < self.doc.page_count):
            return False
            
        # Generate default title if not provided
        if not title:
            title = f"Page {page_num + 1}"
            
        # Check if bookmark already exists for this page
        for bookmark in self._bookmarks:
            if bookmark.page_number == page_num:
                return False  # Don't add duplicate bookmark
                
        # Create and add bookmark
        from datetime import datetime
        bookmark = Bookmark(
            title=title,
            page_number=page_num,
            file_path=self.file_path,
            created_at=datetime.now().isoformat()
        )
        
        self._bookmarks.append(bookmark)
        self._bookmarks.sort(key=lambda b: b.page_number)  # Keep sorted by page
        
        self.bookmarks_changed.emit()
        return True
    
    def remove_bookmark(self, page_number: int) -> bool:
        """Remove bookmark for the specified page."""
        for i, bookmark in enumerate(self._bookmarks):
            if bookmark.page_number == page_number:
                del self._bookmarks[i]
                self.bookmarks_changed.emit()
                return True
        return False
    
    def get_bookmarks(self) -> list[Bookmark]:
        """Get all bookmarks for this document."""
        return self._bookmarks.copy()
    
    def has_bookmark(self, page_number: int) -> bool:
        """Check if a page has a bookmark."""
        return any(b.page_number == page_number for b in self._bookmarks)
    
    def jump_to_bookmark(self, bookmark: Bookmark):
        """Jump to a specific bookmark."""
        if bookmark.file_path == self.file_path:
            self.jump_to_page(bookmark.page_number)
    
    # Annotation functionality
    def _redraw_all_pages(self):
        """Redraw all pages to update annotations across the entire document."""
        if not self.doc:
            return
            
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            # In continuous scroll, redraw all currently inflated pages
            for i in range(self.doc.page_count):
                if i < len(self._page_widgets) and self._page_widgets[i] is not None:
                    self._render_page_with_annotations(i, False, None)
        else:
            # In single/double page mode, just redraw the current view
            self.render_page_with_annotations()

    def _redraw_page(self, page_idx, preview=False, preview_end=None):
        """Redraw a page with annotations."""
        if not self.doc or page_idx < 0 or page_idx >= self.doc.page_count:
            return
            
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            if page_idx < len(self._page_widgets) and self._page_widgets[page_idx]:
                self._render_page_with_annotations(page_idx, preview, preview_end)
        else:
            self.render_page_with_annotations(preview, preview_end)
    
    def render_page_with_annotations(self, preview=False, preview_end=None):
        """Render the current page with annotations for single/double page modes."""
        self.render_page()  # Call the original render_page method
        pixmap = self.single_double_canvas.pixmap()
        if not pixmap or pixmap.isNull():
            return
            
        painter = QPainter(pixmap)
        self._draw_annotations(painter, self.current_page, preview, preview_end)
        if self.view_mode == ViewMode.DOUBLE_PAGE and self.current_page + 1 < self.doc.page_count:
            offset_x = int(self.doc.load_page(self.current_page).bound().width * self.zoom_factor)
            painter.translate(offset_x, 0)
            self._draw_annotations(painter, self.current_page + 1, preview, preview_end)
        painter.end()
        self.single_double_canvas.setPixmap(pixmap)
    
    def _render_page_with_annotations(self, page_idx, preview=False, preview_end=None):
        """Render a specific page with annotations for continuous scroll mode."""
        if page_idx >= len(self._page_widgets) or not self._page_widgets[page_idx]:
            return
            
        page = self.doc.load_page(page_idx)
        mat = fitz.Matrix(self._continuous_render_zoom, self._continuous_render_zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        
        painter = QPainter(pixmap)
        self._draw_annotations(painter, page_idx, preview, preview_end)
        painter.end()
        
        self._page_widgets[page_idx].setPixmap(pixmap)
        
    def _draw_annotations(self, painter, page_idx, preview, preview_end):
        """Draw all annotations for a specific page."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get the current zoom factor for this context
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            current_zoom = self._continuous_render_zoom
        else:
            current_zoom = self.zoom_factor
        
        for ann in self.annotations:
            if ann.page != page_idx:
                continue
                
            # Scale annotation coordinates from base PDF coordinates to current zoom
            # Annotations are stored in base PDF coordinates (zoom=1.0)
            scaled_start = QPoint(
                int(ann.start.x() * current_zoom),
                int(ann.start.y() * current_zoom)
            )
            scaled_end = QPoint(
                int(ann.end.x() * current_zoom),
                int(ann.end.y() * current_zoom)
            )
                
            if ann.type == AnnotationType.HIGHLIGHT:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(255, 255, 0, 100))
                painter.drawRect(QRect(scaled_start, scaled_end))
                
            elif ann.type == AnnotationType.UNDERLINE:
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawLine(scaled_start, QPoint(scaled_end.x(), scaled_start.y()))
                
            elif ann.type == AnnotationType.TEXT:
                painter.setPen(QPen(QColor(0, 0, 255)))
                painter.setFont(QFont("Arial", int(12 * current_zoom)))
                painter.drawText(scaled_start, ann.text)
          # Draw preview annotation while dragging
        if preview and self.is_annotating and self.annotation_start_point and preview_end:
            # For preview, we need to convert preview_end to the current coordinate system
            # Since preview_end is in widget coordinates, we need to convert it
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                # In continuous scroll, preview_end is already in the right scale for the current page
                scaled_preview_start = QPoint(
                    int(self.annotation_start_point.x() * current_zoom),
                    int(self.annotation_start_point.y() * current_zoom)
                )
                # For preview_end, we assume it's already in screen coordinates for the current zoom
                scaled_preview_end = preview_end
            else:
                # In single page mode, both coordinates use the same scale
                scaled_preview_start = QPoint(
                    int(self.annotation_start_point.x() * current_zoom),
                    int(self.annotation_start_point.y() * current_zoom)
                )
                scaled_preview_end = preview_end
            
            if self.active_annotation_type == AnnotationType.HIGHLIGHT:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(255, 255, 0, 100))
                painter.drawRect(QRect(scaled_preview_start, scaled_preview_end))
            elif self.active_annotation_type == AnnotationType.UNDERLINE:
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawLine(scaled_preview_start, QPoint(scaled_preview_end.x(), scaled_preview_start.y()))

    def _screen_to_normalized_coords(self, screen_point, page_idx):
        """Convert screen coordinates to normalized PDF coordinates (0.0-1.0)."""
        if not self.doc:
            return screen_point
            
        # Get the current zoom factor
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            current_zoom = self._continuous_render_zoom
        else:
            current_zoom = self.zoom_factor
            
        # Convert screen coordinates back to base PDF coordinates (zoom=1.0)
        base_x = screen_point.x() / current_zoom
        base_y = screen_point.y() / current_zoom
        
        return QPoint(int(base_x), int(base_y))
    
    def _normalized_to_screen_coords(self, norm_point, page_idx, target_zoom):
        """Convert normalized PDF coordinates to screen coordinates at target zoom."""
        if not self.doc:
            return norm_point
            
        # Scale the normalized coordinates by the target zoom
        screen_x = norm_point.x() * target_zoom
        screen_y = norm_point.y() * target_zoom
        
        return QPoint(int(screen_x), int(screen_y))

    def _get_pdf_position(self, source, widget_pos):
        """Convert widget position to normalized PDF coordinate system (0-1 scale)."""
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            # For continuous scroll mode
            if source in self._page_widgets:
                # Direct click on a page widget - normalize coordinates
                page_idx = self._page_widgets.index(source)
                page_rect = self.doc.load_page(page_idx).bound()
                # Convert from scaled coordinates to normalized (0-1) coordinates
                norm_x = widget_pos.x() / (page_rect.width * self._continuous_render_zoom)
                norm_y = widget_pos.y() / (page_rect.height * self._continuous_render_zoom)
                return QPoint(int(norm_x * page_rect.width), int(norm_y * page_rect.height))
            else:
                # Click on container - map position relative to current page
                page_rect = self.doc.load_page(self.current_page).bound()
                norm_x = widget_pos.x() / (page_rect.width * self._continuous_render_zoom)
                norm_y = widget_pos.y() / (page_rect.height * self._continuous_render_zoom)
                return QPoint(int(norm_x * page_rect.width), int(norm_y * page_rect.height))
        else:
            # For single/double page modes
            if source == self.single_double_canvas:
                # The canvas is centered, so we need to map from widget coords to pixmap coords
                pixmap = self.single_double_canvas.pixmap()
                if not pixmap or pixmap.isNull():
                    return widget_pos
                
                # Get the widget size and pixmap size
                widget_rect = self.single_double_canvas.rect()
                pixmap_size = pixmap.size()
                
                # Calculate the offset due to centering
                x_offset = (widget_rect.width() - pixmap_size.width()) // 2
                y_offset = (widget_rect.height() - pixmap_size.height()) // 2
                
                # Adjust the position by removing the centering offset
                adjusted_x = widget_pos.x() - x_offset
                adjusted_y = widget_pos.y() - y_offset
                
                # Ensure the position is within the pixmap bounds
                adjusted_x = max(0, min(adjusted_x, pixmap_size.width() - 1))
                adjusted_y = max(0, min(adjusted_y, pixmap_size.height() - 1))
                
                # Convert from scaled coordinates to base PDF coordinates (zoom=1.0)
                page_rect = self.doc.load_page(self.current_page).bound()
                base_x = adjusted_x / self.zoom_factor
                base_y = adjusted_y / self.zoom_factor
                
                return QPoint(int(base_x), int(base_y))
            else:
                return widget_pos
    def _handle_annotation_right_click(self, source, pos):
        """Handle right-click for annotation deletion."""
        from PyQt6.QtWidgets import QMenu
        
        # Find annotations at this position
        page_idx = self.current_page
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL and source in self._page_widgets:
            try:
                page_idx = self._page_widgets.index(source)
            except ValueError:
                page_idx = self.current_page
        
        # Convert click position to PDF coordinates for comparison
        pdf_pos = self._get_pdf_position(source, pos)
        
        # Find annotations near the click position (within 20 pixels)
        clicked_annotations = []
        for i, ann in enumerate(self.annotations):
            if ann.page == page_idx:
                # Check if click is within annotation bounds
                if self._is_point_in_annotation(pdf_pos, ann):
                    clicked_annotations.append((i, ann))
        
        if clicked_annotations:
            # Show context menu for annotation deletion
            menu = QMenu(self)
            
            if len(clicked_annotations) == 1:
                i, ann = clicked_annotations[0]
                action = menu.addAction(f"Delete {ann.type.name.lower()} annotation")
                action.triggered.connect(lambda: self._delete_annotation(i))
            else:
                # Multiple annotations at this position
                for i, ann in clicked_annotations:
                    action = menu.addAction(f"Delete {ann.type.name.lower()} annotation")
                    action.triggered.connect(lambda checked, idx=i: self._delete_annotation(idx))
                
                menu.addSeparator()
                delete_all_action = menu.addAction("Delete all annotations here")
                delete_all_action.triggered.connect(lambda: self._delete_multiple_annotations([i for i, _ in clicked_annotations]))
            
            # Show the menu at the cursor position
            global_pos = source.mapToGlobal(pos)
            menu.exec(global_pos)
    def _is_point_in_annotation(self, point, annotation):
        """Check if a point is within an annotation's bounds.
        
        Args:
            point: QPoint in PDF coordinates (base PDF coordinates, zoom=1.0)
            annotation: Annotation object with coordinates in base PDF coordinates
        """
        tolerance = 40  # Increased base tolerance for easier clicking
        
        # Get current zoom factor for tolerance scaling
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            current_zoom = self._continuous_render_zoom
        else:
            current_zoom = self.zoom_factor
            
        # Scale tolerance by current zoom and convert to integer
        # Ensure minimum tolerance of 15 pixels for very high zoom levels
        scaled_tolerance = max(15, int(tolerance / current_zoom))
        
        if annotation.type == AnnotationType.TEXT:
            # For text annotations, use a larger circular area
            distance = ((point.x() - annotation.start.x()) ** 2 + 
                       (point.y() - annotation.start.y()) ** 2) ** 0.5
            return distance <= scaled_tolerance
        else:
            # For highlight and underline, create a more generous hit area
            rect = QRect(annotation.start, annotation.end).normalized()
            
            # For underlines, make the hit area taller since underlines are thin
            if annotation.type == AnnotationType.UNDERLINE:
                # Make underline hit area at least 20 pixels tall
                min_height = max(20 / current_zoom, scaled_tolerance)
                if rect.height() < min_height:
                    center_y = rect.center().y()
                    half_height = int(min_height / 2)
                    rect.setTop(int(center_y - half_height))
                    rect.setBottom(int(center_y + half_height))
            
            # Expand the rectangle by the tolerance
            expanded_rect = rect.adjusted(-scaled_tolerance, -scaled_tolerance, 
                                        scaled_tolerance, scaled_tolerance)
            return expanded_rect.contains(point)
    def _delete_annotation(self, annotation_index):
        """Delete a specific annotation by index."""
        if 0 <= annotation_index < len(self.annotations):
            deleted_ann = self.annotations.pop(annotation_index)
            
            # Use appropriate redraw method based on view mode
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self._redraw_all_pages()
            else:
                self._redraw_page(deleted_ann.page)
                
            print(f"Deleted {deleted_ann.type.name.lower()} annotation on page {deleted_ann.page + 1}")
    
    def _delete_multiple_annotations(self, annotation_indices):
        """Delete multiple annotations by their indices."""
        # Collect affected pages before deletion
        affected_pages = set()
        for idx in annotation_indices:
            if 0 <= idx < len(self.annotations):
                affected_pages.add(self.annotations[idx].page)
        
        # Sort indices in reverse order to avoid index shifting issues
        for idx in sorted(annotation_indices, reverse=True):
            if 0 <= idx < len(self.annotations):
                deleted_ann = self.annotations.pop(idx)
                print(f"Deleted {deleted_ann.type.name.lower()} annotation on page {deleted_ann.page + 1}")
        
        # Redraw the affected pages
        if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
            self._redraw_all_pages()
        else:
            for page_idx in affected_pages:
                self._redraw_page(page_idx)
    
    def set_annotation_mode(self, enabled):
        """Enable or disable annotation mode."""
        self.annotation_mode_enabled = enabled
        if not enabled:
            # Cancel any ongoing annotation
            self.is_annotating = False
            self.annotation_start_point = None
    
    def toggle_annotation_mode(self):
        """Toggle annotation mode on/off."""
        self.annotation_mode_enabled = not self.annotation_mode_enabled
        if not self.annotation_mode_enabled:
            # Cancel any ongoing annotation
            self.is_annotating = False
            self.annotation_start_point = None
        return self.annotation_mode_enabled
