import platform
import copy
from Qt import QtWidgets, QtCore
from pype.tools.settings.settings import ProjectListWidget
from pype.settings.constants import (
    PROJECT_ANATOMY_KEY,
    DEFAULT_PROJECT_KEY
)
from .widgets import SpacerWidget

LOCAL_ROOTS_KEY = "roots"


class _ProjectListWidget(ProjectListWidget):
    def on_item_clicked(self, new_index):
        new_project_name = new_index.data(QtCore.Qt.DisplayRole)
        if new_project_name is None:
            return

        if self.current_project == new_project_name:
            return

        self.select_project(new_project_name)
        self.current_project = new_project_name
        self.project_changed.emit()

    def project_name(self):
        if self.current_project == self.default:
            return DEFAULT_PROJECT_KEY
        return self.current_project


class RootInputWidget(QtWidgets.QWidget):
    def __init__(
        self,
        local_project_settings,
        local_project_settings_orig,
        platform_root_entity,
        root_name,
        project_name,
        site_name,
        parent
    ):
        super(RootInputWidget, self).__init__(parent)

        self.local_project_settings = local_project_settings
        self.local_project_settings_orig = local_project_settings_orig
        self.platform_root_entity = platform_root_entity
        self.root_name = root_name
        self.site_name = site_name
        self.project_name = project_name

        self.origin_value = self._get_site_value_for_project(
            self.project_name, self.local_project_settings_orig
        )

        key_label = QtWidgets.QLabel(root_name, self)
        value_input = QtWidgets.QLineEdit(self)

        is_default_project = bool(project_name == DEFAULT_PROJECT_KEY)

        default_input_value = self._get_site_value_for_project(
            DEFAULT_PROJECT_KEY
        )
        if is_default_project:
            project_value = None
            input_value = default_input_value
        else:
            input_value = self._get_site_value_for_project(self.project_name)
            project_value = input_value

        # Placeholder
        placeholder = None
        if not is_default_project:
            placeholder = default_input_value

        if not placeholder:
            placeholder = platform_root_entity.value

        value_input.setPlaceholderText("< {} >".format(placeholder))

        # Root value
        if input_value:
            value_input.setText(input_value)

        value_input.textChanged.connect(self._on_value_change)

        root_layout = QtWidgets.QHBoxLayout(self)
        root_layout.addWidget(key_label)
        root_layout.addWidget(value_input)

        self.value_input = value_input

        self.is_default_project = is_default_project
        self.studio_value = platform_root_entity.value
        self.default_value = default_input_value
        self.project_value = project_value

    @property
    def is_modified(self):
        return self.origin_value != self.value_input.text()

    def _get_site_value_for_project(self, project_name, data=None):
        if data is None:
            data = self.local_project_settings
        project_values = data.get(project_name)
        site_value = {}
        if project_values:
            root_value = project_values.get(LOCAL_ROOTS_KEY)
            if root_value:
                site_value = root_value.get(self.site_name) or {}
        return site_value.get(self.root_name)

    def _on_value_change(self):
        value = self.value_input.text()
        data = self.local_project_settings
        for key in (self.project_name, LOCAL_ROOTS_KEY, self.site_name):
            if key not in data:
                data[key] = {}
            data = data[key]
        data[self.root_name] = value


class RootsWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal()

    def __init__(self, project_settings, parent):
        super(RootsWidget, self).__init__(parent)

        self.project_settings = project_settings
        self.widgts_by_root_name = {}
        self.local_project_settings = None
        self.local_project_settings_orig = None
        self._project_name = None
        self._site_name = None

        self.content_layout = QtWidgets.QVBoxLayout(self)

    def _on_root_value_change(self, root_key):
        print("root value or key {} changed".format(root_key))

    def _clear_widgets(self):
        while self.content_layout.count():
            item = self.content_layout.itemAt(0)
            item.widget().hide()
            self.content_layout.removeItem(item)
        self.widgts_by_root_name.clear()

    def refresh(self):
        self._clear_widgets()

        if self._project_name is None or self._site_name is None:
            return

        roots_entity = (
            self.project_settings[PROJECT_ANATOMY_KEY][LOCAL_ROOTS_KEY]
        )
        for root_name, path_entity in roots_entity.items():
            platform_entity = path_entity[platform.system().lower()]
            root_widget = RootInputWidget(
                self.local_project_settings,
                self.local_project_settings_orig,
                platform_entity,
                root_name,
                self._project_name,
                self._site_name,
                self
            )

            self.content_layout.addWidget(root_widget)
            self.widgts_by_root_name[root_name] = root_widget

        self.content_layout.addWidget(SpacerWidget(self), 1)

    def set_value(self, local_project_settings):
        self.local_project_settings = local_project_settings
        self.local_project_settings_orig = copy.deepcopy(
            dict(local_project_settings)
        )

    def change_site(self, site_name):
        self._site_name = site_name
        self.refresh()

    def change_project(self, project_name):
        self._project_name = project_name
        self.refresh()


class RootSiteWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal()

    def __init__(self, project_settings, parent):
        self._parent_widget = parent
        super(RootSiteWidget, self).__init__(parent)

        self.project_settings = project_settings
        self._project_name = None

        sites_widget = QtWidgets.QWidget(self)
        sites_layout = QtWidgets.QHBoxLayout(sites_widget)
        active_site_combo = QtWidgets.QComboBox(sites_widget)
        remote_site_combo = QtWidgets.QComboBox(sites_widget)
        sites_layout.addWidget(QtWidgets.QLabel("Active Site", sites_widget))
        sites_layout.addWidget(active_site_combo)
        sites_layout.addWidget(QtWidgets.QLabel("Remote Site", sites_widget))
        sites_layout.addWidget(remote_site_combo)

        roots_widget = RootsWidget(project_settings, self)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(sites_widget)
        main_layout.addWidget(roots_widget)
        main_layout.addWidget(SpacerWidget(self), 1)

        self.active_site_combo = active_site_combo
        self.remote_site_combo = remote_site_combo
        self.roots_widget = roots_widget

    def _active_site_values(self):
        global_entity = self.project_settings["project_settings"]["global"]
        sites_entity = global_entity["sync_server"]["sites"]
        return tuple(sites_entity.keys())

    def _remote_site_values(self):
        global_entity = self.project_settings["project_settings"]["global"]
        sites_entity = global_entity["sync_server"]["sites"]
        return tuple(sites_entity.keys())

    def _change_combobox_values(self):
        self.active_site_combo.clear()
        self.remote_site_combo.clear()
        if self._project_name is None:
            return

        active_site_values = self._active_site_values()
        remote_site_values = self._remote_site_values()

        # Set sites from local settings in comboboxes
        active_site = None
        remote_site = None

        project_values = self.local_project_settings.get(self._project_name)
        if project_values:
            active_site = project_values.get("active_site")
            remote_site = project_values.get("remote_site")

        if (
            (not active_site or not remote_site)
            and self._project_name is not DEFAULT_PROJECT_KEY
        ):
            default_values = self.local_project_settings.get(
                DEFAULT_PROJECT_KEY
            )
            if default_values:
                if not active_site:
                    active_site = default_values.get("active_site")
                if not remote_site:
                    remote_site = default_values.get("remote_site")

        self.active_site_combo.addItems(active_site_values)
        self.remote_site_combo.addItems(remote_site_values)

        # Find and set remote site in combobox
        if remote_site:
            idx = self.remote_site_combo.findText(active_site)
            if idx >= 0:
                index = self.remote_site_combo.model().index(idx, 0)
                self.remote_site_combo.setCurrentIndex(index)

        # Find and set active site in combobox
        if active_site:
            idx = self.active_site_combo.findText(active_site)
            if idx < 0:
                active_site = None
            else:
                index = self.active_site_combo.model().index(idx, 0)
                self.active_site_combo.setCurrentIndex(index)

        # Prepare value to change active site in roots widget
        if not active_site:
            if not active_site_values:
                active_site = None
            else:
                active_site = self.active_site_combo.currentText()

        self._change_active_site(active_site)

    def set_value(self, local_project_settings):
        self.local_project_settings = local_project_settings
        self.roots_widget.set_value(local_project_settings)

    def _change_active_site(self, site_name):
        self.roots_widget.change_site(site_name)

    def change_project(self, project_name):
        self._project_name = project_name
        # Set roots project to None so all changes below are ignored
        self.roots_widget.change_project(None)

        # Aply changes in site comboboxes
        self._change_combobox_values()

        # Change project name in roots widget
        self.roots_widget.change_project(project_name)


class ProjectValue(dict):
    pass


class ProjectSettingsWidget(QtWidgets.QWidget):
    def __init__(self, project_settings, parent):
        super(ProjectSettingsWidget, self).__init__(parent)

        self.local_project_settings = {}

        projects_widget = _ProjectListWidget(self)
        roos_site_widget = RootSiteWidget(project_settings, self)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(projects_widget, 0)
        main_layout.addWidget(roos_site_widget, 1)

        projects_widget.project_changed.connect(self._on_project_change)

        self.project_settings = project_settings

        self.projects_widget = projects_widget
        self.roos_site_widget = roos_site_widget

    def project_name(self):
        return self.projects_widget.project_name()

    def _on_project_change(self):
        project_name = self.project_name()
        self.project_settings.change_project(project_name)
        self.roos_site_widget.change_project(project_name)

    def set_value(self, value):
        if not value:
            value = {}
        self.local_project_settings = ProjectValue(value)

        self.roos_site_widget.set_value(self.local_project_settings)

        self.projects_widget.refresh()

    def settings_value(self):
        output = {}
        for project_name, value in self.local_project_settings.items():
            if value:
                output[project_name] = value
        if not output:
            return None
        return output
