import re
import pandas as pd
import locale

INPUT_XLSX = r'C:\Users\Michail\Downloads\Книга1 энергия.xlsx'
OUTPUT_CSV = r'C:\Users\Michail\PycharmProjects\IMEC_ver.3.1\consumption_clean.csv'

def clean_value(x):
    if pd.isna(x):
        return None
    s = str(x)
    s = re.sub(r'[^\d\.\-]', '', s)
    try:
        return float(s)
    except:
        return None

def normalize_name(name):
    """
    Убирает всё до первой кириллической буквы,
    чтобы отбросить префиксы типа "г.", "респ.", а также суффиксы.
    """
    s = "" if pd.isna(name) else str(name)
    # убираем стандартные суффиксы, если нужно
    for suf in [" область", " край", " республика", " автономный округ"]:
        if s.lower().endswith(suf):
            s = s[: -len(suf)]
            break
    # ищем первую кириллическую букву
    m = re.search(r'[А-ЯЁа-яё]', s)
    return s[m.start():].strip() if m else s.strip()

def main():
    # 1) Читаем исходный Excel
    df = pd.read_excel(INPUT_XLSX, header=2, engine='openpyxl')
    df.rename(columns={df.columns[0]: 'region'}, inplace=True)

    # 2) Приводим названия колонок к годам 2008–2023
    col_map = {}
    for col in df.columns:
        try:
            y = int(col)
            if 2008 <= y <= 2023:
                col_map[col] = y
        except:
            digits = ''.join(c for c in str(col) if c.isdigit())
            if digits and 2008 <= int(digits) <= 2023:
                col_map[col] = int(digits)
    df.rename(columns=col_map, inplace=True)

    # 3) Оставляем только столбцы region + годы
    years = [c for c in df.columns if isinstance(c, int)]
    df = df[['region'] + years].copy()

    # 4) Фильтруем «Российская Федерация» и федеральные округа
    df = df[~df['region'].isin(['Российская Федерация'])]
    df = df[~df['region'].str.contains(r'федеральный округ$', case=False, na=False)]

    # 5) Отбрасываем пустые и нестроковые имена
    df = df[df['region'].notna()]
    df = df[df['region'].apply(lambda x: isinstance(x, str) and x.strip() != '')]

    # 6) Подготовка к сортировке по русскому алфавиту
    try:
        locale.setlocale(locale.LC_COLLATE, 'ru_RU.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_COLLATE, 'Russian_Russia.1251')

    # 7) Формируем базовое имя без «область/край» и т. п.
    df['base_name'] = df['region'].apply(normalize_name)

    # 8) Создаём locale-ключ и сортируем по нему
    df['sort_key'] = df['base_name'].map(locale.strxfrm)
    df.sort_values('sort_key', inplace=True)

    # 9) Убираем вспомогательные колонки и сбрасываем индекс
    df.drop(columns=['sort_key', 'base_name'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(">>> First 5 regions AFTER reset_index:")
    print(df.loc[:4, 'region'].tolist())

    # 10) Присваиваем region_code уже в правильном русском порядке
    df['region_code'] = df.index + 1
    # 11) Переводим в длинный формат
    df_long = df.melt(
        id_vars=['region_code', 'region'],
        value_vars=years,
        var_name='period',
        value_name='value_raw'
    )

    # 12) Очищаем и оставляем только валидные значения
    df_long['value'] = df_long['value_raw'].apply(clean_value)
    df_long.dropna(subset=['value'], inplace=True)

    # 13) Сохраняем итоговый CSV с BOM для корректной кириллицы
    df_out = df_long[['region_code', 'region', 'period', 'value']]
    df_out.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f'Wrote {len(df_out)} rows to {OUTPUT_CSV}')

if __name__ == '__main__':
    main()
