VERSION=dev

all: podc

.PHONY: podc
podc: module/pypod.c
	python3 setup.py build
	cp $$(find build/ -wholename "*/lib.*/podc*.so") .

clean:
	rm -rf build *.pyc ui/*.pyc *~ ui/*~ podc.so

dist: clean
	rm -rf line6control-$(VERSION)
	mkdir line6control-$(VERSION)
	cp -r data ui line6control-$(VERSION)/
	cp AUTHORS README Makefile line6control.glade pypod.c controls.py \
		main.py pod.py preset.py setup.py singleton.py \
		line6control-$(VERSION)/
	find line6control-$(VERSION) -name ".arch-ids" -type d | xargs rm -rf
	tar cjf line6control-$(VERSION).tar.bz2 line6control-$(VERSION)/
	rm -rf line6control-$(VERSION)
