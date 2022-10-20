# Script to create release files
# Requires change of release version manually
import os
import zipfile
from pathlib import Path
from zipfile import ZIP_DEFLATED

releaseVer = "0.2.0"
releaseName = "creoBOMtool_"

rootPath = Path(os.curdir).parent
os.chdir(rootPath)
writeDir = rootPath / Path("releases/")

writeName = releaseName + releaseVer + ".zip"
writePath = writeDir / Path(writeName)

with zipfile.ZipFile(str(writePath), "w", ZIP_DEFLATED) as archive:
    archive.write("README.md")
    archive.write("LICENSE")
    archive.write("requirements.txt")
    archive.write("logs")

    for file in rootPath.glob("*.py"):
        archive.write(file, arcname=file.relative_to(rootPath))

    # Import libary files
    libPath = rootPath / Path("lib")
    for file in libPath.rglob("*.py"):
        archive.write(file, arcname=file.relative_to(rootPath))

    # Import export path files
    exportPath = rootPath / Path("exports")
    for file in exportPath.rglob("*"):
        if "engine" in file.name:
            archive.write(file, arcname=file.relative_to(rootPath))

    # Import image files
    imagesPath = rootPath / Path("creo_images/ex_images")
    for file in imagesPath.rglob("*"):
        archive.write(file, arcname=file.relative_to(rootPath))

    # Import bom import path files
    bomImportPath = rootPath / Path("creo_bom_imports")
    for file in bomImportPath.rglob("*"):
        if "engine" in file.name:
            archive.write(file, arcname=file.relative_to(rootPath))
