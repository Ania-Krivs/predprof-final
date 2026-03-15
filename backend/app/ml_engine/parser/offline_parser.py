from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HEX_PREFIX_RE = re.compile(r"^[0-9a-f]{32}", re.IGNORECASE)
INT_LABEL_RE = re.compile(r"^\d+$")


def load_dataset(npz_path: str):
    data = np.load(npz_path, allow_pickle=True)

    required = {"train_x", "train_y", "valid_x", "valid_y"}
    missing = required - set(data.files)
    if missing:
        raise ValueError(f"В архиве отсутствуют массивы: {sorted(missing)}")

    train_x = data["train_x"]
    train_y = data["train_y"]
    valid_x = data["valid_x"]
    valid_y = data["valid_y"]

    return train_x, train_y, valid_x, valid_y


def to_str(x) -> str:
    if isinstance(x, bytes):
        return x.decode("utf-8", errors="ignore")
    return str(x)


def clean_label(label) -> str:
    label = to_str(label).strip()
    label = HEX_PREFIX_RE.sub("", label)
    label = label.strip().lower()
    label = label.replace(" ", "_")
    label = re.sub(r"[^a-z0-9_\-]+", "_", label)
    label = re.sub(r"[_\-]{2,}", "_", label)
    label = label.strip("_")

    if not label:
        raise ValueError("После очистки метка стала пустой строкой")

    return label


def prepare_audio(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)

    if x.ndim == 3 and x.shape[-1] == 1:
        x = x[..., 0]

    if x.ndim != 2:
        raise ValueError(
            f"Ожидалась форма (N, T) или (N, T, 1), получено: {x.shape}"
        )

    max_abs = np.max(np.abs(x), axis=1, keepdims=True)
    max_abs[max_abs < 1e-8] = 1.0
    x = x / max_abs

    return x.astype(np.float32)


def clean_label_array(y: np.ndarray) -> np.ndarray:
    return np.array([clean_label(v) for v in y], dtype=object)


def label_sort_key(label: str):
    if INT_LABEL_RE.fullmatch(label):
        return (0, int(label))
    return (1, label)


def build_global_label_mapping(train_clean: np.ndarray, valid_clean: np.ndarray):
    train_set = set(train_clean.tolist())
    valid_set = set(valid_clean.tolist())

    all_labels = sorted(train_set | valid_set, key=label_sort_key)
    label_to_class_id = {label: idx for idx, label in enumerate(all_labels)}
    class_id_to_label = {idx: label for label, idx in label_to_class_id.items()}

    train_counts = pd.Series(train_clean).value_counts()
    valid_counts = pd.Series(valid_clean).value_counts()

    rows = []
    for label in all_labels:
        rows.append(
            {
                "class_id": label_to_class_id[label],
                "clean_label": label,
                "in_train": label in train_set,
                "in_valid": label in valid_set,
                "train_count": int(train_counts.get(label, 0)),
                "valid_count": int(valid_counts.get(label, 0)),
            }
        )

    mapping_df = pd.DataFrame(rows).sort_values("class_id").reset_index(drop=True)

    only_train = sorted(train_set - valid_set, key=label_sort_key)
    only_valid = sorted(valid_set - train_set, key=label_sort_key)

    return label_to_class_id, class_id_to_label, mapping_df, only_train, only_valid


def encode_labels(clean_y: np.ndarray, label_to_class_id: dict[str, int]) -> np.ndarray:
    return np.array([label_to_class_id[label] for label in clean_y], dtype=np.int64)


