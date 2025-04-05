from redis import Redis

from src.redis_client.consts import HEX_SUFFIX, POIS_SUFFIX
from src.redis_client.utils import check_if_keys_exist


class RedisReadRepository:
    def __init__(self, redis_client: Redis, city: str):
        self.redis_client = redis_client
        self.city = city

    def count_records_per_key(self) -> dict[str, int]:
        result = {}
        for key in self.redis_client.keys("*"):  # type: ignore[union-attr]
            if self.city in key:
                result[key] = self.redis_client.zcard(key)
        return result  # type: ignore[return-value]

    def nearest_pois_to_hex_centers(
        self,
        amenity: str,
        radius: int = 300,
        unit: str = "m",
        count: int | None = 1,
    ) -> dict[str, list[dict[str, float]]]:
        hex_key = self.city + HEX_SUFFIX
        pois_key = self.city + "_" + amenity + POIS_SUFFIX
        check_if_keys_exist(client=self.redis_client, keys=[hex_key, pois_key])

        hex_ids = self.redis_client.zrange(hex_key, 0, -1)
        hex_centers = self._get_hex_centers(
            hex_key=hex_key,
            hex_ids=hex_ids,  # type: ignore[arg-type]
        )
        nearest_pois = self._get_nearest_pois(
            hex_ids=hex_ids,  # type: ignore[arg-type]
            hex_centers=hex_centers,
            pois_key=pois_key,
            radius=radius,
            unit=unit,
            count=count,
        )
        processed_pois = self._pois_postprocessing(
            nearest_pois=nearest_pois,
            hex_ids=hex_ids,  # type: ignore[arg-type]
        )

        return processed_pois

    def _get_hex_centers(
        self, hex_key: str, hex_ids: list[str]
    ) -> list[list[tuple[float, float]]]:
        pipeline = self.redis_client.pipeline()
        for hex_id in hex_ids:
            pipeline.geopos(hex_key, hex_id)
        hex_centers = pipeline.execute()
        return hex_centers  # type: ignore[no-any-return]

    def _get_nearest_pois(
        self,
        hex_ids: list[str],
        hex_centers: list[list[tuple[float, float]]],
        pois_key: str,
        radius: int,
        unit: str,
        count: int | None = 1,
    ) -> list[list[tuple[bytes, float]]]:
        pipeline = self.redis_client.pipeline()
        for hex_id, lon_lat in zip(hex_ids, hex_centers):
            lon, lat = lon_lat[0]
            pipeline.georadius(
                name=pois_key,
                longitude=lon,
                latitude=lat,
                radius=radius,
                unit=unit,
                withdist=True,
                count=count,
                sort="ASC",
            )
        nearest_pois = pipeline.execute()
        return nearest_pois  # type: ignore[no-any-return]

    def _pois_postprocessing(
        self,
        nearest_pois: list[list[tuple[bytes, float]]],
        hex_ids: list[bytes],
    ) -> dict[str, list[dict[str, float]]]:
        data = {
            hex_id.decode("utf-8"): [
                {poi_id.decode("utf-8"): distance}
                for poi_id, distance in hex_pois_distances
            ]
            for hex_id, hex_pois_distances in zip(hex_ids, nearest_pois)
        }
        return data
