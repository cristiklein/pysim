Event-driven Python simulation package
======================================

This Python package includes basic functionality to write an event-driven simulator. It allows to model processes, activate them, make them sleep and make them wait for a specific condition. No particular communication model is implemented, such as queues, however, one can achieve this using global variables.

The included source code provides both a good description of the offered functionality and an example. To test it yourself, proceed as follows:

	# install the greenlet Python package
	sudo apt-get install python-greenlet # e.g., on Ubuntu 12.04.2 LTS
	python ./sim.py

Feedback
--------

I hope you will find this code useful. Feedback is always welcome.

