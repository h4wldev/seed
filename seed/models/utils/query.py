from typing import Any, List


class Query:
    @classmethod
    def get(
        cls,
        *args: List[Any],
    ):
        print(args)
