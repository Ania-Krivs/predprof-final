import json
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


DATA_DIR = Path("data")
DATASET_PATH = DATA_DIR / "processed_dataset.npz"
LABEL_MAPPING_CSV = DATA_DIR / "label_mapping.csv"
TRAIN_MANIFEST_CSV = DATA_DIR / "train_manifest.csv"
VALID_MANIFEST_CSV = DATA_DIR / "valid_manifest.csv"
LABEL_MAPPING_JSON = DATA_DIR / "label_mapping.json"

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 32
EPOCHS = 40
LEARNING_RATE = 1e-3
SEED = 42


def set_seed(seed: int = 42):
    np.random.seed(seed)
    tf.random.set_seed(seed)


def load_dataset(npz_path: Path):
    if not npz_path.exists():
        raise FileNotFoundError(f"Не найден файл датасета: {npz_path}")

    data = np.load(npz_path, allow_pickle=True)

    required_keys = ["train_x", "train_y", "valid_x", "valid_y"]
    for key in required_keys:
        if key not in data:
            raise KeyError(f"В {npz_path} отсутствует массив: {key}")

    train_x = data["train_x"]
    train_y = data["train_y"]
    valid_x = data["valid_x"]
    valid_y = data["valid_y"]

    return train_x, train_y, valid_x, valid_y


def load_optional_metadata():
    metadata = {}

    if LABEL_MAPPING_CSV.exists():
        metadata["label_mapping_csv"] = pd.read_csv(LABEL_MAPPING_CSV)

    if TRAIN_MANIFEST_CSV.exists():
        metadata["train_manifest_csv"] = pd.read_csv(TRAIN_MANIFEST_CSV)

    if VALID_MANIFEST_CSV.exists():
        metadata["valid_manifest_csv"] = pd.read_csv(VALID_MANIFEST_CSV)

    if LABEL_MAPPING_JSON.exists():
        with open(LABEL_MAPPING_JSON, "r", encoding="utf-8") as f:
            metadata["label_mapping_json"] = json.load(f)

    return metadata


def normalize_x(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x).astype("float32")

    if x.ndim == 2:
        mean = np.mean(x, axis=0, keepdims=True)
        std = np.std(x, axis=0, keepdims=True) + 1e-8
    else:
        axes = tuple(range(1, x.ndim))
        mean = np.mean(x, axis=axes, keepdims=True)
        std = np.std(x, axis=axes, keepdims=True) + 1e-8

    x = (x - mean) / std
    return x


def prepare_labels(train_y: np.ndarray, valid_y: np.ndarray):
    train_y = np.asarray(train_y).astype("int32")
    valid_y = np.asarray(valid_y).astype("int32")

    unique_classes = np.unique(train_y)
    class_to_index = {cls: idx for idx, cls in enumerate(sorted(unique_classes.tolist()))}

    train_y_idx = np.array([class_to_index[v] for v in train_y], dtype="int32")
    valid_y_idx = np.array([class_to_index[v] for v in valid_y], dtype="int32")

    index_to_class = {idx: cls for cls, idx in class_to_index.items()}
    num_classes = len(class_to_index)

    return train_y_idx, valid_y_idx, class_to_index, index_to_class, num_classes


def compute_class_weights(y: np.ndarray, num_classes: int):
    counts = np.bincount(y, minlength=num_classes).astype("float32")
    total = np.sum(counts)

    class_weights = {}
    for i in range(num_classes):
        if counts[i] > 0:
            class_weights[i] = float(total / (num_classes * counts[i]))
        else:
            class_weights[i] = 1.0

    return class_weights


def ensure_channel_dim(x: np.ndarray) -> np.ndarray:
    if x.ndim == 3:
        return np.expand_dims(x, axis=-1)
    return x


