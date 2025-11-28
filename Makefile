IMG=vue-build
MAP=-v ./:/project
PROJECT=veeamdex
PROJECTDIR=project

.PHONY: dist

most: run
static: dist statictest

build:
	podman build -t $(IMG)  .
run:
	podman run -p 5173:5173 --rm -it --name veeamdex --entrypoint sh $(MAP) --workdir /$(PROJECTDIR) $(IMG) -c 'npm run dev -- --host 0.0.0.0'
dist:
	mkdir -p docs
	podman run -p 5173:5173 --rm -it --name veeamdex --entrypoint sh $(MAP) --workdir /$(PROJECTDIR) $(IMG) -c 'npm run build -- --outDir docs'
statictest:
	podman run -p 8080:80 -v ./docs:/usr/share/nginx/html --rm -it --name veeamdex-nginx nginx
