import importlib
import inspect
import logging
import sys
import traceback
from enum import Enum
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Dict, Optional

from shared.secrets_resolver import SecretsResolver

MODEL_BASENAME = "model"


class ModelWrapper:
    class Status(Enum):
        NOT_READY = 0
        LOADING = 1
        READY = 2
        FAILED = 3

    _config: Dict
    _model: object
    _load_lock: Lock = Lock()
    _predict_lock: Lock = Lock()
    _status: Status = Status.NOT_READY
    _logger: logging.Logger
    ready: bool
    name: str

    def __init__(self, config: Dict):
        self._config = config
        self.logger = logging.getLogger(__name__)
        self.name = MODEL_BASENAME

    def load(self) -> bool:
        if self.ready:
            return self.ready

        # if we are already loading, just pass; our container will return 503 while we're loading
        if not self._load_lock.acquire(blocking=False):
            return False

        self._status = ModelWrapper.Status.LOADING

        self.logger.info("Executing model.load()...")

        try:
            self.try_load()
            self.ready = True
            self._status = ModelWrapper.Status.READY

            self.logger.info("Completed model.load() execution")

            return self.ready
        except Exception:
            self.logger.exception("Exception while loading model")
            self._status = ModelWrapper.Status.FAILED
        finally:
            self._load_lock.release()

        return self.ready

    def start_load(self):
        if self.should_load():
            thread = Thread(target=self.load)
            thread.start()

    def load_failed(self) -> bool:
        return self._status == ModelWrapper.Status.FAILED

    def should_load(self) -> bool:
        # don't retry failed loads
        return (
            not self._load_lock.locked()
            and not self._status == ModelWrapper.Status.FAILED
            and not self.ready
        )

    def try_load(self):
        if "bundled_packages_dir" in self._config:
            bundled_packages_path = Path("/packages")
            if bundled_packages_path.exists():
                sys.path.append(str(bundled_packages_path))
        model_module_name = str(
            Path(self._config["model_class_filename"]).with_suffix("")
        )
        module = importlib.import_module(
            f"{self._config['model_module_dir']}.{model_module_name}"
        )
        model_class = getattr(module, self._config["model_class_name"])
        model_class_signature = inspect.signature(model_class)
        model_init_params = {}
        if _signature_accepts_keyword_arg(model_class_signature, "config"):
            model_init_params["config"] = self._config
        if _signature_accepts_keyword_arg(model_class_signature, "data_dir"):
            model_init_params["data_dir"] = Path("data")
        if _signature_accepts_keyword_arg(model_class_signature, "secrets"):
            model_init_params["secrets"] = SecretsResolver.get_secrets(self._config)
        self._model = model_class(**model_init_params)

        if hasattr(self._model, "load"):
            self._model.load()

    def preprocess(
        self,
        payload: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        if not hasattr(self._model, "preprocess"):
            return payload
        return self._model.preprocess(payload)  # type: ignore

    def postprocess(
        self,
        response: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        if not hasattr(self._model, "postprocess"):
            return response
        return self._model.postprocess(response)  # type: ignore

    def predict(
        self,
        payload: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        try:
            self._predict_lock.acquire()
            return self._model.predict(payload)  # type: ignore
        except Exception:
            response = {}
            logging.exception("Exception while running predict")
            response["error"] = {"traceback": traceback.format_exc()}
            return response
        finally:
            self._predict_lock.release()

    async def __call__(self, body: Any, headers: Dict[str, str] = None) -> Dict:
        """Method to call predictor or explainer with the given input.

        Args:
            body (Any): Request payload body.
            headers (Dict): Request headers.

        Returns:
            Dict: Response output from preprocess -> predictor -> postprocess
        """
        # TODO(bola): Do we need any of the timing stuff that was dropped here?
        payload = (
            await self.preprocess(body, headers)
            if inspect.iscoroutinefunction(self.preprocess)
            else self.preprocess(body, headers)
        )

        response = (
            (await self.predict(payload, headers))
            if inspect.iscoroutinefunction(self.predict)
            else self.predict(payload, headers)
        )

        response = self.postprocess(response, headers)

        return response


def _signature_accepts_keyword_arg(signature: inspect.Signature, kwarg: str) -> bool:
    return kwarg in signature.parameters or _signature_accepts_kwargs(signature)


def _signature_accepts_kwargs(signature: inspect.Signature) -> bool:
    for param in signature.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False
