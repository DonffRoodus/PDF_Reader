"""Main window and application UI components."""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog,
    QToolBar, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QDockWidget, QInputDialog, QMessageBox, QMenu
)
from PyQt6.QtGui import QIcon, QAction, QActionGroup
from PyQt6.QtCore import Qt, QTimer

from ..core.models import ViewMode, Bookmark, AnnotationType, Annotation
from ..core.config import config
from .pdf_viewer import PDFViewer


class MainWindow(QMainWindow):
    """Main application window containing tabs, menus, and toolbars."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Reader")
        self.setGeometry(100, 100, 1200, 800)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tab_widget)

        self.recent_files = []
        
        # Timer for saving reading progress
        self.progress_save_timer = QTimer()
        self.progress_save_timer.timeout.connect(self.save_current_progress)
        self.progress_save_timer.setSingleShot(True)
        
        self.create_menus_and_toolbar()
        self.create_dock_widgets()
        
        self.load_recent_files()
        self.update_view_menu_state()

    def create_menus_and_toolbar(self):
        """Create the main menu bar and toolbar."""
        file_menu = self.menuBar().addMenu("&File")
        open_action = QAction(QIcon.fromTheme("document-open"), "&Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        self.recent_files_menu = file_menu.addMenu("Recent Files")

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_mode_menu = self.menuBar().addMenu("&View Modes")
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

        self.single_page_action.setChecked(True)

        bookmarks_menu = self.menuBar().addMenu("&Bookmarks")
        
        self.add_bookmark_action = QAction("Add Bookmark", self)
        self.add_bookmark_action.setShortcut("Ctrl+B")
        self.add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(self.add_bookmark_action)
        
        self.remove_bookmark_action = QAction("Remove Bookmark", self)
        self.remove_bookmark_action.setShortcut("Ctrl+Shift+B")
        self.remove_bookmark_action.triggered.connect(self.remove_current_bookmark)
        bookmarks_menu.addAction(self.remove_bookmark_action)

        annotations_menu = self.menuBar().addMenu("&Annotations")
        
        clear_page_annotations_action = QAction("Clear Page Annotations", self)
        clear_page_annotations_action.setShortcut("Ctrl+Alt+C")
        clear_page_annotations_action.triggered.connect(self.clear_current_page_annotations)
        annotations_menu.addAction(clear_page_annotations_action)
        
        clear_all_annotations_action = QAction("Clear All Annotations", self)
        clear_all_annotations_action.setShortcut("Ctrl+Alt+Shift+C")
        clear_all_annotations_action.triggered.connect(self.clear_all_annotations)
        annotations_menu.addAction(clear_all_annotations_action)
        
        annotations_menu.addSeparator()
        
        help_action = QAction("💡 Tip: Right-click annotations to delete individual ones", self)
        help_action.setEnabled(False)
        annotations_menu.addAction(help_action)

        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction(open_action)
        
        self.add_bookmark_toolbar_action = QAction(QIcon.fromTheme("bookmark-new"), "Add Bookmark", self)
        self.add_bookmark_toolbar_action.setToolTip("Add bookmark for current page (Ctrl+B)")
        self.add_bookmark_toolbar_action.triggered.connect(self.add_bookmark)
        toolbar.addAction(self.add_bookmark_toolbar_action)
        
        toolbar.addSeparator()

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
        
        toolbar.addSeparator()

        self.search_input = QLineEdit()
        self.search_input.setFixedWidth(150)
        self.search_input.setPlaceholderText("Search text...")
        self.search_input.returnPressed.connect(self.perform_search)
        toolbar.addWidget(QLabel("Search:"))
        toolbar.addWidget(self.search_input)

        self.search_button = QAction(QIcon.fromTheme("edit-find"), "Search", self)
        self.search_button.setToolTip("Search text in PDF")
        self.search_button.triggered.connect(self.perform_search)
        toolbar.addAction(self.search_button)

        self.search_next_action = QAction(QIcon.fromTheme("go-down"), "Next Result", self)
        self.search_next_action.setToolTip("Go to next search result")
        self.search_next_action.triggered.connect(lambda: self.navigate_search(True))
        self.search_next_action.setEnabled(False)
        toolbar.addAction(self.search_next_action)

        self.search_prev_action = QAction(QIcon.fromTheme("go-up"), "Previous Result", self)
        self.search_prev_action.setToolTip("Go to previous search result")
        self.search_prev_action.triggered.connect(lambda: self.navigate_search(False))
        self.search_prev_action.setEnabled(False)
        toolbar.addAction(self.search_prev_action)

        self.search_result_label = QLabel("0 results")
        toolbar.addWidget(self.search_result_label)

        self.create_annotation_toolbar()

    def create_dock_widgets(self):
        """Create dock widgets for table of contents and bookmarks."""
        panels_menu = self.menuBar().addMenu("&Panels")

        self.toc_dock = QDockWidget("Table of Contents", self)
        self.toc_list_widget = QListWidget()
        self.toc_list_widget.itemClicked.connect(self.toc_navigate)
        self.toc_dock.setWidget(self.toc_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.toc_dock)
        self.toc_dock.setVisible(False)

        self.bookmarks_dock = QDockWidget("Bookmarks", self)
        self.bookmarks_list_widget = QListWidget()
        self.bookmarks_list_widget.itemClicked.connect(self.bookmark_navigate)
        self.bookmarks_list_widget.itemDoubleClicked.connect(self.bookmark_navigate)
        self.bookmarks_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmarks_list_widget.customContextMenuRequested.connect(self.show_bookmark_context_menu)
        self.bookmarks_dock.setWidget(self.bookmarks_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.bookmarks_dock)
        self.bookmarks_dock.setVisible(False)

        toggle_toc_action = QAction("Toggle Table of Contents", self)
        toggle_toc_action.setCheckable(True)
        toggle_toc_action.setChecked(False)
        toggle_toc_action.triggered.connect(self.toc_dock.setVisible)
        self.toc_dock.visibilityChanged.connect(toggle_toc_action.setChecked)
        panels_menu.addAction(toggle_toc_action)

        toggle_bookmarks_action = QAction("Toggle Bookmarks", self)
        toggle_bookmarks_action.setCheckable(True)
        toggle_bookmarks_action.setChecked(False)
        toggle_bookmarks_action.triggered.connect(self.bookmarks_dock.setVisible)
        self.bookmarks_dock.visibilityChanged.connect(toggle_bookmarks_action.setChecked)
        panels_menu.addAction(toggle_bookmarks_action)

    def create_annotation_toolbar(self):
        """Create the annotation toolbar."""
        annotation_toolbar = self.addToolBar("Annotation Toolbar")
        annotation_toolbar.setObjectName("AnnotationToolbar")
        
        annotation_mode_action = QAction(QIcon.fromTheme("edit-entry"), "Annotation Mode", self)
        annotation_mode_action.setCheckable=True
        annotation_mode_action.setToolTip("Enable/Disable annotation mode")
        annotation_mode_action.triggered.connect(self.toggle_annotation_mode)
        annotation_toolbar.addAction(annotation_mode_action)
        
        annotation_toolbar.addSeparator()
        
        highlight_action = QAction(QIcon.fromTheme("marker"), "Highlight", self)
        highlight_action.setCheckable=False
        highlight_action.setToolTip("Highlight text - Right-click annotations to delete individual ones")
        highlight_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.HIGHLIGHT))
        annotation_toolbar.addAction(highlight_action)
        
        underline_action = QAction(QIcon.fromTheme("format-text-underline"), "Underline", self)
        underline_action.setCheckable=False
        underline_action.setToolTip("Underline text - Right-click annotations to delete individual ones")
        underline_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.UNDERLINE))
        annotation_toolbar.addAction(underline_action)
        
        text_action = QAction(QIcon.fromTheme("text-field"), "Text", self)
        text_action.setCheckable=False
        text_action.setToolTip("Add text annotation - Right-click annotations to delete individual ones")
        text_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.TEXT))
        annotation_toolbar.addAction(text_action)
        
        annotation_toolbar.addSeparator()
        
        clear_annotations_action = QAction(QIcon.fromTheme("edit-clear"), "Clear All", self)
        clear_annotations_action.setToolTip("Clear all annotations on current page")
        clear_annotations_action.triggered.connect(self.clear_current_page_annotations)
        annotation_toolbar.addAction(clear_annotations_action)
        
        self.annotation_mode_action = annotation_mode_action
        self.annotation_actions = [highlight_action, underline_action, text_action]

    def perform_search(self):
        """Perform search with the input text."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            self.search_result_label.setText("0 results")
            self.search_next_action.setEnabled(False)
            self.search_prev_action.setEnabled(False)
            return
        try:
            text = self.search_input.text().strip()
            if not text:
                viewer.search_text("")
                self.search_result_label.setText("0 results")
                self.search_next_action.setEnabled(False)
                self.search_prev_action.setEnabled(False)
                return
            count = viewer.search_text(text)
            self.search_result_label.setText(f"{count} results")
            self.search_next_action.setEnabled(count > 0)
            self.search_prev_action.setEnabled(count > 0)
            if count > 0:
                viewer.navigate_search(forward=True)
        except Exception as e:
            print(f"Error performing search: {e}")
            self.search_result_label.setText("0 results")
            self.search_next_action.setEnabled(False)
            self.search_prev_action.setEnabled(False)

    def navigate_search(self, forward=True):
        """Navigate to the next or previous search result."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
        try:
            viewer.navigate_search(forward)
        except Exception as e:
            print(f"Error navigating search results: {e}")

    def _update_annotation_ui_state(self, enabled: bool):
        """Update the UI state of annotation-related actions."""
        for action in self.annotation_actions:
            action.setEnabled(enabled)

        if enabled:
            self.annotation_mode_action.setToolTip("Disable annotation mode")
        else:
            self.annotation_mode_action.setToolTip("Enable annotation mode")
            viewer = self.current_viewer()
            if viewer:
                viewer.active_annotation_type = None
            for tool_action in self.annotation_actions:
                tool_action.setChecked(False)

    def toggle_annotation(self, ann_type):
        """Toggle annotation mode for the specified type."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            for action in self.annotation_actions:
                action.setChecked(False)
            return
            
        if viewer.active_annotation_type == ann_type:
            viewer.active_annotation_type = None
            for action in self.annotation_actions:
                action.setChecked(False)
        else:
            viewer.active_annotation_type = ann_type
            for action in self.annotation_actions:
                action.setChecked(action.text().lower() == ann_type.name.lower())
    
    def toggle_annotation_mode(self):
        """Toggle annotation mode for the current viewer."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            self.annotation_mode_action.setChecked(False)
            self._update_annotation_ui_state(False)
            return
            
        mode_enabled = viewer.toggle_annotation_mode()
        self.annotation_mode_action.setChecked(mode_enabled)
        self._update_annotation_ui_state(mode_enabled)
        
        if not mode_enabled:
            viewer.active_annotation_type = None
            for action in self.annotation_actions:
                action.setChecked(False)
        if mode_enabled:
            self.search_input.clear()
            viewer.search_text("")
            self.search_result_label.setText("0 results")
            self.search_next_action.setEnabled(False)
            self.search_prev_action.setEnabled(False)

    def change_view_mode(self, mode: ViewMode):
        """Change the view mode of the current PDF viewer."""
        current_viewer = self.tab_widget.currentWidget()
        if isinstance(current_viewer, PDFViewer):
            current_viewer.set_view_mode(mode)

    def open_file(self):
        """Open a PDF file dialog and load the selected file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.add_pdf_tab(file_path)
            self.add_to_recent_files(file_path)

    def add_pdf_tab(self, file_path):
        """Add a new PDF tab to the tab widget."""
        viewer = PDFViewer(file_path)
        viewer.view_mode_changed.connect(self.update_view_menu_state)
        viewer.current_page_changed_in_continuous_scroll.connect(
            self.update_page_info_from_signal
        )
        viewer.current_page_changed_in_continuous_scroll.connect(
            lambda: self.schedule_progress_save()
        )
        viewer.current_page_changed.connect(
            lambda: self.schedule_progress_save()
        )
        viewer.bookmarks_changed.connect(self.update_bookmarks)

        tab_index = self.tab_widget.addTab(viewer, os.path.basename(file_path))
        self.tab_widget.setCurrentIndex(tab_index)
          # Restore last read page if available
        if viewer.doc:
            last_page = config.get_last_page(file_path)
            print(f"DEBUG: Restoring document {os.path.basename(file_path)}, last_page from config: {last_page}, current_page: {viewer.current_page}")
            if last_page >= 0 and last_page < viewer.doc.page_count:
                print(f"DEBUG: Jumping to saved page: {last_page}")
                viewer.jump_to_page(last_page)
                # Don't save immediately after restoring - let the scheduled save handle it
            else:
                print(f"DEBUG: Not jumping - last_page: {last_page}, total_pages: {viewer.doc.page_count}")
                # Only save immediately if this is a new document (last_page < 0)
                if last_page < 0:
                    config.update_document_progress(file_path, viewer.current_page, viewer.doc.page_count)
                    config.save()

    def close_tab(self, index):
        """Close a tab and clean up resources."""
        widget = self.tab_widget.widget(index)
        if widget:
            widget.deleteLater()
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.total_pages_label.setText("/ N/A")
            self.page_num_input.clear()
            self.toc_list_widget.clear()
            self.bookmarks_list_widget.clear()

    def current_viewer(self) -> PDFViewer | None:
        """Get the currently active PDF viewer."""
        return self.tab_widget.currentWidget()

    def next_page(self):
        """Navigate to the next page in the current viewer."""
        viewer = self.current_viewer()
        if viewer:
            viewer.next_page()
            self.update_page_info()

    def prev_page(self):
        """Navigate to the previous page in the current viewer."""
        viewer = self.current_viewer()
        if viewer:
            viewer.prev_page()
            self.update_page_info()

    def zoom_in(self):
        """Zoom in on the current viewer."""
        viewer = self.current_viewer()
        if viewer:
            viewer.zoom_in()

    def zoom_out(self):
        """Zoom out on the current viewer."""
        viewer = self.current_viewer()
        if viewer:
            viewer.zoom_out()

    def go_to_page_from_input(self):
        """Navigate to the page number entered in the input field."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            try:
                page_num = int(self.page_num_input.text()) - 1
                if 0 <= page_num < viewer.doc.page_count:
                    viewer.jump_to_page(page_num)
                    self.update_page_info()
                else:
                    self.page_num_input.setText(str(viewer.current_page + 1))
            except ValueError:
                self.page_num_input.setText(str(viewer.current_page + 1))

    def update_page_info(self):
        """Update the page information display."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            current_display_page = viewer.current_page
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
        """Update the table of contents display."""
        self.toc_list_widget.clear()
        viewer = self.current_viewer()
        if viewer:
            toc = viewer.get_toc()
            for entry in toc:
                level, title, page = entry
                item = QListWidgetItem("  " * (level - 1) + title)
                item.setData(Qt.ItemDataRole.UserRole, page - 1)
                self.toc_list_widget.addItem(item)

    def toc_navigate(self, item):
        """Navigate to the page selected in the table of contents."""
        viewer = self.current_viewer()
        if viewer and item:
            page_num = item.data(Qt.ItemDataRole.UserRole)
            viewer.jump_to_page(page_num)
            self.update_page_info()

    def add_bookmark(self):
        """Add a bookmark for the current page."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            title, ok = QInputDialog.getText(self, "Add Bookmark", "Enter bookmark title:")
            if ok and title:
                success = viewer.add_bookmark(title=title)
                if success:
                    self.update_bookmarks()
                else:
                    QMessageBox.warning(self, "Warning", "Bookmark already exists for this page.")

    def remove_current_bookmark(self):
        """Remove the bookmark for the current page."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            success = viewer.remove_bookmark(viewer.current_page)
            if success:
                self.update_bookmarks()
            else:
                QMessageBox.warning(self, "Warning", "No bookmark exists for this page.")

    def update_bookmarks(self):
        """Update the bookmarks display."""
        self.bookmarks_list_widget.clear()
        viewer = self.current_viewer()
        if viewer:
            bookmarks = viewer.get_bookmarks()
            for bookmark in bookmarks:
                item = QListWidgetItem(f"{bookmark.title} (Page {bookmark.page_number + 1})")
                item.setData(Qt.ItemDataRole.UserRole, bookmark)
                self.bookmarks_list_widget.addItem(item)

    def bookmark_navigate(self, item):
        """Navigate to the selected bookmark."""
        viewer = self.current_viewer()
        if viewer and item:
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            viewer.jump_to_bookmark(bookmark)
            self.update_page_info()

    def show_bookmark_context_menu(self, position):
        """Show context menu for bookmarks."""
        menu = QMenu()
        delete_action = menu.addAction("Delete Bookmark")
        action = menu.exec(self.bookmarks_list_widget.mapToGlobal(position))
        if action == delete_action:
            item = self.bookmarks_list_widget.itemAt(position)
            if item:
                bookmark = item.data(Qt.ItemDataRole.UserRole)
                viewer = self.current_viewer()
                if viewer:
                    viewer.remove_bookmark(bookmark.page_number)
                    self.update_bookmarks()

    def clear_current_page_annotations(self):
        """Clear all annotations on the current page."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            viewer.annotations = [ann for ann in viewer.annotations if ann.page != viewer.current_page]
            viewer._redraw_page(viewer.current_page)

    def clear_all_annotations(self):
        """Clear all annotations in the document."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            reply = QMessageBox.question(
                self, "Confirm", "Are you sure you want to clear all annotations?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                viewer.annotations = []
                viewer._redraw_all_pages()

    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list."""
        # Update both the local list and config
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]
        # Also add to config
        config.add_recent_file(file_path)
        config.save()
        
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update the recent files menu with progress information."""
        self.recent_files_menu.clear()
        recent_docs = config.get_recent_documents()
        
        for file_path in self.recent_files:
            filename = os.path.basename(file_path)
            
            # Try to find progress information
            doc_info = None
            for doc in recent_docs:
                if doc.get('file_path') == file_path:
                    doc_info = doc
                    break
            
            if doc_info:
                # Show filename with page information
                last_page = doc_info.get('last_page', 0) + 1  # Convert to 1-based
                total_pages = doc_info.get('total_pages', 0)
                action_text = f"{filename} (Page {last_page}/{total_pages})"
            else:
                action_text = filename
            
            action = QAction(action_text, self)
            action.setData(file_path)
            action.triggered.connect(self.open_recent_file)
            self.recent_files_menu.addAction(action)

    def open_recent_file(self):
        """Open a file from the recent files menu."""
        action = self.sender()
        if action:
            file_path = action.data()
            if os.path.exists(file_path):
                self.add_pdf_tab(file_path)
            else:
                QMessageBox.warning(self, "Warning", f"File not found: {file_path}")
                self.recent_files.remove(file_path)
                self.update_recent_files_menu()

    def load_recent_files(self):
        """Load recent files from configuration."""
        self.recent_files = config.get_recent_files()
        self.update_recent_files_menu()

    def save_current_progress(self):
        """Save current reading progress to configuration."""
        viewer = self.current_viewer()
        if viewer and viewer.file_path and viewer.doc:
            current_page = viewer.current_page
            total_pages = viewer.doc.page_count
            print(f"Saving progress: {os.path.basename(viewer.file_path)} - Page {current_page + 1}/{total_pages}")
            config.update_document_progress(viewer.file_path, current_page, total_pages)
            config.save()

    def schedule_progress_save(self):
        """Schedule a progress save after a delay to avoid too frequent saves."""
        # Only print if timer wasn't already active
        if not self.progress_save_timer.isActive():
            print(f"Scheduling progress save in 2 seconds...")
        self.progress_save_timer.start(2000)  # Save after 2 seconds of inactivity

    def update_view_menu_state(self):
        """Update the view mode menu based on the current viewer."""
        viewer = self.current_viewer()
        if viewer:
            mode = viewer.view_mode
            self.single_page_action.setChecked(mode == ViewMode.SINGLE_PAGE)
            self.fit_page_action.setChecked(mode == ViewMode.FIT_PAGE)
            self.fit_width_action.setChecked(mode == ViewMode.FIT_WIDTH)
            self.double_page_action.setChecked(mode == ViewMode.DOUBLE_PAGE)
            self.continuous_scroll_action.setChecked(mode == ViewMode.CONTINUOUS_SCROLL)
        else:
            self.single_page_action.setChecked(True)
            self.fit_page_action.setChecked(False)
            self.fit_width_action.setChecked(False)
            self.double_page_action.setChecked(False)
            self.continuous_scroll_action.setChecked(False)

    def update_page_info_from_signal(self, page_num):
        """Update page info from continuous scroll signal."""
        self.update_page_info()

    def on_tab_changed(self, index):
        """Handle tab change events."""
        self.update_page_info()
        self.update_toc()
        self.update_bookmarks()
        self.update_view_menu_state()

    def closeEvent(self, event):
        """Handle application close event to save progress."""
        # Save current progress for all open documents
        for i in range(self.tab_widget.count()):
            viewer = self.tab_widget.widget(i)
            if isinstance(viewer, PDFViewer) and viewer.file_path and viewer.doc:
                current_page = viewer.current_page
                total_pages = viewer.doc.page_count
                config.update_document_progress(viewer.file_path, current_page, total_pages)
        
        # Save configuration
        config.save()
        event.accept()
