"""PDF viewer widget component."""

import os
import fitz  # PyMuPDF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QStackedWidget,
    QSpacerItem, QSizePolicy, QApplication, QInputDialog, QMessageBox, QLineEdit
)
from PyQt6.QtGui import QPixmap, QPainter, QImage, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QRect

from ..core.models import ViewMode, Bookmark, AnnotationType, Annotation


class TextSelection:
    """Represents a text selection on a PDF page."""
    def __init__(self, page: int, start: QPoint, end: QPoint, text: str):
        self.page = page
        self.start = start
        self.end = end
        self.text = text


class SearchResult:
    """Represents a search result on a PDF page."""
    def __init__(self, page: int, rect: fitz.Rect):
        self.page = page
        self.rect = rect


class PDFViewer(QWidget):
    """Main PDF viewing widget with support for multiple view modes."""
    
    view_mode_changed = pyqtSignal(ViewMode)
    current_page_changed_in_continuous_scroll = pyqtSignal(int)
    current_page_changed = pyqtSignal(int)  # General page change signal
    bookmarks_changed = pyqtSignal()
    
    def __init__(self, file_path=None):
        super().__init__()
        self.doc = None
        self.file_path = None
        self.current_page = 0
        self.zoom_factor = 1.0
        self._last_auto_zoom_level = 1.0
        self.view_mode = ViewMode.SINGLE_PAGE

        self._page_widgets = []
        self._page_geometries = []
        self._continuous_render_zoom = 1.0
        self._ignore_scroll_page_updates = False  # Flag to temporarily disable automatic page updates
        self._debug_mode = False  # Set to False to disable debug prints
        
        self._bookmarks = []
        
        self.active_annotation_type = None
        self.annotation_start_point = None
        self.annotations = []
        self.is_annotating = False
        self.annotation_mode_enabled = False
        self._current_annotation_page = 0
        self._page_labels_continuous = []

        self.is_selecting_text = False
        self.text_selection_start = None
        self.current_selection = None
        self._current_selection_page = 0
        self.search_results = []
        self.current_search_index = -1
        self.search_text_str = ""

        self._setup_ui()
        
        if file_path:
            self.load_pdf(file_path)

    def _setup_ui(self):
        """Initialize the user interface components."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.single_double_canvas = QLabel("Single/Double Canvas")
        self.single_double_canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.single_double_canvas.setStyleSheet("background-color: #e0e0e0;")

        self.continuous_page_container = QWidget()
        self.continuous_page_layout = QVBoxLayout(self.continuous_page_container)
        self.continuous_page_layout.setContentsMargins(5, 5, 5, 5)
        self.continuous_page_layout.setSpacing(10)
        self.continuous_page_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.continuous_page_container.setStyleSheet("background-color: #d0d0d0;")

        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self.single_double_canvas)
        self.view_stack.addWidget(self.continuous_page_container)
        self.scroll_area.setWidget(self.view_stack)
        self.layout.addWidget(self.scroll_area)
        
        self.scroll_area.verticalScrollBar().valueChanged.connect(self._update_visible_pages)
        self.scroll_area.viewport().installEventFilter(self)
        self.single_double_canvas.installEventFilter(self)

    def extract_page_text(self, page_idx):
        """Extract all text from a specific page for testing text recognition."""
        if not self.doc or page_idx < 0 or page_idx >= self.doc.page_count:
            return ""
        try:
            page = self.doc.load_page(page_idx)
            text = page.get_text("text")
            print(f"Extracted text from page {page_idx + 1}: {text[:100] + '...' if len(text) > 100 else text}")
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from page {page_idx + 1}: {e}")
            return ""

    def eventFilter(self, source, event):
        """Handle viewport resize events, annotation, and text selection interactions."""
        if source == self.scroll_area.viewport() and event.type() == event.Type.Resize:
            self._update_visible_pages()
            return True

        if not self.doc:
            print("No document loaded")
            return super().eventFilter(source, event)

        zoom = self._continuous_render_zoom if self.view_mode == ViewMode.CONTINUOUS_SCROLL else self.zoom_factor

        # Annotation events
        if self.annotation_mode_enabled and self.active_annotation_type:
            if event.type() == event.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton and not self.is_annotating:
                    self.is_annotating = True
                    try:
                        self.annotation_start_point = self._get_pdf_position(source, event.position().toPoint())
                        page_idx = self._page_labels_continuous.index(source) if source in self._page_labels_continuous else self.current_page
                        self._current_annotation_page = page_idx
                        print(f"Annotation started on page {page_idx + 1}")
                    except Exception as e:
                        print(f"Error starting annotation: {e}")
                    return True
                elif event.button() == Qt.MouseButton.RightButton:
                    self._handle_annotation_right_click(source, event.position().toPoint())
                    return True
            elif event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton and self.is_annotating:
                try:
                    end_point = self._get_pdf_position(source, event.position().toPoint())
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
                    print(f"Annotation added on page {self._current_annotation_page + 1}")
                except Exception as e:
                    print(f"Error adding annotation: {e}")
                return True
            elif event.type() == event.Type.MouseMove and self.is_annotating and self.active_annotation_type != AnnotationType.TEXT:
                try:
                    self._redraw_page(self._current_annotation_page, preview=True, preview_end=event.position().toPoint())
                except Exception as e:
                    print(f"Error previewing annotation: {e}")
                return True
        # Text selection events
        elif not self.annotation_mode_enabled and source in (self.single_double_canvas, *self._page_widgets):
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.is_selecting_text = True
                try:
                    self.text_selection_start = self._map_mouse_pos(source, event, zoom)
                    if self.text_selection_start:
                        self.current_selection = None
                        self._current_selection_page = self._get_page_index(source)
                        print(f"Text selection started at page {self._current_selection_page + 1}, pos {self.text_selection_start}")
                    else:
                        print("Text selection start position invalid")
                except Exception as e:
                    print(f"Error starting text selection: {e}")
                return True
            elif event.type() == event.Type.MouseMove and self.is_selecting_text and self.text_selection_start:
                try:
                    pos = self._map_mouse_pos(source, event, zoom)
                    if pos:
                        text = self._extract_text(self._current_selection_page, self.text_selection_start, pos)
                        self.current_selection = TextSelection(
                            self._current_selection_page,
                            self.text_selection_start,
                            pos,
                            text
                        )
                        print(f"Text selection updated: {text[:50] + '...' if len(text) > 50 else text}")
                        self._redraw_visible_pages()
                    else:
                        print("Text selection move position invalid")
                except Exception as e:
                    print(f"Error updating text selection: {e}")
                return True
            elif event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton and self.is_selecting_text:
                try:
                    pos = self._map_mouse_pos(source, event, zoom)
                    if pos and self.text_selection_start:
                        text = self._extract_text(self._current_selection_page, self.text_selection_start, pos)
                        self.current_selection = TextSelection(
                            self._current_selection_page,
                            self.text_selection_start,
                            pos,
                            text
                        )
                        print(f"Text selection ended: {text[:50] + '...' if len(text) > 50 else text}")
                        self._redraw_visible_pages()
                    else:
                        print("Text selection end position invalid")
                    self.is_selecting_text = False
                    self.text_selection_start = None
                except Exception as e:
                    print(f"Error ending text selection: {e}")
                return True

        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        """Handle key press events for copying selected text."""
        try:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
                if self.current_selection and self.current_selection.text:
                    QApplication.clipboard().setText(self.current_selection.text)
                    print(f"Copied text: {self.current_selection.text[:50] + '...' if len(self.current_selection.text) > 50 else self.current_selection.text}")
        except Exception as e:
            print(f"Error copying text: {e}")
        super().keyPressEvent(event)

    def _map_mouse_pos(self, source, event, zoom):
        """Map mouse position to PDF coordinates."""
        try:
            if source in (self.single_double_canvas, *self._page_widgets):
                pos = source.mapFromGlobal(event.globalPosition().toPoint())
                label = source
                pixmap = label.pixmap()
                if not pixmap or pixmap.isNull():
                    print("No valid pixmap for mouse mapping")
                    return None
                label_size = label.size()
                pixmap_size = pixmap.size()
                offset_x = (label_size.width() - pixmap_size.width()) // 2
                offset_y = (label_size.height() - pixmap_size.height()) // 2
                if not (offset_x <= pos.x() < offset_x + pixmap_size.width() and offset_y <= pos.y() < offset_y + pixmap_size.height()):
                    print(f"Mouse position outside pixmap: pos=({pos.x()}, {pos.y()}), pixmap=({pixmap_size.width()}, {pixmap_size.height()})")
                    return None
                logical_x = (pos.x() - offset_x) / zoom
                logical_y = (pos.y() - offset_y) / zoom
                return QPoint(int(logical_x), int(logical_y))
            print(f"Invalid source for mouse mapping: {source}")
            return None
        except Exception as e:
            print(f"Error mapping mouse position: {e}")
            return None

    def _get_page_index(self, source):
        """Get page index from source widget."""
        try:
            if source == self.single_double_canvas:
                return self.current_page
            elif source in self._page_widgets:
                return self._page_widgets.index(source)
            print("Using default page index")
            return self.current_page
        except Exception as e:
            print(f"Error getting page index: {e}")
            return self.current_page

    def _extract_text(self, page_idx, start, end):
        """Extract text from a rectangular area on a page."""
        if not self.doc or page_idx < 0 or page_idx >= self.doc.page_count:
            print(f"Invalid page index {page_idx}")
            return ""
        try:
            page = self.doc.load_page(page_idx)
            rect = fitz.Rect(
                min(start.x(), end.x()),
                min(start.y(), end.y()),
                max(start.x(), end.x()),
                max(start.y(), end.y())
            )
            text = page.get_text("text", clip=rect)
            print(f"Extracted text: {text[:50] + '...' if len(text) > 50 else text}")
            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def search_text(self, text):
        """Search for text in the PDF and store results."""
        self.search_text_str = text
        self.search_results = []
        self.current_search_index = -1
        if not self.doc or not text:
            self._redraw_visible_pages()
            print("Search text empty or no document loaded")
            return 0

        try:
            for page_idx in range(self.doc.page_count):
                page = self.doc.load_page(page_idx)
                results = page.search_for(text, quads=True)
                for quad in results:
                    # Convert Quad to Rect for consistent rendering
                    rect = fitz.Rect(quad.ul, quad.lr)
                    print(f"Converted Quad to Rect on page {page_idx + 1}: {rect}")
                    self.search_results.append(SearchResult(page_idx, rect))
        except Exception as e:
            print(f"Error searching text: {e}")
            return 0

        self._redraw_visible_pages()
        print(f"Search found {len(self.search_results)} results for '{text}'")
        return len(self.search_results)

    def navigate_search(self, forward=True):
        """Navigate to the next or previous search result."""
        if not self.search_results:
            print("No search results to navigate")
            return
        try:
            self.current_search_index = (self.current_search_index + (1 if forward else -1)) % len(self.search_results)
            result = self.search_results[self.current_search_index]
            self.jump_to_page(result.page)
            self._redraw_visible_pages()
            print(f"Navigated to search result {self.current_search_index + 1}/{len(self.search_results)} on page {result.page + 1}")
        except Exception as e:
            print(f"Error navigating search: {e}")

    def _redraw_visible_pages(self):
        """Redraw all visible pages to update text operations."""
        if not self.doc:
            return
        try:
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                for i in range(self.doc.page_count):
                    if i < len(self._page_widgets) and self._page_widgets[i]:
                        self._render_page_with_annotations(i)
            else:
                self.render_page_with_annotations()
        except Exception as e:
            print(f"Error redrawing visible pages: {e}")

    def load_pdf(self, file_path):
        """Load a PDF file for viewing with comprehensive error handling."""
        self.file_path = file_path
        
        # Validate file path
        if not file_path or not os.path.exists(file_path):
            self._show_error_message("File not found", f"The file '{file_path}' does not exist.")
            return False
            
        # Check file size (warn for very large files)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                reply = QMessageBox.question(
                    self,
                    "Large File Warning",
                    f"This file is {file_size // (1024*1024)}MB. Loading may take some time. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return False
        except OSError:
            pass  # File size check failed, continue anyway
        
        try:
            # Attempt to open the PDF
            self.doc = fitz.open(file_path)
            
            # Validate PDF content
            if self.doc.page_count == 0:
                self._show_error_message("Invalid PDF", "This PDF file contains no pages.")
                return False
                
            # Check if PDF is encrypted and handle password
            if self.doc.needs_pass:
                success = self._handle_encrypted_pdf()
                if not success:
                    return False
            
            # Initialize page structures
            self._page_labels_continuous = [None] * self.doc.page_count
            self._setup_annotation_event_filters()
            
            # Set default view mode
            self.set_view_mode(ViewMode.SINGLE_PAGE, force_setup=True)
            
            # Test text extraction on first page for search functionality
            text = self.extract_page_text(0)
            if self._debug_mode:
                print(f"Sample text from page 1: {text[:100] + '...' if len(text) > 100 else text}")
            
            # Emit success signal
            self.current_page_changed.emit(self.current_page)
            return True
            
        except fitz.FileDataError:
            self._show_error_message("Corrupted File", "This PDF file appears to be corrupted and cannot be opened.")
            return False
        except fitz.FileNotFoundError:
            self._show_error_message("File Not Found", f"Could not find the file: {file_path}")
            return False
        except PermissionError:
            self._show_error_message("Permission Denied", "You don't have permission to open this file.")
            return False
        except Exception as e:
            self._show_error_message("Error Loading PDF", f"An unexpected error occurred while loading the PDF:\n{str(e)}")
            return False

    def _handle_encrypted_pdf(self):
        """Handle password-protected PDF files."""
        from PyQt6.QtWidgets import QInputDialog
        
        max_attempts = 3
        for attempt in range(max_attempts):
            password, ok = QInputDialog.getText(
                self,
                "Password Required",
                f"This PDF is password protected. Please enter the password:\n"
                f"(Attempt {attempt + 1} of {max_attempts})",
                QLineEdit.EchoMode.Password
            )
            
            if not ok:  # User cancelled
                return False
                
            if self.doc.authenticate(password):
                return True
            else:
                if attempt < max_attempts - 1:
                    QMessageBox.warning(
                        self,
                        "Incorrect Password",
                        "The password you entered is incorrect. Please try again."
                    )
        
        QMessageBox.critical(
            self,
            "Authentication Failed",
            "Failed to authenticate after multiple attempts. The file cannot be opened."
        )
        return False

    def _show_error_message(self, title, message):
        """Show error message and update UI accordingly."""
        # Update canvas to show error
        self.single_double_canvas.setText(f"❌ {title}\n\n{message}")
        self.single_double_canvas.setStyleSheet("""
            QLabel {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 6px;
                padding: 20px;
                font-size: 14px;
                text-align: center;
            }
        """)
        self.view_stack.setCurrentWidget(self.single_double_canvas)
        
        # Show message box for critical errors
        QMessageBox.critical(self, title, message)
    
    def _setup_annotation_event_filters(self):
        """Set up event filters for annotation handling."""
        try:
            if self.doc:
                self.continuous_page_container.installEventFilter(self)
        except Exception as e:
            print(f"Error setting up annotation event filters: {e}")

    def _clear_continuous_view(self):
        """Clear all widgets from continuous view layout."""
        try:
            while self.continuous_page_layout.count():
                item = self.continuous_page_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self._page_widgets = []
            self._page_geometries = []
        except Exception as e:
            print(f"Error clearing continuous view: {e}")

    def _update_visible_pages(self, value=None):
        """Update visible pages in continuous scroll mode for performance."""
        if (
            not self.doc
            or self.view_mode != ViewMode.CONTINUOUS_SCROLL
            or not self._page_widgets
        ):
            return

        try:
            viewport_rect = self.scroll_area.viewport().rect()
            visible_pages = set()
            current_y = self.continuous_page_layout.contentsMargins().top()

            for i in range(self.doc.page_count):
                page_height = self._page_geometries[i].height()
                spacing = self.continuous_page_layout.spacing()
                page_top = current_y
                page_bottom = current_y + page_height

                if (
                    page_bottom
                    >= self.scroll_area.verticalScrollBar().value() - viewport_rect.height()
                    and page_top
                    <= self.scroll_area.verticalScrollBar().value()
                    + viewport_rect.height() * 2
                ):
                    visible_pages.add(i)

                current_y += page_height + spacing

            for i in sorted(list(visible_pages)):
                if self._page_widgets[i] is None:
                    self._inflate_page(i)

            for i in range(self.doc.page_count):
                if i not in visible_pages and self._page_widgets[i] is not None:
                    self._deflate_page(i)

            self._update_current_page_in_scroll_view()
        except Exception as e:
            print(f"Error updating visible pages: {e}")

    def _inflate_page(self, page_idx):
        """Replace a spacer with a real, rendered page widget."""
        if (
            not self.doc
            or not (0 <= page_idx < len(self._page_widgets))
            or self._page_widgets[page_idx] is not None
        ):
            return

        try:
            size = self._page_geometries[page_idx]
            page_label = QLabel()
            page_label.setFixedSize(size)
            page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            page = self.doc.load_page(page_idx)
            mat = fitz.Matrix(self._continuous_render_zoom, self._continuous_render_zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = QImage(
                pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap.fromImage(img)
            
            painter = QPainter(pixmap)
            self._draw_annotations(painter, page_idx, False, None)
            self._draw_text_operations(painter, page_idx)
            painter.end()
            
            page_label.setPixmap(pixmap)

            item = self.continuous_page_layout.takeAt(page_idx)
            if item:
                del item
            self.continuous_page_layout.insertWidget(page_idx, page_label)
            self._page_widgets[page_idx] = page_label
            
            page_label.installEventFilter(self)
            self._page_labels_continuous[page_idx] = page_label
        except Exception as e:
            print(f"Error inflating page {page_idx + 1}: {e}")
        
    def _deflate_page(self, page_idx):
        """Replace a real widget with a lightweight spacer to save memory."""
        if not (0 <= page_idx < len(self._page_widgets)) or self._page_widgets[page_idx] is None:
            return

        try:
            widget = self._page_widgets[page_idx]
            self.continuous_page_layout.removeWidget(widget)
            widget.deleteLater()

            size = self._page_geometries[page_idx]
            spacer = QSpacerItem(
                size.width(),
                size.height(),                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Fixed,
            )
            self.continuous_page_layout.insertItem(page_idx, spacer)
            self._page_widgets[page_idx] = None
            if page_idx < len(self._page_labels_continuous):
                self._page_labels_continuous[page_idx] = None
        except Exception as e:
            print(f"Error deflating page {page_idx + 1}: {e}")

    def _update_current_page_in_scroll_view(self):
        """Update current page based on scroll position in continuous mode."""
        if self.view_mode != ViewMode.CONTINUOUS_SCROLL:
            return
        
        # Skip automatic page updates if we just manually jumped to a page
        if self._ignore_scroll_page_updates:
            self._debug_print("Skipping automatic page update due to _ignore_scroll_page_updates flag")
            return

        try:
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
                old_page = self.current_page
                self.current_page = best_page_idx
                self._debug_print(f"Auto page change from {old_page} to {best_page_idx} (scroll position: {self.scroll_area.verticalScrollBar().value()})")
                self.current_page_changed_in_continuous_scroll.emit(self.current_page)
                self.current_page_changed.emit(self.current_page)
        except Exception as e:
            print(f"Error updating current page in scroll view: {e}")

    def _setup_continuous_view(self):
        """Set up the continuous scroll view with virtualized pages."""
        if not self.doc:
            return

        try:
            self._debug_print(f"_setup_continuous_view starting, current_page: {self.current_page}")
            self._clear_continuous_view()
            self._debug_print(f"After _clear_continuous_view, current_page: {self.current_page}")
            QApplication.processEvents()
            vp_width = self.scroll_area.viewport().width()
            if vp_width > 20:
                sample_page_rect = self.doc.load_page(self.current_page).bound()
                if sample_page_rect.width > 0:
                    margins = self.continuous_page_layout.contentsMargins()
                    available_width = (
                        vp_width - margins.left() - margins.right() - 20
                    )
                    self.zoom_factor = available_width / sample_page_rect.width
            else:
                self.zoom_factor = 1.0
            self._continuous_render_zoom = self.zoom_factor

            for i in range(self.doc.page_count):
                page_rect = self.doc.load_page(i).bound()
                width = int(page_rect.width * self._continuous_render_zoom)
                height = int(page_rect.height * self._continuous_render_zoom)
                self._page_geometries.append(QSize(width, height))
                self._page_widgets.append(None)

                spacer = QSpacerItem(
                    width, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
                )
                self.continuous_page_layout.addSpacerItem(spacer)            # Process events to ensure layout is updated before jumping to page
            QApplication.processEvents()

            # Use a timer to delay the jump until the layout is fully processed
            from PyQt6.QtCore import QTimer
            def delayed_jump():
                self.jump_to_page(self.current_page)
            
            QTimer.singleShot(10, delayed_jump)  # Small delay for layout to process
        except Exception as e:
            print(f"Error setting up continuous view: {e}")

    def render_page(self):
        """Render the current page(s) for single and double page modes."""
        if not self.doc:
            self.single_double_canvas.clear()
            self.single_double_canvas.setText("Could not load PDF.")
            return

        try:
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
        except Exception as e:
            print(f"Error rendering page: {e}")
    
    def _set_view_mode_internal(self, mode: ViewMode):
        """Internal method to set view mode."""
        self.view_mode = mode

    def set_view_mode(self, mode: ViewMode, force_setup=False):
        """Set the view mode for the PDF viewer."""
        if not self.doc:
            return
        if self.view_mode == mode and not force_setup:
            return
            
        try:
            previous_mode = self.view_mode
            current_page_backup = self.current_page  # Backup current page
            self._set_view_mode_internal(mode)
            if mode == ViewMode.CONTINUOUS_SCROLL:
                self.view_stack.setCurrentWidget(self.continuous_page_container)
                if previous_mode != ViewMode.CONTINUOUS_SCROLL or force_setup:
                    self.current_page = current_page_backup  # Restore page before setup
                    self.jump_to_page(self.current_page)
                    self._debug_print(f"Setting up continuous view, restored to page: {self.current_page}")
                    self._setup_continuous_view()
                else:
                    # Jump to current page to ensure proper scrolling
                    self.jump_to_page(self.current_page)
            else:
                if previous_mode == ViewMode.CONTINUOUS_SCROLL:
                    self._clear_continuous_view()
                self.view_stack.setCurrentWidget(self.single_double_canvas)
                  # Restore current page
                self.current_page = current_page_backup
                
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
                
                self.render_page_with_annotations()
                
                self.single_double_canvas.update()
                self.view_stack.update()
                self.scroll_area.update()
                self.update()
                QApplication.processEvents()

            print(f"DEBUG: View mode switch complete, final page: {self.current_page}")
            self.view_mode_changed.emit(self.view_mode)
        except Exception as e:
            print(f"Error setting view mode: {e}")

    def zoom_in(self):
        """Zoom in on the PDF."""
        if not self.doc:
            return

        try:
            if self.view_mode in [ViewMode.FIT_PAGE, ViewMode.FIT_WIDTH]:
                self.zoom_factor = self._last_auto_zoom_level

            self.zoom_factor *= 1.2

            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self._setup_continuous_view()
            else:
                self._set_view_mode_internal(
                    ViewMode.SINGLE_PAGE
                    if self.view_mode != ViewMode.DOUBLE_PAGE
                    else ViewMode.DOUBLE_PAGE
                )
                self.render_page_with_annotations()
            self.view_mode_changed.emit(self.view_mode)
        except Exception as e:
            print(f"Error zooming in: {e}")

    def zoom_out(self):
        """Zoom out on the PDF."""
        if not self.doc:
            return

        try:
            if self.view_mode in [ViewMode.FIT_PAGE, ViewMode.FIT_WIDTH]:
                self.zoom_factor = self._last_auto_zoom_level

            self.zoom_factor /= 1.2

            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self._setup_continuous_view()
            else:
                self._set_view_mode_internal(
                    ViewMode.SINGLE_PAGE
                    if self.view_mode != ViewMode.DOUBLE_PAGE
                    else ViewMode.DOUBLE_PAGE
                )
                self.render_page_with_annotations()
            self.view_mode_changed.emit(self.view_mode)
        except Exception as e:
            print(f"Error zooming out: {e}")

    def reset_zoom(self):
        """Reset zoom to the default value (100%)."""
        if not self.doc:
            return

        try:
            from ..core.config import DEFAULT_ZOOM_FACTOR
            
            # Reset zoom factor to default
            self.zoom_factor = DEFAULT_ZOOM_FACTOR
            
            # Switch out of automatic fit modes to manual zoom
            if self.view_mode in [ViewMode.FIT_PAGE, ViewMode.FIT_WIDTH]:
                self._set_view_mode_internal(ViewMode.SINGLE_PAGE)
            
            # Re-render based on current view mode
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                self._setup_continuous_view()
            else:
                self.render_page_with_annotations()
                
            self.view_mode_changed.emit(self.view_mode)
        except Exception as e:
            print(f"Error resetting zoom: {e}")

    def next_page(self):
        """Navigate to the next page."""
        if not self.doc:
            return
            
        try:
            old_page = self.current_page
            page_increment = 2 if self.view_mode == ViewMode.DOUBLE_PAGE else 1
            if self.current_page < self.doc.page_count - page_increment:
                self.current_page += page_increment
                if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                    self.jump_to_page(self.current_page, force_scroll_continuous=True)
                    self.current_page_changed_in_continuous_scroll.emit(self.current_page)
                else:
                    self.render_page_with_annotations()
                    self.current_page_changed.emit(self.current_page)
            elif (
                self.view_mode == ViewMode.DOUBLE_PAGE
                and self.current_page == self.doc.page_count - 2
                and self.doc.page_count % 2 == 1
            ):
                self.current_page += 1
                self.render_page_with_annotations()
                self.current_page_changed.emit(self.current_page)
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
                    self.current_page_changed.emit(self.current_page)
            
            # Emit general page change signal if page actually changed
            if old_page != self.current_page:
                self.current_page_changed.emit(self.current_page)
                
        except Exception as e:
            print(f"Error navigating to next page: {e}")

    def prev_page(self):
        """Navigate to the previous page."""
        if not self.doc:
            return
            
        try:
            old_page = self.current_page
            page_decrement = 2 if self.view_mode == ViewMode.DOUBLE_PAGE else 1
            if self.current_page > 0:
                self.current_page = max(0, self.current_page - page_decrement)
                if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                    self.jump_to_page(self.current_page, force_scroll_continuous=True)
                    self.current_page_changed_in_continuous_scroll.emit(self.current_page)
                else:
                    self.render_page_with_annotations()
            
            # Emit general page change signal if page actually changed
            if old_page != self.current_page:                self.current_page_changed.emit(self.current_page)
                
        except Exception as e:
            print(f"Error navigating to previous page: {e}")

    def _debug_print(self, message: str):
        """Print debug message if debug mode is enabled."""
        if self._debug_mode:
            print(f"DEBUG: {message}")

    def jump_to_page(self, page_num, force_scroll_continuous=True):
        """Jump to a specific page number."""
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return

        try:
            old_page = self.current_page
            self.current_page = page_num
            self._debug_print(f"jump_to_page called, from {old_page} to {page_num}, view_mode: {self.view_mode}")
            
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                # Set flag to prevent automatic page recalculation after manual jump
                self._ignore_scroll_page_updates = True
                self._debug_print("Setting _ignore_scroll_page_updates=True before scroll")
                
                target_y = self.continuous_page_layout.contentsMargins().top()
                for i in range(page_num):
                    target_y += (
                        self._page_geometries[i].height()
                        + self.continuous_page_layout.spacing()
                    )

                self._debug_print(f"Calculated target_y for page {page_num}: {target_y}")
                self._debug_print(f"Current scroll position: {self.scroll_area.verticalScrollBar().value()}")
                self._debug_print(f"Scroll maximum: {self.scroll_area.verticalScrollBar().maximum()}")
                  # Check if scroll area is ready for scrolling
                scroll_max = self.scroll_area.verticalScrollBar().maximum()
                if scroll_max > 0:
                    # Normal case: scroll area is ready
                    self.scroll_area.verticalScrollBar().setValue(int(target_y))
                    QApplication.processEvents()
                    self._debug_print(f"After scroll, position: {self.scroll_area.verticalScrollBar().value()}")
                else:
                    # Layout not ready yet - use a multi-retry mechanism
                    self._debug_print("Scroll area not ready, scheduling retries")
                    from PyQt6.QtCore import QTimer
                    retry_count = 0
                    max_retries = 5
                    
                    def retry_scroll():
                        nonlocal retry_count
                        retry_count += 1
                        new_max = self.scroll_area.verticalScrollBar().maximum()
                        self._debug_print(f"Retry {retry_count} - max: {new_max}, target_y: {target_y}")
                        if new_max > 0:
                            self.scroll_area.verticalScrollBar().setValue(int(target_y))
                            self._debug_print(f"Retry {retry_count} successful, position: {self.scroll_area.verticalScrollBar().value()}")
                        elif retry_count < max_retries:
                            # Schedule another retry with increasing delay
                            QTimer.singleShot(50 * retry_count, retry_scroll)
                        else:
                            self._debug_print("All retries failed - scroll area not ready")
                    
                    QTimer.singleShot(50, retry_scroll)
                
                # Clear the flag after a delay to allow scroll events to settle
                from PyQt6.QtCore import QTimer
                def clear_flag():
                    self._ignore_scroll_page_updates = False
                    self._debug_print("Cleared _ignore_scroll_page_updates flag")
                
                QTimer.singleShot(200, clear_flag)  # Increased delay to account for retry
                
                # Emit signals to indicate the page changed
                self.current_page_changed_in_continuous_scroll.emit(self.current_page)
            else:
                if self.view_mode == ViewMode.DOUBLE_PAGE:
                    if self.current_page % 2 != 0:
                        self.current_page = max(0, self.current_page - 1)
                self.render_page_with_annotations()
            
            # Emit general page change signal if page actually changed
            if old_page != self.current_page:
                self.current_page_changed.emit(self.current_page)
                
        except Exception as e:
            print(f"Error jumping to page {page_num + 1}: {e}")

    def get_toc(self):
        """Get the table of contents for the PDF."""
        if not self.doc:
            return []
        try:
            return self.doc.get_toc()
        except Exception as e:
            print(f"Error getting TOC: {e}")
            return []
    
    def add_bookmark(self, title: str = None, page_number: int = None) -> bool:
        """Add a bookmark for a page."""
        if not self.doc or not self.file_path:
            return False
            
        try:
            page_num = page_number if page_number is not None else self.current_page
            
            if not (0 <= page_num < self.doc.page_count):
                return False
                
            if not title:
                title = f"Page {page_num + 1}"
                
            for bookmark in self._bookmarks:
                if bookmark.page_number == page_num:
                    return False
                    
            from datetime import datetime
            bookmark = Bookmark(
                title=title,
                page_number=page_num,
                file_path=self.file_path,
                created_at=datetime.now().isoformat()
            )
            
            self._bookmarks.append(bookmark)
            self._bookmarks.sort(key=lambda b: b.page_number)
            
            self.bookmarks_changed.emit()
            return True
        except Exception as e:
            print(f"Error adding bookmark: {e}")
            return False
    
    def remove_bookmark(self, page_number: int) -> bool:
        """Remove a bookmark for a page."""
        try:
            for i, bookmark in enumerate(self._bookmarks):
                if bookmark.page_number == page_number:
                    del self._bookmarks[i]
                    self.bookmarks_changed.emit()
                    return True
            return False
        except Exception as e:
            print(f"Error removing bookmark: {e}")
            return False
    
    def get_bookmarks(self) -> list[Bookmark]:
        """Get all bookmarks."""
        try:
            return self._bookmarks.copy()
        except Exception as e:
            print(f"Error getting bookmarks: {e}")
            return []
    
    def has_bookmark(self, page_number: int) -> bool:
        """Check if a page has a bookmark."""
        try:
            return any(b.page_number == page_number for b in self._bookmarks)
        except Exception as e:
            print(f"Error checking bookmark: {e}")
            return False
    
    def jump_to_bookmark(self, bookmark: Bookmark):
        """Jump to a bookmarked page."""
        try:
            if bookmark.file_path == self.file_path:
                self.jump_to_page(bookmark.page_number)
        except Exception as e:
            print(f"Error jumping to bookmark: {e}")
    
    def _redraw_all_pages(self):
        """Redraw all pages to update annotations and text operations."""
        if not self.doc:
            return
            
        try:
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                for i in range(self.doc.page_count):
                    if i < len(self._page_widgets) and self._page_widgets[i] is not None:
                        self._render_page_with_annotations(i)
            else:
                self.render_page_with_annotations()
        except Exception as e:
            print(f"Error redrawing all pages: {e}")

    def _redraw_page(self, page_idx, preview=False, preview_end=None):
        """Redraw a specific page."""
        if not self.doc or page_idx < 0 or page_idx >= self.doc.page_count:
            return
            
        try:
            if self.view_mode == ViewMode.CONTINUOUS_SCROLL:
                if page_idx < len(self._page_widgets) and self._page_widgets[page_idx]:
                    self._render_page_with_annotations(page_idx, preview, preview_end)
            else:
                self.render_page_with_annotations(preview, preview_end)
        except Exception as e:
            print(f"Error redrawing page {page_idx + 1}: {e}")
    
    def render_page_with_annotations(self, preview=False, preview_end=None):
        """Render the current page with annotations and text operations."""
        try:
            self.render_page()
            pixmap = self.single_double_canvas.pixmap()
            if not pixmap or pixmap.isNull():
                return
                
            painter = QPainter(pixmap)
            self._draw_annotations(painter, self.current_page, preview, preview_end)
            self._draw_text_operations(painter, self.current_page)
            if self.view_mode == ViewMode.DOUBLE_PAGE and self.current_page + 1 < self.doc.page_count:
                offset_x = int(self.doc.load_page(self.current_page).bound().width * self.zoom_factor)
                painter.translate(offset_x, 0)
                self._draw_annotations(painter, self.current_page + 1, preview, preview_end)
                self._draw_text_operations(painter, self.current_page + 1)
            painter.end()
            self.single_double_canvas.setPixmap(pixmap)
        except Exception as e:
            print(f"Error rendering page with annotations: {e}")
    
    def _render_page_with_annotations(self, page_idx, preview=False, preview_end=None):
        """Render a specific page in continuous scroll mode."""
        if page_idx >= len(self._page_widgets) or not self._page_widgets[page_idx]:
            return
            
        try:
            page = self.doc.load_page(page_idx)
            mat = fitz.Matrix(self._continuous_render_zoom, self._continuous_render_zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            
            painter = QPainter(pixmap)
            self._draw_annotations(painter, page_idx, preview, preview_end)
            self._draw_text_operations(painter, page_idx)
            painter.end()
            
            self._page_widgets[page_idx].setPixmap(pixmap)
        except Exception as e:
            print(f"Error rendering page {page_idx + 1} with annotations: {e}")
        
    def _draw_annotations(self, painter, page_idx, preview, preview_end):
        """Draw annotations on a page."""
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            current_zoom = self._continuous_render_zoom if self.view_mode == ViewMode.CONTINUOUS_SCROLL else self.zoom_factor
            
            for ann in self.annotations:
                if ann.page != page_idx:
                    continue
                    
                scaled_start = QPoint(
                    int(ann.start.x() * current_zoom),
                    int(ann.start.y() * current_zoom)
                )
                scaled_end = QPoint(
                    int(ann.end.x() * current_zoom) if ann.end else scaled_start.x(),
                    int(ann.end.y() * current_zoom) if ann.end else scaled_start.y()
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
            
            if preview and self.is_annotating and self.annotation_start_point and preview_end:
                scaled_preview_start = QPoint(
                    int(self.annotation_start_point.x() * current_zoom),
                    int(self.annotation_start_point.y() * current_zoom)
                )
                scaled_preview_end = self._get_pdf_position(
                    self._page_widgets[page_idx] if page_idx < len(self._page_widgets) else self.single_double_canvas,
                    preview_end
                )
                scaled_preview_end = QPoint(
                    int(scaled_preview_end.x() * current_zoom),
                    int(scaled_preview_end.y() * current_zoom)
                )
                
                if self.active_annotation_type == AnnotationType.HIGHLIGHT:
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(255, 255, 0, 100))
                    painter.drawRect(QRect(scaled_preview_start, scaled_preview_end))
                elif self.active_annotation_type == AnnotationType.UNDERLINE:
                    painter.setPen(QPen(QColor(255, 0, 0), 2))
                    painter.drawLine(scaled_preview_start, QPoint(scaled_preview_end.x(), scaled_preview_start.y()))
        except Exception as e:
            print(f"Error drawing annotations on page {page_idx + 1}: {e}")

    def _draw_text_operations(self, painter, page_idx):
        """Draw text selection and search results."""
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            current_zoom = self._continuous_render_zoom if self.view_mode == ViewMode.CONTINUOUS_SCROLL else self.zoom_factor

            # Draw non-current search results with yellow highlight
            for i, result in enumerate(self.search_results):
                if result.page == page_idx and i != self.current_search_index:
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(255, 255, 0, 100))
                    rect = QRect(
                        int(result.rect.x0 * current_zoom),
                        int(result.rect.y0 * current_zoom),
                        int(result.rect.width * current_zoom),
                        int(result.rect.height * current_zoom)
                    )
                    painter.drawRect(rect)
                    print(f"Drawing yellow search result {i + 1} on page {page_idx + 1}: {rect}")

            # Draw current search result with blue highlight
            if self.current_search_index >= 0 and self.current_search_index < len(self.search_results):
                result = self.search_results[self.current_search_index]
                if result.page == page_idx:
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(0, 0, 255, 100))
                    rect = QRect(
                        int(result.rect.x0 * current_zoom),
                        int(result.rect.y0 * current_zoom),
                        int(result.rect.width * current_zoom),
                        int(result.rect.height * current_zoom)
                    )
                    painter.drawRect(rect)
                    print(f"Drawing blue search result {self.current_search_index + 1} on page {page_idx + 1}: {rect}")

            # Draw text selection with blue highlight
            if self.current_selection and self.current_selection.page == page_idx:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(0, 0, 255, 100))
                rect = QRect(
                    int(self.current_selection.start.x() * current_zoom),
                    int(self.current_selection.start.y() * current_zoom),
                    int((self.current_selection.end.x() - self.current_selection.start.x()) * current_zoom),
                    int((self.current_selection.end.y() - self.current_selection.start.y()) * current_zoom)
                )
                painter.drawRect(rect)
                print(f"Drawing text selection on page {page_idx + 1}: {rect}")
        except Exception as e:
            print(f"Error drawing text operations on page {page_idx + 1}: {e}")

    def _get_pdf_position(self, source, widget_pos):
        """Get PDF position from widget coordinates."""
        try:
            current_zoom = self._continuous_render_zoom if self.view_mode == ViewMode.CONTINUOUS_SCROLL else self.zoom_factor
            if source in (self.single_double_canvas, *self._page_widgets):
                pixmap = source.pixmap()
                if not pixmap or pixmap.isNull():
                    print("No valid pixmap for PDF position")
                    return widget_pos
                label_size = source.size()
                pixmap_size = pixmap.size()
                offset_x = (label_size.width() - pixmap_size.width()) // 2
                offset_y = (label_size.height() - pixmap_size.height()) // 2
                adjusted_x = widget_pos.x() - offset_x
                adjusted_y = widget_pos.y() - offset_y
                if not (0 <= adjusted_x < pixmap_size.width() and 0 <= adjusted_y < pixmap_size.height()):
                    print(f"Position outside pixmap: adjusted=({adjusted_x}, {adjusted_y}), pixmap=({pixmap_size.width()}, {pixmap_size.height()})")
                    return widget_pos
                pdf_x = adjusted_x / current_zoom
                pdf_y = adjusted_y / current_zoom
                return QPoint(int(pdf_x), int(pdf_y))
            print(f"Invalid source for PDF position: {source}")
            return widget_pos
        except Exception as e:
            print(f"Error getting PDF position: {e}")
            return widget_pos
    
    def _handle_annotation_right_click(self, source, pos):
        """Handle right-click on annotations."""
        from PyQt6.QtWidgets import QMenu
        
        try:
            page_idx = self.current_page
            if source in self._page_widgets:
                page_idx = self._page_widgets.index(source)
            
            pdf_pos = self._get_pdf_position(source, pos)
            
            clicked_annotations = []
            for i, ann in enumerate(self.annotations):
                if ann.page == page_idx:
                    if self._is_point_in_annotation(pdf_pos, ann):
                        clicked_annotations.append((i, ann))
            
            if clicked_annotations:
                menu = QMenu(self)
                if len(clicked_annotations) == 1:
                    i, ann = clicked_annotations[0]
                    action = menu.addAction(f"Delete {ann.type.name.lower()} annotation")
                    action.triggered.connect(lambda checked: self._delete_annotation(i))
                else:
                    for i, ann in enumerate(clicked_annotations):
                        action = menu.addAction(f"Delete {ann.type.name.lower()} annotation")
                        action.triggered.connect(lambda checked, idx=i: self._delete_annotation(idx))
                    menu.addSeparator()
                    delete_all_action = menu.addAction("Delete all annotations here")
                    delete_all_action.triggered.connect(
                        lambda checked: self._delete_multiple_annotations([i for i, _ in clicked_annotations])
                    )
                
                global_pos = source.mapToGlobal(pos)
                menu.exec(global_pos)
        except Exception as e:
            print(f"Error handling annotation right-click: {e}")
    
    def _is_point_in_annotation(self, point, annotation):
        """Check if a point is within an annotation."""
        try:
            tolerance = 40
            current_zoom = self._continuous_render_zoom if self.view_mode == ViewMode.CONTINUOUS_SCROLL else self.zoom_factor
            scaled_tolerance = max(15, int(tolerance / current_zoom))
            
            if annotation.type == AnnotationType.TEXT:
                distance = ((point.x() - annotation.start.x()) ** 2 + 
                           (point.y() - annotation.start.y()) ** 2) ** 0.5
                return distance <= scaled_tolerance
            else:
                rect = QRect(annotation.start, annotation.end).normalized() if annotation.end else QRect(annotation.start, annotation.start)
                if annotation.type == AnnotationType.UNDERLINE:
                    min_height = max(20 / current_zoom, scaled_tolerance)
                    if rect.height() < min_height:
                        center_y = rect.center().y()
                        half_height = int(min_height / 2)
                        rect.setTop(int(center_y - half_height))
                        rect.setBottom(int(center_y + half_height))
                
                expanded_rect = rect.adjusted(-scaled_tolerance, -scaled_tolerance, 
                                            scaled_tolerance, scaled_tolerance)
                return expanded_rect.contains(point)
        except Exception as e:
            print(f"Error checking point in annotation: {e}")
            return False
    
    def _delete_annotation(self, annotation_index):
        """Delete a specific annotation."""
        try:
            if 0 <= annotation_index < len(self.annotations):
                deleted_ann = self.annotations.pop(annotation_index)
                self._redraw_page(deleted_ann.page)
                print(f"Deleted {deleted_ann.type.name.lower()} annotation on page {deleted_ann.page + 1}")
        except Exception as e:
            print(f"Error deleting annotation: {e}")
    
    def _delete_multiple_annotations(self, annotation_indices):
        """Delete multiple annotations."""
        try:
            affected_pages = set()
            for idx in sorted(annotation_indices, reverse=True):
                if 0 <= idx < len(self.annotations):
                    deleted_ann = self.annotations.pop(idx)
                    affected_pages.add(deleted_ann.page)
                    print(f"Deleted {deleted_ann.type.name.lower()} annotation on page {deleted_ann.page + 1}")
            
            for page_idx in affected_pages:
                self._redraw_page(page_idx)
        except Exception as e:
            print(f"Error deleting multiple annotations: {e}")
    
    def set_annotation_mode(self, enabled):
        """Set annotation mode state."""
        try:
            self.annotation_mode_enabled = enabled
            if not enabled:
                self.is_annotating = False
                self.annotation_start_point = None
                self.current_selection = None
                self.search_results = []
                self.current_search_index = -1
                self.search_text_str = ""
                self._redraw_visible_pages()
        except Exception as e:
            print(f"Error setting annotation mode: {e}")
    
    def toggle_annotation_mode(self):
        """Toggle annotation mode."""
        try:
            self.annotation_mode_enabled = not self.annotation_mode_enabled
            if not self.annotation_mode_enabled:
                self.is_annotating = False
                self.annotation_start_point = None
                self.current_selection = None
                self.search_results = []
                self.current_search_index = -1
                self.search_text_str = ""
                self._redraw_visible_pages()
            print(f"Annotation mode {'enabled' if self.annotation_mode_enabled else 'disabled'}")
            return self.annotation_mode_enabled
        except Exception as e:
            print(f"Error toggling annotation mode: {e}")
            return self.annotation_mode_enabled
