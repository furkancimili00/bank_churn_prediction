"""Model dosyalarini yukleyen saf servis modulu."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

import skops.io as sio


@dataclass(frozen=True)
class ModelArtifacts:
    """Tahmin icin gereken model bilesenlerini tasir."""

    model: Any
    scaler: Any
    expected_features: list[str]


def load_model_artifacts(model_path: Union[str, Path]) -> ModelArtifacts:
    """Skops model paketini yukler ve dogrulanmis bilesenleri dondurur.

    Args:
        model_path: Model paketinin dosya yolu.

    Returns:
        ModelArtifacts: Model, scaler ve beklenen ozellik listesi.

    Raises:
        KeyError: Model paketinde zorunlu anahtarlar eksikse.
    """
    resolved_path = Path(model_path)
    untrusted_types = sio.get_untrusted_types(file=str(resolved_path))
    model_pack = sio.load(str(resolved_path), trusted=untrusted_types)

    return ModelArtifacts(
        model=model_pack["model"],
        scaler=model_pack["scaler"],
        expected_features=list(model_pack["features"]),
    )
