.PHONY: install uninstall run test clean

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin

install:
	pip install --break-system-packages -e .
	@echo "commiefetch installed. Run 'commiefetch --help' to get started."

install-user:
	pip install --user -e .
	@echo "commiefetch installed for current user."

uninstall:
	pip uninstall commiefetch -y

run:
	python3 commiefetch

test:
	python3 -m commiefetch --no-color

test-all:
	python3 -m commiefetch --list-logos
	python3 -m commiefetch --list-themes
	python3 -m commiefetch --show-colors
	python3 -m commiefetch --no-color
	python3 -m commiefetch -l random

clean:
	rm -rf *.egg-info build dist __pycache__ src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
