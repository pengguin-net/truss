
from typing import Set
from truss.constants import PYTORCH_DIRECTML_REQ_MODULE_NAMES
from truss.model_frameworks.pytorch import PyTorch


class PytorchDirectML(PyTorch):
    def required_python_depedencies(self) -> Set[str]:
        return PYTORCH_DIRECTML_REQ_MODULE_NAMES

