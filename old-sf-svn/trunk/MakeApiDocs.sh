# create the API docs in APIDOC

epydoc --no-sourcecode -o SP_APIDOC \
                                BorgSingleton.py SPConstants.py\
                                SPDataManager.py\
                                SPgdm.py SPGoodies.py \
                                SPLogging.py SPMainCore.py SPMenu.py \
                                SPOptionParser.py \
                                SPVersion.py SQLTables.py \
                                utils.py \
                                gui/AdminGui.py gui/SPGuiDBModel.py \
                                sp_cr.py
                                                                    
epydoc  --no-sourcecode  -o SP_ActivityDOC \
                                     SPConstants.py SPDataManager.py \
                                    SPGoodies.py utils.py sp_cr.py 
