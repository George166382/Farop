import os
import re
from enum import Enum
import rsync_folder as folder
import rsync_ftp as ftp
import rsync_zip as archive


class LocationType(Enum):
    """This class holds all the possible locations types.
    It has methods to check if a location url is valid and knows how to call specific methods for each location type"""
    FTP = 'ftp',
    ZIP = 'zip',
    FOLDER = 'folder'

    @staticmethod
    def contains_key(key: str):
        """This method checks if the given parameter key corresponds to a value in the enum keys
        and returns true if found or false otherwise"""
        values = set(i.value for i in LocationType)
        for value in values:
            if type(value) is tuple:
                if key == value[0]:
                    return True
            if type(value) is str:
                if key == value:
                    return True
        return False

    @staticmethod
    def is_path_valid(type_str, _path: str):
        """This method checks if the location path specified at parameter 'path' matches a certain regular expression"""
        regular_expressions = {
            LocationType.FTP: r"^.*$",
            LocationType.ZIP: r"^[a-zA-Z]:[\\\/](?:[a-zA-Z0-9_]+[\\\/])*([a-zA-Z0-9]+).zip$",
            LocationType.FOLDER: r"^[a-zA-Z]:[\\\/](?:[a-zA-Z0-9_]+[\\\/])*([a-zA-Z0-9]+)$"
        }
        _type: LocationType = LocationType.FOLDER
        if type_str.lower() == 'zip':
            _type = LocationType.ZIP
        elif type_str.lower() == 'ftp':
            _type = LocationType.FTP
        elif type_str.lower() == 'folder':
            _type = LocationType.FOLDER
        else:
            return False

        _regex = regular_expressions[_type]
        pattern = re.compile(_regex)
        if pattern.match(_path) is None:
            return False
        return True

    @staticmethod
    def exists(type_str: str, _path: str):
        """This method checks if the location path given as parameter of type type_str exists or not."""
        if type_str.lower() == 'zip' or type_str.lower() == 'folder':
            return os.path.exists(_path)
        else:
            return ftp.ftp_exists(_path)

    @staticmethod
    def is_valid(input_string: str):
        """This method checks if a location path given as parameter is valid and if it exists."""
        if input_string.count(':') == 0:
            return False

        _type, _path = input_string.split(':', 1)

        if not LocationType.contains_key(_type.lower()):
            return False
        if not LocationType.is_path_valid(_type, _path):
            return False
        if not LocationType.exists(_type, _path):
            return False
        return True

    def get_hash(self, path):
        """This method calls the specific method for each type of location
        to get the hash for the path given as parameter"""
        if self.value == LocationType.FOLDER.value:
            return folder.get_hash(path)
        if self.value == LocationType.ZIP.value:
            return archive.get_hash(path)
        if self.value == LocationType.FTP.value:
            return ftp.get_hash(path)

    def get_files_list(self, path):
        """This method calls the specific method for each type of location
        to get the files list for the path given as parameter"""
        if self.value == LocationType.FOLDER.value:
            return folder.get_files_list(path)
        if self.value == LocationType.ZIP.value:
            return archive.get_files_list(path)
        if self.value == LocationType.FTP.value:
            return ftp.get_files_list(path)

    def copy_file_to_storage(self, path, file):
        """This method calls the specific method for each type of location
        to copy the file given as parameter to the storage for the path given as parameter"""
        if self.value == LocationType.FOLDER.value:
            folder.copy_to_storage(path, file)
        if self.value == LocationType.ZIP.value:
            archive.copy_to_storage(path, file)
        if self.value == LocationType.FTP.value:
            ftp.copy_to_storage(path, file)

    def copy_file_from_storage(self, path, file):
        """This method calls the specific method for each type of location
        to copy the file given as parameter from the storage for the path given as parameter"""
        if self.value == LocationType.FOLDER.value:
            folder.copy_from_storage(path, file)
        if self.value == LocationType.ZIP.value:
            archive.copy_from_storage(path, file)
        if self.value == LocationType.FTP.value:
            ftp.copy_from_storage(path, file)

    def get_files_with_hash(self, path):
        """This method calls the specific method for each type of location
        to get a list of lists where the first element is a file path and the second element is it's hash
         for the path given as parameter"""
        if self.value == LocationType.FOLDER.value:
            return folder.get_files_with_hash(path)
        if self.value == LocationType.ZIP.value:
            return archive.get_files_with_hash(path)
        if self.value == LocationType.FTP.value:
            return ftp.get_files_with_hash(path)

    def get_last_modification_date_of_file(self, path, file):
        """This method calls the specific method for each type of location
        to get the last modification date of the file given as parameter for the path given as parameter"""
        if self.value == LocationType.FOLDER.value:
            return folder.get_last_modification_date_of_file(path, file)
        if self.value == LocationType.ZIP.value:
            return archive.get_last_modification_date_of_file(path, file)
        if self.value == LocationType.FTP.value:
            return ftp.get_last_modification_date_of_file(path, file)

    def delete_file(self, path, file):
        """This method calls the specific method for each type of location
        delete the file specified as parameter for the path given as parameter"""
        if self.value == LocationType.FOLDER.value:
            return folder.delete_file(path, file)
        if self.value == LocationType.ZIP.value:
            return archive.delete_file(path, file)
        if self.value == LocationType.FTP.value:
            return ftp.delete_file(path, file)


class Location:
    """This class holds a location information:
    what type it is and the path where it's located.
    It also calls methods to execute tasks required to keep two locations synchronised."""
    type: LocationType
    path: str

    def __init__(self, location_string: str):
        """Constructor that creates type LocationType enums and creates the path from the location url parameter"""
        v = location_string.split(':', 1)
        if v[0].lower() == 'zip':
            self.type = LocationType.ZIP
        elif v[0].lower() == 'ftp':
            self.type = LocationType.FTP
        elif v[0].lower() == 'folder':
            self.type = LocationType(v[0].lower())
        self.path = v[1]

    @staticmethod
    def generate(input_string, n):
        """This factory method creates a Location object if the input given as parameter is valid.
        The n parameter is just an index for printing."""
        if not LocationType.is_valid(input_string):
            print(f"Invalid input for location {n}.")
            exit(-1)
        return Location(input_string)

    def get_hash(self):
        """Calls the get hash method for it's corresponding type and path."""
        return self.type.get_hash(self.path)

    def get_files_list(self):
        """Calls the get files list method for it's corresponding type and path."""
        return self.type.get_files_list(self.path)

    def copy_file_to_storage(self, file):
        """Calls the copy file to storage method for the file parameter for it's corresponding type and path."""
        self.type.copy_file_to_storage(self.path, file)

    def copy_file_from_storage(self, file):
        """Calls the copy file from storage method for the file parameter for it's corresponding type and path."""
        self.type.copy_file_from_storage(self.path, file)

    def get_files_with_hash(self):
        """Calls the get files with hash method for it's corresponding type and path."""
        return self.type.get_files_with_hash(self.path)

    def get_last_modification_date_of_file(self, file):
        """Calls the get last modification date of file method for the file parameter
         for it's corresponding type and path."""
        return self.type.get_last_modification_date_of_file(self.path, file)

    def delete_file(self, file):
        """Calls the delete file method for the file parameter for it's corresponding type and path."""
        return self.type.delete_file(self.path, file)
