import pandas as pd
import os

base_dir   = os.path.dirname(os.path.abspath(__file__))
input_csv  = os.path.join(base_dir, 'regions_with_geometry.csv')
output_csv = os.path.join(base_dir, 'regions_with_geometry_utf8.csv')

# 1) Читаем, убирая BOM, если он есть
#    Попробуем 'utf-8-sig' — он удаляет BOM; если файл на ANSI, смените на encoding='cp1251'
df = pd.read_csv(input_csv, encoding='utf-8-sig')

# 2) Проверим первые строки
print("Первое имя региона:", df.loc[0, 'name'])

# 3) Сохраняем в чистый UTF-8
df.to_csv(output_csv, index=False, encoding='utf-8')

print(f"Успешно сохранён {output_csv}")
