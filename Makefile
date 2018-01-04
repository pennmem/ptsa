CC="ccache gcc"
CXX="ccache g++"

dev:
	CC=$(CC) CXX=$(CXX) python setup.py develop
