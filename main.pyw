from elevate import elevate
elevate()
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import uic
from pxpowersh import PxPowershell
import hjson
import sys
import os
from collections import OrderedDict
from random import randrange
from threading import Thread
import requests
import re
from urllib.parse import quote, unquote

from tkinter import messagebox
import tkinter as tk

root = tk.Tk()
root.withdraw()

try:
    requests.get('https://1.1.1.1')
except requests.exceptions.ConnectionError:
    messagebox.showerror('Connection error', 'Could not connect to the internet. Please check your connection and try again.')
    sys.exit()


sys.stdout = open('log.txt', 'w')

def remove_special_chars(s):
    return ' '.join(''.join(i for i in s if i not in "\/:*?<>|").split()).replace('...', '…').rstrip('.')


def web_download(url, path):
    if os.path.exists(path): return
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("design.ui", self)

        # find the widgets in the xml file
        self.debloatTree = self.findChild(QtWidgets.QTreeWidget, "treeWidget_2")
        self.optimizeTree = self.findChild(QtWidgets.QTreeWidget, "treeWidget_3")
        self.uicustomizationTree = self.findChild(QtWidgets.QTreeWidget, "treeWidget_4")
        self.installprogramsTree = self.findChild(QtWidgets.QTreeWidget, "treeWidget_5")
        self.stackedWidget = self.findChild(QtWidgets.QStackedWidget, "stackedWidget")
        self.run_button = self.findChild(QtWidgets.QPushButton, "pushButton")
        self.install_programs_button = self.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.log_list = self.findChild(QtWidgets.QListWidget, "listWidget")
        self.create_restore_point = self.findChild(QtWidgets.QCheckBox, "checkBox")
        self.status_label = self.findChild(QtWidgets.QLabel, "label_2")
        self.progress_bar = self.findChild(QtWidgets.QProgressBar, "progressBar")

        self.debloat_select_default = self.findChild(QtWidgets.QPushButton, "pushButton_3")
        self.debloat_unselect_all = self.findChild(QtWidgets.QPushButton, "pushButton_4")
        self.debloat_unselect_uwp = self.findChild(QtWidgets.QPushButton, "pushButton_9")
        self.optimize_select_default = self.findChild(QtWidgets.QPushButton, "pushButton_5")
        self.optimize_unselect_all = self.findChild(QtWidgets.QPushButton, "pushButton_6")
        self.ui_select_default = self.findChild(QtWidgets.QPushButton, "pushButton_7")
        self.ui_unselect_all = self.findChild(QtWidgets.QPushButton, "pushButton_8")

        self.debloat_essential = self.findChild(QtWidgets.QCheckBox, "checkBox_2")
        self.optimize_essential = self.findChild(QtWidgets.QCheckBox, "checkBox_3")
        self.ui_essential = self.findChild(QtWidgets.QCheckBox, "checkBox_4")


        # set default column widths
        self.optimizeTree.setColumnWidth(0, 400)
        self.installprogramsTree.setColumnWidth(0, 250)

        # load data
        self.data = dict(hjson.load(open('data.hjson')))
        self.treeitems = {'debloat': [], 'optimize': [], 'ui': [], 'install': []}

        # load ui
        self.loadui(self.debloatTree, self.data['Debloat'], 'debloat')
        self.loadui(self.optimizeTree, self.data['Optimization'], 'optimize', columns=['recommend'])
        self.loadui(self.uicustomizationTree, self.data['UI Customization'], 'ui')
        self.loadui(self.installprogramsTree, self.data['Install Programs'], 'install', columns=['description'])

        # expand trees
        self.optimizeTree.expandToDepth(0)
        self.uicustomizationTree.expandToDepth(0)
        self.installprogramsTree.expandToDepth(0)

        # set connections
        self.run_button.clicked.connect(lambda: self.start(None))
        self.install_programs_button.clicked.connect(lambda: self.start(['install']))

        self.debloat_select_default.clicked.connect(lambda: self.group_select('debloat', True))
        self.debloat_unselect_all.clicked.connect(lambda: self.group_select('debloat', False))
        self.optimize_select_default.clicked.connect(lambda: self.group_select('optimize', True))
        self.optimize_unselect_all.clicked.connect(lambda: self.group_select('optimize', False))
        self.ui_select_default.clicked.connect(lambda: self.group_select('ui', True))
        self.ui_unselect_all.clicked.connect(lambda: self.group_select('ui', False))
        self.debloat_unselect_uwp.clicked.connect(self.unselect_uwp)
        

        # show the ui
        self.show()

    def unselect_uwp(self):
        self.group_select('debloat', True)
        for item in self.treeitems['debloat']:
            if item['value'].get('uwppackage'):
                item['treeitem'].setCheckState(0, QtCore.Qt.Unchecked)


    def group_select(self, section, defaults=True):
        essentials_check = {'debloat': self.debloat_essential, 'optimize': self.optimize_essential, 'ui': self.ui_essential}
        for item in self.treeitems[section]:
            if defaults:
                item['treeitem'].setCheckState(0, QtCore.Qt.Checked if item['value'].get('default') else QtCore.Qt.Unchecked)
            else:
                item['treeitem'].setCheckState(0, QtCore.Qt.Unchecked)
        if essentials_check.get(section):
            essentials_check[section].setChecked(defaults)


    def start(self, sections=None):
        # get items to run
        if sections == None:
            sections = ['debloat', 'optimize', 'ui', 'install']
        treeitems = {}
        for key in self.treeitems.keys():
            if key in sections:
                treeitems[key] = self.treeitems[key]

        self.stackedWidget.setCurrentIndex(1)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        QtWidgets.QApplication.processEvents()

        # run
        t = Thread(target=self.run, args=(treeitems,))
        t.daeomon = True
        t.start()

        while t.is_alive():
            self.log_list.scrollToBottom()
            QtWidgets.QApplication.processEvents()

        # change progress bar
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        QtWidgets.QApplication.processEvents()

        if len(sections) == len(self.treeitems): # if all sections was ran
            if self.error_output:
                self.log('Error', append_dots=False, add_to_list=False, process_events=True)
                messagebox.showerror('Amelio - Error', self.error_output)
                self.error_output = False
            else:
                self.log('Restarting explorer')
                print(self.px.run('stop-process -name explorer -force'))
                self.log('Complete.', append_dots=False, process_events=True)
                if messagebox.askyesno('Amelio - Complete', 'Operation has completed. Would you like to restart now?'):
                    self.px.run('shutdown /r /t 0')
                sys.exit()
        else:
            self.log('Complete.', append_dots=False, process_events=True)
            messagebox.showinfo('Amelio - Complete', 'Operation has completed.')

        self.stackedWidget.setCurrentIndex(0)
        QtWidgets.QApplication.processEvents()


    def download_installer(self, download_url, args=None):      
        name = remove_special_chars(unquote(download_url.split('/')[-1]))
        self.log('Downloading '+name)
        name = name.split('.')
        name = '.'.join(name[:-1]) + ''.join([str(randrange(10)) for _ in range(10)]) + '.' + name[-1]
        
        path = os.path.join(os.environ['tmp'], name)
        
        web_download(download_url, path)

        return f'cmd /c "{path}" ' + (args if args else '')


    def get_essential(self, section):
        commands = []
        if self.data[section].get('essential'):
            if self.data[section]['essential'].get('command'):
                for i in self.data[section]['essential']['command'].split('\n'):
                    commands.append(i)
            if self.data[section]['essential'].get('sophia'):
                commands.append('./scripts/Sophia/Sophia.ps1 -Functions "' + '", "'.join(self.data[section]['essential']['sophia'].split('\n')) + '"')
        return commands


    def log(self, x, append_dots=True, add_to_list=True, process_events=False):
        if append_dots: x += (('' if ':' in x else '...') if not x.endswith('.') else '')
        print(x)
        self.status_label.setText(x)
        if add_to_list:
            self.log_list.addItem(x)
            self.log_list.scrollToBottom()
        if process_events:
            QtWidgets.QApplication.processEvents()


    def run_shutup10(self, ooconfig):
        name = 'ooshutup10' + ''.join([str(randrange(10)) for _ in range(10)]) + '.cfg'
        path = os.path.join(os.environ['tmp'], name)

        with open(path, 'w') as f:
            for key, value in ooconfig.items():
                f.write(key + '\t' + ('+' if value else '-') + '\n')
        
        return f'cmd /c scripts\Shutup10\OOSU10.exe "{path}" /quiet'


    def run(self, treeitems):
        self.log_list.clear()
        self.error_output = False
        run_all_sections = len(treeitems) == len(self.treeitems)

        self.log('Starting powershell process')

        try:
            self.px = PxPowershell(debug=True)
            self.px.start_process()
        except:
            self.error_output = 'Could not start powershell. Please close out of any other applications and try again.'
            return

        self.log('Setting powershell execution policy')
        self.px.run(self.data['SetExecutionPolicy'])

        try:
            # installing choco
            self.log('Checking if choco is installed')
            if len(self.px.run('choco -v', timeout=9999).strip()) > 15:
                self.log('Installing choco')
                self.px.run(self.data['InstallChoco'], timeout=9999)

            if self.optimize_essential.isChecked():
                ooconfig = self.data['ooconfig']
            else:
                ooconfig = {}
            
            # list of commands
            commands = []

            # initialize lists for packages
            uwppackages = []
            chocopackages = {}
            pippackages = []

            # other functions list
            otherfuncslist = []
        
            # get essential commands
            if run_all_sections:
                self.log('Getting essential commands')
                for x, y in {'Debloat': self.debloat_essential.isChecked(),
                            'UI Customization': self.optimize_essential.isChecked(),
                            'Optimization': self.ui_essential.isChecked()}.items():
                    if y: commands.append({'Running essential commands: '+x: self.get_essential(x)})


            # get selected commands
            for section_items in treeitems.values():
                for item in section_items:
                    if item['treeitem'].checkState(0):
                        if item['value'].get('command'):        # commands
                            commands.append({'Running: '+item['name']: item['value']['command'].split('\n')})
                        if item['value'].get('uwppackage'):     # uwp packages to remove
                            uwppackages.append(item['value']['uwppackage'])
                        elif item['value'].get('choco'):        # choco packages to install
                            chocopackages.update({item['name']: item['value']['choco'].split('\n')})
                        elif item['value'].get('pip'):          # pip packages to install
                            pippackages += item['value']['pip'].split('\n')
                        elif item['value'].get('ooconfig'):     # ooconfig
                            ooconfig.update(item['value']['ooconfig'])
                        elif item['value'].get('download'):     # download installer files
                            commands.append({'Installing '+item['name']: [self.download_installer(item['value']['download'], item['value'].get('args'))]})
                        elif item['value'].get('run_in_file'):  # other (idk how to do these in powershell so these will be ran in python)
                            otherfuncslist.append(item['value']['flag'])

            # o&o shutup10 config
            if len(ooconfig) != 0 and run_all_sections:
                commands.insert(0, {'Runing O&O Shutup10 config': [self.run_shutup10(ooconfig)]})

            # adding package commands
            if len(uwppackages) > 0: commands.insert(0, {'Removing bloatware UWP packages': ['./scripts/Windows10Debloater/DebloatWindows.ps1 "'+ '\" \"'.join(uwppackages)+ '\"']})
            if len(pippackages) > 0: commands.append({'Installing pip packages': ['pip install '+ ' '.join(pippackages)]})
            if len(chocopackages) > 0:
                for name, chocopackage in chocopackages.items():
                    commands.append({f'Installing {name}': ['choco install '+ ' '.join(chocopackage) + ' -y --no-progress --no-color -r' ]})

            
            # create restore point
            if self.create_restore_point.isChecked():
                commands.insert(0, {'Creating restore point': [self.data['CreateRestorePoint']]})


            # final commands
            for item in commands:
                for name, commandlist in item.items():
                    self.log(name)
                    for command in commandlist:
                        print(command)
                        print(self.px.run(command, timeout=9999))
            # run this after config
            for flag in otherfuncslist:
                self.other_functions(flag)

        except Exception as e:
            self.error_output = f'An error occured while running.\n\nMore details:\n{e}'
            return


    def loadui(self, parent, items, section: str, columns: list=[]):
        for key, value in items.items():
            # ignore essential commands section
            if key != 'essential':
                # if value has children
                if all(type(x) in [OrderedDict, dict] for x in value.values()):
                    sectionItem = QtWidgets.QTreeWidgetItem(parent, [key])
                    self.loadui(sectionItem, value, section, columns)
                else:
                    self.treeitems[section].append({
                        'treeitem': QtWidgets.QTreeWidgetItem(parent, [key] + [('' if value.get(x) == None else str(value[x])) for x in columns]),
                        'name': key,
                        'value': value
                    })
                    if value.get('default'):
                        self.treeitems[section][-1]['treeitem'].setCheckState(0, QtCore.Qt.Checked)
                    else:
                        self.treeitems[section][-1]['treeitem'].setCheckState(0, QtCore.Qt.Unchecked)
                    # if value has children
                    if value.get('img'):
                        icon = QtGui.QIcon()
                        icon.addPixmap(QtGui.QPixmap(f"img/{value['img']}"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                        self.treeitems[section][-1]['treeitem'].setIcon(0, icon)
                    if value.get('children'):
                        self.loadui(self.treeitems[section][-1]['treeitem'], value['children'], section, columns)
    



    def other_functions(self, flag):
        '''
        Other commands will be ran here that cannot be ran in powershell
        set this in the json:
            run_in_file: true
            flag: "flag"
        '''

        # set ultumate performance
        # this will be changed to switch cases once 3.10 is released and fully supported
        if flag == 'ultimateperformance':
            self.log('Setting ultimate performance mode')
            if os.popen('powercfg /L | findstr "Ultimate Performance"').readline().strip() == '':
                os.system('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61')
            # get ultimate performance scheme id
            scheme_id = os.popen('powercfg /L | findstr "Ultimate Performance"').readlines()[0].strip().split()[3]
            self.px.run(f'powercfg /S {scheme_id}')
            return

        # theme patcher
        elif flag == 'themepatcher':
            self.log('Downloading Secure UXTheme')
            # path = os.path.join(os.environ['userprofile'], 'Desktop')
            path = os.path.join(os.environ['userprofile'], 'Desktop', 'SecureUxTheme')
            if not os.path.exists(path):
                os.mkdir(path)
            web_download('https://cdn.discordapp.com/attachments/714922631693860956/858886114642231346/ThemeTool.exe', os.path.join(path, 'ThemeTool.exe'))
            web_download('https://cdn.discordapp.com/attachments/714922631693860956/858886114453225482/SecureUxTheme.dll', os.path.join(path, 'SecureUxTheme.dll'))
            # ^^^^^ files compiled by me
            # original project: https://github.com/namazso/SecureUxTheme
            web_download('https://raw.githubusercontent.com/angelsix/youtube/develop/Windows%2010%20Dark%20Theme/Windows/Tools/MakeAppsUseDarkTheme.reg', os.path.join(path, 'Use Windows Dark Mode.reg'))
            # some themes will automatically set windows back to light mode, this will create a shortcut to change it back
            return

        # after dark cc v2 theme
        elif flag == 'afterdarktheme':
            self.log('Installing After Dark CC v2')
            path = os.path.join('C:\\Windows', 'Resources', 'Themes')

            for folder_path in [os.path.join(path, 'After Dark CC'),
                                os.path.join(path, 'After Dark CC', 'Shell'),
                                os.path.join(path, 'After Dark CC', 'Shell', 'NormalColor'),
                                os.path.join(path, 'After Dark CC', 'Shell', 'NormalColor', 'en-US')]:
                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)

            web_download('https://raw.githubusercontent.com/angelsix/youtube/develop/Windows%2010%20Dark%20Theme/Windows/Themes/After%20Dark%20CC%20(Creators%20Update%201709)/Show%20Commandbar/After%20Dark%20CC%20v2.theme',
                os.path.join(path, 'After Dark CC v2.theme'))
            web_download('https://raw.githubusercontent.com/angelsix/youtube/develop/Windows%2010%20Dark%20Theme/Windows/Themes/After%20Dark%20CC%20(Creators%20Update%201709)/Show%20Commandbar/After%20Dark%20CC/After%20Dark%20CC2.msstyles',
                os.path.join(path, 'After Dark CC', 'After Dark CC2.msstyles'))
            web_download('https://raw.githubusercontent.com/angelsix/youtube/develop/Windows%2010%20Dark%20Theme/Windows/Themes/After%20Dark%20CC%20(Creators%20Update%201709)/Show%20Commandbar/After%20Dark%20CC/Shell/NormalColor/shellstyle.dll',
                os.path.join(path, 'After Dark CC', 'Shell', 'NormalColor', 'shellstyle.dll'))
            web_download('https://raw.githubusercontent.com//angelsix/youtube/develop/Windows%2010%20Dark%20Theme/Windows/Themes/After%20Dark%20CC%20(Creators%20Update%201709)/Show%20Commandbar/After%20Dark%20CC/Shell/NormalColor/en-US/shellstyle.dll.mui',
                os.path.join(path, 'After Dark CC', 'Shell', 'NormalColor', 'en-US', 'shellstyle.dll.mui'))
            return

        # get the latest sandboxie
        elif flag == 'sandboxie-plus':
            self.log('Installing Sandboxie-Plus')
            github_data = requests.get('https://api.github.com/repos/sandboxie-plus/Sandboxie/releases/latest').json()
            for asset in github_data['assets']:
                if 'Plus-x64' in asset['browser_download_url']:
                    print(self.px.run(self.download_installer(asset['browser_download_url'], '/VERYSILENT'), timeout=9999))
                    return
        
        # install betterdiscord
        elif flag == 'betterdiscord':
            # this could have been ran as a normal command but it requires discord already installed
            self.log('Installing BetterDiscord')
            print(self.px.run('./scripts/InstallBetterDiscord.ps1', timeout=9999))
            return
        
        elif flag == "lunarclient":
            self.log('Installing Lunar Client')
            a = requests.get('https://launcherupdates.lunarclientcdn.com/latest.yml').text
            url = 'https://launcherupdates.lunarclientcdn.com/' + quote(re.findall('url:.*\n', a)[0].replace('url: ', '').strip())
            print(self.px.run(self.download_installer(url, '/S'), timeout=9999))

        elif flag == "userbenchmark":
            web_download('https://www.userbenchmark.com/resources/download/UserBenchMark.exe', os.path.join(os.environ['userprofile'], 'Desktop', 'UserBenchMark.exe'))
    
        elif flag == "faboptimized":
            mod_files = [
                '/files/3358/614/fabric-api-0.36.0%2B1.16.jar',
                '/files/3270/425/notenoughcrashes-3.2.0-fabric.jar',
                '/files/3344/188/item-model-fix-1.0.2%2B1.16.jar',
                '/files/3294/303/phosphor-fabric-mc1.16.3-0.7.2%2Bbuild.12.jar',
                '/files/3271/155/fabrishot-1.4.0.jar',
                '/files/3196/688/betterbeds-1.1.0.jar',
                '/files/3048/200/okzoomer-4.0.1%2B1.16.2.jar',
                '/files/3268/909/modmenu-1.16.9.jar',
                '/files/3067/101/sodium-fabric-mc1.16.3-0.1.0.jar',
                '/files/3209/972/lazydfu-0.1.2.jar',
                '/files/3223/126/cullleaves-2.1.0.jar',
                '/files/3366/159/architectury-1.18.25-fabric.jar',
                '/files/2963/760/SmoothScrollingEverywhere-3.0.3-unstable.jar',
                '/files/3202/525/slight-gui-modifications-1.7.1.jar',
                '/files/3299/645/capes-1.1.2.jar',
                '/files/3358/432/ferritecore-2.0.5-fabric.jar',
                '/files/3355/671/sodium-extra-0.3.2.jar',
                '/files/3248/104/smoothboot-fabric-1.16.5-1.6.0.jar',
                '/files/3193/496/antighost-1.16.5-fabric0.30.0-1.1.3.jar',
                '/files/3298/609/custom-fog-1.5.1.jar',
                '/files/3222/361/fast-chest-1.2%2B1.16.jar',
                '/files/3358/819/EntityCulling-Fabric-1.3.0.jar',
                '/files/3330/753/fabric-language-kotlin-1.6.1%2Bkotlin.1.5.10.jar',
                '/files/3172/563/lambdynamiclights-fabric-1.3.4%2B1.16.jar',
                '/files/3302/730/dynamic-fps-2.0.2.jar',
                '/files/3228/523/nofade-1.16.5-1.0.1.jar',
                '/files/3311/351/cloth-config-4.11.26-fabric.jar',
                '/files/3344/974/lithium-fabric-mc1.16.5-0.6.6.jar',
                '/files/3356/722/colormatic-2.2.9%2Bmc.1.16.5.jar',
                '/files/3224/921/tweakeroo-fabric-1.16.4-0.10.0-dev.20210303.123654.jar',
                '/files/3252/979/malilib-fabric-1.16.4-0.10.0-dev.21%2Barne.5.jar',
            ]

            mc_folder = os.path.join(os.environ['appdata'], '.minecraft')
            if not os.path.exists(mc_folder): os.mkdir(mc_folder)

            mc_folder = os.path.join(mc_folder, 'mods')
            if not os.path.exists(mc_folder): os.mkdir(mc_folder)

            for mod in mod_files:
                name = unquote(mod.split('/')[-1])
                if not os.path.exists(os.path.join(mc_folder, name)):
                    self.log('Downloading mc mod: '+name)
                    web_download('https://media.forgecdn.net'+mod, os.path.join(mc_folder, name))







# initialize app
app = QApplication(sys.argv)

MainWindow = QtWidgets.QMainWindow()

window = UI()
app.exec_()