# ##### BEGIN GPL LICENCE BLOCK #####
#  Copyright (C) 2022  Arthur Langlard
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENCE BLOCK #####


# Author: Arthur Langlard, arthur.langlard@universite-paris-saclay.fr
# Start of the project: 24-02-2022
# Last modification: 07-03-2022
#
# This software is a plugin for the Veusz software.
# it is designed to load DQL files produced by the X-ray diffractometer
# D-8 Brucker. DQL files are text files containing experimental parameters
# and data. This plugin loads a DQL file, and imports only the information
# stored below the [Data] tag.
# Two datasets are created: one containing the 2-theta angle of diffraction
# and one containing the corresponding intensity of the diffracted beam.

from veusz.plugins import ImportPlugin, importpluginregistry

class ImportDQL(ImportPlugin):
    name = "DQL"
    author = "Arthur Langlard"
    description = "Imports X-ray diffraction measurements stored in a DQL file."

    # Comment this line to remove the tab of the plugin
    promote_tab = 'DQL'
    file_extensions = set(['.dql', '.DQL'])

    def formatLine(self, line):
        # Removal of all spaces.
        return line.replace(' ', '').splitlines()[0]
    
    def getNpArray(self, file):
        import numpy as np
        dataFlag = False

        data = []
        
        try:
            for line in file:
                if line == '[Data]\r\n' or line == '[Data]\n':  # Only interested in the [Data] part.
                    dataFlag = True
                
                if dataFlag:
                    line = self.formatLine(line).split(",")
                    #raise

                    # When "Foo,Bar,".split(',') == ["Foo", "Bar", ""] or
                    # "Foo,Bar,\n".split(',') == ["Foo", "Bar", "\n"] generates a
                    # useless item, remove this last one.
                    if line[-1] == "\n" or line[-1] == '':
                        line.pop(-1)
                    
                    data.append(line)
                

            datasetNames = data[1]
            output = (datasetNames, np.array(data[2:]))  # Return (Names, Data).

        except:
            output = None

        return output



    def __init__(self):
        from veusz.plugins import ImportPlugin
        ImportPlugin.__init__(self)


    def getPreview(self, params):
        import numpy as np
        f = params.openFileWithEncoding()

        allowImport = False
        npArray = self.getNpArray(f)

        if npArray != None: # If the data was loaded, display it.
            allowImport = True
            longString = str(npArray[0][0]) + ',' + str(npArray[0][1]) + '\n'
            for data in npArray[1]:
                longString = longString + str(data[0]) + ',' + str(data[1]) + '\n'

        else:
            longString = "File cannot be displayed"

        return (longString, allowImport)
    

    def doImport(self, params):
        from veusz.plugins import ImportDataset1D
        import numpy as np
        """Actually imports data.
        params is a ImportPluginParams object.
        Return a list of ImportDataset1D objects.
        """
        f = params.openFileWithEncoding()


        names, npData = self.getNpArray(f)

        # Return two 1D datasets: one containing the Angle and the other containing the PSD value.
        # (PSD: Position-sensitive-detector)
        return [ImportDataset1D(names[0], npData[:,0]),
        ImportDataset1D(names[1], npData[:,1])]

# add the class to the registry.
importpluginregistry.append(ImportDQL)