<img src="buildfrom/sources/assets-all/logo_full.png">

## TODOS:
- Fix release archive
- Fix account support (Microsoft makes it SO HARD)

## Docs

### How to use

[See the main page](.)

### Build dependencies
- jq

### Building

Clone this repo with

```sh
git clone https://api.glitch.com/git/quickcraft && cd quickcraft
```

Build with
./buildfrom/release.sh <\version> <\rootUrl> <\name (of builder)> <\channel>
I.e.

```sh
./buildfrom/release.sh 2.0.0 https://yourwebsite.com/quickcraft yourwebsite release
```

### Info

#### release_index.json format

```typescript
type format = {
  releases: {
    version: "major.minor.patch";
    win: "windows download url (zip)";
    linux: "linux download url (tar.gz)";
    macos: "macos download url (tar.gz)";
    channel: "dev" | "stable";
  }[];
};
```

#### Release format

##### All

Contains an assets directory with the icons/most source code.

###### Direct dependencies

- Python3 (auto installed localy on windows, installed via package manager on linux, required to be already installed on macOS)
- minecraft_launcher_lib (Auto installed)
- pyqt6 (Auto installed)
- jpype (Auto installed)

###### release_manifest.json format

In assets, there is release_manifest.json. This is usedto tell the code info about the build.

```typescript
type manifest = {
  vendor: {
    rootUrl: "(the root url of the website that hosts the build releases, ie rootUrl/README.md)";
    name: "(The name of the vendor)";
  };
  platform: "win" | "linux" | "macos";
  version: "(version of release, major.minor.patch)";
  channel: "dev" | "stable";
};
```

##### Windows

Release is a .zip file. The main directory, (not assets) has the public entry points installer.ps1 (for installing to the local dir) and start.ps1 (for starting). The assets directory has installer.ps1 and start.ps1 (what the main directory calls), get-pip.py for installing pip for the downloaded python version, and add_shortcut.py for adding the windows shortcut.

###### Extra dependencies for platform

- pywin32

##### Linux

Release is a .tar.gz file. The main directory, (not assets) has the public entry points installer.sh (for installing to the local dir), and start.sh (for starting). The assets directory has installer.sh, start.sh (what the main directory calls), and shortcut.desktop.from as a template for the shortcut.

###### Extra dependencies for platform

- None

##### macOS

Release is a .tar.gz file. The main directory, (not assets) has the public entry points installer.sh (for installing to the local dir), and start.sh (for starting). The assets directory has installer.sh and start.sh (what the main directory calls).

(macOS support is untested and minimal).

###### Extra dependencies for platform

- None
