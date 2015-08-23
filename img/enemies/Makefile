.PHONY: all
all:


combined/enemy_gray.png: $(shell ./parts.sh gray gray gray gray gray)
	bash combine.sh $@ $^
ENEMIES=gray

combined/enemy_white.png: $(shell ./parts.sh white white white white white)
	bash combine.sh $@ $^
ENEMIES+=white

combined/enemy_redshirt1.png: $(shell ./parts.sh gray red1 skin gray skin)
	bash combine.sh $@ $^
combined/enemy_redshirt2.png: $(shell ./parts.sh blue2 red2 skin gray skin)
	bash combine.sh $@ $^
combined/enemy_redshirt3.png: $(shell ./parts.sh gray red1 skin gray skin)
	bash combine.sh $@ $^
ENEMIES+=redshirt1 redshirt2 redshirt3

tmp/%_white.png: %.png parts.sh Makefile
	convert -modulate 150,0,100 $< $@
tmp/%_gray.png: %.png parts.sh Makefile
	convert -modulate 100,0,100 $< $@
tmp/%_blue.png: %.png parts.sh Makefile
	convert -modulate 70,90,100 $< $@
tmp/%_cyan.png: %.png parts.sh Makefile
	convert -modulate 70,90,60 $< $@
tmp/%_red1.png: %.png parts.sh Makefile
	convert -modulate 70,90,170 $< $@
tmp/%_red2.png: %.png parts.sh Makefile
	convert -modulate 80,100,170 $< $@
tmp/%_blue2.png: %.png parts.sh Makefile
	convert -modulate 70,80,95 $< $@
tmp/%_skin.png: %.png parts.sh Makefile
	convert -modulate 115,10,115 $< $@

TARGETS:=$(patsubst %,combined/enemy_%.png,$(ENEMIES))
all: $(TARGETS)
