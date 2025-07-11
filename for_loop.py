from pprint import pprint

from mariachi.parser import run

if __name__ == '__main__':

    test_code = """
    sea i = 3
    """
    result, error = run('<test>', test_code)
    pprint((result, error))
