import time


class CircuitBreaker:
    """
    Production-style circuit breaker
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold=3,
        recovery_timeout=30,
        half_open_trials=2
    ):

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_trials = half_open_trials

        self.state = self.CLOSED

        self.failure_count = 0
        self.last_failure_time = None
        self.trial_count = 0

    # -----------------------------

    def _open(self):

        self.state = self.OPEN
        self.last_failure_time = time.time()

    def _half_open(self):

        self.state = self.HALF_OPEN
        self.trial_count = 0

    def _close(self):

        self.state = self.CLOSED
        self.failure_count = 0
        self.trial_count = 0

    # -----------------------------

    def can_execute(self) -> bool:

        if self.state == self.CLOSED:
            return True

        if self.state == self.OPEN:

            if time.time() - self.last_failure_time > self.recovery_timeout:

                self._half_open()
                return True

            return False

        if self.state == self.HALF_OPEN:

            return self.trial_count < self.half_open_trials

        return False

    # -----------------------------

    def record_success(self):

        if self.state in [self.HALF_OPEN, self.OPEN]:
            self._close()

        self.failure_count = 0

    def record_failure(self):

        self.failure_count += 1

        if self.state == self.HALF_OPEN:
            self._open()

        elif self.failure_count >= self.failure_threshold:
            self._open()

        self.last_failure_time = time.time()

    # -----------------------------

    def register_trial(self):

        if self.state == self.HALF_OPEN:
            self.trial_count += 1
