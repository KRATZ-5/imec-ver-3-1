import pandas as pd
from app.services.consumption_service import load_regions

def main():
    # 1) Собираем все имена из GeoJSON
    regions_geojson = load_regions()
    geo_names = sorted({feat["properties"]["name"] for feat in regions_geojson["features"]})

    # 2) Собираем все имена из consumption.csv
    df_cons = pd.read_csv("../data/consumption.csv")
    # если у вас там нет колонки 'region', замените на фактическое имя
    csv_names = sorted(df_cons["region"].unique())

    # 3) Выравниваем длину списков
    max_len = max(len(geo_names), len(csv_names))
    geo_names += ["" for _ in range(max_len - len(geo_names))]
    csv_names += ["" for _ in range(max_len - len(csv_names))]

    # 4) Присваиваем region_code по порядку
    region_codes = list(range(1, max_len + 1))

    # 5) Собираем DataFrame
    df_map = pd.DataFrame({
        "region_code": region_codes,
        "geo_name":     geo_names,
        "csv_name":     csv_names
    })

    # 6) Сохраняем в CSV
    out_path = "../region_mapping_draft.csv"
    df_map.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Draft mapping saved to {out_path}")
    print(df_map.head(20))  # показываем первые 20 строк в консоль

if __name__ == "__main__":
    main()
