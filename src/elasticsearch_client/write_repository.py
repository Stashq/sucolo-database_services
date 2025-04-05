from typing import Any, Iterator

import geopandas as gpd
from elasticsearch import Elasticsearch, helpers

from src.utils.polygons2hexagons import polygons2hexagons


class ElasticsearchWriteRepository:
    def __init__(self, es_client: Elasticsearch, index_name: str):
        self.es = es_client
        self.index_name = index_name

    def upload_pois(
        self,
        gdf: gpd.GeoDataFrame,
        extra_features: list[str] = [],
    ) -> None:
        def doc_stream() -> Iterator[dict[str, Any]]:
            pois_features = gdf[extra_features].to_dict()
            for amenity, point in zip(gdf["amenity"], gdf["geometry"]):
                data = {
                    "type": "poi",
                    "amenity": amenity,
                    "location": {"lon": point.x, "lat": point.y},
                }
                data.update(pois_features)
                yield data

        for status_ok, response in helpers.streaming_bulk(
            self.es,
            actions=doc_stream(),
            chunk_size=1000,
            index=self.index_name,
        ):
            if not status_ok:
                print(response)

    def upload_districts(
        self,
        gdf: gpd.GeoDataFrame,
    ) -> None:
        gdf["polygon"] = gdf["geometry"].apply(lambda g: g.wkt)
        gdf = gdf.drop(columns=["geometry"])
        gdf["type"] = "district"

        def doc_stream() -> Iterator[dict[str, Any]]:
            for row_dict in gdf.to_dict(orient="records"):
                yield row_dict

        for doc in doc_stream():
            self.es.index(index=self.index_name, body=doc)

    def upload_hex_centers(
        self,
        districts: gpd.GeoDataFrame,
        hex_resolution: int,
        extra_features: list[str] = [],
    ) -> None:
        distric_hexagons = polygons2hexagons(
            districts, resolution=hex_resolution
        )

        def doc_stream() -> Iterator[dict[str, Any]]:
            for distric_id, hex_centers in distric_hexagons.items():
                district_features = districts.loc[
                    distric_id, extra_features
                ].to_dict()
                for id_, center in hex_centers:
                    data = {
                        "type": "hex_center",
                        "hex_id": id_,
                        "location": {"lon": center.x, "lat": center.y},
                    }
                    data.update(district_features)
                    yield data

        for status_ok, response in helpers.streaming_bulk(
            self.es,
            actions=doc_stream(),
            chunk_size=1000,
            index=self.index_name,
        ):
            if not status_ok:
                print(response)
