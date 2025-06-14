"""Main window and application UI components."""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QFileDialog,
    QToolBar, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QDockWidget, QInputDialog, QMessageBox, QMenu, QStatusBar,
    QProgressBar, QFrame, QHBoxLayout, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QIcon, QAction, QActionGroup, QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize

from ..core.models import ViewMode, Bookmark, AnnotationType, Annotation
from ..core.config import config
from .pdf_viewer import PDFViewer
from .error_dialog import UserFeedbackWidget, show_error_dialog


class LoadingThread(QThread):
    """Background thread for loading PDF files."""
    progress_updated = pyqtSignal(int)
    loading_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            # Simulate loading progress for better UX
            for i in range(0, 101, 10):
                self.progress_updated.emit(i)
                self.msleep(50)  # Small delay to show progress
            
            self.loading_finished.emit(True, "Document loaded successfully")
        except Exception as e:
            self.loading_finished.emit(False, f"Error loading document: {str(e)}")


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
        self.loading_thread = None
        
        # Timer for saving reading progress
        self.progress_save_timer = QTimer()
        self.progress_save_timer.timeout.connect(self.save_current_progress)
        self.progress_save_timer.setSingleShot(True)
        
        # Timer for auto-hiding status messages
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.clear_status_message)
        self.status_timer.setSingleShot(True)
        
        self.create_status_bar()
        self.create_menus_and_toolbar()
        self.create_dock_widgets()
        self.create_feedback_system()
        self.setup_keyboard_navigation()
        self.setup_accessibility_features()
        
        self.load_recent_files()
        self.update_view_menu_state()
        self.restore_window_state()
        self.show_status_message("Ready", 3000)

    def setup_keyboard_navigation(self):
        """Set up comprehensive keyboard navigation."""
        # File operations
        self.addAction(self.create_shortcut("Ctrl+O", self.open_file, "Open document"))
        self.addAction(self.create_shortcut("Ctrl+W", self.close_current_tab, "Close current tab"))
        self.addAction(self.create_shortcut("Ctrl+Q", self.close, "Exit application"))
        self.addAction(self.create_shortcut("Ctrl+Shift+T", self.reopen_last_closed, "Reopen last closed tab"))
        
        # Navigation
        self.addAction(self.create_shortcut("Left", self.prev_page, "Previous page"))
        self.addAction(self.create_shortcut("Right", self.next_page, "Next page"))
        self.addAction(self.create_shortcut("Page_Up", self.prev_page, "Previous page"))
        self.addAction(self.create_shortcut("Page_Down", self.next_page, "Next page"))
        self.addAction(self.create_shortcut("Home", self.first_page, "First page"))
        self.addAction(self.create_shortcut("End", self.last_page, "Last page"))
        self.addAction(self.create_shortcut("Ctrl+G", self.go_to_page_dialog, "Go to page"))
        
        # View modes
        self.addAction(self.create_shortcut("1", lambda: self.change_view_mode(ViewMode.SINGLE_PAGE), "Single page view"))
        self.addAction(self.create_shortcut("2", lambda: self.change_view_mode(ViewMode.FIT_PAGE), "Fit page view"))
        self.addAction(self.create_shortcut("3", lambda: self.change_view_mode(ViewMode.FIT_WIDTH), "Fit width view"))
        self.addAction(self.create_shortcut("4", lambda: self.change_view_mode(ViewMode.DOUBLE_PAGE), "Double page view"))
        self.addAction(self.create_shortcut("5", lambda: self.change_view_mode(ViewMode.CONTINUOUS_SCROLL), "Continuous scroll view"))
        
        # Zoom
        self.addAction(self.create_shortcut("Ctrl+=", self.zoom_in, "Zoom in"))
        self.addAction(self.create_shortcut("Ctrl+-", self.zoom_out, "Zoom out"))
        self.addAction(self.create_shortcut("Ctrl+0", self.reset_zoom, "Reset zoom"))
        
        # Search
        self.addAction(self.create_shortcut("Ctrl+F", self.focus_search, "Focus search box"))
        self.addAction(self.create_shortcut("F3", lambda: self.navigate_search(True), "Find next"))
        self.addAction(self.create_shortcut("Shift+F3", lambda: self.navigate_search(False), "Find previous"))
        self.addAction(self.create_shortcut("Escape", self.clear_search, "Clear search"))
        
        # Annotations
        self.addAction(self.create_shortcut("Ctrl+H", lambda: self.toggle_annotation(AnnotationType.HIGHLIGHT), "Highlight text"))
        self.addAction(self.create_shortcut("Ctrl+U", lambda: self.toggle_annotation(AnnotationType.UNDERLINE), "Underline text"))
        self.addAction(self.create_shortcut("Ctrl+T", lambda: self.toggle_annotation(AnnotationType.TEXT), "Add text note"))
        
        # Bookmarks
        self.addAction(self.create_shortcut("Ctrl+B", self.add_bookmark, "Add bookmark"))
        self.addAction(self.create_shortcut("Ctrl+Shift+B", self.remove_current_bookmark, "Remove bookmark"))
        
        # Panels
        self.addAction(self.create_shortcut("F9", self.toggle_bookmarks_panel, "Toggle bookmarks panel"))
        self.addAction(self.create_shortcut("F10", self.toggle_toc_panel, "Toggle table of contents"))
        
        # Help
        self.addAction(self.create_shortcut("F1", self.show_keyboard_shortcuts, "Show keyboard shortcuts"))

    def create_shortcut(self, key_sequence, slot, description):
        """Create a keyboard shortcut action."""
        action = QAction(description, self)
        action.setShortcut(key_sequence)
        action.triggered.connect(slot)
        return action

    def setup_accessibility_features(self):
        """Set up accessibility features for better usability."""
        # Set accessible names and descriptions
        self.setAccessibleName("PDF Reader Main Window")
        self.setAccessibleDescription("Main window for viewing and annotating PDF documents")
        
        # Tab widget accessibility
        self.tab_widget.setAccessibleName("Document Tabs")
        self.tab_widget.setAccessibleDescription("Tabs for open PDF documents")
        
        # Enable focus tracking for better keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set window role for screen readers
        self.setWindowRole("MainWindow")
        
        # Enable automatic tooltips on buttons
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)

    def create_feedback_system(self):
        """Create user feedback system."""
        # Add feedback widget to main layout
        self.feedback_widget = UserFeedbackWidget(self)
        self.feedback_widget.action_requested.connect(self.handle_feedback_action)
        
        # Insert at top of central widget
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        central_layout.addWidget(self.feedback_widget)
        central_layout.addWidget(self.tab_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def handle_feedback_action(self, action_data):
        """Handle feedback widget action requests."""
        if action_data == "open_file":
            self.open_file()
        elif action_data == "show_help":
            self.show_user_guide()
        # Add more action handlers as needed

    def show_feedback(self, message, message_type="info", action_text=None, action_data=None, timeout=5000):
        """Show user feedback message."""
        self.feedback_widget.show_message(message, message_type, action_text, action_data, timeout)

    def restore_window_state(self):
        """Restore window state from configuration."""
        state = config.get_window_state()
        
        self.resize(state['width'], state['height'])
        self.move(state['x'], state['y'])
        
        if state['maximized']:
            self.showMaximized()

    def save_window_state(self):
        """Save current window state to configuration."""
        if not self.isMaximized():
            config.save_window_state(
                self.width(), self.height(),
                self.x(), self.y(),
                False
            )
        else:
            config.save_window_state(
                config.get('window.width', 1200),
                config.get('window.height', 800),
                config.get('window.x', 100),
                config.get('window.y', 100),
                True
            )

    def create_status_bar(self):
        """Create status bar with document info and progress indicators."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Document info widget
        self.doc_info_widget = QWidget()
        doc_info_layout = QHBoxLayout(self.doc_info_widget)
        doc_info_layout.setContentsMargins(5, 0, 5, 0)
        
        self.document_name_label = QLabel("No document")
        self.document_name_label.setStyleSheet("font-weight: bold; color: #333;")
        doc_info_layout.addWidget(self.document_name_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        doc_info_layout.addWidget(separator)
        
        self.page_info_label = QLabel("Page: - / -")
        doc_info_layout.addWidget(self.page_info_label)
        
        # Another separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        doc_info_layout.addWidget(separator2)
        
        self.zoom_info_label = QLabel("Zoom: 100%")
        doc_info_layout.addWidget(self.zoom_info_label)
        
        self.status_bar.addPermanentWidget(self.doc_info_widget)
        
        # Progress bar for loading operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Operation status label
        self.operation_status_label = QLabel()
        self.operation_status_label.setStyleSheet("color: #666;")
        self.status_bar.addWidget(self.operation_status_label)

    def show_status_message(self, message, timeout=5000):
        """Show a temporary status message."""
        self.operation_status_label.setText(message)
        if timeout > 0:
            self.status_timer.start(timeout)

    def clear_status_message(self):
        """Clear the temporary status message."""
        self.operation_status_label.setText("")

    def show_loading_progress(self, visible=True):
        """Show or hide loading progress indicator."""
        self.progress_bar.setVisible(visible)
        if visible:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)

    def update_document_status(self, document_name=None, current_page=None, total_pages=None, zoom_factor=None):
        """Update document status information in status bar."""
        if document_name is not None:
            self.document_name_label.setText(document_name)        
        if current_page is not None and total_pages is not None:
            self.page_info_label.setText(f"Page: {current_page + 1} / {total_pages}")
        
        if zoom_factor is not None:
            self.zoom_info_label.setText(f"Zoom: {int(zoom_factor * 100)}%")

    def create_menus_and_toolbar(self):
        """Create the main menu bar and toolbar with improved accessibility."""
        # File Menu
        file_menu = self.menuBar().addMenu("&File")
        
        open_action = QAction(QIcon.fromTheme("document-open"), "&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip("Open a PDF document (Ctrl+O)")
        open_action.setStatusTip("Open a PDF document from your computer")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()
        
        self.recent_files_menu = file_menu.addMenu("&Recent Files")
        self.recent_files_menu.setIcon(QIcon.fromTheme("document-open-recent"))
        
        clear_recent_action = QAction("Clear Recent Files", self)
        clear_recent_action.triggered.connect(self.clear_recent_files)
        self.recent_files_menu.addSeparator()
        self.recent_files_menu.addAction(clear_recent_action)

        file_menu.addSeparator()
        
        close_tab_action = QAction("&Close Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.setToolTip("Close current document tab (Ctrl+W)")
        close_tab_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setToolTip("Exit the application (Ctrl+Q)")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)        # View Menu
        view_mode_menu = self.menuBar().addMenu("&View")
        view_mode_menu.setIcon(QIcon.fromTheme("view-preview"))
        
        # View Mode submenu
        view_modes_submenu = view_mode_menu.addMenu("View &Modes")
        self.view_mode_group = QActionGroup(self)
        self.view_mode_group.setExclusive(True)

        self.single_page_action = QAction("&Single Page", self, checkable=True)
        self.single_page_action.setShortcut("1")
        self.single_page_action.setToolTip("Single page view (Press 1)")
        self.single_page_action.setStatusTip("Display one page at a time")
        self.single_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.SINGLE_PAGE)
        )
        view_modes_submenu.addAction(self.single_page_action)
        self.view_mode_group.addAction(self.single_page_action)

        self.fit_page_action = QAction("Fit &Page", self, checkable=True)
        self.fit_page_action.setShortcut("2")
        self.fit_page_action.setToolTip("Fit page to window (Press 2)")
        self.fit_page_action.setStatusTip("Fit entire page within the window")
        self.fit_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.FIT_PAGE)
        )
        view_modes_submenu.addAction(self.fit_page_action)
        self.view_mode_group.addAction(self.fit_page_action)

        self.fit_width_action = QAction("Fit &Width", self, checkable=True)
        self.fit_width_action.setShortcut("3")
        self.fit_width_action.setToolTip("Fit page width to window (Press 3)")
        self.fit_width_action.setStatusTip("Fit page width to window for optimal reading")
        self.fit_width_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.FIT_WIDTH)
        )
        view_modes_submenu.addAction(self.fit_width_action)
        self.view_mode_group.addAction(self.fit_width_action)

        self.double_page_action = QAction("&Double Page", self, checkable=True)
        self.double_page_action.setShortcut("4")
        self.double_page_action.setToolTip("Double page view (Press 4)")
        self.double_page_action.setStatusTip("Display two pages side by side")
        self.double_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.DOUBLE_PAGE)
        )
        view_modes_submenu.addAction(self.double_page_action)
        self.view_mode_group.addAction(self.double_page_action)

        self.continuous_scroll_action = QAction("&Continuous Scroll", self, checkable=True)
        self.continuous_scroll_action.setShortcut("5")
        self.continuous_scroll_action.setToolTip("Continuous scroll view (Press 5)")
        self.continuous_scroll_action.setStatusTip("Scroll through all pages continuously")
        self.continuous_scroll_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.CONTINUOUS_SCROLL)
        )
        view_modes_submenu.addAction(self.continuous_scroll_action)
        self.view_mode_group.addAction(self.continuous_scroll_action)

        self.single_page_action.setChecked(True)
        
        view_mode_menu.addSeparator()
        
        # Zoom actions
        zoom_in_menu_action = QAction("Zoom &In", self)
        zoom_in_menu_action.setShortcut("Ctrl++")
        zoom_in_menu_action.setToolTip("Zoom in (Ctrl++)")
        zoom_in_menu_action.triggered.connect(self.zoom_in)
        view_mode_menu.addAction(zoom_in_menu_action)
        
        zoom_out_menu_action = QAction("Zoom &Out", self)
        zoom_out_menu_action.setShortcut("Ctrl+-")
        zoom_out_menu_action.setToolTip("Zoom out (Ctrl+-)")
        zoom_out_menu_action.triggered.connect(self.zoom_out)
        view_mode_menu.addAction(zoom_out_menu_action)
        
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.setToolTip("Reset zoom to 100% (Ctrl+0)")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_mode_menu.addAction(reset_zoom_action)        # Bookmarks Menu
        bookmarks_menu = self.menuBar().addMenu("&Bookmarks")
        bookmarks_menu.setIcon(QIcon.fromTheme("bookmark"))
        
        self.add_bookmark_action = QAction(QIcon.fromTheme("bookmark-new"), "&Add Bookmark", self)
        self.add_bookmark_action.setShortcut("Ctrl+B")
        self.add_bookmark_action.setToolTip("Add bookmark for current page (Ctrl+B)")
        self.add_bookmark_action.setStatusTip("Create a bookmark for the current page")
        self.add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(self.add_bookmark_action)
        
        self.remove_bookmark_action = QAction(QIcon.fromTheme("bookmark-remove"), "&Remove Bookmark", self)
        self.remove_bookmark_action.setShortcut("Ctrl+Shift+B")
        self.remove_bookmark_action.setToolTip("Remove bookmark from current page (Ctrl+Shift+B)")
        self.remove_bookmark_action.setStatusTip("Remove bookmark from the current page")
        self.remove_bookmark_action.triggered.connect(self.remove_current_bookmark)
        bookmarks_menu.addAction(self.remove_bookmark_action)
        
        bookmarks_menu.addSeparator()
        
        manage_bookmarks_action = QAction("&Manage Bookmarks...", self)
        manage_bookmarks_action.setToolTip("Open bookmark management panel")
        manage_bookmarks_action.triggered.connect(lambda: self.bookmarks_dock.setVisible(True))
        bookmarks_menu.addAction(manage_bookmarks_action)

        # Annotations Menu
        annotations_menu = self.menuBar().addMenu("&Annotations")
        annotations_menu.setIcon(QIcon.fromTheme("text-field"))
        
        # Annotation tools submenu
        annotation_tools_submenu = annotations_menu.addMenu("Annotation &Tools")
        
        highlight_menu_action = QAction(QIcon.fromTheme("marker"), "&Highlight Text", self)
        highlight_menu_action.setShortcut("Ctrl+H")
        highlight_menu_action.setToolTip("Highlight selected text (Ctrl+H)")
        highlight_menu_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.HIGHLIGHT))
        annotation_tools_submenu.addAction(highlight_menu_action)
        
        underline_menu_action = QAction(QIcon.fromTheme("format-text-underline"), "&Underline Text", self)
        underline_menu_action.setShortcut("Ctrl+U")
        underline_menu_action.setToolTip("Underline selected text (Ctrl+U)")
        underline_menu_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.UNDERLINE))
        annotation_tools_submenu.addAction(underline_menu_action)
        
        text_note_menu_action = QAction(QIcon.fromTheme("text-field"), "Add &Text Note", self)
        text_note_menu_action.setShortcut("Ctrl+T")
        text_note_menu_action.setToolTip("Add text annotation (Ctrl+T)")
        text_note_menu_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.TEXT))
        annotation_tools_submenu.addAction(text_note_menu_action)
        
        annotations_menu.addSeparator()
        
        clear_page_annotations_action = QAction(QIcon.fromTheme("edit-clear"), "Clear &Page Annotations", self)
        clear_page_annotations_action.setShortcut("Ctrl+Alt+C")
        clear_page_annotations_action.setToolTip("Clear all annotations on current page (Ctrl+Alt+C)")
        clear_page_annotations_action.setStatusTip("Remove all annotations from the current page")
        clear_page_annotations_action.triggered.connect(self.clear_current_page_annotations)
        annotations_menu.addAction(clear_page_annotations_action)
        
        clear_all_annotations_action = QAction(QIcon.fromTheme("edit-clear-all"), "Clear &All Annotations", self)
        clear_all_annotations_action.setShortcut("Ctrl+Alt+Shift+C")
        clear_all_annotations_action.setToolTip("Clear all annotations in document (Ctrl+Alt+Shift+C)")
        clear_all_annotations_action.setStatusTip("Remove all annotations from the entire document")
        clear_all_annotations_action.triggered.connect(self.clear_all_annotations)
        annotations_menu.addAction(clear_all_annotations_action)
        annotations_menu.addSeparator()
        
        annotation_help_action = QAction("💡 Tip: Right-click annotations to delete individual ones", self)
        annotation_help_action.setEnabled(False)
        annotations_menu.addAction(annotation_help_action)
        
        # Help Menu
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.setIcon(QIcon.fromTheme("help-about"))
        
        keyboard_shortcuts_action = QAction(QIcon.fromTheme("preferences-desktop-keyboard"), "&Keyboard Shortcuts", self)
        keyboard_shortcuts_action.setShortcut("F1")
        keyboard_shortcuts_action.setToolTip("Show keyboard shortcuts (F1)")
        keyboard_shortcuts_action.triggered.connect(self.show_keyboard_shortcuts)
        help_menu.addAction(keyboard_shortcuts_action)
        
        user_guide_action = QAction(QIcon.fromTheme("help-contents"), "&User Guide", self)
        user_guide_action.setToolTip("Open user guide")
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
        
        help_menu.addSeparator()
        
        report_issue_action = QAction(QIcon.fromTheme("dialog-warning"), "&Report Issue", self)
        report_issue_action.setToolTip("Report a bug or issue")
        report_issue_action.triggered.connect(self.report_issue)
        help_menu.addAction(report_issue_action)
        
        help_menu.addSeparator()
        
        about_action = QAction(QIcon.fromTheme("help-about"), "&About PDF Reader", self)
        about_action.setToolTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
          # Create improved toolbar
        self.create_toolbar()

    def create_toolbar(self):
        """Create organized toolbars with improved responsiveness."""
        # Single compact toolbar
        toolbar = QToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setObjectName("MainToolbar")
        self.addToolBar(toolbar)
        
        # File operations
        open_action = QAction(QIcon.fromTheme("document-open"), "Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip("Open a PDF document (Ctrl+O)")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # Navigation
        self.prev_page_action = QAction(QIcon.fromTheme("go-previous"), "Previous", self)
        self.prev_page_action.setShortcut("Left")
        self.prev_page_action.setToolTip("Previous page (Left arrow or Page Up)")
        self.prev_page_action.triggered.connect(self.prev_page)
        self.prev_page_action.setEnabled(False)
        toolbar.addAction(self.prev_page_action)

        self.next_page_action = QAction(QIcon.fromTheme("go-next"), "Next", self)
        self.next_page_action.setShortcut("Right")
        self.next_page_action.setToolTip("Next page (Right arrow or Page Down)")
        self.next_page_action.triggered.connect(self.next_page)
        self.next_page_action.setEnabled(False)
        toolbar.addAction(self.next_page_action)
          # Page input (more readable width)
        self.page_num_input = QLineEdit()
        self.page_num_input.setFixedWidth(50)
        self.page_num_input.setToolTip("Page number")
        self.page_num_input.setPlaceholderText("1")
        self.page_num_input.returnPressed.connect(self.go_to_page_from_input)
        toolbar.addWidget(self.page_num_input)
        
        self.total_pages_label = QLabel("/N/A")
        self.total_pages_label.setStyleSheet("font-size: 10px; margin: 1px;")
        toolbar.addWidget(self.total_pages_label)

        # Zoom controls
        self.zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Zoom Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.setToolTip("Zoom out (Ctrl+-)")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_out_action.setEnabled(False)
        toolbar.addAction(self.zoom_out_action)

        self.zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Zoom In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.setToolTip("Zoom in (Ctrl++)")
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_in_action.setEnabled(False)
        toolbar.addAction(self.zoom_in_action)
        
        toolbar.addSeparator()
        
        # Bookmarks
        self.add_bookmark_toolbar_action = QAction(QIcon.fromTheme("bookmark-new"), "Bookmark", self)
        self.add_bookmark_toolbar_action.setShortcut("Ctrl+B")
        self.add_bookmark_toolbar_action.setToolTip("Add bookmark for current page (Ctrl+B)")
        self.add_bookmark_toolbar_action.triggered.connect(self.add_bookmark)
        self.add_bookmark_toolbar_action.setEnabled(False)
        toolbar.addAction(self.add_bookmark_toolbar_action)        # Search (with navigation buttons)
        toolbar.addSeparator()
        self.search_input = QLineEdit()
        self.search_input.setFixedWidth(80)
        self.search_input.setPlaceholderText("Find...")
        self.search_input.setToolTip("Search text")
        self.search_input.returnPressed.connect(self.perform_search)
        toolbar.addWidget(self.search_input)

        self.search_button = QAction(QIcon.fromTheme("edit-find"), "Search", self)
        self.search_button.setToolTip("Search")
        self.search_button.triggered.connect(self.perform_search)
        self.search_button.setEnabled(False)
        toolbar.addAction(self.search_button)
        
        # Search navigation
        self.search_prev_action = QAction(QIcon.fromTheme("go-up"), "Previous Result", self)
        self.search_prev_action.setShortcut("Shift+F3")
        self.search_prev_action.setToolTip("Previous search result (Shift+F3)")
        self.search_prev_action.triggered.connect(lambda: self.navigate_search(False))
        self.search_prev_action.setEnabled(False)
        toolbar.addAction(self.search_prev_action)

        self.search_next_action = QAction(QIcon.fromTheme("go-down"), "Next Result", self)
        self.search_next_action.setShortcut("F3")
        self.search_next_action.setToolTip("Next search result (F3)")
        self.search_next_action.triggered.connect(lambda: self.navigate_search(True))
        self.search_next_action.setEnabled(False)
        toolbar.addAction(self.search_next_action)
        
        # Search result status
        self.search_result_label = QLabel("0 results")
        self.search_result_label.setStyleSheet("font-size: 10px; margin: 2px;")
        toolbar.addWidget(self.search_result_label)        
        # No longer create annotation toolbar - moved to dock
        # self.create_annotation_toolbar()

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

        # Create annotation dock widget
        self.create_annotation_dock()
        
        # Add annotation dock toggle to panels menu
        toggle_annotations_action = QAction("Toggle Annotations", self)
        toggle_annotations_action.setCheckable(True)
        toggle_annotations_action.setChecked(True)  # Show by default
        toggle_annotations_action.triggered.connect(self.annotations_dock.setVisible)
        self.annotations_dock.visibilityChanged.connect(toggle_annotations_action.setChecked)
        panels_menu.addAction(toggle_annotations_action)

    def create_annotation_dock(self):
        """Create annotation dock widget instead of toolbar."""
        self.annotations_dock = QDockWidget("Annotations", self)
        self.annotations_dock.setObjectName("AnnotationsDock")
        
        # Create container widget with vertical layout
        annotations_widget = QWidget()
        layout = QVBoxLayout(annotations_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Annotation mode toggle
        annotation_mode_action = QAction(QIcon.fromTheme("edit-entry"), "Toggle Annotation Mode", self)
        annotation_mode_action.setCheckable(True)
        annotation_mode_action.setToolTip("Toggle annotation mode")
        annotation_mode_action.triggered.connect(self.toggle_annotation_mode)
        self.annotation_mode_action = annotation_mode_action
        
        # Create toolbar-style buttons in the dock
        from PyQt6.QtWidgets import QPushButton
        
        # Mode toggle button
        mode_btn = QPushButton("📝 Annotation Mode")
        mode_btn.setCheckable(True)
        mode_btn.setToolTip("Toggle annotation mode")
        mode_btn.clicked.connect(self.toggle_annotation_mode)
        layout.addWidget(mode_btn)
        self.annotation_mode_button = mode_btn
        
        # Annotation type buttons
        highlight_btn = QPushButton("🖍️ Highlight")
        highlight_btn.setToolTip("Highlight text")
        highlight_btn.clicked.connect(lambda: self.toggle_annotation(AnnotationType.HIGHLIGHT))
        layout.addWidget(highlight_btn)
        
        underline_btn = QPushButton("📏 Underline")
        underline_btn.setToolTip("Underline text")
        underline_btn.clicked.connect(lambda: self.toggle_annotation(AnnotationType.UNDERLINE))
        layout.addWidget(underline_btn)
        
        text_btn = QPushButton("💬 Text Note")
        text_btn.setToolTip("Add text annotation")
        text_btn.clicked.connect(lambda: self.toggle_annotation(AnnotationType.TEXT))
        layout.addWidget(text_btn)
        
        # Separator
        layout.addWidget(QFrame())
        
        # Clear actions
        clear_page_btn = QPushButton("🗑️ Clear Page")
        clear_page_btn.setToolTip("Clear annotations on current page")
        clear_page_btn.clicked.connect(self.clear_current_page_annotations)
        layout.addWidget(clear_page_btn)
        
        clear_all_btn = QPushButton("🗑️ Clear All")
        clear_all_btn.setToolTip("Clear all annotations")
        clear_all_btn.clicked.connect(self.clear_all_annotations)
        layout.addWidget(clear_all_btn)
        
        # Store button references for enabling/disabling
        self.annotation_actions = [highlight_btn, underline_btn, text_btn]
        
        # Add stretch to push buttons to top
        layout.addStretch()
        
        self.annotations_dock.setWidget(annotations_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.annotations_dock)
        self.annotations_dock.setVisible(True)  # Show by default

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
        """Update the UI state of annotation-related buttons."""
        for button in self.annotation_actions:
            button.setEnabled(enabled)

        if enabled:
            self.annotation_mode_button.setToolTip("Disable annotation mode")
        else:
            self.annotation_mode_button.setToolTip("Enable annotation mode")
            viewer = self.current_viewer()
            if viewer:
                viewer.active_annotation_type = None
            # Note: buttons don't have setChecked, visual feedback handled differently

    def toggle_annotation(self, ann_type):
        """Toggle annotation mode for the specified type."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            # No document loaded, can't annotate
            return
            
        if viewer.active_annotation_type == ann_type:
            # Turning off this annotation type
            viewer.active_annotation_type = None
        else:            # Setting this annotation type
            viewer.active_annotation_type = ann_type
    
    def toggle_annotation_mode(self):
        """Toggle annotation mode for the current viewer."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            self.annotation_mode_button.setChecked(False)
            self._update_annotation_ui_state(False)
            return
            
        mode_enabled = viewer.toggle_annotation_mode()
        self.annotation_mode_button.setChecked(mode_enabled)
        self._update_annotation_ui_state(mode_enabled)
        
        if not mode_enabled:
            viewer.active_annotation_type = None
            # Note: buttons don't have setChecked, visual feedback handled differently
            
        if mode_enabled:
            self.search_input.clear()
            viewer.search_text("")
            self.search_result_label.setText("0 results")
            self.search_next_action.setEnabled(False)
            self.search_prev_action.setEnabled(False)
            self.search_prev_action.setEnabled(False)

    def change_view_mode(self, mode: ViewMode):
        """Change the view mode of the current PDF viewer."""
        current_viewer = self.tab_widget.currentWidget()
        if isinstance(current_viewer, PDFViewer):            current_viewer.set_view_mode(mode)

    def open_file(self):
        """Open a PDF file dialog and load the selected file with improved error handling."""
        try:
            # Remember the last opened directory
            last_dir = config.get('files.last_directory', os.path.expanduser('~'))
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Open PDF Document", 
                last_dir, 
                "PDF Files (*.pdf);;All Files (*.*)"
            )
            
            if file_path:
                # Save the directory for next time
                config.set('files.last_directory', os.path.dirname(file_path))
                
                # Show loading feedback
                self.show_feedback("Loading document...", "info", timeout=0)
                
                # Attempt to add the tab
                success = self.add_pdf_tab(file_path)
                
                if success:
                    self.add_to_recent_files(file_path)
                    self.show_feedback(
                        f"Successfully opened {os.path.basename(file_path)}", 
                        "success", 
                        timeout=3000
                    )
                else:
                    self.show_feedback(
                        "Failed to open document", 
                        "error",
                        "Try Again",
                        "open_file",
                        timeout=10000
                    )
        except Exception as e:            show_error_dialog(
                self,
                "Error Opening File",
                "An unexpected error occurred while trying to open the file dialog.",
                str(e)
            )

    def add_pdf_tab(self, file_path):
        """Add a new PDF tab to the tab widget with enhanced error handling."""
        try:
            # Validate file path
            if not os.path.exists(file_path):
                show_error_dialog(
                    self,
                    "File Not Found",
                    f"The file '{file_path}' no longer exists.",
                    "The file may have been moved, renamed, or deleted."
                )
                return False
            
            # Check if file is already open
            for i in range(self.tab_widget.count()):
                viewer = self.tab_widget.widget(i)
                if isinstance(viewer, PDFViewer) and viewer.file_path == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    self.show_feedback(
                        f"{os.path.basename(file_path)} is already open", 
                        "info", 
                        timeout=2000
                    )
                    return True
            
            # Create viewer and load PDF
            viewer = PDFViewer()
            success = viewer.load_pdf(file_path)
            
            if not success:
                viewer.deleteLater()
                return False
            
            # Setup connections
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

            # Add tab with truncated filename for display
            display_name = os.path.basename(file_path)
            if len(display_name) > 30:
                display_name = display_name[:27] + "..."
            
            tab_index = self.tab_widget.addTab(viewer, display_name)
            self.tab_widget.setCurrentIndex(tab_index)
            self.tab_widget.setTabToolTip(tab_index, file_path)  # Show full path on hover
            
            # Update UI state
            self.update_document_status(
                os.path.basename(file_path),
                viewer.current_page,
                viewer.doc.page_count if viewer.doc else 0,
                viewer.zoom_factor
            )
            
            # Enable toolbar actions
            self.prev_page_action.setEnabled(True)
            self.next_page_action.setEnabled(True)
            self.zoom_in_action.setEnabled(True)
            self.zoom_out_action.setEnabled(True)
            self.add_bookmark_toolbar_action.setEnabled(True)
            self.search_button.setEnabled(True)
            
            # Restore last read page if available
            if viewer.doc:
                last_page = config.get_last_page(file_path)
                if last_page >= 0 and last_page < viewer.doc.page_count:
                    viewer.jump_to_page(last_page)
                else:
                    # Save initial progress for new documents
                    if last_page < 0:
                        config.update_document_progress(file_path, viewer.current_page, viewer.doc.page_count)
                        config.save()
            return True
            
        except Exception as e:
            show_error_dialog(
                self,
                "Error Loading Document",
                f"Failed to load the document '{os.path.basename(file_path)}'.",
                str(e)
            )
            return False

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

    def close_current_tab(self):
        """Close the currently active tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)

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

    def reset_zoom(self):
        """Reset zoom to 100%."""
        viewer = self.current_viewer()
        if viewer:
            viewer.zoom_factor = 1.0
            viewer.render_current_page()
            self.show_status_message("Zoom reset to 100%", 2000)

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

    def clear_recent_files(self):
        """Clear the recent files list."""
        reply = QMessageBox.question(
            self, 
            "Clear Recent Files", 
            "Are you sure you want to clear all recent files?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            config.clear_recent_files()
            self.load_recent_files()
            self.show_status_message("Recent files cleared", 2000)

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
        self.progress_save_timer.start(2000) # Save after 2 seconds of inactivity

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

    # Helper methods for improved UX and missing functionality
    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """
<h3>Keyboard Shortcuts</h3>
<table border="1" cellpadding="5" cellspacing="0">
<tr><th>Action</th><th>Shortcut</th></tr>
<tr><td>Open document</td><td>Ctrl+O</td></tr>
<tr><td>Close tab</td><td>Ctrl+W</td></tr>
<tr><td>Exit application</td><td>Ctrl+Q</td></tr>
<tr><td>Previous page</td><td>Left Arrow, Page Up</td></tr>
<tr><td>Next page</td><td>Right Arrow, Page Down</td></tr>
<tr><td>First page</td><td>Home</td></tr>
<tr><td>Last page</td><td>End</td></tr>
<tr><td>Go to page</td><td>Ctrl+G</td></tr>
<tr><td>Zoom in</td><td>Ctrl++ or Ctrl+Scroll Up</td></tr>
<tr><td>Zoom out</td><td>Ctrl+- or Ctrl+Scroll Down</td></tr>
<tr><td>Reset zoom</td><td>Ctrl+0</td></tr>
<tr><td>Add bookmark</td><td>Ctrl+B</td></tr>
<tr><td>Remove bookmark</td><td>Ctrl+Shift+B</td></tr>
<tr><td>Highlight text</td><td>Ctrl+H</td></tr>
<tr><td>Underline text</td><td>Ctrl+U</td></tr>
<tr><td>Add text note</td><td>Ctrl+T</td></tr>
<tr><td>Focus search</td><td>Ctrl+F</td></tr>
<tr><td>Find next</td><td>F3</td></tr>
<tr><td>Find previous</td><td>Shift+F3</td></tr>
<tr><td>Clear search</td><td>Escape</td></tr>
<tr><td>View modes</td><td>1-5 (number keys)</td></tr>
<tr><td>Toggle bookmarks panel</td><td>F9</td></tr>
<tr><td>Toggle TOC panel</td><td>F10</td></tr>
<tr><td>Help</td><td>F1</td></tr>
</table>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keyboard Shortcuts")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(shortcuts_text)
        msg_box.exec()

    def show_user_guide(self):
        """Show user guide dialog."""
        guide_text = """
<h3>PDF Reader User Guide</h3>
<h4>Getting Started</h4>
<ul>
<li><b>Opening Documents:</b> Use File �?Open or Ctrl+O to open PDF files</li>
<li><b>Navigation:</b> Use arrow keys, page up/down, or toolbar buttons to navigate</li>
<li><b>Tabs:</b> Open multiple documents in tabs for easy switching</li>
</ul>

<h4>View Modes</h4>
<ul>
<li><b>Single Page:</b> View one page at a time (Press 1)</li>
<li><b>Fit Page:</b> Automatically fit page to window (Press 2)</li>
<li><b>Fit Width:</b> Fit page width for optimal reading (Press 3)</li>
<li><b>Double Page:</b> View two pages side by side (Press 4)</li>
<li><b>Continuous Scroll:</b> Scroll through all pages continuously (Press 5)</li>
</ul>

<h4>Annotations</h4>
<ul>
<li><b>Highlighting:</b> Select text and use Ctrl+H or the highlight tool</li>
<li><b>Underlining:</b> Select text and use Ctrl+U or the underline tool</li>
<li><b>Text Notes:</b> Click and use Ctrl+T to add text annotations</li>
<li><b>Managing:</b> Right-click annotations to delete individual ones</li>
</ul>

<h4>Bookmarks</h4>
<ul>
<li><b>Adding:</b> Use Ctrl+B or the bookmark button to bookmark current page</li>
<li><b>Navigation:</b> Click bookmarks in the panel to jump to pages</li>
<li><b>Management:</b> Right-click bookmarks to rename or delete them</li>
</ul>

<h4>Search</h4>
<ul>
<li><b>Text Search:</b> Enter text in search box and press Enter</li>
<li><b>Navigation:</b> Use F3/Shift+F3 to navigate between results</li>
<li><b>Highlighting:</b> Search results are automatically highlighted</li>
</ul>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("User Guide")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(guide_text)
        msg_box.exec()

    def report_issue(self):
        """Show issue reporting dialog."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Report Issue")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(
            "To report issues or bugs:\n\n"
            "1. Check the GitHub repository for existing issues\n"
            "2. Create a new issue with detailed description\n"
            "3. Include steps to reproduce the problem\n"
            "4. Attach sample PDF if relevant\n\n"
            "Thank you for helping improve PDF Reader!"
        )
        msg_box.exec()

    def show_about(self):
        """Show about dialog."""
        about_text = """
<h3>PDF Reader</h3>
<p><b>Version:</b> 1.0.0</p>
<p><b>Built with:</b> PyQt6 and PyMuPDF</p>
<p><b>Author:</b> HCI Course Project</p>

<h4>Features:</h4>
<ul>
<li>Multiple view modes</li>
<li>Tabbed interface</li>
<li>Annotation support</li>
<li>Bookmark management</li>
<li>Text search</li>
<li>Reading progress tracking</li>
</ul>

<p><b>License:</b> MIT License</p>
<p>© 2025 PDF Reader. All rights reserved.</p>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About PDF Reader")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.exec()

    def first_page(self):
        """Navigate to the first page."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            viewer.jump_to_page(0)
            self.show_status_message("Navigated to first page", 2000)

    def last_page(self):
        """Navigate to the last page."""
        viewer = self.current_viewer()
        if viewer and viewer.doc:
            last_page = viewer.doc.page_count - 1
            viewer.jump_to_page(last_page)
            self.show_status_message(f"Navigated to last page ({last_page + 1})", 2000)

    def go_to_page_dialog(self):
        """Show dialog to go to a specific page."""
        viewer = self.current_viewer()
        if not viewer or not viewer.doc:
            self.show_feedback("No document open", "warning")
            return
        
        current_page = viewer.current_page + 1
        total_pages = viewer.doc.page_count
        
        page_num, ok = QInputDialog.getInt(
            self,
            "Go to Page",
            f"Enter page number (1-{total_pages}):",
            current_page,
            1,
            total_pages
        )
        
        if ok:
            viewer.jump_to_page(page_num - 1)
            self.show_status_message(f"Navigated to page {page_num}", 2000)

    def focus_search(self):
        """Focus the search input field."""
        if hasattr(self, 'search_input'):
            self.search_input.setFocus()
            self.search_input.selectAll()

    def clear_search(self):
        """Clear search and hide results."""
        if hasattr(self, 'search_input'):
            self.search_input.clear()
        viewer = self.current_viewer()
        if viewer:
            viewer.search_text("")
        if hasattr(self, 'search_result_label'):
            self.search_result_label.setText("No results")
        if hasattr(self, 'search_next_action'):
            self.search_next_action.setEnabled(False)
        if hasattr(self, 'search_prev_action'):
            self.search_prev_action.setEnabled(False)

    def toggle_bookmarks_panel(self):
        """Toggle the bookmarks panel visibility."""
        if hasattr(self, 'bookmarks_dock'):
            self.bookmarks_dock.setVisible(not self.bookmarks_dock.isVisible())

    def toggle_toc_panel(self):
        """Toggle the table of contents panel visibility."""
        if hasattr(self, 'toc_dock'):
            self.toc_dock.setVisible(not self.toc_dock.isVisible())

    def reopen_last_closed(self):
        """Reopen the last closed document."""
        recent_files = config.get_recent_files()
        if recent_files:
            self.add_pdf_tab(recent_files[0])
            self.show_status_message(f"Reopened {os.path.basename(recent_files[0])}", 3000)
        else:
            self.show_feedback("No recent files to reopen", "info")

    def handle_document_load_error(self, file_path, error_message):
        """Handle document loading errors with helpful feedback."""
        error_title = "Unable to Open Document"
        
        if "corrupted" in error_message.lower():
            suggestion = "The PDF file appears to be corrupted. Try opening it with another PDF viewer to verify."
        elif "password" in error_message.lower() or "encrypted" in error_message.lower():
            suggestion = "This PDF is password-protected. Password-protected PDFs are not currently supported."
        elif "not found" in error_message.lower():
            suggestion = "The file could not be found. It may have been moved, renamed, or deleted."
        elif "permission" in error_message.lower():
            suggestion = "Access to this file is denied. Check file permissions or try running as administrator."
        else:
            suggestion = "Try the following:\n�?Ensure the file is a valid PDF\n�?Check if the file is open in another application\n�?Restart the application and try again"
        
        show_error_dialog(
            self,
            error_title,
            f"Could not open '{os.path.basename(file_path)}'",
            error_message,
            suggestion
        )

    def show_welcome_message(self):
        """Show welcome message for new users."""
        if config.is_first_run():
            self.show_feedback(
                "Welcome to PDF Reader! Press F1 for keyboard shortcuts or use the Help menu for guidance.",
                "info",
                "Show Guide",
                "show_help",
                timeout=10000
            )
            config.mark_first_run_complete()

    def update_ui_state(self):
        """Update UI state based on current document."""
        viewer = self.current_viewer()
        has_document = viewer is not None and viewer.doc is not None
        
        # Update action states
        actions_requiring_document = [
            self.prev_page_action,
            self.next_page_action,
            self.zoom_in_action,
            self.zoom_out_action,
            self.add_bookmark_toolbar_action,
            self.search_button
        ]
        
        for action in actions_requiring_document:
            if hasattr(self, action.objectName()) or action:
                action.setEnabled(has_document)
        
        # Update page input
        if hasattr(self, 'page_num_input'):
            self.page_num_input.setEnabled(has_document)
        
        # Update search input
        if hasattr(self, 'search_input'):
            self.search_input.setEnabled(has_document)
        
        # Update status bar
        if has_document:
            doc_name = os.path.basename(viewer.file_path) if viewer.file_path else "Untitled"
            self.update_document_status(
                doc_name,
                viewer.current_page,
                viewer.doc.page_count,
                viewer.zoom_factor
            )
        else:
            self.update_document_status("No document", None, None, None)
            self.document_name_label.setText("No document")
            self.page_info_label.setText("Page: - / -")
            self.zoom_info_label.setText("Zoom: -")

    def toggle_toolbar_visibility(self, toolbar_name, visible):
        """Toggle the visibility of a toolbar by name."""
        toolbar = self.findChild(QToolBar, toolbar_name)
        if toolbar:
            toolbar.setVisible(visible)

    def create_menus_and_toolbar(self):
        """Create the main menu bar and toolbar with improved accessibility."""
        # File Menu
        file_menu = self.menuBar().addMenu("&File")
        
        open_action = QAction(QIcon.fromTheme("document-open"), "&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip("Open a PDF document (Ctrl+O)")
        open_action.setStatusTip("Open a PDF document from your computer")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()
        
        self.recent_files_menu = file_menu.addMenu("&Recent Files")
        self.recent_files_menu.setIcon(QIcon.fromTheme("document-open-recent"))
        
        clear_recent_action = QAction("Clear Recent Files", self)
        clear_recent_action.triggered.connect(self.clear_recent_files)
        self.recent_files_menu.addSeparator()
        self.recent_files_menu.addAction(clear_recent_action)

        file_menu.addSeparator()
        
        close_tab_action = QAction("&Close Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.setToolTip("Close current document tab (Ctrl+W)")
        close_tab_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setToolTip("Exit the application (Ctrl+Q)")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)        # View Menu
        view_mode_menu = self.menuBar().addMenu("&View")
        view_mode_menu.setIcon(QIcon.fromTheme("view-preview"))
        
        # View Mode submenu
        view_modes_submenu = view_mode_menu.addMenu("View &Modes")
        self.view_mode_group = QActionGroup(self)
        self.view_mode_group.setExclusive(True)

        self.single_page_action = QAction("&Single Page", self, checkable=True)
        self.single_page_action.setShortcut("1")
        self.single_page_action.setToolTip("Single page view (Press 1)")
        self.single_page_action.setStatusTip("Display one page at a time")
        self.single_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.SINGLE_PAGE)
        )
        view_modes_submenu.addAction(self.single_page_action)
        self.view_mode_group.addAction(self.single_page_action)

        self.fit_page_action = QAction("Fit &Page", self, checkable=True)
        self.fit_page_action.setShortcut("2")
        self.fit_page_action.setToolTip("Fit page to window (Press 2)")
        self.fit_page_action.setStatusTip("Fit entire page within the window")
        self.fit_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.FIT_PAGE)
        )
        view_modes_submenu.addAction(self.fit_page_action)
        self.view_mode_group.addAction(self.fit_page_action)

        self.fit_width_action = QAction("Fit &Width", self, checkable=True)
        self.fit_width_action.setShortcut("3")
        self.fit_width_action.setToolTip("Fit page width to window (Press 3)")
        self.fit_width_action.setStatusTip("Fit page width to window for optimal reading")
        self.fit_width_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.FIT_WIDTH)
        )
        view_modes_submenu.addAction(self.fit_width_action)
        self.view_mode_group.addAction(self.fit_width_action)

        self.double_page_action = QAction("&Double Page", self, checkable=True)
        self.double_page_action.setShortcut("4")
        self.double_page_action.setToolTip("Double page view (Press 4)")
        self.double_page_action.setStatusTip("Display two pages side by side")
        self.double_page_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.DOUBLE_PAGE)
        )
        view_modes_submenu.addAction(self.double_page_action)
        self.view_mode_group.addAction(self.double_page_action)

        self.continuous_scroll_action = QAction("&Continuous Scroll", self, checkable=True)
        self.continuous_scroll_action.setShortcut("5")
        self.continuous_scroll_action.setToolTip("Continuous scroll view (Press 5)")
        self.continuous_scroll_action.setStatusTip("Scroll through all pages continuously")
        self.continuous_scroll_action.triggered.connect(
            lambda: self.change_view_mode(ViewMode.CONTINUOUS_SCROLL)
        )
        view_modes_submenu.addAction(self.continuous_scroll_action)
        self.view_mode_group.addAction(self.continuous_scroll_action)

        self.single_page_action.setChecked(True)
        
        view_mode_menu.addSeparator()
        
        # Zoom actions
        zoom_in_menu_action = QAction("Zoom &In", self)
        zoom_in_menu_action.setShortcut("Ctrl++")
        zoom_in_menu_action.setToolTip("Zoom in (Ctrl++)")
        zoom_in_menu_action.triggered.connect(self.zoom_in)
        view_mode_menu.addAction(zoom_in_menu_action)
        
        zoom_out_menu_action = QAction("Zoom &Out", self)
        zoom_out_menu_action.setShortcut("Ctrl+-")
        zoom_out_menu_action.setToolTip("Zoom out (Ctrl+-)")
        zoom_out_menu_action.triggered.connect(self.zoom_out)
        view_mode_menu.addAction(zoom_out_menu_action)
        
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.setToolTip("Reset zoom to 100% (Ctrl+0)")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_mode_menu.addAction(reset_zoom_action)        # Bookmarks Menu
        bookmarks_menu = self.menuBar().addMenu("&Bookmarks")
        bookmarks_menu.setIcon(QIcon.fromTheme("bookmark"))
        
        self.add_bookmark_action = QAction(QIcon.fromTheme("bookmark-new"), "&Add Bookmark", self)
        self.add_bookmark_action.setShortcut("Ctrl+B")
        self.add_bookmark_action.setToolTip("Add bookmark for current page (Ctrl+B)")
        self.add_bookmark_action.setStatusTip("Create a bookmark for the current page")
        self.add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(self.add_bookmark_action)
        
        self.remove_bookmark_action = QAction(QIcon.fromTheme("bookmark-remove"), "&Remove Bookmark", self)
        self.remove_bookmark_action.setShortcut("Ctrl+Shift+B")
        self.remove_bookmark_action.setToolTip("Remove bookmark from current page (Ctrl+Shift+B)")
        self.remove_bookmark_action.setStatusTip("Remove bookmark from the current page")
        self.remove_bookmark_action.triggered.connect(self.remove_current_bookmark)
        bookmarks_menu.addAction(self.remove_bookmark_action)
        
        bookmarks_menu.addSeparator()
        
        manage_bookmarks_action = QAction("&Manage Bookmarks...", self)
        manage_bookmarks_action.setToolTip("Open bookmark management panel")
        manage_bookmarks_action.triggered.connect(lambda: self.bookmarks_dock.setVisible(True))
        bookmarks_menu.addAction(manage_bookmarks_action)

        # Annotations Menu
        annotations_menu = self.menuBar().addMenu("&Annotations")
        annotations_menu.setIcon(QIcon.fromTheme("text-field"))
        
        # Annotation tools submenu
        annotation_tools_submenu = annotations_menu.addMenu("Annotation &Tools")
        
        highlight_menu_action = QAction(QIcon.fromTheme("marker"), "&Highlight Text", self)
        highlight_menu_action.setShortcut("Ctrl+H")
        highlight_menu_action.setToolTip("Highlight selected text (Ctrl+H)")
        highlight_menu_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.HIGHLIGHT))
        annotation_tools_submenu.addAction(highlight_menu_action)
        
        underline_menu_action = QAction(QIcon.fromTheme("format-text-underline"), "&Underline Text", self)
        underline_menu_action.setShortcut("Ctrl+U")
        underline_menu_action.setToolTip("Underline selected text (Ctrl+U)")
        underline_menu_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.UNDERLINE))
        annotation_tools_submenu.addAction(underline_menu_action)
        
        text_note_menu_action = QAction(QIcon.fromTheme("text-field"), "Add &Text Note", self)
        text_note_menu_action.setShortcut("Ctrl+T")
        text_note_menu_action.setToolTip("Add text annotation (Ctrl+T)")
        text_note_menu_action.triggered.connect(lambda: self.toggle_annotation(AnnotationType.TEXT))
        annotation_tools_submenu.addAction(text_note_menu_action)
        
        annotations_menu.addSeparator()
        
        clear_page_annotations_action = QAction(QIcon.fromTheme("edit-clear"), "Clear &Page Annotations", self)
        clear_page_annotations_action.setShortcut("Ctrl+Alt+C")
        clear_page_annotations_action.setToolTip("Clear all annotations on current page (Ctrl+Alt+C)")
        clear_page_annotations_action.setStatusTip("Remove all annotations from the current page")
        clear_page_annotations_action.triggered.connect(self.clear_current_page_annotations)
        annotations_menu.addAction(clear_page_annotations_action)
        
        clear_all_annotations_action = QAction(QIcon.fromTheme("edit-clear-all"), "Clear &All Annotations", self)
        clear_all_annotations_action.setShortcut("Ctrl+Alt+Shift+C")
        clear_all_annotations_action.setToolTip("Clear all annotations in document (Ctrl+Alt+Shift+C)")
        clear_all_annotations_action.setStatusTip("Remove all annotations from the entire document")
        clear_all_annotations_action.triggered.connect(self.clear_all_annotations)
        annotations_menu.addAction(clear_all_annotations_action)
        annotations_menu.addSeparator()
        
        annotation_help_action = QAction("💡 Tip: Right-click annotations to delete individual ones", self)
        annotation_help_action.setEnabled(False)
        annotations_menu.addAction(annotation_help_action)
        
        # Help Menu
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.setIcon(QIcon.fromTheme("help-about"))
        
        keyboard_shortcuts_action = QAction(QIcon.fromTheme("preferences-desktop-keyboard"), "&Keyboard Shortcuts", self)
        keyboard_shortcuts_action.setShortcut("F1")
        keyboard_shortcuts_action.setToolTip("Show keyboard shortcuts (F1)")
        keyboard_shortcuts_action.triggered.connect(self.show_keyboard_shortcuts)
        help_menu.addAction(keyboard_shortcuts_action)
        
        user_guide_action = QAction(QIcon.fromTheme("help-contents"), "&User Guide", self)
        user_guide_action.setToolTip("Open user guide")
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
        
        help_menu.addSeparator()
        
        report_issue_action = QAction(QIcon.fromTheme("dialog-warning"), "&Report Issue", self)
        report_issue_action.setToolTip("Report a bug or issue")
        report_issue_action.triggered.connect(self.report_issue)
        help_menu.addAction(report_issue_action)
        
        help_menu.addSeparator()
        
        about_action = QAction(QIcon.fromTheme("help-about"), "&About PDF Reader", self)
        about_action.setToolTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
          # Create improved toolbar
        self.create_toolbar()
