import pandas as pd
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# === Функция для обучения модели ===
def train_model(train_file):
    # Загрузка тренировочной выборки
    df = pd.read_csv(train_file, sep=';')
    X_train = df["info_message"].values
    y_train = df["message_type"].values

    # Векторизация текста
    vect = CountVectorizer(analyzer='word')
    X_train_vect = vect.fit_transform(X_train)

    # Обучение модели
    clf = RandomForestClassifier(n_estimators=30, n_jobs=-1)
    clf.fit(X_train_vect, y_train)

    # Сохранение модели и векторизатора
    with open("model.pkl", "wb") as model_file:
        pickle.dump(clf, model_file)
    with open("vectorizer.pkl", "wb") as vect_file:
        pickle.dump(vect, vect_file)

    print("Модель и векторизатор сохранены.")


# === Функция для классификации тестового набора данных ===
def test_model(test_file):
    # Загрузка модели и векторизатора
    with open("model.pkl", "rb") as model_file:
        clf = pickle.load(model_file)
    with open("vectorizer.pkl", "rb") as vect_file:
        vect = pickle.load(vect_file)

    # Загрузка тестовых данных
    df_test = pd.read_csv(test_file, sep=';')
    X_test = df_test["info_message"].values
    y_test = df_test["message_type"].values

    # Векторизация тестовых данных
    X_test_vect = vect.transform(X_test)

    # Предсказание на тестовых данных
    y_pred = clf.predict(X_test_vect)

    # Расчет accuracy
    acc = accuracy_score(y_test, y_pred)
    print(f"Точность модели на тестовых данных: {acc:.4f}")


# === Асинхронная функция для классификации новых сообщений ===
async def classify_logs(mongo_uri, db_name, collection_name):
    # Загрузка модели и векторизатора
    with open("model.pkl", "rb") as model_file:
        clf = pickle.load(model_file)
    with open("vectorizer.pkl", "rb") as vect_file:
        vect = pickle.load(vect_file)

    # Подключение к MongoDB (асинхронное)
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    print("Ожидание новых данных...")

    try:
        async with collection.watch() as stream:
            async for change in stream:
                if change["operationType"] == "insert":
                    # Получение новых данных
                    new_document = change["fullDocument"]
                    new_message = new_document["info_message"]

                    # Классификация нового сообщения
                    new_message_vect = vect.transform([new_message])
                    predicted_type = clf.predict(new_message_vect)[0]

                    # Сохранение результата обратно в MongoDB
                    await collection.update_one(
                        {"_id": new_document["_id"]},
                        {"$set": {"predicted_message_type": predicted_type}}
                    )
                    print(f"Сообщение: {new_message} классифицировано как {predicted_type}")

    except OperationFailure as e:
        print(f"Ошибка работы с Change Stream: {e}")


# === Основной блок вызова ===
if __name__ == "__main__":
    # Параметры обучения
    train_file = "linux_syslogs.csv"  # Файл с обучающими данными
    test_file = "linux_syslogs_test.csv"  # Файл с тестовыми данными

    # Параметры MongoDB
    mongo_uri = "mongodb://192.168.2.52:27017"
    db_name = "logstash_db"
    collection_name = "dhcp_logs"

    # Вызов функций
    train_model(train_file)
    test_model(test_file)

    # Запуск асинхронного обработчика логов
    asyncio.run(classify_logs(mongo_uri, db_name, collection_name))
