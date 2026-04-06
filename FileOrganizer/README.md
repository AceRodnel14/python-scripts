## renameSubdirs.py
This script can be used to rename subdirectories that follow this format: <br/>
`'this that there random string-yyyymmdd...'`<br/>
will become<br/>
`'this—that—there—random string'`
### Usage
1. CD to the directory and run the script using the command below<br/>
`python renameSubdirs.py --dir PATH`<br/>
`python renameSubdirs.py --dir PATH --dry-run`<br/>
### Additional parameters/ arguments
| | Description |
| ----------- | ----------- |
| --dir \"path\" | This specifies the parent directory where you want to rename subdirectories |
| --dry-run | Add this to get a preview of what might happen.<br/>No changes will be made when this is added |

## initMirrorSubdirs.py
This script can be used to check the source directory.<br/>Get the list of subdirectories and try to create empty<br/>subdirectories in the destination directory.
### Usage
1. CD to the directory and run the script using the command below<br/>
`python initMirrorSubdirs.py --src PATH1 --dst PATH2`<br/>
`python initMirrorSubdirs.py --src PATH1 --dst PATH2 --dry-run`<br/>
### Additional parameters/ arguments
| | Description |
| ----------- | ----------- |
| --src \"path\" | This specifies the directory where the subdirectory list will be taken |
| --dst \"path\" | This specifies the directory where the empty subdirectories will be created |
| --dry-run | Add this to get a preview of what might happen.<br/>No changes will be made when this is added |

## categorizeFiles.py
This script can be used to check the source directory.<br/>Try to come up with a pattern for the files in that directory<br/>,and if --move is present, try to create subdirectories based on the pattern. <br/>This supports concurrency but only when scanning files not moving them, to be safe.
### Usage
1. CD to the directory and run the script using the command below<br/>
`python categorizeFiles.py --dir PATH --separator '__'`<br/>
`python categorizeFiles.py --dir PATH --separator '__' --parallel-scan`<br/>
`python categorizeFiles.py --dir PATH --separator '__' --parallel-scan --move`<br/>
### Additional parameters/ arguments
| | Description |
| ----------- | ----------- |
| --dir \"path\" | This specifies the directory |
| --separator \"__\" | This defines the separator or the characters that separate the <br/>possible name and the hash or random string |
| --parallel-scan | Add this to enable concurrent scanning. By default it uses 80% of CPUs |
| --workers PERCENT | This defines the number of CPUs to use, in percentage |
| --move | This will enable the move functionality. This will move the files to the <br/>categories/ subdirectories it came up with |

## decategorizeFiles.py
This script is the reverse of categorizeFiles.py. This checks the subdirectories <br/>and try to move the files to the parent directory
### Usage
1. CD to the directory and run the script using the command below<br/>
`python decategorizeFiles.py --dir PATH`<br/>
`python decategorizeFiles.py --dir PATH --dry-run`<br/>
### Additional parameters/ arguments
| | Description |
| ----------- | ----------- |
| --dir \"path\" | This specifies the directory |
| --dry-run | Add this to get a preview of what might happen.<br/>No changes will be made when this is added |
