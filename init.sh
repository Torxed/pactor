#!/bin/bash

# Do "pacman -Syu" and abort it, pick two packages.
# Add them to /etc/pacman.conf as two IgnorePkg = "<package"> entries.
# Add one of the packages full name to this variable:

package="gajim-1.8.3-1-any.pkg.tar.zst"

# .
# └── x86_64
#     └── databases
#         ├── community
#         │   ├── community.db
#         │   └── community.db.tar.gz

_USERNAME="$1"
_PASSWORD="$2"

mkdir -p /var/cache/pactor
cd /var/cache/pactor

rm -rf x86_64
mkdir -p x86_64/databases/core
mkdir -p x86_64/databases/extra
mkdir -p x86_64/databases/community
mkdir -p x86_64/databases/multilib

mkdir -p x86_64/packages/core
mkdir -p x86_64/packages/extra
mkdir -p x86_64/packages/community
mkdir -p x86_64/packages/multilib

mkdir -p x86_64/torrents/core
mkdir -p x86_64/torrents/extra
mkdir -p x86_64/torrents/community
mkdir -p x86_64/torrents/multilib

# Core
repo='core'
arch='x86_64'
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db" --output-document="./$arch/databases/$repo/$repo.db"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.tar.gz" --output-document="./$arch/databases/$repo/$repo.db.tar.gz"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.sig" --output-document="./$arch/databases/$repo/$repo.db.sig"
torf "./$arch/databases/$repo/$repo.db" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.torrent"
torf "./$arch/databases/$repo/$repo.db.tar.gz" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.tar.gz.torrent"
torf "./$arch/databases/$repo/$repo.db.sig" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.sig.torrent"

# Extra
repo='extra'
arch='x86_64'
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db" --output-document="./$arch/databases/$repo/$repo.db"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.tar.gz" --output-document="./$arch/databases/$repo/$repo.db.tar.gz"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.sig" --output-document="./$arch/databases/$repo/$repo.db.sig"
torf "./$arch/databases/$repo/$repo.db" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.torrent"
torf "./$arch/databases/$repo/$repo.db.tar.gz" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.tar.gz.torrent"
torf "./$arch/databases/$repo/$repo.db.sig" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.sig.torrent"

# Community
repo='community'
arch='x86_64'
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db" --output-document="./$arch/databases/$repo/$repo.db"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.tar.gz" --output-document="./$arch/databases/$repo/$repo.db.tar.gz"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.sig" --output-document="./$arch/databases/$repo/$repo.db.sig"
torf "./$arch/databases/$repo/$repo.db" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.torrent"
torf "./$arch/databases/$repo/$repo.db.tar.gz" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.tar.gz.torrent"
torf "./$arch/databases/$repo/$repo.db.sig" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.sig.torrent"

# Multilib
repo='multilib'
arch='x86_64'
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db" --output-document="./$arch/databases/$repo/$repo.db"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.tar.gz" --output-document="./$arch/databases/$repo/$repo.db.tar.gz"
wget "https://$_USERNAME:$_PASSWORD@repos.archlinux.org/$repo/os/$arch/$repo.db.sig" --output-document="./$arch/databases/$repo/$repo.db.sig"
torf "./$arch/databases/$repo/$repo.db" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.torrent"
torf "./$arch/databases/$repo/$repo.db.tar.gz" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.tar.gz.torrent"
torf "./$arch/databases/$repo/$repo.db.sig" -t http://announce.archlinux.life:8001/announce -o "./$arch/torrents/$repo/$repo.db.sig.torrent"


# Some debug packages
echo "http://ftp.lysator.liu.se/pub/archlinux/extra/os/x86_64/$package $(pwd)/x86_64/packages/extra/$package"
wget "http://ftp.lysator.liu.se/pub/archlinux/extra/os/x86_64/$package" -O"./x86_64/packages/extra/$package"
wget "http://ftp.lysator.liu.se/pub/archlinux/extra/os/x86_64/$package.sig" -O"./x86_64/packages/extra/$package.sig"

torf "./x86_64/packages/extra/$package" -t http://announce.archlinux.life:8001/announce -o "./x86_64/packages/extra/$package.torrent"
torf "./x86_64/packages/extra/$package.sig" -t http://announce.archlinux.life:8001/announce -o "./x86_64/packages/extra/$package.sig.torrent"

cp ./x86_64/packages/extra/$package* /home/anton/Downloads/
chown -R anton: /home/anton/Downloads/$package*

rm ./x86_64/packages/extra/$package*
