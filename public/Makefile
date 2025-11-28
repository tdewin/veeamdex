

make:
	rsvg-convert favicon.svg -o favicon.png
	rsvg-convert favicon.svg -o favicon_16.png -w 16 -h 16
	rsvg-convert favicon.svg -o favicon_32.png -w 32 -h 32
	rsvg-convert favicon.svg -o favicon_64.png -w 64 -h 64
	rsvg-convert favicon.svg -o favicon_128.png -w 128 -h 128
	cp favicon.png apple-touch-icon.png
	cp favicon.png apple-touch-icon-precomposed.png
makeicon:
	podman run --rm -it --name convert -v ./:/src --workdir /src --entrypoint /bin/sh python -c "pip install Pillow;./ico.py -i favicon.png -o favicon.ico"
