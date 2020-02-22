from PyInstaller.utils.hooks import copy_metadata, collect_dynamic_libs, collect_data_files

datas = copy_metadata('hlsvdpro')
datas += collect_data_files('hlsvdpro')
binaries = collect_dynamic_libs('hlsvdpro')