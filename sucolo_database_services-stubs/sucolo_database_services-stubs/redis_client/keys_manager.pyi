from _typeshed import Incomplete
from redis import Redis as Redis

class RedisKeysManager:
    redis_client: Incomplete
    def __init__(self, redis_client: Redis) -> None: ...
    def get_city_keys(self, city: str) -> list[str]: ...
    def delete_city_keys(self, city: str) -> None: ...