def save_outputs(
    out_dir: Path,
    train_x: np.ndarray,
    train_y: np.ndarray,
    valid_x: np.ndarray,
    valid_y: np.ndarray,
    raw_train_y: np.ndarray,
    raw_valid_y: np.ndarray,
    clean_train_y: np.ndarray,
    clean_valid_y: np.ndarray,
    mapping_df: pd.DataFrame,
    label_to_class_id: dict[str, int],
    class_id_to_label: dict[int, str],
    only_train: list[str],
    only_valid: list[str],
):
    out_dir.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        out_dir / "processed_dataset.npz",
        train_x=train_x.astype(np.float32),
        train_y=train_y.astype(np.int64),
        valid_x=valid_x.astype(np.float32),
        valid_y=valid_y.astype(np.int64),
    )

    train_manifest = pd.DataFrame(
        {
            "sample_id": np.arange(len(raw_train_y)),
            "raw_label": [to_str(x) for x in raw_train_y],
            "clean_label": clean_train_y,
            "class_id": train_y,
        }
    )

    valid_manifest = pd.DataFrame(
        {
            "sample_id": np.arange(len(raw_valid_y)),
            "raw_label": [to_str(x) for x in raw_valid_y],
            "clean_label": clean_valid_y,
            "class_id": valid_y,
        }
    )

    train_manifest.to_csv(out_dir / "train_manifest.csv", index=False)
    valid_manifest.to_csv(out_dir / "valid_manifest.csv", index=False)
    mapping_df.to_csv(out_dir / "label_mapping.csv", index=False)

    json_payload = {
        "label_to_class_id": {k: int(v) for k, v in label_to_class_id.items()},
        "class_id_to_label": {str(k): v for k, v in class_id_to_label.items()},
        "only_in_train": only_train,
        "only_in_valid": only_valid,
    }

    with open(out_dir / "label_mapping.json", "w", encoding="utf-8") as f:
        json.dump(json_payload, f, ensure_ascii=False, indent=2)

    stats = {
        "train_samples": int(len(train_x)),
        "valid_samples": int(len(valid_x)),
        "train_unique_clean_labels": int(len(set(clean_train_y.tolist()))),
        "valid_unique_clean_labels": int(len(set(clean_valid_y.tolist()))),
        "total_unique_labels": int(len(label_to_class_id)),
        "signal_length": int(train_x.shape[1]),
        "only_in_train_count": int(len(only_train)),
        "only_in_valid_count": int(len(only_valid)),
    }

    with open(out_dir / "dataset_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def main(npz_path: str, out_dir: str):
    train_x, train_y_raw, valid_x, valid_y_raw = load_dataset(npz_path)

    train_x = prepare_audio(train_x)
    valid_x = prepare_audio(valid_x)

    clean_train_y = clean_label_array(train_y_raw)
    clean_valid_y = clean_label_array(valid_y_raw)

    label_to_class_id, class_id_to_label, mapping_df, only_train, only_valid = build_global_label_mapping(
        clean_train_y,
        clean_valid_y,
    )

    train_y = encode_labels(clean_train_y, label_to_class_id)
    valid_y = encode_labels(clean_valid_y, label_to_class_id)

    save_outputs(
        out_dir=Path(out_dir),
        train_x=train_x,
        train_y=train_y,
        valid_x=valid_x,
        valid_y=valid_y,
        raw_train_y=train_y_raw,
        raw_valid_y=valid_y_raw,
        clean_train_y=clean_train_y,
        clean_valid_y=clean_valid_y,
        mapping_df=mapping_df,
        label_to_class_id=label_to_class_id,
        class_id_to_label=class_id_to_label,
        only_train=only_train,
        only_valid=only_valid,
    )

    print("Готово.")
    print(f"train_x shape: {train_x.shape}")
    print(f"valid_x shape: {valid_x.shape}")
    print(f"Уникальных cleaned train labels: {len(set(clean_train_y.tolist()))}")
    print(f"Уникальных cleaned valid labels: {len(set(clean_valid_y.tolist()))}")
    print(f"Всего уникальных классов: {len(label_to_class_id)}")

    if only_train:
        print(f"Метки только в train ({len(only_train)}): {only_train[:10]}")
    if only_valid:
        print(f"Метки только в valid ({len(only_valid)}): {only_valid[:10]}")
    if not only_train and not only_valid:
        print("Наборы классов train и valid совпадают после очистки.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline parser для alien signal dataset")
    parser.add_argument("--input", required=True, help="Путь к исходному .npz")
    parser.add_argument("--output", required=True, help="Папка для сохранения результатов")
    args = parser.parse_args()

    main(npz_path=args.input, out_dir=args.output)