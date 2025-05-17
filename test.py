import onnxruntime

def test_onnxruntime():
    try:
        print("ONNXRuntime version:", onnxruntime.__version__)
        print("Available providers:", onnxruntime.get_available_providers())
    except Exception as e:
        print("ONNXRuntime import or initialization failed:")
        print(e)

if __name__ == "__main__":
    test_onnxruntime()
