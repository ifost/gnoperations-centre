import sched
import time
import select

MINIMUM_ACTION_SPAWN_WAIT_TIME = 0.001
# This time in seconds is the length of time between two actions getting
# run regardless of whether they were scheduled to run together.  The
# idea is to guarantee there are little windows of time for network i/o
# to be received and handled.

class gnpcFileDescriptorWrapper:
    def __init__(self,fd):        self.fd=fd
    def fileno(self):  return self.fd.fileno()
    def read_action(self): pass
    def error_action(self): self.close()
    def close(self):  Global_Scheduler.remove_input_source(self)


class gnpcScheduler(sched.scheduler):
    def __init__(self):
        sched.scheduler.__init__(time.time,time.sleep)
        self.input_sources_table = {}
    def add_input_source(self,source):
        """source should be derived from gnpcFileDescriptorWrapper"""
        self.input_sources_table[source.fileno()] = source
    def remove_input_source(self,source):
        """source should be derived from gnpcFileDescriptorWrapper"""
        del self.input_sources_table[source.fileno()] 
    def run(self):
        q = self.queue
        while 1:
            if len(q) != 0:
                next_time, priority, action, argument = q[0]
            else:
                next_time = None
            now = self.timefunc()
            if next_time is None:
                diff = None
            else:
                diff = next_time - now
                if diff < 0: diff = MINIMUM_ACTION_SPAWN_WAIT_TIME
                (input_waiting,output_waiting,error_waiting) = select.select(self.input_sources_table.values(),[],self.input_sources_table.values(),diff)

                # Only if we have no outstanding network operations to do
                # will we both doing a scheduled action.  This is probably
                # OK, even though it does open up a kind of network
                # denial-of-service attack.
                if (input_waiting + output_waiting + error_waiting) == 0:
                    del q[0]
                    void = apply(action, argument)
                    #self.delayfunc(0) # Let other threads run
                else:
                    for input in input_waiting:
                        input.read_action()
                    for error in error_waiting:
                        input.error_action()
                        


Global_Scheduler = gnpcScheduler()
