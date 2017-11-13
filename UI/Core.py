from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QIcon
import os

class Paths() :
	Resources = "Resources"
	ResourcesAbs = os.path.abspath(Resources)
	
	Icon = os.path.join(Resources, "icons")

	Project = "project.utopiia"
	Model = "Model.xml"
	SystemConfiguration = "sysconfig.data"
	ControllerData = "ctlmgr.data"

	Setting = os.path.join(Resources, "setting")
	Context = os.path.join(Setting, "context.data")
	TempProjectRoot = os.path.join(Setting, "temp_project")
	BasicModel = os.path.join(Setting, Model)

	BuildResource = os.path.join(ResourcesAbs, "build")
	PlatformList = os.path.join(BuildResource, "platform_list.xml")

	def getPlatformResourcePath(platform, targetOS) :
		return os.path.join(Paths.BuildResource, platform + "_" + targetOS)

class Icons() :
	def init() :
		Icons.Project = QIcon(os.path.join(Paths.Icon, "sample.png"))

		Icons.NewProject = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.OpenProject = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.SaveProject = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.SaveProjectAs = QIcon(os.path.join(Paths.Icon, "sample.png"))

		Icons.ImportModel = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.EditModel = QIcon(os.path.join(Paths.Icon, "sample.png"))

		Icons.SystemConfiguration = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.ControllerConfiguration = QIcon(os.path.join(Paths.Icon, "sample.png"))

		Icons.Generate = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.Regenerate = QIcon(os.path.join(Paths.Icon, "sample.png"))

		Icons.Refresh = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.Insert = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.Remove = QIcon(os.path.join(Paths.Icon, "sample.png"))

		Icons.Connect = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.Disconnect = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.Transmit = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.Run = QIcon(os.path.join(Paths.Icon, "sample.png"))
		Icons.Stop = QIcon(os.path.join(Paths.Icon, "sample.png"))

class Platform() :
	LocalPlatform = "x86_64"
	LocalOS = "Linux"

	CorrectUppaal41 = \
"""#!/usr/bin/env bash

#  
# Run this script to start UPPAAL 4.1.x.
#
"""
	CorrectUppaal40 = \
"""#!/usr/bin/env bash

#  
# Run this script to start UPPAAL 4.0.x.
#
"""
	CorrectModel41 = \
"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' \
'http://www.it.uu.se/research/group/darts/uppaal/flat-1_2.dtd'>
"""
	CorrectModel40 = \
"""<?xml version='1.0' encoding='utf-8'?>\
<!DOCTYPE nta PUBLIC '-//Uppaal Team//DTD Flat System 1.1//EN' \
'http://www.it.uu.se/research/group/darts/uppaal/flat-1_1.dtd'>\
<nta><declaration>"""
	
	def uppaalCommand(UppaalPath, ModelPath) :
		return UppaalPath + " " + ModelPath

	def buildCommand(isLocal) :
		command = []
		if isLocal :
			command.append("cmake .")
		else :
			command.append("cmake -DCMAKE_TOOLCHAIN_FILE=./toolchain.cmake .")
		command.append("make")
		return command

class Console() :
	console = None

	def getDefaultConsole() :
		if not Console.console :
			Console.console = QTextEdit()
			Console.console.setReadOnly(True)
		return Console.console

	def print(data) :
		if Console.console :
			Console.console.setPlainText(Console.console.toPlainText() + data)
			Console.console.verticalScrollBar().setValue(Console.console.verticalScrollBar().maximum())
