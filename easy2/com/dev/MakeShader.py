from jonlin.utils import Math, Bit


def encode_shader(shader):
    shader_size = len(shader)
    shader_hash = Math.hash_bkdr(shader)
    print(shader_size, shader_hash)
    print('-------------------------------------------')
    print(shader)
    print('-------------------------------------------')

    encrypt_keys = b'shader'
    encrypt_klen = len(encrypt_keys)
    hexes, array = '', []
    for i in range(shader_size):
        s = '0x%x' % (ord(shader[i]) ^ encrypt_keys[i % encrypt_klen])
        array.append(s)
        hexes += s + ','
        if (i + 1) % 32 == 0:
            hexes += '\n'
    encrypt_size = len(array)

    hexes = Bit.bytes2hex(encrypt_keys) + Bit.bytes2hex(Bit.u32_bytes(shader_hash)) + Bit.bytes2hex(Bit.u32_bytes(encrypt_size)) + '\n' + hexes[0:-1]
    encrypt_size += 14  # magic + hash + length
    print(('[%d]={\n' % encrypt_size) + hexes + '\n};')
    print('-------------------------------------------')
    shader = ''
    for c in array:
        shader += chr(int(c, 16))
    print(shader)
    print('-------------------------------------------')