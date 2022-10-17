b = 0x5b69
k = 0x87b2

def babyr_enc(block, key):
    """
    block = [h_0, h_1, h_2, h_3] 2*2 matrix
    key = [k_0, k_1, k_2, k_3] 2*2 matrix
    a = initial 8*2 state matrix mapped from block
    E(a) = r_4(r_3(r_2(r_1(a XOR km_0)))) (km: round key)
    r_i(a) = (t * sigHat(S(a))) XOR km_i
        - at each round, apply S -> apply sigHat -> apply multiply t
    
    - S: S operation
    - sigHat: swap entries in 2nd row of the 2*2 state
    - t: an 8*2 matrix
    - in r_4, multiplication by t is omitted.
    - km_i: [w_2i, w_2i+1], where:
        - w_0 = [k_0, k_1]
        - w_1 = [k_2, k_3]
        - w_2i = w_2i-2 XOR S(reverse(w_2i-1)) XOR y_i, and
        - w_2i+1 = w_2i-1 XOR w_2i
            - reverse: interchange 2 entries in a column
            - y_i = [2^i-1, 0]
    """
    return 0

def babyr_dec(block, key):
    """
    D(a) = ri_1(ri_2(ri_3(ri_4(a))))
    ri_i(a) = Si(sigHat(ti * (a XOR km_i)))
        - at each round, XOR km_i -> multiply ti -> apply sigHat -> apply Si
    """
    return 0