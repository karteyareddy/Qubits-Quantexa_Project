"""Validated JSON cache for normalized network contracts."""

from hashlib import sha256
from pathlib import Path

from pydantic import ValidationError

from app.domain.network import Network


class NetworkCache:
    """Best-effort cache that never loads executable pickle content."""

    def __init__(self, cache_dir: Path, *, enabled: bool = True) -> None:
        self.cache_dir = cache_dir
        self.enabled = enabled

    def path_for(self, cache_key: str) -> Path:
        digest = sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def load(self, cache_key: str) -> Network | None:
        if not self.enabled:
            return None
        path = self.path_for(cache_key)
        try:
            return Network.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, ValidationError):
            return None

    def save(self, cache_key: str, network: Network) -> bool:
        if not self.enabled:
            return False
        path = self.path_for(cache_key)
        temporary_path = path.with_suffix(".tmp")
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(network.model_dump_json(indent=2), encoding="utf-8")
            temporary_path.replace(path)
        except OSError:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            return False
        return True
