#/usr/bin/make
SRC = $(DESTDIR)/usr/src
SHARE = $(DESTDIR)/usr/share/$(NAME)-dkms

all:

clean:

install:

#source tree
ifeq ("$(wildcard $(NAME))", "$(NAME)")
	install -d "$(SRC)"
	cp -LR --preserve=all "$(NAME)" "$(SRC)/$(NAME)-$(VERSION)"
	chmod 644 -R "$(SRC)/$(NAME)-$(VERSION)"
	chmod 755 `find "$(SRC)/$(NAME)-$(VERSION)" -iname *.sh`
endif

#tarball, possibly with binaries
ifeq ("$(wildcard $(NAME)-$(VERSION).dkms.tar.gz)", "$(NAME)-$(VERSION).dkms.tar.gz")
	install -d "$(SHARE)"
	install -m 644 $(NAME)-$(VERSION).dkms.tar.gz "$(SHARE)"
endif

#postinst, only if we are supporting legacy mode
ifeq ("$(wildcard common.postinst)", "common.postinst")
	install -d "$(SHARE)"
	install -m 755 common.postinst $(SHARE)/postinst
endif
