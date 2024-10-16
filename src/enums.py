from enum import Enum

class Role(Enum):
    USER = "user"
    ADMIN= "admin"

    def __to_list__(self):
        to_list = []
        for data in Role:
            to_list.append(data.value)

        return to_list