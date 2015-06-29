import os
import json
import re
from collections import OrderedDict
from log_prompt import prompts

import pymongo

p = prompts()


# validation functions, fields, etc.
class validate():

    def __init__(self):

        self.interface = False

        # store prompt inputs
        self.data = {}

        # base path
        self.dir_base = os.path.dirname(os.path.abspath(__file__))

        # available licenses
        self.licenses = json.load(open(self.dir_base + "/licenses.json", 'r'))

        # init file format
        self.file_format = ""

        # acceptable inputs for various fields (dataset types, vector formats, raster formats, etc.)
        self.types = {
            "licenses": self.licenses.keys(),
            "data": ['raster', 'polydata', 'document', 'point', 'multipoint', 'boundary'],
            "file_extensions": {
                "vector": ['geojson', 'shp'],
                "raster": ['tif', 'asc']
            },
            "extracts": ['mean', 'max']
        }

        # error messages to go with validation functions
        self.error = {
            "is_dir": "not a directory",
            "name": "name exists or was rejected by user",
            "license_types": "at least one license id given not in list of valid license ids",
            "data_type": "not in list of valid types",
            "file_extension": "not a valid primary file extension",
            "extract_types": "at least one extract type given not in list of valid extract types",
            "factor": "could not be converted to float",
            "day_range": "could not be converted to int",
            "string": "could not be converted to string"
        }

        # current datapackage fields
        self.fields = json.load(open(self.dir_base + "/fields.json", 'r'), object_pairs_hook=OrderedDict)

        # mongo stuff
        self.client = pymongo.MongoClient()
        self.db = self.client.daf
        self.c_data = self.db.data


    # -------------------------
    #  misc functions


    # set file format 
    def update_file_format(self, val):
        self.file_format = val


    # -------------------------
    # input validation functions


    # base path exists and is a directory
    # ***going to add check to make sure path is in REU/data/internal(?) folder***
    def is_dir(self, val):
        return os.path.isdir(str(val)), str(val), self.error["is_dir"]


    # check if name is unique and valid
    def name(self, val):
        val = re.sub('[^0-9a-zA-Z._-]+', '', val)

        if val == "":
            return False, None, "??? Error message needed ???"


        val = val.lower()
        
        if self.interface and not p.user_prompt_use_input(value=val):
            return False, None, "??? Error message needed ???"
        
        # check mongodb
        # 
        # unique = 

        # unique = True 
        
        # if not unique:   
        #   return False, None, None
        
        return True, val, None


    # each extract type in extract_types
    def license_types(self, val):
        valx = [x.strip(' ') for x in val.split(",")]

        if len(valx) == 1 and valx[0] == "":
            return True, [], None

        valid = False not in [x in self.types["licenses"] for x in valx]

        vals = None
        if valid:
            vals = [self.licenses[x] for x in valx]

        return valid, vals, self.error["license_types"]


    # type in types
    def data_type(self, val):
        return val in self.types["data"], val, self.error["data_type"]


    # each extract type in extract_types
    def file_extension(self, val):
        valid = self.file_format in self.types["file_extensions"].keys() and val in self.types["file_extensions"][self.file_format]
        return valid, val, self.error["file_extension"]

    # each extract type in extract_types
    def extract_types(self, val):
        vals = [x.strip(' ') for x in val.split(",")]
        valid = False not in [x in self.types["extracts"] for x in vals]
        return valid, vals, self.error["extract_types"]


    # factor is a float
    def factor(self, val):
        if val == "":
            val = 1.0

        try:
            float(val)
            return True, float(val), None
        except:
            return False, None, self.error["factor"]


    # day_range is string
    def day_range(self, val):
        if val == "":
            val = 1

        try:
            int(float(val))
            return True, int(float(val)), None
        except:
            return False, None, self.error["day_range"]


    # generic string
    def string(self, val):
        try:
            str(val)
            return True, str(val), None
        except:
            return False, None, self.error["string"]


    # boundary group
    def group(self, val):

        val = str(val)

        name = self.data["name"]

        # group is boundary name if empty
        if val == "":
            val = name

        # check if boundary with group exists
        exists = c_data.find({"type": "boundary", "group": val}).limit(1).count() > 0

    
        if not exists and self.interface and not p.user_prompt_bool("Group \""+val+"\" does not exist. Are you sure you want to create it?" ):
            return False, None, "group did not pass due to user request"

        else:
            return True, str(val), None

    
        # # check if group is 3 capital letters (ISO3)
        # if len(val) == 3 and val.isupper():
        #     # check if name == group_adm0
        #     if name == val + "_adm0":
        #         return True, str(val), None
        #     else:
        #         # check if boundary with group exists
        #         exists = c_data.find({"type": "boundary", "group": val}).limit(1)
        #         if len(exists) > 0:
        #             return True, str(val), None
        #         else: 
        #             return False, None, "country group (adm0 dataset) must exist before adding"

        # else:
        #     if val == name:
        #         return True, str(val), None
        #     else:
        #         exists = c_data.find({"type": "boundary", "group": val}).limit(1)
        #         if len(exists) > 0:
        #             return True, str(val), None
        #         else:
        #             return False, None, "group does not match name or existing group"

