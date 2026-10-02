import numpy as np
import numpy.typing as npt


class SparseTable:
    def __init__(
        self,
        a: npt.NDArray[np.float64],
        f,
    ):
        self.len = len(a)

        assert self.len > 0

        self.lg = self.len.bit_length()

        self.rec: list[npt.NDArray[np.float64]] = [a.copy()]

        for b in range(1, self.lg):
            size = self.len - (1 << b) + 1

            self.rec.append(
                f(
                    self.rec[b - 1][:size],
                    self.rec[b - 1][1 << (b - 1):1 << (b - 1) + size],
                )
            )

        self.f = f

    def __getitem__(self, lr: tuple[int, int]) -> np.float64:
        l, r = lr

        assert 0 <= l <= r < self.len

        b = (r - l + 1).bit_length() - 1

        return self.f(
            self.rec[b][l],
            self.rec[b][r + 1 - (1 << b)],
        )
