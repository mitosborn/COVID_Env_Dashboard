import sys
from importlib import import_module
from expected import results

def test_buggy_impl(impl_path, fname, args):
    path = impl_path.split("/")
    mod_name = path[-1][:-3]
    pkg_name = ".".join(path[:-1])[1:]
    mod = import_module(mod_name, package = pkg_name)
    func = getattr(mod,fname)
    actual = func(*args)
    expected = results[case_num]
    return (actual == expected)

if __name__ == "__main__":
    case_num = int(sys.argv[1])
    impl_path = sys.argv[2]
    fname = sys.argv[3]
    args = sys.argv[4:]
    new_args = [eval(arg) for arg in args]
    print (test_buggy_impl(impl_path, fname, new_args))
