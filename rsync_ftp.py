import hashlib
import os
import time
import ftputil

storage_path: str = "E:\\Info\\FACULTATE\\ANUL_3\\PYTHON\\PROIECT\\Advanced RSync\\storage"

_temp_path: str = "E:\\Info\\FACULTATE\\ANUL_3\\PYTHON\\PROIECT\\Advanced RSync\\_temp\\_temp.tmp"
"""this file is used to copy from the ftp server to it when trying to read bytes or other functionalities"""


def extract_path(URL: str):
    """This method returns the path of the server from the ftp location url given as argument from the command line"""
    return '/' + URL.split('/', 1)[1]


def extract_connection_information(URL: str):
    """This method returns the hostname, username and password tuple from the ftp location url given as parameter
    from the command line"""
    split1 = URL.split('@')
    hostname = split1[1].split('/')[0].split('/')[0]
    split2 = split1[0].split(':')
    username, password = split2[0], split2[1]
    return hostname, username, password


def get_connection(URL: str):
    """This method returns a FTPHost connection from the ftp url given as parameter form the command line
    OR None if that location is invalid"""
    hostname, username, password = extract_connection_information(URL)
    try:
        ftp = ftputil.FTPHost(hostname, username, password)
        return ftp
    except BaseException:
        return None


def ftp_exists(URL: str):
    """This method returns a boolean checking if the ftp location url
    given as parameter from the command line is valid."""
    con = get_connection(URL)
    if con is None:
        return False
    else:
        con.close()
        return True


def md5(file_path, hash_md5, a_host):
    """This method receives a relative path in file_path from the ftp server,the FTPHost parameter given at a_host
       and updates the hash_md5 parameter by downloading the file and reading chunks of 4096 bytes."""
    f = open(_temp_path, "w+")
    f.truncate()
    f.close()
    a_host.download(file_path, _temp_path)
    with open(_temp_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    f = open(_temp_path, "w+")
    f.truncate()
    f.close()


def get_hash(ftp_url: str):
    """This method returns the md5 hash for the ftp server at the url given as parameter.
    The hash is created from the relative path of the files sorted and then,
    for each file in sorted order, hashing chunks of 4096 bytes."""
    hash_md5 = hashlib.md5()

    server = get_connection(ftp_url)
    path = extract_path(ftp_url)

    files_paths = []
    for root, dirs, files in server.walk(path):
        if root == '/':
            root = ''
        for file in files:
            files_paths.append(root + '/' + file)

    files_list = get_files_list(ftp_url)
    files_list.sort()
    for file in files_list:
        hash_md5.update(file.encode('UTF-8'))

    files_paths.sort()
    for file in files_paths:
        md5(file, hash_md5, server)

    return hash_md5.hexdigest()


def get_files_list(ftp_url):
    """This method returns a list with all the files relative path of the the ftp server at the url given as parameter
    The paths returned have a specific syntax in order to be correlate with other locations structures."""
    server = get_connection(ftp_url)
    path = extract_path(ftp_url)
    files_list = []

    for root, dirs, files in server.walk(path):
        prefix: str = root.removeprefix(path)
        prefix = prefix.replace('\\', '/')
        for file in files:
            if len(prefix) > 0:
                files_list.append(prefix + '/' + file)
            else:
                files_list.append(file)
        for directory in dirs:
            if len(prefix) > 0:
                files_list.append(prefix + '/' + directory + '/')
            else:
                files_list.append(directory + '/')
    return files_list


def get_last_modification_date_of_file(ftp_url: str, filePath: str):
    """This method returns the last modification date of the file given as parameter of the ftp server at the url
    It has a specific format in order to be correlate with other locations structures."""
    server = get_connection(ftp_url)
    # Get file's Last modification time stamp only in terms of seconds since epoch
    modTimesinceEpoc = server.path.getmtime(filePath)
    # Convert seconds since epoch to readable timestamp
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))


def get_files_with_hash(ftp_url):
    """This method returns a list of lists where
    the first element in each list is a file relative path from the server path( similar to get files list)
    and the second element is that file's hash."""
    server = get_connection(ftp_url)
    path = extract_path(ftp_url)
    files_list = []
    for root, dirs, files in server.walk(path):
        prefix: str = root.removeprefix(path)
        prefix = prefix.replace('\\', '/')
        if root == '/':
            root = ''
        for file in files:
            hash_md5 = hashlib.md5()
            md5(root + '\\' + file, hash_md5, server)
            file_hash = hash_md5.hexdigest()
            if len(prefix) > 0:
                files_list.append([prefix + '/' + file, file_hash])
            else:
                files_list.append([file, file_hash])
        for directory in dirs:
            if len(prefix) > 0:
                files_list.append(
                    [prefix + '/' + directory + '/', "directory"])
            else:
                files_list.append([directory + '/', "directory"])
    return files_list


def copy_to_storage(ftp_url: str, file: str):
    """This method copies the file given as parameter from the ftp server at the url given as parameter to the storage
    If the file is a folder, it copies the files inside it."""
    server = get_connection(ftp_url)
    remote_path = extract_path(ftp_url)

    remote_path = remote_path + file
    remote_path = remote_path.removesuffix('/')

    if server.path.isfile(remote_path):
        local_path = storage_path.replace('\\', '/') + '/' + file
        file_split = local_path.split("/")
        file_name = file_split[len(file_split) - 1]
        os.makedirs(local_path.removesuffix('/' + file_name),
                    exist_ok=True)  # create directory tree needed for the file
        server.download(remote_path, local_path)

    if server.path.isdir(remote_path):
        local_path = storage_path.replace('\\', '/') + remote_path
        os.makedirs(local_path)


def copy_from_storage(ftp_url: str, file: str):
    """This method copies the file given as parameter from from the ftp server
    at the url given as parameter from the storage.
    If the file is a folder, it copies the files inside it."""
    server = get_connection(ftp_url)
    ftp_path = extract_path(ftp_url)

    local_path = storage_path + '\\' + file

    if os.path.isfile(local_path):
        remote_path = ftp_path + file
        file_split = remote_path.split("/")
        file_name = file_split[len(file_split) - 1]
        if remote_path.removesuffix('/' + file_name) != '':
            server.makedirs(remote_path.removesuffix('/' + file_name),
                            exist_ok=True)  # create directory tree needed for the file
        server.upload(local_path, remote_path)

    if os.path.isdir(local_path):
        remote_path = ftp_path + file.removesuffix('/')
        if not server.path.exists(remote_path):
            server.mkdir(remote_path)


def delete_file(ftp_url: str, file: str):
    """This method deletes the file given as parameter
    from the ftp server at the url given as parameter
    If the file is a folder, it deletes all the the files inside it."""
    server = get_connection(ftp_url)
    ftp_path = extract_path(ftp_url)

    path = ftp_path + file
    path = path.removesuffix('/')
    if server.path.isfile(path):
        server.remove(path)
    if server.path.isdir(path):
        server.rmtree(path)
