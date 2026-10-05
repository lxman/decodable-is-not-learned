"""Import first in EVERY synthetic entry point; deliberately no optional bypass."""
import sys
import builtins

BLOCKED = frozenset({"torch", "transformers", "mlx", "mlx_lm", "mlx_vlm",
    "huggingface_hub", "tokenizers", "safetensors", "datasets", "accelerate",
    "hf_xet", "sentencepiece", "socket", "_socket", "ssl", "_ssl", "http",
    "httpx", "requests", "aiohttp", "ftplib", "smtplib", "websockets", "boto3",
    "botocore", "paramiko", "experiments", "torchvision", "torchaudio", "jax", "jaxlib",
    "tensorflow", "keras", "vllm", "llama_cpp", "onnxruntime", "subprocess",
    "multiprocessing", "_posixsubprocess", "ctypes"})

def forbidden(name):
    return name.split(".")[0] in BLOCKED or (name.startswith("urllib.") and name != "urllib.parse")

if any(forbidden(n) for n in sys.modules):
    raise RuntimeError("guard installed after forbidden import")
attempts = []
original_import = builtins.__import__

def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if forbidden(name):
        attempts.append(name)
        raise ImportError("HARD-REFUSED: " + name)
    return original_import(name, globals, locals, fromlist, level)

class Finder:
    def find_spec(self, fullname, path=None, target=None):
        if forbidden(fullname):
            attempts.append(fullname)
            raise ImportError("HARD-REFUSED: " + fullname)
        return None

def audit(event, args):
    if event == "import" and forbidden(args[0]):
        attempts.append(args[0])
        raise ImportError("HARD-REFUSED: " + args[0])
    if event.startswith("socket.") or event in {"subprocess.Popen", "os.system",
            "os.posix_spawn", "os.fork", "os.forkpty", "os.exec", "pty.spawn",
            "ctypes.dlopen", "ctypes.dlsym"}:
        raise RuntimeError("HARD-REFUSED operation: " + event)

builtins.__import__ = guarded_import
sys.meta_path.insert(0, Finder())
sys.addaudithook(audit)
sys.dont_write_bytecode = True
