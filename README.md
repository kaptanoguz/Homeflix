# Lumbuz

**Your own little Netflix, running at home.**

*Lumbuz* is the Turkish word for a ship's porthole: a small round window onto the world. (It used to be called Homeflix.)

You have a computer full of movies and series. Lumbuz turns it into a cozy streaming service for the whole house: open it on the TV in the living room, on your phone in bed, or in any browser, and pick up right where you left off. No accounts, no subscriptions, no cloud. Everything stays on your own computer.

![The Lumbuz home page](docs/screenshots/home.jpg)

## Get it

Grab the latest version from the [Releases page](https://github.com/kaptanoguz/Lumbuz/releases/latest). There is a ready-to-run download for **Windows**, **macOS** (Apple Silicon and Intel) and **Linux**, plus the **Lumbuz TV** app for Android TV and Android phones. You don't need to install Python or anything else.

Then:

1. Open Lumbuz and go to **Settings → Library** to pick your movie and series folders.
2. Give it a minute. Lumbuz finds posters, descriptions, cast and ratings for everything on its own.
3. On your other devices, scan the QR code in **Settings → Other devices**, or install the TV app, which finds the server by itself.

That's it. Grab the popcorn.

## What's inside

### Your library, looking its best

Every movie and series gets a proper poster, backdrop, description, cast and rating. Sequels are grouped into collections automatically (all the John Wicks together, all the Harry Potters together), and episodes of the same show spread over different folders end up in one place.

![Movies](docs/screenshots/movies.jpg)

![Collections](docs/screenshots/collections.jpg)

Open any title for the details: which streaming services also carry it, the rest of its collection, similar titles, and a download button to take it with you.

![A movie's details](docs/screenshots/detail.jpg)

![A series with its episodes](docs/screenshots/series-detail.jpg)

### It just plays

MKV, AVI and other files that browsers normally refuse are converted on the fly, so they simply start playing. You can switch between the dubbed and original audio, and subtitles are easy: files next to the video, subtitles inside the video, or a search on the internet. If a foreign film has no Turkish subtitle, Lumbuz goes and finds one for you.

Stop a movie on your phone and continue on the TV. When you pause, Lumbuz shows you who's in the scene and what to watch next. When an episode ends, the next one starts by itself.

### Online

Want to watch something you don't have? The **Online** tab shows popular and trending movies and series (the list comes from TMDb) and plays them over the internet through frameXTV's player. Nothing is downloaded. Titles you already own are marked *In library*, and your progress is remembered just like with your own files.

![The Online tab](docs/screenshots/online.jpg)

### Live TV

More than 60 free channels, straight from the broadcasters' own websites: national channels, news, sports, documentaries, kids and music. Channels that go off the air quietly disappear from the list.

![Live TV](docs/screenshots/live.jpg)

### Music Videos

Point Lumbuz at a folder of music videos and you get a music channel of your own. Browse by artist, shuffle everything, or let one video roll into the next. Each artist gets a page with a photo and a short bio.

![Music Videos](docs/screenshots/clips.jpg)

![An artist page](docs/screenshots/artist.jpg)

Pause a video to see the song's album, year and genre, more from the same artist, and similar videos.

![The pause screen of a music video](docs/screenshots/clip-pause.jpg)

### Kids Zone

A bright, friendly corner with only cartoons, animations and family movies, and a *Surprise Movie!* button for when nobody can decide.

![Kids Zone](docs/screenshots/kids.jpg)

### Find anything fast

Press `/` anywhere and start typing. Search doesn't mind missing Turkish letters, so "sirin" finds "Şirin". It looks in your library and in the Online catalog at the same time. Can't decide at all? The shuffle button picks a random movie, filtered by genre and rating if you like.

![Search](docs/screenshots/search.jpg)

### On every screen

Lumbuz works on a computer, a phone, a tablet and a TV. On phones the menu moves to the bottom, and on Android TV the remote's arrows, OK and play/pause buttons do what you expect. Everyone in the house keeps their own *Continue Watching* and *My List*.

![Lumbuz on a phone](docs/screenshots/phones.jpg)

## Settings

Everything is in one place, with a big panel that's easy to use from the couch with a TV remote.

| | |
|---|---|
| ![Library settings](docs/screenshots/settings-library.jpg) | ![Subtitle settings](docs/screenshots/settings-subs.jpg) |
| **Library:** as many movie, series and music video folders as you like, picked with a folder browser. | **Subtitles:** size and background, and whether Turkish subtitles turn on by themselves. |
| ![Random movie settings](docs/screenshots/settings-random.jpg) | ![Download settings](docs/screenshots/settings-downloads.jpg) |
| **Random movie:** which genres and minimum rating the shuffle button picks from. | **Downloads:** a speed limit, so a download never slows down someone who's watching. |
| ![Other devices](docs/screenshots/settings-devices.jpg) | ![Language](docs/screenshots/settings-lang.jpg) |
| **Other devices:** a QR code and the address to open on your phone, tablet or TV. | **Language:** Lumbuz speaks English and Turkish. |

## The TV app

**Lumbuz TV** is a small Android app for TVs and phones. Install it, open it, and it finds the Lumbuz server on your Wi-Fi by itself. If you have more than one, it asks which one to use. You'll find it on the [Releases page](https://github.com/kaptanoguz/Lumbuz/releases), and the details are in [android-tv/README.md](android-tv/README.md).

## Good to know

- **ffmpeg** makes MKV/AVI playback and built-in subtitles work. Install it once with `winget install ffmpeg` (Windows), `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux).
- **Movie details** come from TMDb. If you'd like to use your own keys for TMDb, OMDb or OpenSubtitles (for subtitle search), put them in a `secrets.json` file. [`secrets.example.json`](secrets.example.json) shows how it looks.
- **Your data** (library, posters, watch history) is stored on your computer: `%APPDATA%\Lumbuz` on Windows, `~/Library/Application Support/Lumbuz` on macOS, `~/.local/share/lumbuz` on Linux. If you used it back when it was called Homeflix, your library stays in the old `Homeflix` folder and simply keeps working.
- Lumbuz is meant for your home network. Other devices connect to `http://<your-computer's-address>:5000`, which Settings shows you.

## Running from source

If you'd rather run the code directly on Linux, all you need is Python 3. The first run sets everything up by itself.

```bash
./run.sh              # opens in its own window
./run.sh --browser    # opens in your browser
./run.sh --headless   # just the server, for a computer without a screen
```

Lumbuz uses port 5000. If something else on your computer already uses it, pick another one with the `LUMBUZ_PORT` setting, for example `LUMBUZ_PORT=8080 ./run.sh`.

## Contact

Questions, ideas or just want to say hi? Write to [info@esoramaritime.com](mailto:info@esoramaritime.com) or visit [esoramaritime.com](https://esoramaritime.com).

## License

Lumbuz is free software under the [GNU General Public License v3.0](LICENSE). Use it, change it, share it. If you share a changed version, share its source code under the same license too.
