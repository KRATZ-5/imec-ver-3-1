from passlib.hash import bcrypt
stored = "$2b$12$.4qAnrfmSEpxw4xaqL0SZOitgQO4yuRYkh.Ay.Yyx4Kbrz6cbhJqW"
print(bcrypt.verify("adminpass", stored))  # должно вывести True
