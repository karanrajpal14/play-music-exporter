# Google Play Music Exporter

I don't really fancy YouTube Music's UI/UX and the negligence of Google Play Music left a bitter taste in my mouth which led to me writing this script over the weekend. It's still a bit rough around the edges but it does get the job done. Should you find any problems with the script, feel free to open an issue and I'll do my best to fix it.

This script alows you to make use of [gmusicapi][1] - an unoffocial Google Play Music API to export all your uploaded and purchased music. My main intention behind building this is to export all my tracks before they sunset the service.

This script does a few basic things such as:

- Downloads all (uploaded/purchased) tracks from your library using
- Adds basic ID3 tags to the tracks using [eyeD3][2] (file returned by Google does not have any metadata embedded)
- Delete's downloaded tracks from your library to make consecutive runs faster
- Exports a JSON of your current library's metadata and a list of IDs for all the downloaded tracks. Both can be found under the `logs/` directory.

## Requirements
- [gmusicapi][1]
- [eyeD3][2]

## Instructions

1. Clone the repository
2. Install the requirements using `pip install -r requirements.txt` preferably within a virtual environment
3. Rename `.env.sample` to `.env`
4. Run the script and follow the instructions on the console to authenticate using OAuth.
5. The script will display a set of devices in the console that are tied to your account. Select any one of the devices that you use Play Music (preferably an Android device) on and paste the ID in the `.env` file.

    For example, if your registered devices look like this:

    ```json
    [
        {
            "kind": "...",
            "id": "0x12a34bc5678def9g",
            "friendlyName": "...",
            "type": "ANDROID",
            "lastAccessedTimeMs": "..."
        },
        ...
        ...
        ...
    ]
    ```

    Then, your `.env` file will look like this:
    ```
    DEVICE_ID=12a34bc5678def9g
    ```
    **Ensure that you omit the '0x' prefix**

6. **Re-run the script after setting up the `.env` file to begin exporting your library**

## Note:

1. You will see a warning **Lame tag CRC check failed** when trying to save the ID3 tags to a file. You can ignore it for now as I couldn't find a way to fix it (any help would be appreciated). **This does not affect the saving of the metadata in any way.**
2. If you don't want the track to be removed from your library, set the `POST_DOWNLOAD_DELETE` flag to `False` **(which it is by default)**.
3. **The ID3 tags that are added using this script are there just to help music players display basic metadata. You should use more advanced programs such as [MusicBrainz Picard][5] to clean them up for long-term use. Also, none of the tracks will have any album-art (for now).**

## Credits

- [Simon Weber][3] who built [gmusicapi][1]
- [nicfit][4] who built [eyeD3][2]
- All the developers who help maintain these libraries

[1]: https://github.com/simon-weber/gmusicapi
[2]: https://github.com/nicfit/eyeD3
[3]: https://github.com/simon-weber
[4]: https://github.com/nicfit
[5]: https://musicbrainz.org/