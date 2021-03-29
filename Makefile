help:
	@echo "LDP ARCHIVE MIRROR - $$(cat VERSION)"

dist-src:
	@rm -f docker/ldp-archive-mirror-*.tar.gz
	@python3 setup.py sdist -d docker

build-docker: dist-src
	@docker build -t ldp-archive-mirror docker

