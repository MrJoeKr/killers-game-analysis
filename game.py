import random
import pandas as pd  # type: ignore
from typing import Tuple, Dict, Any, List, Callable


Player = int
Players = List[Player]
ShuffleFunc = Callable[[Players], None]


class Zabijaci:
    def __init__(self, n: int):
        self.n = n
        # _targets[i] = j --> i targets j
        self._targets: Players = [_ for _ in range(n)]

        if n < 2:
            raise ValueError("There must be at least 2 players")

    def __len__(self):
        return self.n

    def __getitem__(self, i: int):
        return self._targets[i]

    def _valid_targets(self) -> bool:
        for i in range(self.n):
            if self._targets[i] == i:
                return False

        return True

    def start_game(self, shuffle_func: ShuffleFunc = random.shuffle):
        shuffle_func(self._targets)

        while not self._valid_targets():
            shuffle_func(self._targets)

    def get_targets(self) -> list:
        return self._targets

    def count_cycles(self) -> Tuple[int, Dict[int, int]]:
        """
        Returns the number of cycles and the length of each cycle
        together with the number of players in the cycle.
        """
        cycles = 0
        cycle_count: Dict[int, int] = dict()
        visited = [False for _ in range(self.n)]

        for i in range(self.n):
            if visited[i]:
                continue

            visited[i] = True
            cycles += 1
            curr_cycle_length = 1

            j = self._targets[i]
            while not visited[j]:
                visited[j] = True
                j = self._targets[j]
                curr_cycle_length += 1

            cycle_count[curr_cycle_length] = cycle_count.get(curr_cycle_length, 0) + 1

        return cycles, cycle_count


def generate_data(
    num_games: int, players: int, shuffle_func: ShuffleFunc = random.shuffle
) -> pd.DataFrame:
    """
    Generate dataframe with num_games rows,
    each row representing one game and containing cycle length
    and number of players in the cycle.
    """

    rows_list: list[Dict[str, Any]] = []

    for _ in range(num_games):
        game = Zabijaci(players)
        game.start_game(shuffle_func=shuffle_func)
        cycle_count, cycle_length = game.count_cycles()

        row: Dict[str, Any] = {
            f"cycle_{length}": count for length, count in cycle_length.items()
        }
        row["cycles_count"] = cycle_count

        rows_list.append(row)

    data = pd.DataFrame(rows_list)

    # Add missing cycle columns
    for i in range(1, players + 1):
        if f"cycle_{i}" not in data.columns:
            data[f"cycle_{i}"] = 0

    # Reorder columns
    cols = data.columns.tolist()
    cols.sort(key=lambda x: int(x.split("_")[1]) if x != "cycles_count" else 0)

    data = data[cols]

    # Replace NaN with 0
    data.fillna(0, inplace=True)

    # Set columns types
    data = data.astype(int)

    return data


def count_cycles(data: pd.DataFrame) -> List[int]:
    """
    Returns dataframe with cycle counts for each cycle length.
    """
    cycle_counts = data.drop("cycles_count", axis=1).sum(axis=0)

    # # Rename cols
    # cycle_counts.index = [int(x.split("_")[1]) for x in cycle_counts.index]

    return list(cycle_counts)


def shuffle_from_box(targets: Players) -> None:
    """
    Shuffling method, where each player takes a random target from the box.
    if they choose themselves, they put the target back and choose again.
    """
    n = len(targets)
    box = [_ for _ in range(n)]
    random.shuffle(box)

    for i in range(n):
        targets[i] = box[-1]
        while targets[i] == i:
            if len(box) == 1:
                # Go again -> unlikely for large enough n
                shuffle_from_box(targets)
                return

            random.shuffle(box)
            targets[i] = box[-1]

        box.pop()


# Testing
if __name__ == "__main__":
    data = generate_data(10**4, 60, shuffle_func=shuffle_from_box)
    print(data.shape)
    print(data.head(10))

    # print(data.describe())

    cycles = count_cycles(data)
    print(len(cycles))
    print(cycles)
