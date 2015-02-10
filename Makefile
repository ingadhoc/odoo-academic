all: addons

design/academic.xmi: design/academic.zargo
	-echo "REBUILD academic.xmi from academic.zargo. I cant do it"

addons: academic

academic: design/academic.uml
	xmi2odoo -r -i $< -t addons -v 2 -V 8.0

clean:
	sleep 1
	touch design/academic.uml