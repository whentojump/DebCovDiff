#!/usr/bin/make -f

# This is to demonstrate and experiment how dpkg-buildflags works

# dpkg-buildpackage
#   debian/rules binary
#     (variables not visible)
#     dh binary
#       debian/rules override_dh_auto_build
#         (variables visible)
#         dh_auto_build

export DEB_BUILD_MAINT_OPTIONS = hardening=+all

override_dh_auto_build:
	echo FINDME2
	echo $(CFLAGS)
	dh_auto_build

%:
	echo FINDME1
	echo $(CFLAGS)
	dh $@
