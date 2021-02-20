def raw(data_bytes):
    return f"{data_bytes}"[2:-1]
def ascii(data_bytes):
    try:
        data_str = data_bytes.decode('utf-8') #read the bytes and convert from binary array to ASCII
        data_str=data_str.replace('\b', "\\b") 
        data_str=data_str.replace('\t', "\\t") 
        data_str=data_str.replace('\n', "\\n\n") 
        data_str=data_str.replace('\f', "\\f") 
        data_str=data_str.replace('\r', "\\r") 
    except UnicodeDecodeError as e:
        print (e)
        data_str=raw(data_bytes)
    return data_str
def hex(data_bytes):
    data_str=' '.join(format(x, '02X') for x in data_bytes)
    data_str=data_str.replace('0A', "0A\n") 
    return data_str
def dec(data_bytes):
    data_str=' '.join(format(x, '3') for x in data_bytes)
    data_str=data_str.replace('  10', "  10\n") 
    return data_str