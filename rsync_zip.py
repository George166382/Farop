import hashlib
import os
import zipfile as zip

storage_path: str = "E:\\Info\\FACULTATE\\ANUL_3\\PYTHON\\PROIECT\\Advanced RSync\\storage"


def md5(zip_path, file_name, hash_md5):
    """This method receives a relative path in file_path from the zip file,and the zip path given in zip_path
    and updates the hash_md5 parameter by opening the file from the zip and reading chunks of 4096 bytes."""
    with zip.ZipFile(zip_path, 'r') as archive:
        with archive.open(file_name) as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)


def get_hash(zip_path: str):
    """This method returns the md5 hash for the zip from the path given as parameter.
       The hash is created from the relative path of the files sorted and then,
       for each file in sorted order, hashing chunks of 4096 bytes."""
    hash_md5 = hashlib.md5()

    files_paths = []
    while 1:
        try:
            with zip.ZipFile(zip_path, "r") as archive:
                namesList = archive.namelist()
                for file in namesList:
                    if not file.endswith('/'):
                        files_paths.append(file)
            archive.close()
            break
        except Exception:
            pass

    files_list = get_files_list(zip_path)
    files_list.sort()
    for file in files_list:
        hash_md5.update(file.encode('UTF-8'))

    files_paths.sort()
    for file in files_paths:
        md5(zip_path, file, hash_md5)

    return hash_md5.hexdigest()


def get_files_list(zip_path: str):
    """This method returns a list with all the files relative path of zip at the path given as parameter
    The paths returned have a specific syntax in order to be correlate with other locations structures."""
    files_list = []
    while 1:
        try:
            with zip.ZipFile(zip_path, "r") as archive:
                for file_path in archive.namelist():
                    files_list.append(file_path)
            return files_list
        except Exception:
            pass


def get_last_modification_date_of_file(zip_path: str, file: str):
    """This method returns the last modification date of the file given as parameter of the zip at zip_path parameter
    It has a specific format in order to be correlate with other locations structures."""
    with zip.ZipFile(zip_path, "r") as archive:
        year, month, day, hours, minutes, seconds = archive.getinfo(file).date_time
        if month < 10:
            month = '0' + str(month)
        if day < 10:
            day = '0' + str(day)
        if hours < 10:
            hours = '0' + str(hours)
        if minutes < 10:
            minutes = '0' + str(minutes)
        if seconds < 10:
            seconds = '0' + str(seconds)
        # 2021-02-07 14:12:18
        return f"{year}-{month}-{day} {hours}:{minutes}:{seconds}"


def get_files_with_hash(zip_path):
    """This method returns a list of lists where
    the first element in each list is a file relative path from the zip (similar to get files list)
    and the second element is that file's hash."""
    files_list = []
    with zip.ZipFile(zip_path, "r") as archive:
        for file_path in archive.namelist():

            if not file_path.endswith('/'):
                hash_md5 = hashlib.md5()
                md5(zip_path, file_path, hash_md5)
                file_hash = hash_md5.hexdigest()
            else:
                file_hash = "directory"
            files_list.append([file_path, file_hash])
    return files_list


def copy_to_storage(zip_path: str, file: str):
    """This method copies the file given as parameter from the zip at the path given as parameter to the storage
    If the file is a folder, it copies the files inside it."""
    file = file.replace("/", "\\")
    if file.endswith('\\'):
        file = file.removesuffix('\\')
        if not os.path.exists(storage_path + '\\' + file):
            os.mkdir(storage_path + '\\' + file)
    else:
        with zip.ZipFile(zip_path, "r") as archive:
            for file_path in archive.namelist():
                if file_path.replace("/", "\\") == file:
                    archive.extract(file_path, storage_path)
                    return


def copy_from_storage(zip_path: str, file: str):
    """This method copies the file given as parameter from the zip at zip_path parameter from the storage.
    If the file is a folder, it copies the files inside it."""
    path = storage_path + '\\' + file

    archive = zip.ZipFile(zip_path, "a")
    if file in archive.namelist():
        archive.close()
        delete_file(zip_path, file)
        archive = zip.ZipFile(zip_path, "a")

    archive.write(path, file, zip.ZIP_DEFLATED)


def delete_file(zip_path: str, file: str):
    """This method deletes the file given as parameter
    from the zip at zip_path given as parameter
    If the file is a folder, it deletes all the the files inside it."""
    s = zip_path.split('\\')
    old_zip_path = zip_path.removesuffix(s[len(s) - 1])

    os.rename(zip_path, old_zip_path + "old.zip")
    old = zip.ZipFile(old_zip_path + "old.zip", 'r')
    new = zip.ZipFile(zip_path, 'w')

    for item in old.infolist():
        buffer = old.read(item.filename)
        if not item.filename.startswith(file):
            new.writestr(item, buffer)

    old.close()
    os.remove(old_zip_path + "old.zip")
    new.close()