def build_dense_model(input_shape, num_classes: int) -> keras.Model:
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        layers.Dense(256, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),

        layers.Dense(128, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),

        layers.Dense(64, activation="relu"),
        layers.Dropout(0.2),

        layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def build_conv1d_model(input_shape, num_classes: int) -> keras.Model:
    model = keras.Sequential([
        layers.Input(shape=input_shape),

        layers.Conv1D(32, kernel_size=5, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.2),

        layers.Conv1D(64, kernel_size=5, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.25),

        layers.Conv1D(128, kernel_size=3, padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling1D(),

        layers.Dense(128, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def build_conv2d_model(input_shape, num_classes: int) -> keras.Model:
    model = keras.Sequential([
        layers.Input(shape=input_shape),

        layers.Conv2D(32, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.2),

        layers.Conv2D(64, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        layers.Conv2D(128, (3, 3), padding="same", activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.3),

        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation="relu"),
        layers.Dropout(0.3),

        layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def build_model(x_train: np.ndarray, num_classes: int) -> keras.Model:
    if x_train.ndim == 2:
        return build_dense_model(input_shape=x_train.shape[1:], num_classes=num_classes)

    if x_train.ndim == 3:
        return build_conv1d_model(input_shape=x_train.shape[1:], num_classes=num_classes)

    if x_train.ndim == 4:
        return build_conv2d_model(input_shape=x_train.shape[1:], num_classes=num_classes)

    raise ValueError(
        f"Неподдерживаемая размерность train_x: {x_train.ndim}. "
        f"Ожидается 2D, 3D или 4D массив."
    )


def save_training_info(
    history,
    class_to_index,
    index_to_class,
    metadata,
    x_train_shape,
    x_valid_shape,
):
    history_path = ARTIFACTS_DIR / "history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history.history, f, ensure_ascii=False, indent=2)

    mapping_path = ARTIFACTS_DIR / "training_label_mapping.json"
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "class_to_index": {str(k): int(v) for k, v in class_to_index.items()},
                "index_to_class": {str(k): int(v) for k, v in index_to_class.items()},
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    meta_path = ARTIFACTS_DIR / "dataset_info.json"
    info = {
        "train_shape": list(x_train_shape),
        "valid_shape": list(x_valid_shape),
        "has_label_mapping_csv": "label_mapping_csv" in metadata,
        "has_train_manifest_csv": "train_manifest_csv" in metadata,
        "has_valid_manifest_csv": "valid_manifest_csv" in metadata,
        "has_label_mapping_json": "label_mapping_json" in metadata,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


def main():
    set_seed(SEED)

    train_x, train_y_raw, valid_x, valid_y_raw = load_dataset(DATASET_PATH)
    metadata = load_optional_metadata()

    train_x = normalize_x(train_x)
    valid_x = normalize_x(valid_x)

    if train_x.ndim == 3 and valid_x.ndim == 3:
        pass
    elif train_x.ndim == 4 and valid_x.ndim == 4:
        pass
    elif train_x.ndim == 2 and valid_x.ndim == 2:
        pass
    else:
        train_x = ensure_channel_dim(train_x)
        valid_x = ensure_channel_dim(valid_x)

    train_y, valid_y, class_to_index, index_to_class, num_classes = prepare_labels(
        train_y_raw, valid_y_raw
    )

    model = build_model(train_x, num_classes=num_classes)
    class_weights = compute_class_weights(train_y, num_classes)

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=str(ARTIFACTS_DIR / "model.h5"),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            mode="max",
            patience=8,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    history = model.fit(
        train_x,
        train_y,
        validation_data=(valid_x, valid_y),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    val_probs = model.predict(valid_x, verbose=0)
    val_pred_idx = np.argmax(val_probs, axis=1)
    val_pred_class_id = np.array([index_to_class[int(i)] for i in val_pred_idx])

    np.savez_compressed(
        ARTIFACTS_DIR / "valid_predictions.npz",
        y_true=valid_y_raw,
        y_pred=val_pred_class_id,
        probabilities=val_probs,
    )

    save_training_info(
        history=history,
        class_to_index=class_to_index,
        index_to_class=index_to_class,
        metadata=metadata,
        x_train_shape=train_x.shape,
        x_valid_shape=valid_x.shape,
    )

