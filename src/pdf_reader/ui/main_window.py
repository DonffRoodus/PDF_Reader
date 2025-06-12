"""Main window and application UI components."""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog,
    QToolBar, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QDockWidget, QInputDialog, QMessageBox, QMenu
)
from PyQt6.QtGui import QIcon, QAction, QActionGroup
from PyQt6.QtCore import Qt

from ..core.models import ViewMode, Bookmark, AnnotationType, Annotation
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

        self.recent_files = []  # For simplicity, store in memory
        
        self.create_menus_and_toolbar()
        self.create_dock_widgets()
        
        self.load_recent_files()
        self.update_view_menu_state()  # Initial state when no tabs might be open

    def create_menus_and_toolbar(self):
        """Create the main menu bar and toolbar."""
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

        self.single_page_action.setChecked(True)  # Default        # Bookmarks Menu
        bookmarks_menu = self.menuBar().addMenu("&Bookmarks")
        
        self.add_bookmark_action = QAction("Add Bookmark", self)
        self.add_bookmark_action.setShortcut("Ctrl+B")
        self.add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(self.add_bookmark_action)
        
        self.remove_bookmark_action = QAction("Remove Bookmark", self)
        self.remove_bookmark_action.setShortcut("Ctrl+Shift+B")
        self.remove_bookmark_action.triggered.connect(self.remove_current_bookmark)
        bookmarks_menu.addAction(self.remove_bookmark_action)

        # Annotations Menu
        annotations_menu = self.menuBar().addMenu("&Annotations")
        
        clear_page_annotations_action = QAction("Clear Page Annotations", self)
        clear_page_annotations_action.setShortcut("Ctrl+Alt+C")
        clear_page_annotations_action.triggered.connect(self.clear_current_page_annotations)
        annotations_menu.addAction(clear_page_annotations_action)
        
        clear_all_annotations_action = QAction("Clear All Annotations", self)
        clear_all_annotations_action.setShortcut("Ctrl+Alt+Shift+C")
        clear_all_annotations_action.triggered.connect(self.clear_all_annotations)
        annotations_menu.addAction(clear_all_annotations_action)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction(open_action)
        
        # Add bookmark button to toolbar
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
        
        # Create annotation toolbar
        self.create_annotation_toolbar()

    def create_dock_widgets(self):
        """Create dock widgets for table of contents and bookmarks."""
        # Panels Menu
        panels_menu = self.menuBar().addMenu("&Panels")

        # Table of Contents Dock
        self.toc_dock = QDockWidget("Table of Contents", self)
        self.toc_list_widget = QListWidget()
        self.toc_list_widget.itemClicked.connect(self.toc_navigate)
        self.toc_dock.setWidget(self.toc_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.toc_dock)
        self.toc_dock.setVisible(False)

        # Bookmarks Dock
        self.bookmarks_dock = QDockWidget("Bookmarks", self)
        self.bookmarks_list_widget = QListWidget()
        self.bookmarks_list_widget.itemClicked.connect(self.bookmark_navigate)
        self.bookmarks_list_widget.itemDoubleClicked.connect(self.bookmark_navigate)
        self.bookmarks_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmarks_list_widget.customContextMenuRequested.connect(self.show_bookmark_context_menu)
        self.bookmarks_dock.setWidget(self.bookmarks_list_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.bookmarks_dock)
        self.bookmarks_dock.setVisible(False)

        # Add toggle actions to the 'Panels' menu
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
        
        # Add annotation mode toggle
        annotation_mode_action = QAction(QIcon.fromTheme("edit-entry"), "Annotation Mode", self)
        annotation_mode_action.setCheckable(True)
        annotation_mode_action.setToolTip("Enable/Disable annotation mode")
        annotation_mode_action.triggered.connect(self.toggle_annotation_mode)
        annotation_toolbar.addAction(annotation_mode_action)
        
        annotation_toolbar.addSeparator()
        
        highlight_action = QAction(QIcon.fromTheme("marker"), "Highlight", self)
        highlight_action.setCheckable(True)
        highlight_action.setToolTip("Highlight text")
        highlight_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.HIGHLIGHT))
        annotation_toolbar.addAction(highlight_action)
        
        underline_action = QAction(QIcon.fromTheme("format-text-underline"), "Underline", self)
        underline_action.setCheckable(True)
        underline_action.setToolTip("Underline text")
        underline_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.UNDERLINE))
        annotation_toolbar.addAction(underline_action)
        
        text_action = QAction(QIcon.fromTheme("text-field"), "Text", self)
        text_action.setCheckable(True)
        text_action.setToolTip("Add text annotation")
        text_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.TEXT))
        annotation_toolbar.addAction(text_action)
        
        annotation_toolbar.addSeparator()
        
        clear_annotations_action = QAction(QIcon.fromTheme("edit-clear"), "Clear All", self)
        clear_annotations_action.setToolTip("Clear all annotations on current page")
        clear_annotations_action.triggered.connect(self.clear_current_page_annotations)
        annotation_toolbar.addAction(clear_annotations_action)
        
        self.annotation_mode_action = annotation_mode_action
        self.annotation_actions = [highlight_action, underline_action, text_action]

    def _update_annotation_ui_state(self, enabled: bool):
        """Update the UI state of annotation-related actions."""
        for action in self.annotation_actions:
            action.setEnabled(enabled)

        if enabled:
            self.annotation_mode_action.setToolTip("Disable annotation mode")
            # Optionally, change the button style when active
            # self.annotation_mode_action.setIcon(QIcon.fromTheme("edit-select")) # Example icon change
            # Or change stylesheet for the button if you have specific styles
            # self.annotation_mode_action.parentWidget().setStyleSheet(
            #     "QToolButton:checked { background-color: lightblue; }" \n
            # ) # This would require the toolbar to be the parent
        else:
            self.annotation_mode_action.setToolTip("Enable annotation mode")
            # Revert to default icon/style if changed
            # self.annotation_mode_action.setIcon(QIcon.fromTheme("edit-entry"))
            # self.annotation_mode_action.parentWidget().setStyleSheet("") # Clear specific styles

            # Also, uncheck any active annotation type tool if mode is disabled
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
            
        # Toggle the annotation mode
        mode_enabled = viewer.toggle_annotation_mode()
        self.annotation_mode_action.setChecked(mode_enabled)
        
        # Update UI state based on annotation mode
        self._update_annotation_ui_state(mode_enabled)
        
        # If annotation mode is disabled, also disable any selected annotation type
        if not mode_enabled:
            viewer.active_annotation_type = None
            for action in self.annotation_actions:
                action.setChecked(False)

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
        viewer.bookmarks_changed.connect(self.update_bookmarks)

        tab_index = self.tab_widget.addTab(viewer, os.path.basename(file_path))
        self.tab_widget.setCurrentIndex(tab_index)

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
                page_num = int(self.page_num_input.text()) - 1  # User sees 1-based
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
        """Update the table of contents display."""
        self.toc_list_widget.clear()
        viewer = self.current_viewer()
        if viewer:
            toc = viewer.get_toc()
            for level, title, page_num in toc:
                item = QListWidgetItem(f"{'  ' * (level-1)}{title} (Page {page_num})")
                item.setData(Qt.ItemDataRole.UserRole, page_num - 1)  # Store 0-based page num
                self.toc_list_widget.addItem(item)

    def toc_navigate(self, item):
        """Navigate to a page from the table of contents."""
        viewer = self.current_viewer()
        if viewer:
            page_num = item.data(Qt.ItemDataRole.UserRole)
            viewer.jump_to_page(page_num)
            self.update_page_info()
    def add_bookmark(self):
        """Add a bookmark for the current page."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        # Get bookmark title from user
        title, ok = QInputDialog.getText(
            self, 
            "Add Bookmark", 
            f"Enter bookmark title for page {viewer.current_page + 1}:",
            text=f"Page {viewer.current_page + 1}"
        )
        
        if ok and title.strip():
            if viewer.add_bookmark(title.strip()):
                QMessageBox.information(self, "Bookmark Added", f"Bookmark '{title}' added successfully!")
            else:
                QMessageBox.warning(self, "Bookmark Error", "Could not add bookmark. Page may already be bookmarked.")
    
    def remove_current_bookmark(self):
        """Remove bookmark for the current page."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        if viewer.has_bookmark(viewer.current_page):
            if viewer.remove_bookmark(viewer.current_page):
                QMessageBox.information(self, "Bookmark Removed", "Bookmark removed successfully!")
        else:
            QMessageBox.information(self, "No Bookmark", "Current page does not have a bookmark.")
    
    def update_bookmarks(self):
        """Update the bookmarks display."""
        self.bookmarks_list_widget.clear()
        viewer = self.current_viewer()
        if viewer:
            bookmarks = viewer.get_bookmarks()
            for bookmark in bookmarks:
                item = QListWidgetItem(bookmark.display_title())
                item.setData(Qt.ItemDataRole.UserRole, bookmark)  # Store the bookmark object
                self.bookmarks_list_widget.addItem(item)
    
    def bookmark_navigate(self, item):
        """Navigate to a page from the bookmarks panel."""
        viewer = self.current_viewer()
        if viewer:
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(bookmark, Bookmark):
                viewer.jump_to_bookmark(bookmark)
                self.update_page_info()
    
    def show_bookmark_context_menu(self, position):
        """Show context menu for bookmarks list."""
        item = self.bookmarks_list_widget.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # Go to bookmark action
        goto_action = QAction("Go to Page", self)
        goto_action.triggered.connect(lambda: self.bookmark_navigate(item))
        menu.addAction(goto_action)
        
        # Remove bookmark action
        remove_action = QAction("Remove Bookmark", self)
        remove_action.triggered.connect(lambda: self.remove_bookmark_from_list(item))
        menu.addAction(remove_action)
        
        # Show menu at the cursor position
        menu.exec(self.bookmarks_list_widget.mapToGlobal(position))
    
    def remove_bookmark_from_list(self, item):
        """Remove a bookmark from the list."""
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(bookmark, Bookmark):
            viewer = self.current_viewer()
            if viewer and viewer.remove_bookmark(bookmark.page_number):
                QMessageBox.information(self, "Bookmark Removed", f"Bookmark '{bookmark.title}' removed successfully!")

    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep last 10
        self.update_recent_files_menu()

    def load_recent_files(self):
        """Load recent files from storage (placeholder implementation)."""
        # TODO: Load from a settings file
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update the recent files menu."""
        self.recent_files_menu.clear()
        for file_path in self.recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.triggered.connect(self.open_recent_file)
            self.recent_files_menu.addAction(action)

    def open_recent_file(self):
        """Open a file from the recent files menu."""
        action = self.sender()
        if action:
            file_path = action.data()
            self.add_pdf_tab(file_path)

    def on_tab_changed(self, index):
        """Handle tab change events."""
        self.update_page_info()
        self.update_toc()
        self.update_bookmarks()
        current_viewer = self.current_viewer()
        if current_viewer:
            current_viewer.view_mode_changed.connect(self.update_view_menu_state)
            current_viewer.current_page_changed_in_continuous_scroll.connect(
                self.update_page_info_from_signal
            )
            current_viewer.bookmarks_changed.connect(self.update_bookmarks)
            self.update_view_menu_state(current_viewer.view_mode)
        else:
            self.update_view_menu_state()
            self.update_page_info()

    def update_page_info_from_signal(self, page_num):
        """Update page info from signals (specifically for continuous scroll)."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            self.page_num_input.setText(str(page_num + 1))  # page_num is 0-indexed
        elif not viewer:
            self.page_num_input.clear()
            self.total_pages_label.setText("/ N/A")

    def update_view_menu_state(self, active_mode: ViewMode | None = None):
        """Update the view menu state based on the active view mode."""
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
            act.setEnabled(True if viewer and viewer.doc else False)
        
        # Enable/disable bookmark actions based on document availability
        self.add_bookmark_action.setEnabled(True if viewer and viewer.doc else False)
        self.add_bookmark_toolbar_action.setEnabled(True if viewer and viewer.doc else False)
        self.remove_bookmark_action.setEnabled(True if viewer and viewer.doc else False)

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
        """Handle window resize events."""
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
            ):
                # For continuous FIT_WIDTH, a full rebuild is needed as zoom_factor for all pages changes
                vp_width = viewer.scroll_area.viewport().width()
                page_rect = viewer.doc.load_page(viewer.current_page).bound()
                if vp_width > 0 and page_rect.width > 0:
                    viewer.zoom_factor = (
                        vp_width - viewer.scroll_area.verticalScrollBar().width()
                    ) / page_rect.width
                else:
                    viewer.zoom_factor = 1.0
                viewer._setup_continuous_view()

    def clear_current_page_annotations(self):
        """Clear all annotations on the current page."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        current_page = viewer.current_page
        
        # Count annotations on current page
        annotations_on_page = [ann for ann in viewer.annotations if ann.page == current_page]
        
        if not annotations_on_page:
            QMessageBox.information(self, "No Annotations", f"No annotations found on page {current_page + 1}.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Clear Annotations", 
            f"Are you sure you want to clear all {len(annotations_on_page)} annotation(s) on page {current_page + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove annotations on current page
            viewer.annotations = [ann for ann in viewer.annotations if ann.page != current_page]
            
            # Redraw the page
            viewer._redraw_page(current_page)
            
            QMessageBox.information(self, "Annotations Cleared", f"Cleared {len(annotations_on_page)} annotation(s) from page {current_page + 1}.")

    def clear_all_annotations(self):
        """Clear all annotations from the entire document."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        if not viewer.annotations:
            QMessageBox.information(self, "No Annotations", "No annotations found in this document.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Clear All Annotations", 
            f"Are you sure you want to clear all {len(viewer.annotations)} annotation(s) from this document?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            annotation_count = len(viewer.annotations)
            viewer.annotations.clear()
            
            # Redraw current page
            viewer._redraw_page(viewer.current_page)
            
            QMessageBox.information(self, "All Annotations Cleared", f"Cleared {annotation_count} annotation(s) from the document.")

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
        viewer.bookmarks_changed.connect(self.update_bookmarks)

        tab_index = self.tab_widget.addTab(viewer, os.path.basename(file_path))
        self.tab_widget.setCurrentIndex(tab_index)

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
                page_num = int(self.page_num_input.text()) - 1  # User sees 1-based
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
        """Update the table of contents display."""
        self.toc_list_widget.clear()
        viewer = self.current_viewer()
        if viewer:
            toc = viewer.get_toc()
            for level, title, page_num in toc:
                item = QListWidgetItem(f"{'  ' * (level-1)}{title} (Page {page_num})")
                item.setData(Qt.ItemDataRole.UserRole, page_num - 1)  # Store 0-based page num
                self.toc_list_widget.addItem(item)

    def toc_navigate(self, item):
        """Navigate to a page from the table of contents."""
        viewer = self.current_viewer()
        if viewer:
            page_num = item.data(Qt.ItemDataRole.UserRole)
            viewer.jump_to_page(page_num)
            self.update_page_info()
    def add_bookmark(self):
        """Add a bookmark for the current page."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        # Get bookmark title from user
        title, ok = QInputDialog.getText(
            self, 
            "Add Bookmark", 
            f"Enter bookmark title for page {viewer.current_page + 1}:",
            text=f"Page {viewer.current_page + 1}"
        )
        
        if ok and title.strip():
            if viewer.add_bookmark(title.strip()):
                QMessageBox.information(self, "Bookmark Added", f"Bookmark '{title}' added successfully!")
            else:
                QMessageBox.warning(self, "Bookmark Error", "Could not add bookmark. Page may already be bookmarked.")
    
    def remove_current_bookmark(self):
        """Remove bookmark for the current page."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        if viewer.has_bookmark(viewer.current_page):
            if viewer.remove_bookmark(viewer.current_page):
                QMessageBox.information(self, "Bookmark Removed", "Bookmark removed successfully!")
        else:
            QMessageBox.information(self, "No Bookmark", "Current page does not have a bookmark.")
    
    def update_bookmarks(self):
        """Update the bookmarks display."""
        self.bookmarks_list_widget.clear()
        viewer = self.current_viewer()
        if viewer:
            bookmarks = viewer.get_bookmarks()
            for bookmark in bookmarks:
                item = QListWidgetItem(bookmark.display_title())
                item.setData(Qt.ItemDataRole.UserRole, bookmark)  # Store the bookmark object
                self.bookmarks_list_widget.addItem(item)
    
    def bookmark_navigate(self, item):
        """Navigate to a page from the bookmarks panel."""
        viewer = self.current_viewer()
        if viewer:
            bookmark = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(bookmark, Bookmark):
                viewer.jump_to_bookmark(bookmark)
                self.update_page_info()
    
    def show_bookmark_context_menu(self, position):
        """Show context menu for bookmarks list."""
        item = self.bookmarks_list_widget.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # Go to bookmark action
        goto_action = QAction("Go to Page", self)
        goto_action.triggered.connect(lambda: self.bookmark_navigate(item))
        menu.addAction(goto_action)
        
        # Remove bookmark action
        remove_action = QAction("Remove Bookmark", self)
        remove_action.triggered.connect(lambda: self.remove_bookmark_from_list(item))
        menu.addAction(remove_action)
        
        # Show menu at the cursor position
        menu.exec(self.bookmarks_list_widget.mapToGlobal(position))
    
    def remove_bookmark_from_list(self, item):
        """Remove a bookmark from the list."""
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(bookmark, Bookmark):
            viewer = self.current_viewer()
            if viewer and viewer.remove_bookmark(bookmark.page_number):
                QMessageBox.information(self, "Bookmark Removed", f"Bookmark '{bookmark.title}' removed successfully!")

    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep last 10
        self.update_recent_files_menu()

    def load_recent_files(self):
        """Load recent files from storage (placeholder implementation)."""
        # TODO: Load from a settings file
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update the recent files menu."""
        self.recent_files_menu.clear()
        for file_path in self.recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.triggered.connect(self.open_recent_file)
            self.recent_files_menu.addAction(action)

    def open_recent_file(self):
        """Open a file from the recent files menu."""
        action = self.sender()
        if action:
            file_path = action.data()
            self.add_pdf_tab(file_path)

    def on_tab_changed(self, index):
        """Handle tab change events."""
        self.update_page_info()
        self.update_toc()
        self.update_bookmarks()
        current_viewer = self.current_viewer()
        if current_viewer:
            current_viewer.view_mode_changed.connect(self.update_view_menu_state)
            current_viewer.current_page_changed_in_continuous_scroll.connect(
                self.update_page_info_from_signal
            )
            current_viewer.bookmarks_changed.connect(self.update_bookmarks)
            self.update_view_menu_state(current_viewer.view_mode)
        else:
            self.update_view_menu_state()
            self.update_page_info()

    def update_page_info_from_signal(self, page_num):
        """Update page info from signals (specifically for continuous scroll)."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            self.page_num_input.setText(str(page_num + 1))  # page_num is 0-indexed
        elif not viewer:
            self.page_num_input.clear()
            self.total_pages_label.setText("/ N/A")

    def update_view_menu_state(self, active_mode: ViewMode | None = None):
        """Update the view menu state based on the active view mode."""
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
            act.setEnabled(True if viewer and viewer.doc else False)
        
        # Enable/disable bookmark actions based on document availability
        self.add_bookmark_action.setEnabled(True if viewer and viewer.doc else False)
        self.add_bookmark_toolbar_action.setEnabled(True if viewer and viewer.doc else False)
        self.remove_bookmark_action.setEnabled(True if viewer and viewer.doc else False)

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
        """Handle window resize events."""
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
            ):
                # For continuous FIT_WIDTH, a full rebuild is needed as zoom_factor for all pages changes
                vp_width = viewer.scroll_area.viewport().width()
                page_rect = viewer.doc.load_page(viewer.current_page).bound()
                if vp_width > 0 and page_rect.width > 0:
                    viewer.zoom_factor = (
                        vp_width - viewer.scroll_area.verticalScrollBar().width()
                    ) / page_rect.width
                else:
                    viewer.zoom_factor = 1.0
                viewer._setup_continuous_view()

    def clear_current_page_annotations(self):
        """Clear all annotations on the current page."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        current_page = viewer.current_page
        
        # Count annotations on current page
        annotations_on_page = [ann for ann in viewer.annotations if ann.page == current_page]
        
        if not annotations_on_page:
            QMessageBox.information(self, "No Annotations", f"No annotations found on page {current_page + 1}.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Clear Annotations", 
            f"Are you sure you want to clear all {len(annotations_on_page)} annotation(s) on page {current_page + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove annotations on current page
            viewer.annotations = [ann for ann in viewer.annotations if ann.page != current_page]
            
            # Redraw the page
            viewer._redraw_page(current_page)
            
            QMessageBox.information(self, "Annotations Cleared", f"Cleared {len(annotations_on_page)} annotation(s) from page {current_page + 1}.")

    def clear_all_annotations(self):
        """Clear all annotations from the entire document."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            return
            
        if not viewer.annotations:
            QMessageBox.information(self, "No Annotations", "No annotations found in this document.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Clear All Annotations", 
            f"Are you sure you want to clear all {len(viewer.annotations)} annotation(s) from this document?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            annotation_count = len(viewer.annotations)
            viewer.annotations.clear()
            
            # Redraw current page
            viewer._redraw_page(viewer.current_page)
            
            QMessageBox.information(self, "All Annotations Cleared", f"Cleared {annotation_count} annotation(s) from the document.")
