all:

include targets.mk

BRIDGES=$(patsubst %,parts/bridge_%.png,$(shell seq 0 15))
BRIDGE_TEMP_PARTS=$(patsubst %,tmp/bridge_%.png,up down left right)

BUILDING_FILES=$(patsubst %,$(patsubst %,combined/building_%_0.png,$(BUILDING_NAMES)),$(shell seq 0 15))

.PHONY: all .force
all: $(BUILDING_FILES)

parts/bridge_%.png: $(BRIDGE_TEMP_PARTS)
	$(eval I=$(patsubst parts/bridge_%.png,%,$@))
	@mkdir -p parts
	bash build_bridge.sh $I

tmp/bridge_%.png: bridge_down.png
	@mkdir -p tmp
	bash build_bridge.sh
