# MediaMetadataUpdater

This script automates the updating of .jpeg, .jpg, .mp4 or any media files. It uses exiftool.exe to update the media files. The python script focuses on checking provided folders (absolute path) and processes files that matches the required naming convention.

### Supported Patterns
\<username\>=_=YYYY-MM-DDThhmmss.msZ\<slug\><br/>
\<username\>__YYYY-MM-DDThhmmss.msZ\<slug\><br/>
YYYY-MM-DD hh.mm.ss \<image id\><br/>
YYMMDD \<image id\><br/>
YYMMDD-\<image id\><br/>

## Prerequisites
1. Install textual package by using the command below<br/>
`pip install -r requirements.txt`<br/>
2. Download the 32-bit or 64-bit Windows Executable from the ExifTool home page.<br/>
3. Extract the "exiftool-13.41_xx" folder from the ".zip" file, and place it in the folder where MediaMetadataUpdater.py is saved.
4. Rename "exiftool(-k).exe" to "exiftool.exe".

## MediaMetadataUpdater.py 
### Usage
1. Update line 9 in MediaMetadataUpdater.py<br/>Update the folders variable
2. CD to the directory and run the script using the command below<br/>
`python MediaMetadataUpdater.py`<br/>
`python MediaMetadataUpdater.py --dir /downloads --verbose --workers 50`<br/>
### Additional parameters/ arguments
| | Description |
| ----------- | ----------- |
| --dir \"path or paths\" | Add this to overwrite the folder list already<br/>provided inside the python script |
| --verbose | Add this to get logs for each files processed, <br/>instead of progress bar |
| --workers \<int\> | Add this with an integer for the percent of <br/>CPU cores to use for this script. <br/>Default is 80 or 80% |
| --workers all | Add this with \'all\' to use all available CPU cores<br/>Default is 80 or 80% |

## CheckMediaMetadata.py
This script can be used to pre-check the files in certain folder and it will list files that match the defined patterns.
### Usage
1. CD to the directory and run the script using the command below<br/>
`python CheckMediaMetadata.py --dir /downloads`<br/>
### Required parameters/ arguments
| | Description |
| ----------- | ----------- |
| --dir \"path or paths\" | Comma delimited list of directories<br/>THIS IS NOT RECURSIVE |

## CheckMediaMetadataUI.py
This script can be used to manually check if files match any pattern (builtin or in pattern.json)
### Usage
1. CD to the directory and run the script using the command below<br/>
`python CheckMediaMetadataUI.py`<br/>


## ConvertJpgToWebp.py
This script can be used to convert JPG files to WEBP to be able to update Image metadata.
### Usage
1. CD to the directory and run the script using the command below<br/>
`python ConvertJpgToWebp.py 「comma delimited list」`<br/>

## MediaMetadataUpdaterByFolder.py
This script can be used to bulk update files and update the image or video date metadata based on the directory it is in. It should follow YYMMDD format.
### Usage
1. CD to the directory and run the script using the command below<br/>
`python MediaMetadataUpdaterByFolder.py --dir /downloads --workers 50`<br/>
### Additional parameters/ arguments
| | Description |
| ----------- | ----------- |
| --dir \"path or paths\" | Comma delimited list of directories |
| --workers \<int\> | Add this with an integer for the percent of <br/>CPU cores to use for this script. <br/>Default is 80 or 80% |
| --workers all | Add this with \'all\' to use all available CPU cores<br/>Default is 80 or 80% |