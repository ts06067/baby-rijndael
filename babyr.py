enc_block_set = [0x5b69, 0x8f57]
enc_key_set = [0x87b2, 0x5274]

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
    # Assume block size of 16 bits, default round No. 4.

    # basic configuration
    t = [[1,0,1,0,0,0,1,1], [1,1,0,1,0,0,0,1], [1,1,1,0,1,0,0,0], [0,1,0,1,0,1,1,1], [0,0,1,1,1,0,1,0], [0,0,0,1,1,1,0,1], [1,0,0,0,1,1,1,0], [0,1,1,1,0,1,0,1]]

    # set bit mask
    m0 = 0xf000
    m1 = 0x0f00
    m2 = 0x00f0
    m3 = 0x000f

    # get state entries
    h0 = (block & m0) >> 12
    h1 = (block & m1) >> 8
    h2 = (block & m2) >> 4
    h3 = block & m3

    # get key entries
    k0 = (key & m0) >> 12
    k1 = (key & m1) >> 8
    k2 = (key & m2) >> 4
    k3 = (key & m3)

    # make state
    a = [h0, h1, h2, h3]
    k = [k0, k1, k2, k3]

    #configure round keys km_0...4
    km_list = [get_key_m(k, i) + get_key_m(k, i+1) for i in range(0, 10, 2)]

    # round operation
    for i in range(5):
        # before round
        if i == 0:
            a = XOR_m(a, km_list[i], 4)
        # final round
        elif i == 4:
            a = XOR_m(sig_hat_operation(S_operation(a)), km_list[i], 4)
        else:
            a = XOR_m(mult_m(t, sig_hat_operation(S_operation(a))), km_list[i], 4)
    return a

def mult_m(t, x):
    # input: t: binary matrix 8*8, x: original
    bin_x_m = convert_to_bin_m(x) # now 8*2

    product_m = [[], []] # size 8*2

    for i in range(2):
        for j in range(8):
            sum = 0
            for k in range(8):
                sum += bin_x_m[i][k] * t[j][k]
            product_m[i].append(sum%2)
    
    product_m = [product_m[0][:4], product_m[0][4:], product_m[1][:4], product_m[1][4:]] # intermediate 4*4 form

    res_m = []  # final hex size 4 arr
    for n in product_m:
        x3 = n[0] * 8
        x2 = n[1] * 4
        x1 = n[2] * 2
        x0 = n[3]
        res_m.append(x3 + x2 + x1 + x0)
    return res_m

def convert_to_bin_m(x):
    # input: x: size 4, output: 8*2
    m0 = 0x1
    m1 = 0x2
    m2 = 0x4
    m3 = 0x8

    bin_m = [] # intermediate 4*4 form
    for i in range(4):
        x3 = x[i]&m3
        x2 = x[i]&m2
        x1 = x[i]&m1
        x0 = x[i]&m0
        xi = [x3, x2, x1, x0]
        for i in range(4):
            if xi[i] > 0:
                xi[i] = 1
        bin_m.append(xi)
    return [bin_m[0]+bin_m[1], bin_m[2]+bin_m[3]] # final 8*2 form


def XOR_m(x, y, l):
    # assume x, y of same size
    # execute XOR operation for each entry
    for i in range(l):
        x[i] = x[i] ^ y[i]
    return x

def reverse_m(x):
    # assume size 2
    tmp = x[0]
    x[0] = x[1]
    x[1] = tmp
    return x

def S_operation(x):
    S_table = [10, 4, 3, 11, 8, 14, 2, 12, 5, 7, 6, 15, 0, 1, 9, 13]
    for i in range(len(x)):
        x[i] = S_table[x[i]]
    return x

def sig_hat_operation(x):
    # assume size 4
    tmp = x[1]
    x[1] = x[3]
    x[3] = tmp
    return x

def get_y_m(n):
    # assume n is between 1-4
    return [2**(n-1), 0]

def get_key_m(key, key_id):
    #input: key: [k0, k1, k2, k3], key_id: 0-4
    k0 = key[0]
    k1 = key[1]
    k2 = key[2]
    k3 = key[3]

    if key_id == 0:
        return [k0, k1]
    elif key_id == 1:
        return [k2, k3]
    else:
        if key_id%2 == 0:
            return XOR_m(XOR_m(get_key_m(key, key_id-2), S_operation(reverse_m(get_key_m(key, key_id-1))), 2), get_y_m(key_id//2), 2)
        else:
            return XOR_m(get_key_m(key, key_id-2), get_key_m(key, key_id-1), 2)

def babyr_dec(block, key):
    """
    D(a) = ri_1(ri_2(ri_3(ri_4(a))))
    ri_i(a) = Si(sigHat(ti * (a XOR km_i)))
        - at each round, XOR km_i -> multiply ti -> apply sigHat -> apply Si
    """
    return 0

for i in range(2):
    print("encrypted block: ", babyr_enc(enc_block_set[i], enc_key_set[i]))