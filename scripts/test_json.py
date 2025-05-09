#!/usr/bin/env python3
"""
Скрипт для обработки GeoJSON-файлов из указанной директории и вывода CSV с двумя колонками: name, code.
Путь к папке и выходному CSV явно прописаны внутри скрипта.
"""
import json
import csv
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform, unary_union

# Параметры (жестко заданные пути)
REGIONS_DIR = Path(r"/data/Regions")
OUTPUT_CSV = Path(r"C:/Users/Michail/PycharmProjects/IMEC_ver.3.1/data/regions.csv")

# Функция нормализации долготы

def wrap_longitude(x, y, z=None):
    lon = ((x + 180) % 360) - 180
    return lon, y


def load_regions(regions_dir: Path):
    """
    Читает все GeoJSON-файлы из regions_dir,
    нормализует и объединяет геометрию,
    присваивает порядковый код и возвращает список (name, code).
    """
    regions = []
    geojson_files = sorted(regions_dir.rglob("*.geojson"), key=lambda p: p.name)

    for idx, geojson_file in enumerate(geojson_files, start=1):
        stem = geojson_file.stem
        name = stem.split('_', 1)[0]
        try:
            data = json.loads(geojson_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Ошибка чтения {geojson_file}: {e}")
            continue

        geoms = []
        if data.get("type") == "FeatureCollection":
            for feat in data.get("features", []):
                geom = feat.get("geometry")
                if geom:
                    geoms.append(shape(geom))
        elif data.get("type") == "Feature":
            geom = data.get("geometry")
            if geom:
                geoms.append(shape(geom))
        else:
            continue

        if not geoms:
            continue

        # Нормализация и очистка топологических ошибок
        wrapped = []
        for g in geoms:
            gw = transform(wrap_longitude, g)
            if not gw.is_valid:
                try:
                    gw = gw.buffer(0)
                except Exception as fix_err:
                    print(f"Не удалось исправить геометрию для {geojson_file}: {fix_err}")
            wrapped.append(gw)

        # Объединение геометрий
        try:
            merged = unary_union(wrapped)
        except Exception as union_err:
            print(f"Ошибка объединения геометрий в {geojson_file}: {union_err}")
            continue

        regions.append((name, idx))

    return regions


def write_csv(regions, output_file: Path):
    """
    Записывает список (name, code) в CSV с BOM для корректной кодировки в Excel.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    # Используем utf-8-sig, чтобы добавить BOM и сохранить русские названия
    with output_file.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'code'])
        for name, code in regions:
            writer.writerow([name, code])


def main():
    if not REGIONS_DIR.exists():
        print(f"Указанная папка не найдена: {REGIONS_DIR}")
        return

    regions = load_regions(REGIONS_DIR)
    write_csv(regions, OUTPUT_CSV)
    print(f"Записано {len(regions)} регионов в {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
