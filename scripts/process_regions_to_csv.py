#!/usr/bin/env python3
# process_regions_to_csv.py

import json
import csv
from pathlib import Path

from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform

# Функция для «обёртки» долгот за Гринвичем
def wrap_longitude(x, y, z=None):
    if x > 180:
        x -= 360
    elif x < -100:
        x += 360
    return (x, y)

def load_regions() -> dict:
    """
    Собирает все GeoJSON-файлы из папки data/Regions,
    объединяет геометрии, нормализует долготы и выдаёт GeoJSON FeatureCollection.
    """
    # Путь к папке data/Regions рядом с этим скриптом
    REGIONS_DIR = Path(__file__).resolve().parent / "data" / "Regions"
    features = []
    geojson_files = sorted(REGIONS_DIR.rglob("*.geojson"), key=lambda p: p.name)

    for idx, geojson_file in enumerate(geojson_files, start=1):
        stem = geojson_file.stem  # например 'Белгородская область_Belgorod region'
        name = stem.split("_", 1)[0]

        try:
            data = json.loads(geojson_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Ошибка чтения {geojson_file}: {e}")
            continue

        geoms = []
        if data.get("type") == "FeatureCollection":
            for feat in data.get("features", []):
                if feat.get("geometry"):
                    geoms.append(shape(feat["geometry"]))
        elif data.get("type") == "Feature":
            if data.get("geometry"):
                geoms.append(shape(data["geometry"]))
        else:
            continue

        if not geoms:
            continue

        # Нормализация долгот
        wrapped = [transform(wrap_longitude, g) for g in geoms]
        # Объединяем
        merged = unary_union(wrapped)
        features.append({
            "type": "Feature",
            "geometry": mapping(merged),
            "properties": {"code": idx, "name": name}
        })

    return {"type": "FeatureCollection", "features": features}

def main():
    fc = load_regions()
    out_csv = Path(__file__).resolve().parent / "data" / "regions_with_geometry.csv"
    out_csv.parent.mkdir(exist_ok=True, parents=True)

    # Записываем CSV: code,name,geometry(WKT)
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["code", "name", "geometry"])
        for feat in fc["features"]:
            code = feat["properties"]["code"]
            name = feat["properties"]["name"]
            geom = shape(feat["geometry"])
            writer.writerow([code, name, geom.wkt])

    print(f"✔ Сгенерирован файл CSV: {out_csv} ({len(fc['features'])} регионов)")

if __name__ == "__main__":
    main()
