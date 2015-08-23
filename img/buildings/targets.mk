BUILDING_NAMES=metals energy heart

combined/building_metals_0.png: $(BRIDGES) parts/hue_metals.png ziggurat_base.png pylon_base.png
	bash combine.sh metals parts/hue_metals.png
combined/building_energy_0.png: $(BRIDGES) parts/hue_energy.png ziggurat_base.png pylon_base.png
	bash combine.sh energy parts/hue_energy.png
combined/building_heart_0.png: $(BRIDGES) parts/hue_heart.png ziggurat_base.png pylon_base.png
	bash combine.sh heart parts/hue_heart.png

parts/hue_metals.png:
	bash buildHue.sh $@ 120,20,100 5
parts/hue_energy.png:
	bash buildHue.sh $@ 100,100,0
parts/hue_heart.png:
	bash buildHue.sh $@ 100,40,100
