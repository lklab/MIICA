from xml.etree.ElementTree import parse

import os

from UI.Core import Paths

def readPlatformList() :
	platformListXML = parse(Paths.PlatformList)
	root = platformListXML.getroot()

	platformList = {}

	for platformElement in root.getchildren() :
		if platformElement.tag == "platform" :
			platform = platformElement.get("arch")
			platformList[platform] = {}

			for osElement in platformElement.getchildren() :
				if osElement.tag == "os" :
					opSys = osElement.get("type")
					platformList[platform][opSys] = []

					for networkElement in osElement.getchildren() :
						if networkElement.tag == "network" :
							platformList[platform][opSys].append(networkElement.text)

	return platformList
