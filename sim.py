from heapq import heappush, heappop
from greenlet import greenlet

##@package sim
# Event-driven simulation framework
#
# Basic event-driven simulation framework. Uses greenlets so
# that each simulation process runs separately. Implements
# sleep(time) and waituntil(condition).

## Stores values which change during simulation
class Monitor:
	## Constructor
	# @param[in] name Name to associate to this Monitor
	def __init__(self, name):
		self._name = name
		self._values = {}

	## Store the specified value
	#
	# Stores the tuples simulation time, specified value
	def observe(self, value):
		self._values[now()] = value

	## Iterate over the stored values
	# @return iterator of simulation time, value tuples.
	def __iter__(self):
		return self._values.iteritems()

## Launch a process
#
# Activated a process, either immediately (if both at and after are None)
# or after a delay.
# @param[in] what A class having a main() method
# @param[in] at At what simulation time to activate the process or None
# @param[in] after Delay activation with specified time or None
def activate(what, at = None, after = None):
	def main():
		sleepuntil(at)
		sleep(after)
		what.main()	
		_sim.next()  # switch to another greenlet, or else execution "fall"
		            # is resumed from the parent's last switch()
	# Add it to the event-queue and launch it as soon as possible.
	_sim.post(who = greenlet(main), cond = lambda: True)

## Wait for a condition to become true
#
# Suspends this process until the condition becomes true. If until is specified
# wake the process up at the specified simulation time.
# @param cond Function to test
# @param until Maximum simulation time to wait for condition to become true
def waituntil(cond, until = None):
	if until != None:
		assert until > now()
		_sim.post(cond = lambda: cond() or (now() == until), when = until)
	else:
		_sim.post(cond = cond)
	_sim.next()
	
## Sleeps until the given simulation time
def sleepuntil(until):
	if until == None: return
	if until == now(): return
	assert until > now()
	_sim.post(cond = lambda: now() == until, when = until)
	_sim.next()

## Sleeps a for the given duration
def sleep(duration):
	if duration == None: return
	sleepuntil(now() + duration)

## Returns the simulation time
def now():
	return _sim.now()

## Starts the simulation
def simulate():
	_sim.simulate()

## Reset the simulation
def reset():
	global _sim
	_sim = _Simulator()

#
# Private API
#

##@cond
## Implements the simulator's "business logic"
#
# Decides who will run next. Processes post
# conditions and times they are interested in.
class _Simulator:
	## Simulation ended exception
	#
	# Thrown (probably inside a greenlet) when
	# there are no more events to process.
	class SimulationEnd(Exception):
		pass

	## Constructor
	def __init__(self):
		self._conds = []
		self._times = []
		self._now = 0

	## Post a condition or a time
	def post(self, who = None, cond = None, when = None):
		if who == None:
			who = greenlet.getcurrent()
		if cond:
			self._conds.append((who, cond))
		if when:
			heappush(self._times, when)

	## Returns current simulation time
	def now(self):
		return self._now
	
	def __pop(self):
		"""
		Pops out a fiber which may run *now*.
		Returns None if no fiber can run now.
		"""
		for fiber, cond in self._conds:
			if cond():
				self._conds.remove((fiber, cond))
				return fiber
		return None

	def simulate(self):
		while True:
			# Is anybody wakeable?
			fiber = self.__pop()

			# Advance time & retry
			while fiber == None:
				# Do we still have process waiting for a new time?
				if self._times:
					self._now = heappop(self._times)
					fiber = self.__pop()
				# if not, the simulation is over
				else:
					return
			# Switch to it
			fiber.switch()
			# Back to scheduling
	
	## Switched to the next awakeable fiber
	def next(self):
		greenlet.getcurrent().parent.switch()

## Singleton implementing the simulation
_sim = _Simulator()
##@endcond

#
# Testing
#
##@cond
if __name__ == "__main__":
	go = False
	class FB1:
		def main(self):
			for i in range(10):
				print "Hello1 @ %s" % now()
				sleep(10)
	
	class FB2:
		def main(self):
			global go
			for i in range(10):
				print "Hello2 @ %s" % now()
				sleep(2)
			go = True
	
	class FB3:
		def main(self):
			waituntil(lambda: go)
			print "Hello3 @ %s" % now()

	fb1 = FB1()
	fb2 = FB2()
	fb3 = FB3()

	activate(fb1)
	activate(fb2, at = 20)
	activate(fb3)
	simulate()
##@endcond
