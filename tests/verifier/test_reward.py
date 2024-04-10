from fractal.verifier.reward import hashing_function 

def test_hashing_function():
    assert hashing_function(None) == '0000000000000000000000000000000000000000000000000000000000000000'
    assert hashing_function('ubiquitous') == 'e0c5561d19d63fc46a0e574cfbf6b18580cc6828aeae99728bf53e8d79501968' 

