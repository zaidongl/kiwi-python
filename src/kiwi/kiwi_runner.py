from behave.runner import Runner as CoreRunner

class KiwiRunner(object):
    def __init__(self, config, **kwargs):
        self.config = config
        self._runner = CoreRunner(config)

    def run(self):
        print("THIS_RUNNER_CLASS=%s::%s" % (self.__class__.__module__,
                                            self.__class__.__name__))
        return self._runner.run()

    @property
    def undefined_steps(self):
        return self._runner.undefined_steps

from behave.api.runner import ITestRunner
ITestRunner.register(KiwiRunner)