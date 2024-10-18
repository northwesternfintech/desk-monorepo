from pysrc.adapters.kraken.future.containers import PositionSide


def str_to_position_side(s: str) -> PositionSide:
    match s:
        case "long":
            return PositionSide.LONG
        case "short":
            return PositionSide.SHORT
        case _:
            raise ValueError(f"Can't convert '{s}' to PositionSide")