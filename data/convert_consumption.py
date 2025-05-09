import pandas as pd
import os

# Пути
base_dir   = os.path.dirname(os.path.abspath(__file__))
input_csv  = os.path.join(base_dir, 'consumption.csv')
output_csv = os.path.join(base_dir, 'consumption_utf8.csv')

# 1) Читаем с кодировкой UTF-8 и убираем BOM
df = pd.read_csv(input_csv, encoding='utf-8-sig')

# 2) Проверим, что заголовки и первые строки читаются правильно
print("Столбцы:", df.columns.tolist())
print("Первые 5 строк:\n", df.head())

# 3) Сохраняем в чистый UTF-8 без BOM
df.to_csv(output_csv, index=False, encoding='utf-8')

print(f"Успешно сохранён файл {output_csv} в UTF-8.")
