from math import sqrt


class EMAFilter:
    """Exponential Moving Average low-pass filter.

    new = alpha * input + (1 - alpha) * previous

    Args:
        alpha: Smoothing factor in [0, 1]. Higher = faster response.
        init:  Initial filter state. Defaults to 0.0.
    """

    def __init__(self, alpha: float, init: float = 0.0) -> None:
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha must be in [0, 1], got {alpha}")
        self.alpha = alpha
        self.value = init

    def update(self, value: float) -> float:
        self.value = self.alpha * value + (1.0 - self.alpha) * self.value
        return self.value


class RMSFilter:
    """RMS-domain exponential filter. Smooths signal power, not amplitude.

    new = sqrt(alpha * input² + (1 - alpha) * previous²)

    Useful for AC signals, vibration energy, or power measurements.
    Always produces non-negative output.

    Args:
        alpha: Smoothing factor in [0, 1].
        init:  Initial filter state. Defaults to 0.0.
    """

    def __init__(self, alpha: float, init: float = 0.0) -> None:
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha must be in [0, 1], got {alpha}")
        self.alpha = alpha
        self.value = init

    def update(self, value: float) -> float:
        self.value = sqrt(self.alpha * value**2 + (1.0 - self.alpha) * self.value**2)
        return self.value


class AsymmetricFilter:
    """EMA filter with separate smoothing rates for rising and falling signals.

    Uses alpha_up when the input exceeds the current state,
    and alpha_down when the input is below the current state.

    Useful when rise and fall speeds must differ (e.g. battery indicators,
    peak detectors, alarm systems).

    Args:
        alpha_up:   Smoothing factor for rising inputs, in [0, 1].
        alpha_down: Smoothing factor for falling inputs, in [0, 1].
        init:       Initial filter state. Defaults to 0.0.
    """

    def __init__(self, alpha_up: float, alpha_down: float, init: float = 0.0) -> None:
        if not 0.0 <= alpha_up <= 1.0:
            raise ValueError(f"alpha_up must be in [0, 1], got {alpha_up}")
        if not 0.0 <= alpha_down <= 1.0:
            raise ValueError(f"alpha_down must be in [0, 1], got {alpha_down}")
        self.alpha_up = alpha_up
        self.alpha_down = alpha_down
        self.value = init

    def update(self, value: float) -> float:
        alpha = self.alpha_up if value > self.value else self.alpha_down
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value
