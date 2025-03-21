#!/usr/bin/env python3
"""
Defines functions for interacting with headless browser sessions.
"""

import shutil
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import se

def initialize_selenium_firefox_webdriver() -> webdriver.Firefox:
	"""
	Initialize a Selenium Firefox driver and return it for use in other applications.

	INPUTS
	None.

	RETURNS
	A Selenium webdriver for Firefox.
	"""

	if not shutil.which("firefox") and not Path("/Applications/Firefox.app/Contents/MacOS/firefox").exists():
		raise se.MissingDependencyException("Couldn’t locate [bash]firefox[/]. Is it installed?")

	# Initialize the selenium driver to take screenshots

	# We have to use the headless option, otherwise it will pop up a Firefox window
	options = Options()
	options.add_argument('-headless')

	# Disable the history, because otherwise links to (for example to end notes) may appear as "visited" in visits to other pages, and thus cause a fake diff
	profile = webdriver.FirefoxProfile()
	profile.set_preference("places.history.enabled", False)
	profile.set_preference("browser.cache.disk.enable", False)
	profile.set_preference("browser.cache.memory.enable", False)
	profile.set_preference("browser.cache.offline.enable", False)
	profile.set_preference("browser.http.use-cache", False)
	profile.set_preference("layout.css.devPixelsPerPx", "2.0")

	options.profile = profile

	return webdriver.Firefox(options=options)
