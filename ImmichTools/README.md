## createSubdirsForAlbums.py
This script gets the list of albums from immich and creates subdirectories for them. This makes it easy to upload media files later.
### Usage
1. CD to the directory and run the script using the command below<br/>
`python createSubdirsForAlbums.py --dir PATH --url URL`<br/>
`python createSubdirsForAlbums.py --dir PATH --url URL --dry-run`<br/>
### Additional parameters/ arguments
| | Description |
| ----------- | ----------- |
| --dir \"path\" | This specifies the directory |
| --url \"url\" | This would contain the immich albums endpoint with the api key |
| --dry-run | Add this to get a preview of what might happen.<br/>No changes will be made when this is added |
