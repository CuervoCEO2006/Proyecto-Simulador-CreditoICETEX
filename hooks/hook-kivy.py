import os
import kivy
from PyInstaller.utils.hooks import collect_submodules

kivy_data_dir = os.path.join(os.path.dirname(kivy.__file__), 'data')

datas = [(kivy_data_dir, os.path.join('kivy_install', 'data'))]
hiddenimports = collect_submodules('kivy.graphics') + collect_submodules('kivy.core')