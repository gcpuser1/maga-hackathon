import maga


def test_the_package_is_installed_from_src() -> None:
    assert maga.__version__ == "0.1.0"
