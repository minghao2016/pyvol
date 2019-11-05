

__version__ = "1.1.0"

import logging
import time

main_logger = logging.getLogger("pyvol")
main_logger.setLevel("DEBUG")

stdio_handler_found = False
for handler in main_logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        stdio_handler_found = True
        break
if not stdio_handler_found:
    log_out = logging.StreamHandler()
    log_out.setLevel("INFO")
    log_out.setFormatter(logging.Formatter("%(name)-12s:".ljust(25) + "\t%(levelname)-8s" + "\t%(message)s"))
    main_logger.addHandler(log_out)

logger = logging.getLogger("pyvol.plugin")

def __init_plugin__(app=None):
    try:
        from pymol import cmd
        from pyvol import pymol_interface
        cmd.extend('pocket', pymol_interface.pocket)
        cmd.extend('load_pocket', pymol_interface.load_pocket)
        logger.debug("PyVOL successfully imported")
    except:
        logger.info("PyVOL not imported; installing from local cache or PyPI to use")

    finally:
        from pymol.plugins import addmenuitemqt
        addmenuitemqt('PyVOL', pyvol_window)


def pyvol_window():
    """ """
    import os
    from pymol.Qt import QtCore, QtWidgets
    from pymol.Qt.utils import loadUi

    dialog = QtWidgets.QDialog()
    uifile = os.path.join(os.path.dirname(__file__), 'pyvol_gui.ui')
    form = loadUi(uifile, dialog)

    def browse_pocket_file(form):
        """ Launches a window to select a file

        """
        pocket_file_name = QtWidgets.QFileDialog.getOpenFileNames(None, 'Open file', os.getcwd(), filter='Pocket Files (*.obj *.csv)')[0][0]
        form.pocket_file_ledit.setText(pocket_file_name)

    def install_remote_pyvol(form):
        """ Attempts a de novo PyVOL installation using pip

        """
        import distutils
        import subprocess
        import sys

        subprocess.check_output([sys.executable, "-m", "pip", "install", "bio-pyvol"])

        msms_exe = distutils.spawn.find_executable("msms")
        if msms_exe == None:
            if os.name in ['posix']:
                conda_path = os.path.join(os.path.dirname(sys.executable), "conda")
                if not os.path.isfile(conda_path):
                    conda_path = "conda"
                subprocess.check_output([conda_path, "install", "-y", "-c", "bioconda", "msms"])
                msms_exe = distutils.spawn.find_executable("msms")
        try:
            from pymol import cmd
            from pyvol import pymol_interface
            cmd.extend('pocket', pymol_interface.pocket)
            cmd.extend('load_pocket', pymol_interface.load_pocket)
        except:
            pass
        refresh_installation_status(form)

    def install_local_pyvol(form):
        import os
        import re
        import subprocess

        installer_dir = os.path.dirname(os.path.realpath(__file__))
        cache_dir = os.path.join(installer_dir, "cached_source")

        if os.path.isdir(cache_dir):
            bio_pyvol_gz = None
            for f in os.listdir(cache_dir):
                if re.match('bio_pyvol', f):
                    bio_pyvol_gz = f
                    break

            if bio_pyvol_gz is None:
                logger.info("Cache directory found but no pyvol distribution")
            else:
                subprocess.check_output([sys.executable, "-m", "pip", "install", bio_pyvol_gz])

                install_status = False
                try:
                    from pyvol import pymol_interface
                    cmd.extend('pocket', pymol_interface.pocket)
                    cmd.extend('load_pocket', pymol_interface.load_pocket)
                    install_status = True
                except:
                    logger.warning("Installation failed")

                if install_status:
                    logger.info("Installation succeeded")

                    import shutil
                    shutil.rmtree(cache_dir)
        else:
            logger.info("Local cache not found; requires installation through GUI")
        refresh_installation_status(form)


    def uninstall_pyvol(form):
        """ Attempts to uninstall PyVOL using pip

        """
        import subprocess
        import sys

        subprocess.check_output([sys.executable, "-m", "pip", "uninstall", "-y", "bio-pyvol"])

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("PyVOL Backend Uninstalled")
        msg.setInformativeText("The PyVOL backend has been uninstalled; however, the plugin must also be uninstalled using PyMOL's plugin manager.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setMinimumSize(QtCore.QSize(600, 200)) # Doesn't seem to work
        msg.exec_()

        refresh_installation_status(form)

    def update_pyvol(form):
        """ Attempts to update PyVOL using pip

        """
        import subprocess
        import sys

        subprocess.check_output([sys.executable, "-m", "pip", "install", "--upgrade", "bio-pyvol"])

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("PyVOL Updated")
        msg.setInformativeText("The PyVOL backend has been updated; however, PyMOL will not load the new code until it is restarted.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setMinimumSize(QtCore.QSize(600, 200)) # Doesn't seem to work
        msg.exec_()

        refresh_installation_status(form)

    def refresh_installation_status(form, check_for_updates=False):
        """ Check for updates and adjust the GUI to reflect the current installation status and availability of updates

        Args:
          check_for_updates (bool): query servers to see if an update is available? (Default value = False)

        """
        import distutils.spawn
        import json
        import subprocess
        import sys

        def apply_color(string, color):
            """ Applies a color to html text

            Args:
              string (str): text
              color (str): color to apply

            Returns:
              colored_text (str): html formatted text

            """
            return "<font color='{0}'>{1}</font>".format(color, string)

        all_pckgs = subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"]).decode('utf-8').strip()
        pckgs = json.loads(all_pckgs)

        status_msg = ""
        pyvol_version = None
        biopython_version = None
        numpy_version = None
        pandas_version = None
        scipy_version = None
        sklearn_version = None
        trimesh_version = None

        remote_msg = None

        pyvol_installed = False
        for pckg in pckgs:
            if pckg["name"] == "bio-pyvol":
                pyvol_version = pckg["version"]
                pyvol_installed = True

        for pckg in pckgs:
            if pckg["name"] == "biopython":
                biopython_version = pckg["version"]
                if pyvol_installed:
                    biopython_version = apply_color(biopython_version, "green")
            elif pckg["name"] == "numpy":
                numpy_version = pckg["version"]
                if pyvol_installed:
                    numpy_version = apply_color(numpy_version, "green")
            elif pckg["name"] == "pandas":
                pandas_version = pckg["version"]
                if pyvol_installed:
                    pandas_version = apply_color(pandas_version, "green")
            elif pckg["name"] == "scipy":
                scipy_version = pckg["version"]
                if pyvol_installed:
                    scipy_version = apply_color(scipy_version, "green")
            elif pckg["name"] == "scikit-learn":
                sklearn_version = pckg["version"]
                if pyvol_installed:
                    sklearn_version = apply_color(sklearn_version, "green")
            elif pckg["name"] == "trimesh":
                trimesh_version = pckg["version"]
                if pyvol_installed:
                    trimesh_version = apply_color(trimesh_version, "green")

        if pyvol_version is None:
            pyvol_version = apply_color("not found", "red")
        if biopython_version is None:
            biopython_version = apply_color("not found", "red")
        if numpy_version is None:
            numpy_version = apply_color("not found", "red")
        if pandas_version is None:
            pandas_version = apply_color("not found", "red")
        if scipy_version is None:
            scipy_version = apply_color("not found", "red")
        if sklearn_version is None:
            sklearn_version = apply_color("not found", "red")
        if trimesh_version is None:
            trimesh_version = apply_color("not found", "red")

        msms_exe = distutils.spawn.find_executable("msms")
        msms_installed = False
        if msms_exe == None:
            msms_exe = apply_color("not found", "red")
        else:
            msms_exe = apply_color(msms_exe, "green")
            msms_installed = True

        if not pyvol_installed:
            gui_version = __version__
            form.run_tab.setEnabled(False)
            form.run_button.setEnabled(False)
            form.load_tab.setEnabled(False)
            form.tabWidget.setCurrentIndex(2)

            form.install_remote_browser.setText("PyPI has not yet been queried.<br>")
            form.install_remote_button.setEnabled(True)
            form.install_remote_button.setText("Install PyVOL from PyPI")
            form.install_remote_button.clicked.connect(lambda: install_remote_pyvol(form))

            form.install_status_button.setText("Install PyVOL from Cache")

            cache_present = False
            # detect the cache

            if cache_present:
                status_msg = status_msg + "PyVOL can be installed from a local cache.<br>"
                form.install_status_button.setEnabled(True)
                form.install_status_button.clicked.connect(lambda: install_local_pyvol(form))
                # display the cache text
            else:
                form.install_status_browser.setText("PyVOL is not currently installed.<br>")
                form.install_status_button.setEnabled(False)

        if pyvol_installed:
            form.setWindowTitle("PyVOL v{0}".format(pyvol_version))
            form.install_status_button.setText("Uninstall PyVOL")
            form.install_status_button.clicked.connect(lambda: uninstall_pyvol(form))
            form.install_status_button.setEnabled(True)

            if not check_for_updates:
                form.install_remote_button.setText("Check for Updates")
                form.install_remote_button.clicked.connect(lambda: refresh_installation_status(form, check_for_updates=True))
                form.install_remote_button.setEnabled(True)
            else:
                update_available = False

                avail_pckgs = subprocess.check_output([sys.executable, "-m", "pip", "list", "--outdated", "--format=json"]).decode('utf-8').strip()
                avail = json.loads(avail_pckgs)
                for pckg in avail:
                    if pckg["name"] == "bio-pyvol":
                        update_available = True
                        # pyvol_version = apply_color("{0} ({1} available)".format(pyvol_version, pckg['latest_version']), "blue")
                        form.install_remote_browser.setText(("A new version of PyVOL is available through PyPI:<br>"
                            "&nbsp;   pyvol: {0} -> {1}").format(pyvol_version, apply_color(pckg['latest_version'], "blue")))
                        break

                if update_available:
                    form.install_remote_button.setText("Update PyVOL")
                    form.install_remote_button.clicked.connect(lambda: update_pyvol(form))
                    form.install_remote_button.setEnabled(True)
                else:
                    form.install_remote_button.setText("Check for Updates")
                    form.install_remote_button.clicked.connect(lambda: refresh_installation_status(form, check_for_updates=True))
                    form.install_remote_button.setEnabled(True)
                    form.install_remote_browser.setText(("Local PyVOL is up to date (version {0})<br>").format(pyvol_version))

            if msms_installed:
                form.run_tab.setEnabled(True)
                form.run_button.setEnabled(True)
                form.load_tab.setEnabled(True)
                status_msg = "PyVOL seems to be correctly installed.<br>"
            else:
                form.run_tab.setEnabled(False)
                form.run_button.setEnabled(False)
                form.load_tab.setEnabled(False)
                form.tabWidget.setCurrentIndex(2)
                status_msg = apply_color("Error: MSMS must be installed for PyVOL to run.<br>", "red")

            gui_version = None
            expected_gui_version = None
            try:
                import pyvol
                expected_gui_version = pyvol.__guiversion__
                if __version__ == expected_gui_version:
                    gui_version = apply_color(__version__, "green")
                else:
                    gui_version = apply_color("{0} ({1} expected)".format(__version__, expected_gui_version), "blue")
                    status_msg = status_msg + "{0}--check whether the PyVOL backend is up-to-date and using the PyMOL plugin manager reinstall the newet version of the plugin from <a href='https://github.com/schlessingerlab/pyvol/blob/master/pyvolgui.zip'>github</a>.<br>".format(apply_color("GUI version mismatch", "red"))
            except:
                gui_version = __version__

            form.install_status_browser.setText((
                "&nbsp;   pyvol: {0}<br>"
                "&nbsp;   pyvol gui: {8}<br>"
                "&nbsp;   biopython: {1}<br>"
                "&nbsp;   numpy: {2}<br>"
                "&nbsp;   pandas: {3}<br>"
                "&nbsp;   scipy: {4}<br>"
                "&nbsp;   sklearn: {5}<br>"
                "&nbsp;   trimesh: {6}<br>"
                "&nbsp;   msms exe: {7}<br><br>"
                "{8}"
            ).format(pyvol_version, biopython_version, numpy_version, pandas_version, scipy_version, sklearn_version, trimesh_version, msms_exe, gui_version, status_msg))

    def run_gui_load(form):
        """ Loads a precalculated pocket into PyMOL

        """
        from pyvol import pymol_interface

        # Loading Parameters
        pocket_file = form.pocket_file_ledit.text()
        if form.load_solid_rbutton.isChecked():
            display_mode = "solid"
        elif form.load_mesh_rbutton.isChecked():
            display_mode = "mesh"
        elif form.load_spheres_rbutton.isChecked():
            display_mode = "spheres"
        color = form.load_color_ledit.text()
        alpha = form.load_alpha_ledit.text()
        prefix = form.load_prefix_ledit.text()

        if color == "":
            color = None
        if alpha == "":
            alpha = None
        if prefix == "":
            prefix = None

        if not os.path.isfile(pocket_file):
            logger.error("Supplied file not found: {0}".format(pocket_file))
            return
        else:
            pymol_interface.load_pocket(pocket_file, name=prefix, display_mode=display_mode, color=color, alpha=alpha)

    def run_gui_pyvol(form):
        """ Runs a PyVOL calculation

        """
        from pyvol import pymol_interface

        # Basic Parameters
        protein = form.prot_sele_ledit.text()
        excl_org = form.excl_org_cbox.isChecked()
        min_rad = form.min_rad_ledit.text()
        max_rad = form.max_rad_ledit.text()
        constrain_inputs = form.constrain_cbox.isChecked()

        # Pocket Selection
        minimum_volume = None
        ligand = None
        lig_incl_rad = None
        lig_excl_rad = None
        residue = None
        resid = None
        pocket_coordinate = None

        if form.all_rbutton.isChecked():
            mode = "all"
            minimum_volume = form.min_volume_ledit.text()
        elif form.largest_rbutton.isChecked():
            mode = "largest"
        elif form.ligand_rbutton.isChecked():
            mode = "specific"
            ligand = form.lig_sele_ledit.text()
            if form.lig_incl_rad_ledit.text() != "":
                lig_incl_rad = form.lig_incl_rad_ledit.text()
            if form.lig_excl_rad_ledit.text() != "":
                lig_excl_rad = form.lig_excl_rad_ledit.text()
        elif form.residue_rbutton.isChecked():
            mode = "specific"
            residue = form.residue_sele_ledit.text()
        elif form.resid_rbutton.isChecked():
            mode = "specific"
            resid = form.resid_ledit.text()
        elif form.coordinate_rbutton.isChecked():
            mode = "specific"
            pocket_coordinate = form.coordinate_ledit.text()

        # Partitioning Parameters
        subdivide = form.subdivide_cbox.isChecked()
        if not subdivide:
            subdivide = None
        max_clusters = form.max_clusters_ledit.text()
        min_subpocket_rad = form.min_internal_rad_ledit.text()
        min_subpocket_surf_rad = form.min_surf_rad_ledit.text()

        # Display and Output Options
        if form.solid_rbutton.isChecked():
            display_mode = "solid"
        elif form.mesh_rbutton.isChecked():
            display_mode = "mesh"
        elif form.spheres_rbutton.isChecked():
            display_mode = "spheres"
        color = form.color_ledit.text()
        alpha = form.alpha_ledit.text()
        prefix = form.prefix_ledit.text()
        if prefix == "":
            prefix = None
        output_dir = form.output_dir_ledit.text()
        if output_dir == "":
            output_dir = None

        pymol_interface.pocket(protein=protein, mode=mode, ligand=ligand, pocket_coordinate=pocket_coordinate, residue=residue, resid=resid, prefix=prefix, min_rad=min_rad, max_rad=max_rad, lig_excl_rad=lig_excl_rad, lig_incl_rad=lig_incl_rad, display_mode=display_mode, color=color, alpha=alpha, output_dir=output_dir, subdivide=subdivide, minimum_volume=minimum_volume, min_subpocket_rad=min_subpocket_rad, min_subpocket_surf_rad=min_subpocket_surf_rad, max_clusters=max_clusters, excl_org=excl_org, constrain_inputs=constrain_inputs)

    refresh_installation_status(form)

    form.close_button.clicked.connect(dialog.close)
    form.run_button.clicked.connect(lambda: run_gui_pyvol(form))

    form.browse_button.clicked.connect(lambda: browse_pocket_file(form))
    form.load_button.clicked.connect(lambda: run_gui_load(form))

    dialog.show()
