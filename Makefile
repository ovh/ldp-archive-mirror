help:
	@echo "LDP ARCHIVE MIRROR - $$(cat VERSION)"

dist-src:
	@rm -f docker/ldp-archive-mirror-*.tar.gz
	@python3 setup.py sdist -d docker

build-docker: dist-src
	@docker build --pull --build-arg UID=$$(id -u) --build-arg USER_NAME=$$(whoami) --build-arg GID=$$(id -g) --build-arg GROUP_NAME=$$(id -g -n $$(whoami)) -t ldp-archive-mirror docker
