MAIN_SCRIPT = bot.py
REQUIREMENTS_FILE = requirements.txt

ifeq ($(OS), Windows_NT)
PYTHON := python
else
PYTHON := python3
endif

# Default target
.PHONY: all
all: run

# Update target: Fetch changes from main, pull latest changes, and install requirements
.PHONY: update
update: requirements.txt
	git fetch origin
	git pull origin main
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(REQUIREMENTS_FILE)

# Run target: Run the main script
.PHONY: run
run:
	$(PYTHON) $(MAIN_SCRIPT)
