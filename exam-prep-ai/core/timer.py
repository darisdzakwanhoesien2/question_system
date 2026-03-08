import time
from threading import Thread, Event
from typing import Optional, Callable

class Timer:
    def __init__(self, duration_seconds: int, on_timeout: Optional[Callable] = None):
        self.duration = duration_seconds
        self.remaining = duration_seconds
        self.start_time = None
        self.is_running = False
        self.is_paused = False
        self.pause_time = None
        self.on_timeout = on_timeout
        self._stop_event = Event()
        self._thread = None

    def start(self):
        """Start the timer."""
        if self.is_running:
            return

        self.start_time = time.time()
        self.is_running = True
        self.is_paused = False
        self._stop_event.clear()

        # Start background thread to monitor timeout
        self._thread = Thread(target=self._monitor_timeout, daemon=True)
        self._thread.start()

    def pause(self):
        """Pause the timer."""
        if not self.is_running or self.is_paused:
            return

        self.is_paused = True
        self.pause_time = time.time()

    def resume(self):
        """Resume the timer."""
        if not self.is_paused:
            return

        paused_duration = time.time() - self.pause_time
        self.start_time += paused_duration
        self.is_paused = False

    def stop(self):
        """Stop the timer."""
        self.is_running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def get_remaining_time(self) -> int:
        """Get remaining time in seconds."""
        if not self.is_running:
            return self.remaining

        if self.is_paused:
            return self.remaining

        elapsed = time.time() - self.start_time
        remaining = max(0, self.duration - elapsed)
        self.remaining = int(remaining)
        return self.remaining

    def get_elapsed_time(self) -> int:
        """Get elapsed time in seconds."""
        if not self.start_time:
            return 0

        if self.is_paused and self.pause_time:
            return int(self.pause_time - self.start_time)

        return int(time.time() - self.start_time)

    def is_expired(self) -> bool:
        """Check if timer has expired."""
        return self.get_remaining_time() == 0

    def _monitor_timeout(self):
        """Monitor for timeout in background thread."""
        while not self._stop_event.is_set():
            if self.is_running and not self.is_paused and self.is_expired():
                if self.on_timeout:
                    self.on_timeout()
                break

            time.sleep(1)  # Check every second

    def __str__(self) -> str:
        """String representation of timer."""
        remaining = self.get_remaining_time()
        minutes = remaining // 60
        seconds = remaining % 60
        return f"{minutes:02d}:{seconds:02d}"

class CountdownTimer(Timer):
    """A timer that counts down and calls callback when reaching zero."""

    def __init__(self, duration_seconds: int, on_tick: Optional[Callable[[int], None]] = None,
                 on_timeout: Optional[Callable] = None):
        super().__init__(duration_seconds, on_timeout)
        self.on_tick = on_tick

    def _monitor_timeout(self):
        """Monitor with tick callback."""
        last_remaining = self.duration

        while not self._stop_event.is_set():
            if self.is_running and not self.is_paused:
                remaining = self.get_remaining_time()

                if remaining != last_remaining and self.on_tick:
                    self.on_tick(remaining)

                if remaining == 0:
                    if self.on_timeout:
                        self.on_timeout()
                    break

                last_remaining = remaining

            time.sleep(1)