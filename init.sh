#!/bin/bash

_USERNAME="$1"
_PASSWORD="$2"
_MIRROR_BASE="https://$_USERNAME:$_PASSWORD@repos.archlinux.org"
_ARCH='x86_64'
_CACHE_DIR="/var/cache/pactor/"
_ANNOUNCE_URL="http://announce.archlinux.life:8002/announce"

if [[ ! -z $SUDO_USER ]]; then
	_SEEDBOX_LOCATION="~/Downloads/torrents"

	mkdir -p "/home/$SUDO_USER/pactor_torrents"
fi

rm -rf "$_CACHE_DIR/"
mkdir -p "$_CACHE_DIR/"

repos=( "core" "extra" "community" "multilib" )
for repo in "${repos[@]}"
do
	# This matches existing mirror structures:
	mkdir -p "$_CACHE_DIR/$repo/os/$_ARCH"

	# But ideally separating things would make listing more clean:
	# mkdir -p "$_CACHE_DIR/$_ARCH/databases/$repo"
	# mkdir -p "$_CACHE_DIR/$_ARCH/packages/$repo"
	# mkdir -p "$_CACHE_DIR/$_ARCH/torrents/$repo"

	# Grab the database, (+archive, +signature)
	wget "$_MIRROR_BASE/$repo/os/$_ARCH/$repo.db" --output-document="$_CACHE_DIR/$repo/os/$_ARCH/$repo.db"
	wget "$_MIRROR_BASE/$repo/os/$_ARCH/$repo.db.tar.gz" --output-document="$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.tar.gz"
	wget "$_MIRROR_BASE/$repo/os/$_ARCH/$repo.db.sig" --output-document="$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.sig" || rm -f "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.sig"

	# Generate torrents for them
	python -m pactor torrent --workdir $_CACHE_DIR --file "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db" --announce $_ANNOUNCE_URL --outfile "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.torrent"
	python -m pactor torrent --workdir $_CACHE_DIR --file "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.tar.gz" --announce $_ANNOUNCE_URL --outfile "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.tar.gz.torrent"

	# Usually there's no signature for the .db, so we skip it
	if [ -f "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.sig" ]; then
		python -m pactor torrent --workdir $_CACHE_DIR --file "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.sig" --announce $_ANNOUNCE_URL --outfile "$_CACHE_DIR/$repo/os/$_ARCH/$repo.db.sig.torrent"
	fi
done

# Get some packages that were meant for updating:
for url in $(pacman -Syup)
do
	if [[ "$url" =~ ^http.* ]]; then
		# Ugly Hack, would be nicer to grab the repo from pacman somehow
		for repo in "${repos[@]}"
		do
			if [[ "$url" == */$repo/* ]]; then
				wget "$url" --output-document="$_CACHE_DIR/$repo/os/$_ARCH/$(basename $url)"
				wget "$url.sig" --output-document="$_CACHE_DIR/$repo/os/$_ARCH/$(basename $url).sig"

				python -m pactor torrent --workdir $_CACHE_DIR --file "$_CACHE_DIR/$repo/os/$_ARCH/$(basename $url)" --announce $_ANNOUNCE_URL --outfile "$_CACHE_DIR/$repo/os/$_ARCH/$(basename $url).torrent"
				python -m pactor torrent --workdir $_CACHE_DIR --file "$_CACHE_DIR/$repo/os/$_ARCH/$(basename $url).sig" --announce $_ANNOUNCE_URL --outfile "$_CACHE_DIR/$repo/os/$_ARCH/$(basename $url).sig.torrent"

				if [[ ! -z $SUDO_USER ]]; then
					cp "$_CACHE_DIR/$repo/os/$_ARCH/$(basename $url).torrent" "/home/$SUDO_USER/pactor_torrents/$(basename $url).torrent"
					chown $SUDO_USER:$SUDO_USER "/home/$SUDO_USER/pactor_torrents/$(basename $url).torrent"
				fi
			fi
		done
	fi
done

# Make sure it's accessible to your test user
# as we don't want to run API's as root (preferably)
if [[ ! -z $SUDO_USER ]]; then
	chown -R $SUDO_USER:$SUDO_USER $_CACHE_DIR
fi

tree $_CACHE_DIR