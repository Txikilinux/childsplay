# create the API docs in APIDOC

epydoc --no-sourcecode -o CP_APIDOC \
                                ../BorgSingleton.py ../SPConstants.py\
                                ../SPDataManager.py\
                                ../SPgdm.py ../SPGoodies.py \
                                ../SPLogging.py ../SPMainCore.py ../SPMenu.py \
                                ../SPWidgets.py ../SPOptionParser.py \
                                ../SPSpriteUtils.py ../SPVersion.py ../SQLTables.py \
                                ../Timer.py ../utils.py \
                                ../gui/AdminGui.py ../gui/SPGuiDBModel.py \
                                ../pangofont.py ../cairoimage.py 
                                    
epydoc  --no-sourcecode -o CP_ActivityDOC \
                                     ../SPConstants.py ../SPDataManager.py \
                                    ../SPGoodies.py ../SPWidgets.py \
                                    ../SPSpriteUtils.py ../Timer.py ../utils.py \
                                    ../pangofont.py 
