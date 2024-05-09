from enum import Enum


class HousingType(str, Enum):
    buy = "buy"
    rent = "rent"

    def to_dutch(self) -> str:
        return {
            HousingType.buy: "koop",
            HousingType.rent: "huur",
        }[self.value]

class PropertyType(str, Enum):
    pass