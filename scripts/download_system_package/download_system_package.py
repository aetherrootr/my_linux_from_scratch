import hashlib
import os
import shutil
import tempfile
import tomllib

import wgetter

LFS_DIR = os.path.join(os.environ.get("LFS", "/mnt/lfs"), "sources")
PROJECT_ROOT = os.getcwd()
PACKAGE_LIST_PATH = os.path.join(PROJECT_ROOT, "system_package_list.toml")
PATCH_LIST_PATH = os.path.join(PROJECT_ROOT, "package_patch_list.toml")


def download_package(package_name: str, url: str, md5sum: str):
    with tempfile.TemporaryDirectory() as tmp:
        filename = wgetter.filename_from_url(url)
        tmp_file_path = os.path.join(tmp, filename)
        dst_file_path = os.path.join(LFS_DIR, filename)
        if os.path.exists(dst_file_path):
            print(f'{dst_file_path} already exists, skip download.')
            return

        wgetter.download(url, tmp)

        file_hash = hashlib.md5()
        with open(tmp_file_path, "rb") as f:
            while chunk := f.read(8192):
                file_hash.update(chunk)

        if file_hash.hexdigest() != md5sum:
            raise ValueError(
                f'{package_name} md5 sum verification failed, '
                f'expect {md5sum}, actual: {file_hash.hexdigest()}',
            )

        shutil.move(tmp_file_path, dst_file_path)


def parse_package_dict(file_name):
    with open(file_name, "rb") as f:
        data = tomllib.load(f)
        return data


if __name__ == "__main__":
    # Download package
    print("====Donwload system package====")
    package_dict = parse_package_dict(PACKAGE_LIST_PATH)
    total_package_count = len(package_dict)
    count = 0

    for package_name, info in package_dict.items():
        count += 1
        print(f"({count}/{total_package_count}) {package_name}")
        download_package(package_name, info.get("url"), info.get("md5"))

    # Download patch
    print("====Donwload system package patch====")
    patch_dict = parse_package_dict(PATCH_LIST_PATH)
    total_package_count = len(patch_dict)
    count = 0

    for patch_name, info in patch_dict.items():
        count += 1
        print(f"({count}/{total_package_count}) {patch_name}")
        download_package(patch_name, info.get("url"), info.get("md5"))
