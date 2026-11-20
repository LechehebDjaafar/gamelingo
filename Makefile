.PHONY: test validate rtl-deps zip
test:
	python -m unittest discover -s tests -v
validate:
	python tools/validate_skills.py
rtl-deps:
	python -m pip install -r requirements-rtl.txt
zip:
	python tools/make_release.py
