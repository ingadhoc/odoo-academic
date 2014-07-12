all: addons

design/academic.xmi: design/academic.zargo
	-echo "REBUILD academic.xmi from academic.zargo. I cant do it"

addons: academic

academic: design/academic.uml
	xmi2oerp -r -i $< -t addons -v 2

clean:
	rm -rf addons/academic/*
	sleep 1
	touch design/academic.uml
