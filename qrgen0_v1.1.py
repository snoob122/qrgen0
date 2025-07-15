#-----------------------------QRGEN0-BY-BEAN------------------------------------------------------------------------------
# Starting
print("-----qrgen0_v1.1----- \n- (Version 1 - 40) \n- (Numeric, Alphanumeric, Byte Encoding Mode) \n- Some Extra Features \n ---- Made By Bean ---- \n - Feel Free To Use This Material For Your Purposes -\n\n")
using_cli = True

# ------------------- Functions -----------------------
# --Algorithmic Generators

# Generate EC Codewords
def generate_ecc_codewords(data_codewords, num_ecc):

    # Data_codewords can be a list of int then it won't need any further process else:
    # Data_codewords is a list of str e.g. ["10010101", "10001100"]
    # Here it will be automatically converted to int and parse through

    is_decimal_formatted = True
    for i in data_codewords:
        if isinstance(i, str):
            is_decimal_formatted = False

    if not is_decimal_formatted:
        data_codewords = [int(("0b" + _), 2) for _ in data_codewords]

    # --- Generate log and exp tables ---
    antilog_table = [1]
    log_table = [0]
    for i in range(255):
        antilog_table.append(antilog_table[i]*2 if antilog_table[i]*2 < 256 else (antilog_table[i]*2)^285)

    for i in range(1, 256):
        log_table.append(antilog_table.index(i))

    def mult(a, b):
        return antilog_table[(log_table[a] + log_table[b]) % 255]

    # --- Get Generator Polynomial ---
    def get_poly_gen(poly_1, poly_2):
        result_length = len(poly_1) + len(poly_2) - 1
        coeffs = [0] * result_length

        for index in range(result_length):
            coeff = 0
            for poly_1_index in range(index + 1):
                poly_2_index = index - poly_1_index

                if poly_1_index < len(poly_1) and poly_2_index < len(poly_2):
                    coeff ^= mult(poly_1[poly_1_index], poly_2[poly_2_index])
            coeffs[index] = coeff
        return coeffs

    cur_poly = [1]
    for element in range(num_ecc):
        cur_poly = get_poly_gen(cur_poly, [1, antilog_table[element]])

    buffer = list(data_codewords) + [0] * num_ecc

    for i in range(len(data_codewords)):
        coef = buffer[i]
        if coef != 0:
            for j in range(len(cur_poly)):
                buffer[i + j] ^= mult(cur_poly[j], coef)

    return buffer[-num_ecc:]

# Generate BCH EC Codewords
def bch_ecc_gen(format_string):
    original_string = format_string
    format_string += "0" * 10
    bch_poly_gen = "10100110111"

    while len(format_string) >= 11:
        temp = ""
        divide_bpg = bch_poly_gen + "0" * (len(format_string) - 11)
        for i in range(len(format_string)):
            temp += "0" if format_string[i] == divide_bpg[i] else "1"
        temp = str(int(temp))

        format_string = temp

    format_bits = original_string + format_string.zfill(10)
    format_mask = "101010000010010"
    format_bits = int(format_bits, 2) ^ int(format_mask, 2)
    return bin(format_bits)[2:].zfill(15)

# -- Processing Specific Steps in QR generation
# Masking Optimization
# EVAL 1
def evaluate_score_condition_1(matrix):
    penalty = 0
    count = 1

    for row in matrix:
        for i in range(len(matrix)-1):
            if row[i] == row[i + 1]:
                count += 1
            else:
                if count >= 5:
                    penalty += 3 + (count - 5)
                count = 1
    count = 1

    for index in range(len(matrix)):
        for column_index in range(len(matrix[index]) - 1):
            if matrix[column_index][index] == matrix[column_index+1][index]:
                count += 1
            else:
                if count >= 5:
                    penalty += 3 + (count - 5)
                count = 1

    return penalty

# EVAL 2
def evaluate_score_condition_2(matrix):
    penalty = 0

    for y in range(len(matrix)-1):
        for x in range(len(matrix)-1):
            block_check = [matrix[y][x], matrix[y][x+1], matrix[y+1][x+1], matrix[y+1][x]]
            if block_check[0] == block_check[1] == block_check[2] == block_check[3]:
                penalty += 3

    return penalty

# EVAL 3
def evaluate_score_condition_3(matrix):
    penalty = 0

    pattern = ['1','0','1','1','1','0','1']

    for row in matrix:
        for i in range(len(row)-10):
            if row[i:i+7] == pattern:
                if row[i:i + 7] == pattern and \
                        (row[i + 7:i + 11] == ['0', '0', '0', '0'] or row[i - 4:i] == ['0', '0', '0', '0']):
                    penalty += 40
                    penalty += 40

    for y in range(len(matrix)):
        column_list = []
        for x in range(len(matrix)):
            column_list.append(matrix[x][y])

        for i in range(len(column_list)-10):
            if column_list[i:i+7] == pattern:
                if column_list[i+7:i+11] == pattern or column_list[i-4:i] == pattern:
                    penalty += 40

    return penalty

# EVAL 4
def evaluate_score_condition_4(matrix):

    dark = 0
    total = 0

    for y in range(len(matrix)):
        for x in range(len(matrix)):
            if matrix[x][y] == 1:
                dark += 1
            total += 1

    darktototal = round((dark/total)*100)
    prev = darktototal
    next = darktototal

    while prev % 5 != 0:
        prev -= 1
    while next % 5 != 0:
        next += 1

    return int(min(abs(prev-50), abs(next-50))*10)

# -- Getting Required Qr Code Data

# Getting Alignment Patterns Center Coordinates
def get_APs_center_coordinates(version_num):
    center_table = {
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
    15: [6, 26, 48, 70],
    16: [6, 26, 50, 74],
    17: [6, 30, 54, 78],
    18: [6, 30, 56, 82],
    19: [6, 30, 58, 86],
    20: [6, 34, 62, 90],
    21: [6, 28, 50, 72, 94],
    22: [6, 26, 50, 74, 98],
    23: [6, 30, 54, 78, 102],
    24: [6, 28, 54, 80, 106],
    25: [6, 32, 58, 84, 110],
    26: [6, 30, 58, 86, 114],
    27: [6, 34, 62, 90, 118],
    28: [6, 26, 50, 74, 98, 122],
    29: [6, 30, 54, 78, 102, 126],
    30: [6, 26, 52, 78, 104, 130],
    31: [6, 30, 56, 82, 108, 134],
    32: [6, 34, 60, 86, 112, 138],
    33: [6, 30, 58, 86, 114, 142],
    34: [6, 34, 62, 90, 118, 146],
    35: [6, 30, 54, 78, 102, 126, 150],
    36: [6, 24, 50, 76, 102, 128, 154],
    37: [6, 28, 54, 80, 106, 132, 158],
    38: [6, 32, 58, 84, 110, 136, 162],
    39: [6, 26, 54, 82, 110, 138, 166],
    40: [6, 30, 58, 86, 114, 142, 170]
    }

    matrix_size = 21 + 4 * (version_num - 1)
    center_coords = center_table.get(version_num)
    coords = []
    for x in center_coords:
        for y in center_coords:
            if (x == 6 and y == 6) or (x == matrix_size - 7 and y == 6) or (x == 6 and y == matrix_size - 7):
                continue
            else:
                coords.append([y, x])
    return coords

# Getting Character Count Indicator
def get_char_count_indicator(version, encode_mode):
    if version is None or encode_mode is None:
        return None

    if 1 <= version <= 9:
        if encode_mode == 1:
            return 10
        elif encode_mode == 2:
            return 9
        elif encode_mode == 3:
            return 8
        elif encode_mode == 4:
            return 8
        return None
    elif 10 <= version <= 26:
        if encode_mode == 1:
            return 12
        elif encode_mode == 2:
            return 11
        elif encode_mode == 3:
            return 16
        elif encode_mode == 4:
            return 10
        return None
    else:
        if encode_mode == 1:
            return 14
        elif encode_mode == 2:
            return 13
        elif encode_mode == 3:
            return 16
        elif encode_mode == 4:
            return 12
        return None


# Getting Data Of Data Blocks
def get_block_data(version_num, error_correction_level):
    block_structure = {
        (1, 'L'): {"num_blocks": 1, "block_sizes": [19], "ecc_per_block": 7},
        (1, 'M'): {"num_blocks": 1, "block_sizes": [16], "ecc_per_block": 10},
        (1, 'Q'): {"num_blocks": 1, "block_sizes": [13], "ecc_per_block": 13},
        (1, 'H'): {"num_blocks": 1, "block_sizes": [9], "ecc_per_block": 17},

        (2, 'L'): {"num_blocks": 1, "block_sizes": [34], "ecc_per_block": 10},
        (2, 'M'): {"num_blocks": 1, "block_sizes": [28], "ecc_per_block": 16},
        (2, 'Q'): {"num_blocks": 1, "block_sizes": [22], "ecc_per_block": 22},
        (2, 'H'): {"num_blocks": 1, "block_sizes": [16], "ecc_per_block": 28},

        (3, 'L'): {"num_blocks": 1, "block_sizes": [55], "ecc_per_block": 15},
        (3, 'M'): {"num_blocks": 1, "block_sizes": [44], "ecc_per_block": 26},
        (3, 'Q'): {"num_blocks": 2, "block_sizes": [17, 17], "ecc_per_block": 18},
        (3, 'H'): {"num_blocks": 2, "block_sizes": [13, 13], "ecc_per_block": 22},

        (4, 'L'): {"num_blocks": 1, "block_sizes": [80], "ecc_per_block": 20},
        (4, 'M'): {"num_blocks": 2, "block_sizes": [32, 32], "ecc_per_block": 18},
        (4, 'Q'): {"num_blocks": 2, "block_sizes": [24, 24], "ecc_per_block": 26},
        (4, 'H'): {"num_blocks": 4, "block_sizes": [9, 9, 9, 9], "ecc_per_block": 16},

        (5, 'L'): {"num_blocks": 1, "block_sizes": [108], "ecc_per_block": 26},
        (5, 'M'): {"num_blocks": 2, "block_sizes": [43, 43], "ecc_per_block": 24},
        (5, 'Q'): {"num_blocks": 4, "block_sizes": [15, 15, 16, 16], "ecc_per_block": 18},
        (5, 'H'): {"num_blocks": 4, "block_sizes": [11, 11, 12, 12], "ecc_per_block": 22},

        (6, 'L'): {"num_blocks": 2, "block_sizes": [68, 68], "ecc_per_block": 18},
        (6, 'M'): {"num_blocks": 4, "block_sizes": [27, 27, 27, 27], "ecc_per_block": 16},
        (6, 'Q'): {"num_blocks": 4, "block_sizes": [19, 19, 19, 19], "ecc_per_block": 24},
        (6, 'H'): {"num_blocks": 4, "block_sizes": [15, 15, 15, 15], "ecc_per_block": 28},

        (7, 'L'): {"num_blocks": 2, "block_sizes": [78, 78], "ecc_per_block": 20},
        (7, 'M'): {"num_blocks": 4, "block_sizes": [31, 31, 31, 31], "ecc_per_block": 18},
        (7, 'Q'): {"num_blocks": 6, "block_sizes": [14, 14, 15, 15, 15, 15], "ecc_per_block": 18},
        (7, 'H'): {"num_blocks": 5, "block_sizes": [13, 13, 13, 13, 14], "ecc_per_block": 26},

        (8, 'L'): {"num_blocks": 2, "block_sizes": [97, 97], "ecc_per_block": 24},
        (8, 'M'): {"num_blocks": 4, "block_sizes": [38, 38, 39, 39], "ecc_per_block": 22},
        (8, 'Q'): {"num_blocks": 6, "block_sizes": [18, 18, 18, 18, 19, 19], "ecc_per_block": 22},
        (8, 'H'): {"num_blocks": 6, "block_sizes": [14, 14, 14, 14, 15, 15], "ecc_per_block": 26},

        (9, 'L'): {"num_blocks": 2, "block_sizes": [116, 116], "ecc_per_block": 30},
        (9, 'M'): {"num_blocks": 5, "block_sizes": [36, 36, 36, 37, 37], "ecc_per_block": 22},
        (9, 'Q'): {"num_blocks": 8, "block_sizes": [16, 16, 16, 16, 17, 17, 17, 17], "ecc_per_block": 20},
        (9, 'H'): {"num_blocks": 8, "block_sizes": [12, 12, 12, 12, 13, 13, 13, 13], "ecc_per_block": 24},

        (10, 'L'): {"num_blocks": 4, "block_sizes": [68, 68, 69, 69], "ecc_per_block": 18},
        (10, 'M'): {"num_blocks": 5, "block_sizes": [43, 43, 43, 43, 44], "ecc_per_block": 26},
        (10, 'Q'): {"num_blocks": 8, "block_sizes": [19, 19, 19, 19, 19, 19, 20, 20], "ecc_per_block": 24},
        (10, 'H'): {"num_blocks": 8, "block_sizes": [15, 15, 15, 15, 15, 15, 16, 16], "ecc_per_block": 28},

        (11, 'L'): {"num_blocks": 4, "block_sizes": [81, 81, 81, 81], "ecc_per_block": 20},
        (11, 'M'): {"num_blocks": 5, "block_sizes": [50, 51, 51, 51, 51], "ecc_per_block": 30},
        (11, 'Q'): {"num_blocks": 8, "block_sizes": [22, 22, 22, 22, 23, 23, 23, 23], "ecc_per_block": 28},
        (11, 'H'): {"num_blocks": 11, "block_sizes": [12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13], "ecc_per_block": 24},

        (12, 'L'): {"num_blocks": 4, "block_sizes": [92, 92, 93, 93], "ecc_per_block": 24},
        (12, 'M'): {"num_blocks": 8, "block_sizes": [36, 36, 36, 36, 36, 36, 37, 37], "ecc_per_block": 22},
        (12, 'Q'): {"num_blocks": 10, "block_sizes": [20, 20, 20, 20, 21, 21, 21, 21, 21, 21], "ecc_per_block": 26},
        (12, 'H'): {"num_blocks": 11, "block_sizes": [14]*7 + [15]*4, "ecc_per_block": 28},

        (13, 'L'): {"num_blocks": 4, "block_sizes": [107]*4, "ecc_per_block": 26},
        (13, 'M'): {"num_blocks": 9, "block_sizes": [37]*8 + [38], "ecc_per_block": 22},
        (13, 'Q'): {"num_blocks": 12, "block_sizes": [20]*8 + [21]*4, "ecc_per_block": 24},
        (13, 'H'): {"num_blocks": 16, "block_sizes": [11]*12 + [12]*4, "ecc_per_block": 22},

        (14, 'L'): {"num_blocks": 4, "block_sizes": [115]*3 + [116], "ecc_per_block": 30},
        (14, 'M'): {"num_blocks": 9, "block_sizes": [40]*4 + [41]*5, "ecc_per_block": 24},
        (14, 'Q'): {"num_blocks": 16, "block_sizes": [16]*11 + [17]*5, "ecc_per_block": 20},
        (14, 'H'): {"num_blocks": 16, "block_sizes": [12]*11 + [13]*5, "ecc_per_block": 24},

        (15, 'L'): {"num_blocks": 6, "block_sizes": [87]*5 + [88], "ecc_per_block": 22},
        (15, 'M'): {"num_blocks": 10, "block_sizes": [41]*5 + [42]*5, "ecc_per_block": 24},
        (15, 'Q'): {"num_blocks": 12, "block_sizes": [24]*5 + [25]*7, "ecc_per_block": 30},
        (15, 'H'): {"num_blocks": 18, "block_sizes": [12]*11 + [13]*7, "ecc_per_block": 24},

        (16, 'L'): {"num_blocks": 6, "block_sizes": [98]*5 + [99], "ecc_per_block": 24},
        (16, 'M'): {"num_blocks": 10, "block_sizes": [45]*7 + [46]*3, "ecc_per_block": 28},
        (16, 'Q'): {"num_blocks": 17, "block_sizes": [19]*15 + [20]*2, "ecc_per_block": 24},
        (16, 'H'): {"num_blocks": 16, "block_sizes": [15]*3 + [16]*13, "ecc_per_block": 30},

        (17, 'L'): {"num_blocks": 6, "block_sizes": [107] + [108]*5, "ecc_per_block": 28},
        (17, 'M'): {"num_blocks": 11, "block_sizes": [46]*10 + [47], "ecc_per_block": 28},
        (17, 'Q'): {"num_blocks": 16, "block_sizes": [22] + [23]*15, "ecc_per_block": 28},
        (17, 'H'): {"num_blocks": 19, "block_sizes": [14]*2 + [15]*17, "ecc_per_block": 28},

        (18, 'L'): {"num_blocks": 6, "block_sizes": [120]*5 + [121], "ecc_per_block": 30},
        (18, 'M'): {"num_blocks": 13, "block_sizes": [43]*9 + [44]*4, "ecc_per_block": 26},
        (18, 'Q'): {"num_blocks": 18, "block_sizes": [22]*17 + [23], "ecc_per_block": 28},
        (18, 'H'): {"num_blocks": 21, "block_sizes": [14]*2 + [15]*19, "ecc_per_block": 28},

        (19, 'L'): {"num_blocks": 7, "block_sizes": [113]*3 + [114]*4, "ecc_per_block": 28},
        (19, 'M'): {"num_blocks": 14, "block_sizes": [44]*3 + [45]*11, "ecc_per_block": 26},
        (19, 'Q'): {"num_blocks": 21, "block_sizes": [21]*17 + [22]*4, "ecc_per_block": 26},
        (19, 'H'): {"num_blocks": 25, "block_sizes": [13]*9 + [14]*16, "ecc_per_block": 26},

        (20, 'L'): {"num_blocks": 8, "block_sizes": [107]*3 + [108]*5, "ecc_per_block": 28},
        (20, 'M'): {"num_blocks": 16, "block_sizes": [41]*3 + [42]*13, "ecc_per_block": 26},
        (20, 'Q'): {"num_blocks": 20, "block_sizes": [24]*15 + [25]*5, "ecc_per_block": 30},
        (20, 'H'): {"num_blocks": 25, "block_sizes": [15]*15 + [16]*10, "ecc_per_block": 28},

        (21, 'L'): {"num_blocks": 8, "block_sizes": [116]*4 + [117]*4, "ecc_per_block": 28},
        (21, 'M'): {"num_blocks": 17, "block_sizes": [42]*17, "ecc_per_block": 26},
        (21, 'Q'): {"num_blocks": 23, "block_sizes": [22]*17 + [23]*6, "ecc_per_block": 28},
        (21, 'H'): {"num_blocks": 25, "block_sizes": [16]*19 + [17]*6, "ecc_per_block": 30},

        (22, 'L'): {"num_blocks": 9, "block_sizes": [111]*2 + [112]*7, "ecc_per_block": 28},
        (22, 'M'): {"num_blocks": 17, "block_sizes": [46]*17, "ecc_per_block": 28},
        (22, 'Q'): {"num_blocks": 23, "block_sizes": [24]*7 + [25]*16, "ecc_per_block": 30},
        (22, 'H'): {"num_blocks": 34, "block_sizes": [13]*34, "ecc_per_block": 24},

        (23, 'L'): {"num_blocks": 9, "block_sizes": [121] * 4 + [122] * 5, "ecc_per_block": 30},
        (23, 'M'): {"num_blocks": 18, "block_sizes": [47] * 4 + [48] * 14, "ecc_per_block": 28},
        (23, 'Q'): {"num_blocks": 25, "block_sizes": [24] * 11 + [25] * 14, "ecc_per_block": 30},
        (23, 'H'): {"num_blocks": 30, "block_sizes": [15] * 16 + [16] * 14, "ecc_per_block": 30},

        (24, 'L'): {"num_blocks": 10, "block_sizes": [117] * 6 + [118] * 4, "ecc_per_block": 30},
        (24, 'M'): {"num_blocks": 20, "block_sizes": [45] * 6 + [46] * 14, "ecc_per_block": 28},
        (24, 'Q'): {"num_blocks": 27, "block_sizes": [24] * 11 + [25] * 16, "ecc_per_block": 30},
        (24, 'H'): {"num_blocks": 32, "block_sizes": [16] * 30 + [17] * 2, "ecc_per_block": 30},

        (25, 'L'): {"num_blocks": 12, "block_sizes": [106] * 8 + [107] * 4, "ecc_per_block": 26},
        (25, 'M'): {"num_blocks": 21, "block_sizes": [47] * 8 + [48] * 13, "ecc_per_block": 28},
        (25, 'Q'): {"num_blocks": 29, "block_sizes": [24] * 7 + [25] * 22, "ecc_per_block": 30},
        (25, 'H'): {"num_blocks": 35, "block_sizes": [15] * 22 + [16] * 13, "ecc_per_block": 30},

        (26, 'L'): {"num_blocks": 12, "block_sizes": [114] * 10 + [115] * 2, "ecc_per_block": 28},
        (26, 'M'): {"num_blocks": 23, "block_sizes": [46] * 19 + [47] * 4, "ecc_per_block": 28},
        (26, 'Q'): {"num_blocks": 34, "block_sizes": [22] * 28 + [23] * 6, "ecc_per_block": 28},
        (26, 'H'): {"num_blocks": 37, "block_sizes": [16] * 33 + [17] * 4, "ecc_per_block": 30},

        (27, 'L'): {"num_blocks": 12, "block_sizes": [122] * 8 + [123] * 4, "ecc_per_block": 30},
        (27, 'M'): {"num_blocks": 25, "block_sizes": [45] * 22 + [46] * 3, "ecc_per_block": 28},
        (27, 'Q'): {"num_blocks": 34, "block_sizes": [23] * 8 + [24] * 26, "ecc_per_block": 30},
        (27, 'H'): {"num_blocks": 40, "block_sizes": [15] * 12 + [16] * 28, "ecc_per_block": 30},

        (28, 'L'): {"num_blocks": 13, "block_sizes": [117] * 3 + [118] * 10, "ecc_per_block": 30},
        (28, 'M'): {"num_blocks": 26, "block_sizes": [45] * 3 + [46] * 23, "ecc_per_block": 28},
        (28, 'Q'): {"num_blocks": 35, "block_sizes": [24] * 4 + [25] * 31, "ecc_per_block": 30},
        (28, 'H'): {"num_blocks": 42, "block_sizes": [15] * 11 + [16] * 31, "ecc_per_block": 30},

        (29, 'L'): {"num_blocks": 14, "block_sizes": [116] * 7 + [117] * 7, "ecc_per_block": 30},
        (29, 'M'): {"num_blocks": 28, "block_sizes": [45] * 21 + [46] * 7, "ecc_per_block": 28},
        (29, 'Q'): {"num_blocks": 38, "block_sizes": [23] * 1 + [24] * 37, "ecc_per_block": 30},
        (29, 'H'): {"num_blocks": 45, "block_sizes": [15] * 19 + [16] * 26, "ecc_per_block": 30},

        (30, 'L'): {"num_blocks": 15, "block_sizes": [115] * 5 + [116] * 10, "ecc_per_block": 30},
        (30, 'M'): {"num_blocks": 29, "block_sizes": [47] * 19 + [48] * 10, "ecc_per_block": 28},
        (30, 'Q'): {"num_blocks": 40, "block_sizes": [24] * 15 + [25] * 25, "ecc_per_block": 30},
        (30, 'H'): {"num_blocks": 48, "block_sizes": [15] * 23 + [16] * 25, "ecc_per_block": 30},

        (31, 'L'): {"num_blocks": 16, "block_sizes": [115] * 13 + [116] * 3, "ecc_per_block": 30},
        (31, 'M'): {"num_blocks": 31, "block_sizes": [46] * 2 + [47] * 29, "ecc_per_block": 28},
        (31, 'Q'): {"num_blocks": 43, "block_sizes": [24] * 42 + [25], "ecc_per_block": 30},
        (31, 'H'): {"num_blocks": 51, "block_sizes": [15] * 23 + [16] * 28, "ecc_per_block": 30},

        (32, 'L'): {"num_blocks": 17, "block_sizes": [115] * 17, "ecc_per_block": 30},
        (32, 'M'): {"num_blocks": 33, "block_sizes": [46] * 10 + [47] * 23, "ecc_per_block": 28},
        (32, 'Q'): {"num_blocks": 45, "block_sizes": [24] * 10 + [25] * 35, "ecc_per_block": 30},
        (32, 'H'): {"num_blocks": 54, "block_sizes": [15] * 19 + [16] * 35, "ecc_per_block": 30},

        (33, 'L'): {"num_blocks": 18, "block_sizes": [115] * 17 + [116], "ecc_per_block": 30},
        (33, 'M'): {"num_blocks": 35, "block_sizes": [46] * 14 + [47] * 21, "ecc_per_block": 28},
        (33, 'Q'): {"num_blocks": 48, "block_sizes": [24] * 29 + [25] * 19, "ecc_per_block": 30},
        (33, 'H'): {"num_blocks": 57, "block_sizes": [15] * 11 + [16] * 46, "ecc_per_block": 30},

        (34, 'L'): {"num_blocks": 19, "block_sizes": [115] * 13 + [116] * 6, "ecc_per_block": 30},
        (34, 'M'): {"num_blocks": 37, "block_sizes": [46] * 14 + [47] * 23, "ecc_per_block": 28},
        (34, 'Q'): {"num_blocks": 51, "block_sizes": [24] * 44 + [25] * 7, "ecc_per_block": 30},
        (34, 'H'): {"num_blocks": 60, "block_sizes": [16] * 59 + [17], "ecc_per_block": 30},

        (35, 'L'): {"num_blocks": 19, "block_sizes": [121] * 12 + [122] * 7, "ecc_per_block": 30},
        (35, 'M'): {"num_blocks": 38, "block_sizes": [47] * 12 + [48] * 26, "ecc_per_block": 28},
        (35, 'Q'): {"num_blocks": 53, "block_sizes": [24] * 39 + [25] * 14, "ecc_per_block": 30},
        (35, 'H'): {"num_blocks": 63, "block_sizes": [15] * 22 + [16] * 41, "ecc_per_block": 30},

        (36, 'L'): {"num_blocks": 20, "block_sizes": [121] * 6 + [122] * 14, "ecc_per_block": 30},
        (36, 'M'): {"num_blocks": 40, "block_sizes": [47] * 6 + [48] * 34, "ecc_per_block": 28},
        (36, 'Q'): {"num_blocks": 56, "block_sizes": [24] * 46 + [25] * 10, "ecc_per_block": 30},
        (36, 'H'): {"num_blocks": 66, "block_sizes": [15] * 2 + [16] * 64, "ecc_per_block": 30},

        (37, 'L'): {"num_blocks": 21, "block_sizes": [122] * 17 + [123] * 4, "ecc_per_block": 30},
        (37, 'M'): {"num_blocks": 43, "block_sizes": [46] * 29 + [47] * 14, "ecc_per_block": 28},
        (37, 'Q'): {"num_blocks": 59, "block_sizes": [24] * 49 + [25] * 10, "ecc_per_block": 30},
        (37, 'H'): {"num_blocks": 70, "block_sizes": [15] * 24 + [16] * 46, "ecc_per_block": 30},

        (38, 'L'): {"num_blocks": 22, "block_sizes": [122] * 4 + [123] * 18, "ecc_per_block": 30},
        (38, 'M'): {"num_blocks": 45, "block_sizes": [46] * 13 + [47] * 32, "ecc_per_block": 28},
        (38, 'Q'): {"num_blocks": 62, "block_sizes": [24] * 48 + [25] * 14, "ecc_per_block": 30},
        (38, 'H'): {"num_blocks": 74, "block_sizes": [15] * 42 + [16] * 32, "ecc_per_block": 30},

        (39, 'L'): {"num_blocks": 24, "block_sizes": [117] * 20 + [118] * 4, "ecc_per_block": 30},
        (39, 'M'): {"num_blocks": 47, "block_sizes": [47] * 40 + [48] * 7, "ecc_per_block": 28},
        (39, 'Q'): {"num_blocks": 65, "block_sizes": [24] * 43 + [25] * 22, "ecc_per_block": 30},
        (39, 'H'): {"num_blocks": 77, "block_sizes": [15] * 10 + [16] * 67, "ecc_per_block": 30},

        (40, 'L'): {"num_blocks": 25, "block_sizes": [118] * 19 + [119] * 6, "ecc_per_block": 30},
        (40, 'M'): {"num_blocks": 49, "block_sizes": [47] * 18 + [48] * 31, "ecc_per_block": 28},
        (40, 'Q'): {"num_blocks": 68, "block_sizes": [24] * 34 + [25] * 34, "ecc_per_block": 30},
        (40, 'H'): {"num_blocks": 81, "block_sizes": [15] * 20 + [16] * 61, "ecc_per_block": 30}
    }

    return block_structure[(version_num, error_correction_level.upper())]

# Get Alphanumeric
def lookup_alphanumeric(char):
    alphanumeric_lookup = {
        '0': 0, '1': 1, '2': 2,
        '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8,
        '9': 9, 'A': 10, 'B': 11,
        'C': 12, 'D': 13, 'E': 14,
        'F': 15, 'G': 16, 'H': 17,
        'I': 18, 'J': 19, 'K': 20,
        'L': 21, 'M': 22, 'N': 23,
        'O': 24, 'P': 25, 'Q': 26,
        'R': 27, 'S': 28, 'T': 29,
        'U': 30, 'V': 31, 'W': 32,
        'X': 33, 'Y': 34, 'Z': 35,
        ' ': 36, '$': 37, '%': 38,
        '*': 39, '+': 40, '-': 41,
        '.': 42,'/': 43, ':': 44
    }

    return alphanumeric_lookup[char]

# Get Version Information
def get_version_info_string(version):
    version_info = {
        7: "000111110010010100",
        8: "001000010110111100",
        9: "001001101010011001",
        10: "001010010011010011",
        11: "001011101111110110",
        12: "001100011101100010",
        13: "001101100001000111",
        14: "001110011000001101",
        15: "001111100100101000",
        16: "010000101101111000",
        17: "010001010001011101",
        18: "010010101000010111",
        19: "010011010100110010",
        20: "010100100110100110",
        21: "010101011010000011",
        22: "010110100011001001",
        23: "010111011111101100",
        24: "011000111011000100",
        25: "011001000111100001",
        26: "011010111110101011",
        27: "011011000010001110",
        28: "011100110000011010",
        29: "011101001100111111",
        30: "011110110101110101",
        31: "011111001001010000",
        32: "100000100111010101",
        33: "100001011011110000",
        34: "100010100010111010",
        35: "100011011110011111",
        36: "100100101100001011",
        37: "100101010000101110",
        38: "100110101001100100",
        39: "100111010101000001",
        40: "101000110001101001"
    }
    return version_info[int(version)]

# Getting The Amount of Writable Codewords For Each Version and ECL
def get_qr_capacity(version_num, error_correction_level, encoding_mode):
    # Data codewords per version and ECC level
    # Format: [L, M, Q, H] for each version

    qr_capacity_table = {
        1: {
            'L': {'numeric': 41, 'alphanumeric': 25, 'byte': 17},
            'M': {'numeric': 34, 'alphanumeric': 20, 'byte': 14},
            'Q': {'numeric': 27, 'alphanumeric': 16, 'byte': 11},
            'H': {'numeric': 17, 'alphanumeric': 10, 'byte': 7},
        },
        2: {
            'L': {'numeric': 77, 'alphanumeric': 47, 'byte': 32},
            'M': {'numeric': 63, 'alphanumeric': 38, 'byte': 26},
            'Q': {'numeric': 48, 'alphanumeric': 29, 'byte': 20},
            'H': {'numeric': 34, 'alphanumeric': 20, 'byte': 14},
        },
        3: {
            'L': {'numeric': 127, 'alphanumeric': 77, 'byte': 53},
            'M': {'numeric': 101, 'alphanumeric': 61, 'byte': 42},
            'Q': {'numeric': 77, 'alphanumeric': 47, 'byte': 32},
            'H': {'numeric': 58, 'alphanumeric': 35, 'byte': 24},
        },
        4: {
            'L': {'numeric': 187, 'alphanumeric': 114, 'byte': 78},
            'M': {'numeric': 149, 'alphanumeric': 90, 'byte': 62},
            'Q': {'numeric': 111, 'alphanumeric': 67, 'byte': 46},
            'H': {'numeric': 82, 'alphanumeric': 50, 'byte': 34},
        },
        5: {
            'L': {'numeric': 255, 'alphanumeric': 154, 'byte': 106},
            'M': {'numeric': 202, 'alphanumeric': 122, 'byte': 84},
            'Q': {'numeric': 144, 'alphanumeric': 87, 'byte': 60},
            'H': {'numeric': 106, 'alphanumeric': 64, 'byte': 44},
        },
        6: {
            'L': {'numeric': 322, 'alphanumeric': 195, 'byte': 134},
            'M': {'numeric': 255, 'alphanumeric': 154, 'byte': 106},
            'Q': {'numeric': 178, 'alphanumeric': 108, 'byte': 74},
            'H': {'numeric': 139, 'alphanumeric': 84, 'byte': 58},
        },
        7: {
            'L': {'numeric': 370, 'alphanumeric': 224, 'byte': 154},
            'M': {'numeric': 293, 'alphanumeric': 178, 'byte': 122},
            'Q': {'numeric': 207, 'alphanumeric': 125, 'byte': 86},
            'H': {'numeric': 154, 'alphanumeric': 93, 'byte': 64},
        },
        8: {
            'L': {'numeric': 461, 'alphanumeric': 279, 'byte': 192},
            'M': {'numeric': 365, 'alphanumeric': 221, 'byte': 152},
            'Q': {'numeric': 259, 'alphanumeric': 157, 'byte': 108},
            'H': {'numeric': 202, 'alphanumeric': 122, 'byte': 84},
        },
        9: {
            'L': {'numeric': 552, 'alphanumeric': 335, 'byte': 230},
            'M': {'numeric': 432, 'alphanumeric': 262, 'byte': 180},
            'Q': {'numeric': 312, 'alphanumeric': 189, 'byte': 130},
            'H': {'numeric': 235, 'alphanumeric': 143, 'byte': 98},
        },
        10: {
            'L': {'numeric': 652, 'alphanumeric': 395, 'byte': 271},
            'M': {'numeric': 513, 'alphanumeric': 311, 'byte': 213},
            'Q': {'numeric': 364, 'alphanumeric': 221, 'byte': 151},
            'H': {'numeric': 288, 'alphanumeric': 174, 'byte': 119},
        },
        11: {
            'L': {'numeric': 772, 'alphanumeric': 468, 'byte': 321},
            'M': {'numeric': 604, 'alphanumeric': 366, 'byte': 251},
            'Q': {'numeric': 427, 'alphanumeric': 259, 'byte': 177},
            'H': {'numeric': 331, 'alphanumeric': 200, 'byte': 137},
        },
        12: {
            'L': {'numeric': 883, 'alphanumeric': 535, 'byte': 367},
            'M': {'numeric': 691, 'alphanumeric': 419, 'byte': 287},
            'Q': {'numeric': 489, 'alphanumeric': 296, 'byte': 203},
            'H': {'numeric': 374, 'alphanumeric': 227, 'byte': 155},
        },
        13: {
            'L': {'numeric': 1022, 'alphanumeric': 619, 'byte': 425},
            'M': {'numeric': 796, 'alphanumeric': 483, 'byte': 331},
            'Q': {'numeric': 580, 'alphanumeric': 352, 'byte': 241},
            'H': {'numeric': 427, 'alphanumeric': 259, 'byte': 177},
        },
        14: {
            'L': {'numeric': 1101, 'alphanumeric': 667, 'byte': 458},
            'M': {'numeric': 871, 'alphanumeric': 528, 'byte': 362},
            'Q': {'numeric': 621, 'alphanumeric': 376, 'byte': 258},
            'H': {'numeric': 468, 'alphanumeric': 283, 'byte': 194},
        },
        15: {
            'L': {'numeric': 1250, 'alphanumeric': 758, 'byte': 520},
            'M': {'numeric': 991, 'alphanumeric': 600, 'byte': 412},
            'Q': {'numeric': 703, 'alphanumeric': 426, 'byte': 292},
            'H': {'numeric': 530, 'alphanumeric': 321, 'byte': 220},
        },
        16: {
            'L': {'numeric': 1408, 'alphanumeric': 854, 'byte': 586},
            'M': {'numeric': 1082, 'alphanumeric': 656, 'byte': 450},
            'Q': {'numeric': 775, 'alphanumeric': 470, 'byte': 322},
            'H': {'numeric': 602, 'alphanumeric': 365, 'byte': 250},
        },
        17: {
            'L': {'numeric': 1548, 'alphanumeric': 938, 'byte': 644},
            'M': {'numeric': 1212, 'alphanumeric': 734, 'byte': 504},
            'Q': {'numeric': 876, 'alphanumeric': 531, 'byte': 364},
            'H': {'numeric': 674, 'alphanumeric': 408, 'byte': 280},
        },
        18: {
            'L': {'numeric': 1725, 'alphanumeric': 1046, 'byte': 718},
            'M': {'numeric': 1346, 'alphanumeric': 816, 'byte': 560},
            'Q': {'numeric': 948, 'alphanumeric': 574, 'byte': 394},
            'H': {'numeric': 746, 'alphanumeric': 452, 'byte': 310},
        },
        19: {
            'L': {'numeric': 1903, 'alphanumeric': 1153, 'byte': 792},
            'M': {'numeric': 1500, 'alphanumeric': 909, 'byte': 624},
            'Q': {'numeric': 1063, 'alphanumeric': 644, 'byte': 442},
            'H': {'numeric': 813, 'alphanumeric': 493, 'byte': 338},
        },
        20: {
            'L': {'numeric': 2061, 'alphanumeric': 1249, 'byte': 858},
            'M': {'numeric': 1600, 'alphanumeric': 970, 'byte': 666},
            'Q': {'numeric': 1159, 'alphanumeric': 702, 'byte': 482},
            'H': {'numeric': 919, 'alphanumeric': 557, 'byte': 382},
        },
        21: {
            'L': {'numeric': 2232, 'alphanumeric': 1352, 'byte': 929},
            'M': {'numeric': 1708, 'alphanumeric': 1035, 'byte': 711},
            'Q': {'numeric': 1224, 'alphanumeric': 742, 'byte': 509},
            'H': {'numeric': 969, 'alphanumeric': 587, 'byte': 403},
        },
        22: {
            'L': {'numeric': 2409, 'alphanumeric': 1460, 'byte': 1003},
            'M': {'numeric': 1872, 'alphanumeric': 1134, 'byte': 779},
            'Q': {'numeric': 1358, 'alphanumeric': 823, 'byte': 565},
            'H': {'numeric': 1056, 'alphanumeric': 640, 'byte': 439},
        },
        23: {
            'L': {'numeric': 2620, 'alphanumeric': 1588, 'byte': 1091},
            'M': {'numeric': 2059, 'alphanumeric': 1248, 'byte': 857},
            'Q': {'numeric': 1468, 'alphanumeric': 890, 'byte': 611},
            'H': {'numeric': 1108, 'alphanumeric': 672, 'byte': 461},
        },
        24: {
            'L': {'numeric': 2812, 'alphanumeric': 1704, 'byte': 1171},
            'M': {'numeric': 2188, 'alphanumeric': 1326, 'byte': 911},
            'Q': {'numeric': 1588, 'alphanumeric': 963, 'byte': 661},
            'H': {'numeric': 1228, 'alphanumeric': 744, 'byte': 511},
        },
        25: {
            'L': {'numeric': 3057, 'alphanumeric': 1853, 'byte': 1273},
            'M': {'numeric': 2395, 'alphanumeric': 1451, 'byte': 997},
            'Q': {'numeric': 1718, 'alphanumeric': 1041, 'byte': 715},
            'H': {'numeric': 1286, 'alphanumeric': 779, 'byte': 535},
        },
        26: {
            'L': {'numeric': 3283, 'alphanumeric': 1990, 'byte': 1367},
            'M': {'numeric': 2544, 'alphanumeric': 1542, 'byte': 1059},
            'Q': {'numeric': 1804, 'alphanumeric': 1094, 'byte': 751},
            'H': {'numeric': 1425, 'alphanumeric': 864, 'byte': 593},
        },
        27: {
            'L': {'numeric': 3517, 'alphanumeric': 2132, 'byte': 1465},
            'M': {'numeric': 2701, 'alphanumeric': 1637, 'byte': 1125},
            'Q': {'numeric': 1933, 'alphanumeric': 1172, 'byte': 805},
            'H': {'numeric': 1501, 'alphanumeric': 910, 'byte': 625},
        },
        28: {
            'L': {'numeric': 3669, 'alphanumeric': 2223, 'byte': 1528},
            'M': {'numeric': 2857, 'alphanumeric': 1732, 'byte': 1190},
            'Q': {'numeric': 2085, 'alphanumeric': 1263, 'byte': 868},
            'H': {'numeric': 1581, 'alphanumeric': 958, 'byte': 658},
        },
        29: {
            'L': {'numeric': 3909, 'alphanumeric': 2369, 'byte': 1628},
            'M': {'numeric': 3035, 'alphanumeric': 1839, 'byte': 1264},
            'Q': {'numeric': 2181, 'alphanumeric': 1322, 'byte': 908},
            'H': {'numeric': 1677, 'alphanumeric': 1016, 'byte': 698},
        },
        30: {
            'L': {'numeric': 4158, 'alphanumeric': 2520, 'byte': 1732},
            'M': {'numeric': 3289, 'alphanumeric': 1994, 'byte': 1370},
            'Q': {'numeric': 2358, 'alphanumeric': 1429, 'byte': 982},
            'H': {'numeric': 1782, 'alphanumeric': 1080, 'byte': 742},
        },
        31: {
            'L': {'numeric': 4417, 'alphanumeric': 2677, 'byte': 1840},
            'M': {'numeric': 3486, 'alphanumeric': 2113, 'byte': 1452},
            'Q': {'numeric': 2473, 'alphanumeric': 1499, 'byte': 1030},
            'H': {'numeric': 1897, 'alphanumeric': 1150, 'byte': 790},
        },
        32: {
            'L': {'numeric': 4686, 'alphanumeric': 2840, 'byte': 1952},
            'M': {'numeric': 3693, 'alphanumeric': 2238, 'byte': 1538},
            'Q': {'numeric': 2670, 'alphanumeric': 1618, 'byte': 1112},
            'H': {'numeric': 2022, 'alphanumeric': 1226, 'byte': 842},
        },
        33: {
            'L': {'numeric': 4965, 'alphanumeric': 3009, 'byte': 2068},
            'M': {'numeric': 3909, 'alphanumeric': 2369, 'byte': 1628},
            'Q': {'numeric': 2805, 'alphanumeric': 1700, 'byte': 1168},
            'H': {'numeric': 2157, 'alphanumeric': 1307, 'byte': 898},
        },
        34: {
            'L': {'numeric': 5253, 'alphanumeric': 3183, 'byte': 2188},
            'M': {'numeric': 4134, 'alphanumeric': 2506, 'byte': 1722},
            'Q': {'numeric': 2949, 'alphanumeric': 1787, 'byte': 1228},
            'H': {'numeric': 2301, 'alphanumeric': 1394, 'byte': 958},
        },
        35: {
            'L': {'numeric': 5529, 'alphanumeric': 3351, 'byte': 2303},
            'M': {'numeric': 4343, 'alphanumeric': 2632, 'byte': 1809},
            'Q': {'numeric': 3081, 'alphanumeric': 1867, 'byte': 1283},
            'H': {'numeric': 2361, 'alphanumeric': 1431, 'byte': 983},
        },
        36: {
            'L': {'numeric': 5836, 'alphanumeric': 3537, 'byte': 2431},
            'M': {'numeric': 4588, 'alphanumeric': 2780, 'byte': 1911},
            'Q': {'numeric': 3244, 'alphanumeric': 1966, 'byte': 1351},
            'H': {'numeric': 2524, 'alphanumeric': 1530, 'byte': 1051},
        },
        37: {
            'L': {'numeric': 6153, 'alphanumeric': 3729, 'byte': 2563},
            'M': {'numeric': 4775, 'alphanumeric': 2894, 'byte': 1989},
            'Q': {'numeric': 3417, 'alphanumeric': 2071, 'byte': 1423},
            'H': {'numeric': 2625, 'alphanumeric': 1591, 'byte': 1093},
        },
        38: {
            'L': {'numeric': 6479, 'alphanumeric': 3927, 'byte': 2699},
            'M': {'numeric': 5039, 'alphanumeric': 3054, 'byte': 2099},
            'Q': {'numeric': 3599, 'alphanumeric': 2181, 'byte': 1499},
            'H': {'numeric': 2735, 'alphanumeric': 1658, 'byte': 1139},
        },
        39: {
            'L': {'numeric': 6743, 'alphanumeric': 4087, 'byte': 2809},
            'M': {'numeric': 5313, 'alphanumeric': 3220, 'byte': 2213},
            'Q': {'numeric': 3791, 'alphanumeric': 2298, 'byte': 1579},
            'H': {'numeric': 2927, 'alphanumeric': 1774, 'byte': 1219},
        },
        40: {
            'L': {'numeric': 7089, 'alphanumeric': 4296, 'byte': 2953},
            'M': {'numeric': 5596, 'alphanumeric': 3391, 'byte': 2331},
            'Q': {'numeric': 3993, 'alphanumeric': 2420, 'byte': 1663},
            'H': {'numeric': 3057, 'alphanumeric': 1852, 'byte': 1273},
        }}

    if encoding_mode == 1:
        encoding_mode = 'numeric'
    elif encoding_mode == 2:
        encoding_mode = 'alphanumeric'
    elif encoding_mode == 3:
        encoding_mode = 'byte'

    return qr_capacity_table[int(version_num)][error_correction_level.upper()][encoding_mode]

# Get Timing Pattern Length
def get_timing_pattern_length(version):
    return 7 + 4 * (version - 1)

# Mask Pattern Functions
mask0 = lambda row, col : (row + col) % 2 == 0
mask1 = lambda row, col : col % 2 == 0
mask2 = lambda row, col : row % 3 == 0
mask3 = lambda row, col : (row + col) % 3 == 0
mask4 = lambda row, col : (col // 2 + row // 3) % 2 == 0
mask5 = lambda row, col : (row * col) % 2 + (row * col) % 3 == 0
mask6 = lambda row, col : ((row * col) % 2 + (row * col) % 3) % 2 == 0
mask7 = lambda row, col : ((row + col) % 2 + (row * col) % 3) % 2 == 0
mask_list = [mask0, mask1, mask2, mask3, mask4, mask5, mask6, mask7]

# Function For Applying Masks
def apply_mask(matrix, size, mask_index):
    for y in range(size):
        for x in range(size):
            if matrix[y][x] == 8 or matrix[y][x] == 9:
                if mask_list[mask_index](x, y):
                    if matrix[y][x] == 9:
                        matrix[y][x] = 8
                    else:
                        matrix[y][x] = 9
    return matrix

# Function for Applying Format Info
def apply_format(matrix, size, ecl, mask_index):

    # Converting ECL to Bits
    if ecl.lower() == "l":
        ecl = "01"
    elif ecl.lower() == "m":
        ecl = "00"
    elif ecl.lower() == "q":
        ecl = "11"
    elif ecl.lower() == "h":
        ecl = "10"

    # Converting Mask Index to Bits
    mask_index = bin(mask_index)[2:].zfill(3)

    format_info = bch_ecc_gen(ecl + mask_index)
    matrix_size = size

    # Filling In format info to the top left reserved area
    bit_index = 0
    top_left_area_coord = [[8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 7], [8, 8], [7, 8], [5, 8], [4, 8], [3, 8], [2, 8], [1, 8], [0, 8]]

    for index in top_left_area_coord:
        matrix[index[0]][index[1]] = int(format_info[bit_index])
        bit_index += 1

    # Filling In Format Info To The Bottom Left and Top Right Reserved Areas
    bit_index = 0
    bl_tr_area_coord = [[matrix_size-1, 8], [matrix_size-2, 8], [matrix_size-3, 8], [matrix_size-4, 8], [matrix_size-5, 8], [matrix_size-6, 8], [matrix_size-7, 8], [8, matrix_size-8], [8, matrix_size-7], [8, matrix_size-6], [8, matrix_size-5], [8, matrix_size-4], [8, matrix_size-3], [8, matrix_size-2], [8, matrix_size-1]]
    for index in bl_tr_area_coord:
        matrix[index[0]][index[1]] = int(format_info[bit_index])
        bit_index += 1

    return matrix

# Function for applying version information
def apply_version(matrix, size, version_num):
    version_info = get_version_info_string(version_num)
    matrix_size = size

    # Filling in bottom left version block
    bit_index = 0
    for x in range(6):
        for y in range(3):
            matrix[matrix_size-9-y][5-x] = int(version_info[bit_index])
            bit_index += 1

    # Filling in the top right version block
    bit_index = 0
    for y in range(6):
        for x in range(3):
            matrix[5-y][matrix_size-9-x] = int(version_info[bit_index])
            bit_index += 1

    return matrix

#function for generating a BMP file to display the qr code:
def bmp_gen(matrix, size, version, ecl, encode_mode, message):
    # Setting Up Quiet Zone
    for y in range(size):
        for _ in range(4):
            matrix[y].append(0)
            matrix[y].insert(0, 0)
    for _ in range(4):
        matrix.insert(0, [0] * (size+8))
        matrix.append([0] * (size+8))

    size += 8
    # Local Variables
    row_size = size*3
    row_padding = (4-(row_size % 4)) %4
    pixel_array_site = (row_size + row_padding) * size
    file_size = 14 + 40 + pixel_array_site

    # --Preparing Data
    # Preparing File Header
    file_header = bytearray()
    file_header.extend(b"BM") # Signature
    file_header.extend(file_size.to_bytes(4, "little")) # File Size
    file_header.extend((0).to_bytes(2, "little")) # Reserved 1
    file_header.extend((0).to_bytes(2, "little")) # Reserved 2
    file_header.extend((54).to_bytes(4, "little")) # Pixel Offset

    # Preparing DIB Header
    dib_header = bytearray()
    dib_header.extend((40).to_bytes(4, "little")) # DIB header size
    dib_header.extend(size.to_bytes(4, "little")) # Image width
    dib_header.extend(size.to_bytes(4, "little")) # Image height
    dib_header.extend((1).to_bytes(2, "little")) # Color Plane
    dib_header.extend((24).to_bytes(2, "little")) # Bits per pixel
    dib_header.extend((0).to_bytes(4, "little")) # Compression (0 for none)
    dib_header.extend(pixel_array_site.to_bytes(4, "little")) # Image Size
    dib_header.extend((0).to_bytes(4, "little")) # X pixels per meter
    dib_header.extend((0).to_bytes(4, "little")) # Y pixels per meter
    dib_header.extend((0).to_bytes(4, "little")) # Colors in palette
    dib_header.extend((0).to_bytes(4, "little")) # Important Colors

    # Preparing Pixel Data
    black = b'\x00\x00\x00'
    white = b'\xFF\xFF\xFF'
    padding_byte = b'\x00'

    pixel_data = bytearray()
    for y in range(size-1, -1, -1):
        for x in range(size):
            if matrix[y][x] == 0:
                pixel_data.extend(white)
            else:
                pixel_data.extend(black)
        for i in range(row_padding):
            pixel_data.extend(padding_byte)

        filename = f'qr_v{version}{ecl}_{encode_mode}_{message[:10].replace(" ", "_").replace(".","")}.bmp'
        with open(filename, "wb") as f:
            f.write(file_header)
            f.write(dib_header)
            f.write(pixel_data)
        f.close()


# ---- Function Handling QR Generation ----
def generate_QR(text="", cli=False, ecl="", encode_mode=0, version=0, export_image=True, export_ascii=True):

    # Prompts advanced mode
    if not cli:
        advanced_mode = input("Advanced Mode [y/n]: ")
        if advanced_mode == "y":
            default_settings = False
        elif advanced_mode == "n":
            default_settings = True
        else:
            print("Invalid Answer Just Gonna Put You On Default Settings!")
            default_settings = True
    else:
        default_settings = False

    # Prompt for encode message
    if not cli:
        input_message = input("Your Text: ")

    # Setting up default variables
    default_version = "a"
    default_encoding = "a"
    default_ecl = "m"
    default_image = True
    default_ascii = False

    # ---- Exporting ----
    print_info = True
    print_qr_code = True
    export_file = export_image
    export_ascii = export_ascii

    if cli:
        print_qr_code = False

    # Getting Datas If CLI is Enabled
    if cli:
        input_message = text
        error_correction_level = ecl
        char_encoding_mode = encode_mode
        version_selection = version
    elif text == "" and not cli:
        input_message = "Something went wrong"

    # Prompting Encoding Mode And Automatically Selecting Best EM If Possible
    if not default_settings and not cli:
        char_encoding_mode = input(
            "\n[a] Auto \n[1] Numeric\n[2] Alphanumeric\n[3] Byte\n Input(a,1,2,3): ")
    elif not cli and default_settings:
        char_encoding_mode = default_encoding
    else:
        char_encoding_mode = "a"

    if char_encoding_mode.isdigit():
        if 1 <= int(char_encoding_mode) <= 3:
            char_encoding_mode = int(char_encoding_mode)
        else:
            print(f"Invalid Encoding Mode {char_encoding_mode}?")
    elif char_encoding_mode != "a":
        print(f"Invalid Encoding Mode {char_encoding_mode}?")

    # Check For Automatic Encoding Mode Selection Is Selected
    if char_encoding_mode == "a" or char_encoding_mode == "A":
        can_numeric = input_message.isnumeric()
        can_alphanum = input_message.isalnum() and input_message.isupper()

        if can_numeric:
            char_encoding_mode = 1
        elif can_alphanum:
            char_encoding_mode = 2
        elif not can_alphanum and not can_numeric:
            char_encoding_mode = 3
        else:
            char_encoding_mode = 3

    # Prompting ECL and Processing Data
    if not default_settings and not cli:
        error_correction_level = input("[Choose EC Level: % Data Recoverable]\n L: ~7% \n M: ~15% \n Q: ~25% \n H: ~30%\n Input (L,M,Q,H or 1,2,3,4)")
    if default_settings and not cli:
        error_correction_level = default_ecl

    # Prompts For Exporting File
    if not default_settings and not cli:
        export_file = input("Export File? [True/False]: ")
        if export_file.lower() == "true" or export_file.lower() == "t" or export_file.lower() == "1":
            export_file = True
        elif export_file.lower() == "false" or export_file.lower() == "f" or export_file.lower() == "0":
            export_file = False
    if default_settings and not cli:
        export_file = default_image

    # Prompts For Exporting ASCII

    if not default_settings and not cli:
        export_ascii = input("Export ASCII? [True/False]: ")
        if export_ascii.lower() == "true" or export_ascii.lower() == "t" or export_ascii.lower() == "1":
            export_ascii = True
        elif export_ascii.lower() == "false" or export_ascii.lower() == "f" or export_ascii.lower() == "0":
            export_ascii = False
    if default_settings and not cli:
        export_ascii = default_ascii

    if error_correction_level.isdigit():
        if 1 <= int(error_correction_level) <= 4:
            error_correction_level = int(error_correction_level)
            if error_correction_level == 1:
                error_correction_level = "l"
            elif error_correction_level == 2:
                error_correction_level = "m"
            elif error_correction_level == 3:
                error_correction_level = "q"
            elif error_correction_level == 4:
                error_correction_level = "h"
        else:
            print(f"Invalid Error Correction Level {error_correction_level}?")
    elif error_correction_level.lower() == "l" or error_correction_level.lower() == "m" or error_correction_level.lower() == "q" or error_correction_level.lower() == "h":
        error_correction_level = error_correction_level.lower()
    else:
        input(f"Invalid Error Correction Level {error_correction_level}?")
        quit()

    # Prompting Version
    if not default_settings and not cli:
        print(
            "\n\n Automatic Mode Will Automatically Choose The Lowest Version Needed Based On Input Length, Encoding Mode and EC Level")
        version_selection = input("Version (1-40) or (A for Automatic): ")
    elif default_settings and not cli:
        version_selection = default_version

    if str(version_selection).isdigit():
        if 1 <= int(version_selection) <= 40:
            version_selection = int(version_selection)
        else:
            input("\nInvalid Version")
    elif version_selection.lower() == "a":
        # A while loop for choosing the correct version
        version_selection = 1
        writable_data = get_qr_capacity(version_selection, error_correction_level, char_encoding_mode)
        while writable_data <= len(input_message):
            version_selection += 1
            writable_data = get_qr_capacity(version_selection, error_correction_level, char_encoding_mode)

            # A timeout in case something goes haywire
            if version_selection > 40:
                print("something went wrong! ;(")
                quit()
    else:
        input("\nInvalid Version")

    # Get Block Information
    block_info = get_block_data(version_selection, error_correction_level)
    block_number = block_info["num_blocks"]
    block_size = block_info["block_sizes"]
    ecc_per_block = block_info["ecc_per_block"]

    # Getting Actual Codeword Capacity
    codewords_capacity = 0
    for size in block_size:
        codewords_capacity += size

    # Converting codewords capacity to bits
    codewords_capacity *= 8

    # Character Count Indicator
    char_count_indicator = bin(len(input_message))[2:].zfill(
        get_char_count_indicator(version_selection, char_encoding_mode))

    # Mode Indicator
    if char_encoding_mode == 1:
        mode_indicator = "0001"
    elif char_encoding_mode == 2:
        mode_indicator = "0010"
    elif char_encoding_mode == 3:
        mode_indicator = "0100"
    elif char_encoding_mode == 4:
        mode_indicator = "1000"
    else:
        print("\nInvalid Mode")
        quit()

    # -----Preprocessing Data-----
    # Adding Necessary Indicators
    message_encoded = mode_indicator + char_count_indicator
    debug = []

    # Adding Encoded Text From Input Message Depending On Encoding Mode
    if char_encoding_mode == 1:  # Numeric
        if not input_message.isnumeric():
            print(f"Numeric Only Support Digits!!")
            quit()
        for i in range(0, len(input_message), 3):
            if i + 2 < len(input_message):
                message_encoded += bin(int(input_message[i:i + 2]))[2:].zfill(10)
            elif i + 1 < len(input_message):
                message_encoded += bin(int(input_message[i:i + 1]))[2:].zfill(7)
            else:
                message_encoded += bin(int(input_message[i]))[2:].zfill(4)
    elif char_encoding_mode == 2:  # Alphanumeric
        if not (input_message.isalnum() and input_message.isupper()):
            print(f"Alphanumeric Only Support Upper A-Z, 0-9, Punctuations!!")
            quit()
        for i in range(0, len(input_message), 2):
            if i + 1 < len(input_message):
                message_encoded += bin(
                    (lookup_alphanumeric(input_message[i]) * 45) + lookup_alphanumeric(input_message[i + 1]))[2:].zfill(
                    11)
            else:
                message_encoded += bin(lookup_alphanumeric(input_message[i]))[2:].zfill(6)
    elif char_encoding_mode == 3:  # Byte
        for i in input_message:
            message_encoded += bin(ord(i))[2:].zfill(8)

    # Adding Terminator Bits
    if len(message_encoded) < codewords_capacity and len(message_encoded) != codewords_capacity:
        message_encoded += "0" * min(4, abs(codewords_capacity - len(message_encoded)))

    # Adding Byte Alignment
    while len(message_encoded) % 8 != 0 and len(message_encoded) != codewords_capacity:
        message_encoded += "0"

    # Alternating 0xEC / 0x11
    pad_bytes = ["11101100", "00010001"]
    pad_bytes_index = 0
    while len(message_encoded) != codewords_capacity:
        message_encoded += pad_bytes[pad_bytes_index]
        if pad_bytes_index == 1:
            pad_bytes_index = 0
        else:
            pad_bytes_index = 1

    # Splitting Encoded Message Into A List Of 8 Bits Elements
    data_codewords = []
    for i in range(int(len(message_encoded) / 8)):
        data_codewords.append(message_encoded[i * 8:(i + 1) * 8])

    # Splitting Data Into Blocks
    data_blocks = []
    if block_number > 1:
        index = 0
        for size in block_size:
            data_blocks.append(data_codewords[index:index + size])
            index += size
    else:
        data_blocks.append(data_codewords)

    # Generating Ecc Blocks From Data Blocks
    ecc_blocks = []
    for element in data_blocks:
        ecc_blocks.append(generate_ecc_codewords(element, ecc_per_block))

    for i in range(len(ecc_blocks)):
        ecc_blocks[i] = [bin(item)[2:].zfill(8) for item in ecc_blocks[i]]

    # Interleaving Process
    if block_number > 1:  # Only Interleave If There are more than 1 block of data
        interleaved_data = []
        interleaved_ecc = []

        # Interleaving Data
        for i in range(max(len(_) for _ in data_blocks)):
            for index in range(len(data_blocks)):
                if i < len(data_blocks[index]):
                    interleaved_data.append(data_blocks[index][i])

        # Interleaving Ecc
        for i in range(max(len(_) for _ in ecc_blocks)):
            for index in range(len(ecc_blocks)):
                if i < len(ecc_blocks[index]):
                    interleaved_ecc.append(ecc_blocks[index][i])

        # Generating a Bitstream from interleaved data and ecc
        bitstream = "".join(interleaved_data + interleaved_ecc)
    else:
        bitstream = "".join(item for item in (data_blocks[0] + ecc_blocks[0]))

    # Setting Up Constants
    qr_size = 21 + 4 * (version_selection - 1)
    qr_matrix = [[0] * qr_size for _ in range(qr_size)]
    if version_selection > 1:
        APs_center = get_APs_center_coordinates(version_selection)
    else:
        APs_center = []
    timing_pattern_length = get_timing_pattern_length(version_selection)

    # 3 is For 1 And 2 is For 0
    # Basically 3 Is Black & 2 Is White
    # This is so that future reserved area checking be more readable and easier to understand
    # because they don't mix up with the 0s and 1s making it harder to work with
    # 4 is for Format Information
    # 5 is for Version Information

    # Setting Up Finder Pattern
    for i in range(0, 7):
        # Top Left Finder Pattern
        qr_matrix[0][i] = 3
        qr_matrix[6][i] = 3
        qr_matrix[i][0] = 3
        qr_matrix[i][6] = 3

        if 0 <= i < 5:
            qr_matrix[i + 1][1] = 2
            qr_matrix[i + 1][5] = 2
            qr_matrix[1][i + 1] = 2
            qr_matrix[5][i + 1] = 2

        if 2 <= i <= 4:
            qr_matrix[2][i] = 3
            qr_matrix[3][i] = 3
            qr_matrix[4][i] = 3

        # Bottom Left Finder Pattern
        qr_matrix[qr_size - 7][i] = 3
        qr_matrix[qr_size - 1][i] = 3
        qr_matrix[qr_size - i - 1][0] = 3
        qr_matrix[qr_size - i - 1][6] = 3

        if 0 <= i < 5:
            qr_matrix[qr_size - 2][i + 1] = 2
            qr_matrix[qr_size - 2 - i][1] = 2
            qr_matrix[qr_size - 2 - i][5] = 2
            qr_matrix[qr_size - 6][i + 1] = 2

        if 2 <= i <= 4:
            qr_matrix[qr_size - 3][i] = 3
            qr_matrix[qr_size - 4][i] = 3
            qr_matrix[qr_size - 5][i] = 3

        # Top Right Finder Pattern
        qr_matrix[0][qr_size - i - 1] = 3
        qr_matrix[6][qr_size - i - 1] = 3
        qr_matrix[i][qr_size - 1] = 3
        qr_matrix[i][qr_size - 7] = 3

        if 0 <= i < 5:
            qr_matrix[1][qr_size - 2 - i] = 2
            qr_matrix[5][qr_size - 2 - i] = 2
            qr_matrix[i + 1][qr_size - 2] = 2
            qr_matrix[i + 1][qr_size - 6] = 2

        if 2 <= i <= 4:
            qr_matrix[2][qr_size - i - 1] = 3
            qr_matrix[3][qr_size - i - 1] = 3
            qr_matrix[4][qr_size - i - 1] = 3

    # Setting Up Separators
    for i in range(8):
        qr_matrix[7][7 - i] = 2
        qr_matrix[7 - i][7] = 2

        qr_matrix[7][qr_size - 8 + i] = 2
        qr_matrix[7 - i][qr_size - 8] = 2

        qr_matrix[qr_size - 8][7 - i] = 2
        qr_matrix[qr_size - 8 + i][7] = 2

    current_bit = 3

    # Setting Up Timing Pattern
    for i in range(timing_pattern_length - 2):
        overlapped = True

        if qr_matrix[6][8 + i] != 3 and qr_matrix[6][8 + i] != 2:
            qr_matrix[6][8 + i] = current_bit
            overlapped = False

        if qr_matrix[8 + i][6] != 3 and qr_matrix[8 + i][6] != 2:
            qr_matrix[8 + i][6] = current_bit
            overlapped = False

        if not overlapped:
            if current_bit == 3:
                current_bit -= 1
            else:
                current_bit += 1

    # Setting Up Alignment Patterns For Version 2 And Up
    if version_selection > 1:
        for _ in APs_center:
            # Placing Black At The Center
            qr_matrix[_[0]][_[1]] = 3

            # Placing Black Outside
            for i in range(5):
                qr_matrix[_[0] - 2 + i][_[1] - 2] = 3
                qr_matrix[_[0] - 2][_[1] - 2 + i] = 3
                qr_matrix[_[0] - 2 + i][_[1] + 2] = 3
                qr_matrix[_[0] + 2][_[1] + 2 - i] = 3

            # Placing White On Inside
            for i in range(3):
                qr_matrix[_[0] - 1 + i][_[1] - 1] = 2
                qr_matrix[_[0] - 1][_[1] - 1 + i] = 2
                qr_matrix[_[0] + 1 - i][_[1] + 1] = 2
                qr_matrix[_[0] + 1][_[1] + 1 - i] = 2

    # Setting Up Dark Module
    if version_selection > 1:
        qr_matrix[qr_size - 8][8] = 3

    # Setting Up Format Reservation
    for i in range(17):
        if qr_matrix[8][i] != 3 and qr_matrix[8 - (i - 8)][8] != 3:
            if i < 9:
                qr_matrix[8][i] = 4
            else:
                qr_matrix[8 - (i - 8)][8] = 4
    for i in range(8):
        qr_matrix[8][qr_size - i - 1] = 4
        if i <= 6:
            qr_matrix[qr_size - i - 1][8] = 4

    # Setting Up Version Reservation (Version 7 or up)
    if version_selection >= 7:
        for i in range(3):
            for j in range(6):
                qr_matrix[j][qr_size - 9 - i] = 5
                qr_matrix[qr_size - 9 - i][j] = 5

    # Change 0s and 1s to 8s and 9s respectively to make for an easier unused bits marking
    bitstream = bitstream.replace("0", "8").replace("1", "9")

    # ------------------- Program Main -----------------------
    # Streaming Bits Into Matrix
    cur_y = qr_size - 1
    cur_x = qr_size - 1
    up = True
    bit_index = 0

    for i in range(int((qr_size * qr_size) / 2)):

        if cur_x == 6:
            cur_x -= 1
        if bit_index >= len(bitstream):
            break
        for dx in [0, -1]:
            x = cur_x + dx
            y = cur_y
            if qr_size > y >= 0 == qr_matrix[y][x] and bit_index < len(bitstream):
                qr_matrix[y][x] = int(bitstream[bit_index])
                bit_index += 1
        cur_y -= 1 if up else -1
        if cur_y > qr_size - 1 or cur_y < 0:
            up = not up
            cur_x -= 2

    # Clone Qr Matrix 8 Times For Each Mask
    qr_matrix_clones = [[row[:] for row in qr_matrix] for _ in range(8)]

    # Applying Mask to each version and filling its respective format and version info
    for i in range(len(qr_matrix_clones)):
        qr_matrix_clones[i] = apply_mask(qr_matrix_clones[i], qr_size, i)

        qr_matrix_clones[i] = apply_format(qr_matrix_clones[i], qr_size, error_correction_level, i)
        if version_selection >= 7:
            qr_matrix_clones[i] = apply_version(qr_matrix_clones[i], qr_size, version_selection)

    # Changing All Markings To Be 1s and 0s
    for index in range(len(qr_matrix_clones)):
        for y in range(qr_size):
            for x in range(qr_size):
                if qr_matrix_clones[index][y][x] == 3 or qr_matrix_clones[index][y][x] == 9:
                    qr_matrix_clones[index][y][x] = 1
                elif qr_matrix_clones[index][y][x] == 8 or qr_matrix_clones[index][y][x] == 2 or \
                        qr_matrix_clones[index][y][x] == -1 or qr_matrix_clones[index][y][x] == 4 or \
                        qr_matrix_clones[index][y][x] == 5:
                    qr_matrix_clones[index][y][x] = 0

    # Getting A Evaluated Score List Of Every Masking
    penalty_list = [evaluate_score_condition_1(m) + evaluate_score_condition_2(m)
                    + evaluate_score_condition_3(m) + evaluate_score_condition_4(m) for m in qr_matrix_clones]

    # Picking The Best Masking Pattern
    qr_result = qr_matrix_clones[penalty_list.index(min(penalty_list))]

    # Get ECL Text
    ecl_text = ""
    if error_correction_level == "l":
        ecl_text = "Low (~7% Recovery Capacity)"
    elif error_correction_level == "m":
        ecl_text = "Medium (~15% Recovery Capacity)"
    elif error_correction_level == "q":
        ecl_text = "Quartile (~25% Recovery Capacity)"
    elif error_correction_level == "h":
        ecl_text = "High (~30% Recovery Capacity)"

    # Get Mask Pattern Text
    mask_pattern_formulas = [
        "(x + y) % 2 == 0",  # Mask 0
        "y % 2 == 0",  # Mask 1
        "x % 3 == 0",  # Mask 2
        "(x + y) % 3 == 0",  # Mask 3
        "((x // 3) + (y // 2)) % 2 == 0",  # Mask 4
        "(x * y) % 2 + (x * y) % 3 == 0",  # Mask 5
        "((x * y) % 2 + (x * y) % 3) % 2 == 0",  # Mask 6
        "((x + y) % 2 + (x * y) % 3) % 2 == 0"  # Mask 7
    ]

    # Get Encode Text
    char_encoding_text = ""
    if char_encoding_mode == 1:
        char_encoding_text = "Numeric"
    elif char_encoding_mode == 2:
        char_encoding_text = "Alphanumeric"
    else:
        char_encoding_text = "Byte"

    separator_length = 120
    if print_info:
        print(
            f"\n\n\n\n\n\n\n\n\n\n\n\n\n ----QR-CODE-INFORMATION{"-" * separator_length}\nVersion: {version_selection}\nError Correction Level: {ecl_text}\n"
            f"Encoding Mode: {char_encoding_text}\nMessage: {input_message}\nMask No.: {penalty_list.index(min(penalty_list))} - [{mask_pattern_formulas[penalty_list.index(min(penalty_list))]}]\n"
            f"Mask Score: {min(penalty_list)} [Min.: {min(penalty_list)} - Max.: {max(penalty_list)}]\n{"-" * (separator_length + 24)}\n")

    # Export A BMP Image If export_file is True
    if export_file:
        bmp_gen(qr_result, qr_size, version_selection, error_correction_level.upper(), char_encoding_text,
                input_message)

    if print_qr_code:
        # For Aesthetic Purposes
        if not print_info:
            print(f"\n{"-" * (separator_length + 24)}")

        # For Aesthetic Purposes
        print(f"\n{"-" * (separator_length + 24)}")

        # Printing Out QR CODE
        for _ in qr_result:
            print((str(_).replace(", ", " "))[1:-1])

    # Write Ascii Of 1s and 0s Of Qr Code To A File
    if export_ascii:
        filename = f'qr_ascii_v{version_selection}{error_correction_level.upper()}_{char_encoding_text}_{input_message[:10].replace(" ", "_").replace(".","")}.txt'

        with open (filename, "w") as f:
            f.write("QR 1s and 0s Version\n")
            f.write(f"Message: {input_message}\nVersion: {version_selection}\nEncoding Mode: {char_encoding_text}\nError Correction Level: {ecl_text}\nMask: {penalty_list.index(min(penalty_list))}\n")
            for _ in qr_result:
                f.write((str(_).replace(", ", " "))[1:-1]+"\n")
        f.close()

    # Warning If Both print_qr_code and export_file is turned off
    if not print_qr_code and not export_file:
        print(
            "*** BEWARE!: Both print_qr_code AND export_file are set to FALSE you will not received any result of the qr code***")

# ----------------- Variables ---------------------
# ---- CLI ----
cli_enabled = using_cli
main_menu = True
in_setting = False
in_version = False
in_em = False
in_ecl = False
encode_new_qr = False
in_gen = False
in_gen_confirm = False
in_export_ascii = False
in_export_image = False

# Exporting
export_ascii_file = True
export_image = True

# Initialising Message
cur_message = ""

loaded_data = []

# Load data and check for file existence
try:
    with open("settings.cfg", "r") as f:
        for line in f:
            loaded_data.append(line.strip().replace(" ", "").split("=")[1])
except FileNotFoundError:
    # Create A New File, Set It To Default Values And Load Default Data
    with open('settings.cfg', "x") as f:
        f.write("version = Auto\nencoding_mode = Auto\nerror correction level = Medium")

        loaded_data.append("Auto")
        loaded_data.append("Auto")
        loaded_data.append("Medium")
        loaded_data.append("True")
        loaded_data.append("False")
data_failed = False
# Check For Error In loaded_data
if len(loaded_data) != 5:
   data_failed = True
else:
    if loaded_data[0].isdigit():
        if not 1 <= int(loaded_data[0]) <= 40:
            data_failed = True
    elif loaded_data[0] != "Auto":
        data_failed = True

    if loaded_data[1] != "Auto" and loaded_data[1] != "Numeric" and loaded_data[1] != "Alphanumeric" and loaded_data[1] != "Byte":
        data_failed = True

    if loaded_data[2] != "Medium" and loaded_data[2] != "Low" and loaded_data[2] != "Quartile" and loaded_data[2] != "High":
        data_failed = True

    if loaded_data[3] != "True" and loaded_data[3] != "False":
        data_failed = True

    if loaded_data[4] != "True" and loaded_data[4] != "False":
        data_failed = True

if data_failed:
    cur_version = "Auto"
    cur_encoding_mode = "Auto"
    cur_ecl = "Medium"
    export_ascii_file = "False"
    export_image = "True"
else:
    cur_version = int(loaded_data[0]) if loaded_data[0].isdigit() else loaded_data[0]
    cur_encoding_mode = loaded_data[1]
    cur_ecl = loaded_data[2]
    export_image = True if loaded_data[3] == "True" else False
    export_ascii_file = True if loaded_data[4] == "True" else False
# Check If Cli Is Enabled Else Just Generate Without A Proper CLI
# There will be prompts to fill in the necessary data if CLI is not enabled
if cli_enabled:
    while True:

        # Save Config Data After Each Iteration
        with open("settings.cfg", "w") as f:
            f.write(f"version = {cur_version}\n")
            f.write(f"encoding_mode = {cur_encoding_mode}\n")
            f.write(f"error correction level = {cur_ecl}\n")
            f.write(f"export image = {export_image}\n")
            f.write(f"export ascii = {export_ascii_file}")
        f.close()

        if main_menu:
            print("\n\n\n\n\n")
            print("====================================\n"
                  "|           qrgen0_v1.1            |\n"
                  "|------------Main-Menu-------------|\n"
                  "|[1]. Encode New Qr                |\n"
                  "|[2]. Settings                     |\n"
                  "|[3]. Exit                         |\n"
                  "============MADE-BY-BEAN============")
        elif in_setting:
            print("\n\n\n\n\n\n\n")
            print("===============================================\n"
                  "|                qrgen0_v1.1                  |\n"
                  "|------------------Settings-------------------|\n"
                  f"|[1]. Version : {cur_version}{" "*(30-len(str(cur_version)))}|\n"
                  f"|[2]. Encoding Mode: {cur_encoding_mode}{" "*(25-len(str(cur_encoding_mode)))}|\n"
                  f"|[3]. Error Correction Level: {cur_ecl}{" "*(16-len(str(cur_ecl)))}|\n"
                  f"|---------------------------------------------|\n"
                  f"|[4]. Export QR Image: {export_image}{" "*(23-len(str(export_image)))}|\n"
                  f"|[5]. Export QR Ascii: {export_ascii_file}{" "*(23-len(str(export_ascii_file)))}|\n"
                  f"|---------------------------------------------|\n"
                  f"|[6]. Back                                    |\n"
                  "==================MADE-BY-BEAN=================")
        elif in_version:
            print("\n\n\n\n\n\n\n")
            print("================================================\n"
                  "|                qrgen0_v1.1                   |\n"
                  "|------------------Settings------------------- |\n"
                  f"|Current Version : {cur_version}{" " * (28 - len(str(cur_version)))}|\n"
                  f"| (a for Auto) (1 - 40 for Manual) (e for exit)|\n"
                  "==================MADE-BY-BEAN==================")
        elif in_em:
            print("\n\n\n\n\n\n\n")
            print("================================================\n"
                  "|                qrgen0_v1.1                   |\n"
                  "|------------------Settings------------------- |\n"
                  f"|Current Encoding Mode : {cur_encoding_mode}{" " * (22 - len(str(cur_encoding_mode)))}|\n"
                  f"| (a for Auto) (e for exit) (1 for Numeric)    |\n"
                  f"| (2 for Alphanumeric) (3 for Byte)            |\n"
                  "=================MADE-BY-BEAN===================")
        elif in_ecl:
            print("\n\n\n\n\n\n\n")
            print("============================================================\n"
                  "|                        qrgen0_v1.1                       |\n"
                  "|-------------------------Settings-------------------------|\n"
                  f"|Current Error Correction Level : {cur_ecl}{" " * (25 - len(str(cur_ecl)))}|\n"
                  f"| (e for exit) (1 for Low ~7%) (2 For Medium ~15%)         |\n"
                  f"| (3 for Quartile ~25%) (4 for High ~30%)                  |\n"
                  "========================MADE-BY-BEAN========================")
        elif in_gen:
            print("\n\n\n\n\n\n\n")
            print("=============================================================\n"
                  "|                      qrgen0_v1.1                          |\n"
                  "|---------------------Generating-QR-------------------------|\n"
                  f"|QR Message :                                               |\n"
                  f"|-----------------------------------------------------------|\n"
                  f"|[-]. Version : {cur_version}{" "*(44-len(str(cur_version)))}|\n"
                  f"|[-]. Encoding Mode: {cur_encoding_mode}{" "*(39-len(str(cur_encoding_mode)))}|\n"
                  f"|[-]. Error Correction Level: {cur_ecl}{" "*(30-len(str(cur_ecl)))}|\n"
                  f"|-----------------------------------------------------------|\n"
                  f"|[-]. Export QR Image: {export_image}{" "*(37-len(str(export_image)))}|\n"
                  f"|[-]. Export QR Ascii: {export_ascii_file}{" "*(37-len(str(export_ascii_file)))}|\n"
                  "======================MADE-BY-BEAN===========================")
        elif in_gen_confirm:
            print("\n\n\n\n\n\n\n")
            print("=============================================================\n"
                  "|                      qrgen0_v1.1                          |\n"
                  "|---------------------Generating-QR-------------------------|\n"
                  f"|QR Message : {cur_message}{" " * (46 - len(cur_message))}|\n"
                  f"|-----------------------------------------------------------|\n"
                  f"|[-]. Version : {cur_version}{" " * (44 - len(str(cur_version)))}|\n"
                  f"|[-]. Encoding Mode: {cur_encoding_mode}{" " * (39 - len(str(cur_encoding_mode)))}|\n"
                  f"|[-]. Error Correction Level: {cur_ecl}{" " * (30 - len(str(cur_ecl)))}|\n"
                  f"|-----------------------------------------------------------|\n"
                  f"|[-]. Export QR Image: {export_image}{" " * (37 - len(str(export_image)))}|\n"
                  f"|[-]. Export QR Ascii: {export_ascii_file}{" " * (37 - len(str(export_ascii_file)))}|\n"
                  "======================MADE-BY-BEAN===========================")
        elif in_export_image:
            print("\n\n\n\n\n\n\n")
            print("==============================================================\n"
                  "|                        qrgen0_v1.1                         |\n"
                  "|--------------------------Settings--------------------------|\n"
                  f"|Export Image : {export_image}{" " * (40 - len(cur_message))}|\n"
                  f"|[e]. Exit                                                   |\n"
                  "=======================MADE-BY-BEAN===========================")
        elif in_export_ascii:
            print("\n\n\n\n\n\n\n")
            print("==============================================================\n"
                  "|                        qrgen0_v1.1                         |\n"
                  "|--------------------------Settings--------------------------|\n"
                  f"|Export ASCII : {export_ascii_file}{" " * (40 - len(cur_message))}|\n"
                  f"|[e]. Exit                                                   |\n"
                  "=======================MADE-BY-BEAN===========================")
        if in_version:
            user_input = input("<Version> ")
        elif in_em:
            user_input = input("<Encoding Mode> ")
        elif in_ecl:
            user_input = input("<Error Correction Level> ")
        elif in_gen:
            user_input = input("<QR Message> ")
        elif in_gen_confirm:
            user_input = input("<Are You Sure? [y/n]> ")
        elif in_export_image:
            user_input = input("<Export Image [true/false]> ")
        elif in_export_ascii:
            user_input = input("<Export ASCII [true/false]> ")
        else:
            user_input = input("<Option> ")

        if main_menu:
            if user_input == "1":
                main_menu = False
                in_gen = True
            elif user_input == "2":
                main_menu = False
                in_setting = True
            elif user_input == "3":
                print("\n\n\n\n\n\n\n\n")
                quit()
        elif in_setting:
            if user_input == "1":
                in_setting = False
                in_version = True
            elif user_input == "2":
                in_setting = False
                in_em = True
            elif user_input == "3":
                in_setting = False
                in_ecl = True
            elif user_input == "4":
                in_setting = False
                in_export_image = True
            elif user_input == "5":
                in_setting = False
                in_export_ascii = True
            elif user_input == "6":
                main_menu = True
                in_setting = False
        elif in_version:
            if user_input.lower() == "a":
                cur_version = "Auto"
                in_setting = True
                in_version = False
            elif user_input.isdigit():
                if 1 <= int(user_input) <= 40:
                    cur_version = int(user_input)
                    in_setting = True
                    in_version = False
                else:
                    print("Invalid Version")
            elif user_input.lower() == "e":
                in_setting = True
                in_version = False
            else:
                print("Invalid Version")
        elif in_em:
            if user_input.lower() == "a":
                cur_encoding_mode = "Auto"
                in_setting = True
                in_em = False
            elif user_input.lower() == "1":
                cur_encoding_mode = "Numeric"
                in_setting = True
                in_em = False
            elif user_input.lower() == "2":
                cur_encoding_mode = "Alphanumeric"
                in_setting = True
                in_em = False
            elif user_input.lower() == "3":
                cur_encoding_mode = "Byte"
                in_setting = True
                in_em = False
            elif user_input.lower() == "e":
                in_setting = True
                in_em = False
            else:
                print("Invalid Encoding Mode")
        elif in_ecl:
            if user_input.lower() == "e":
                in_ecl = False
                in_setting = True
            elif user_input == "1":
                cur_ecl = "Low"
                in_ecl = False
                in_setting = True
            elif user_input == "2":
                cur_ecl = "Medium"
                in_ecl = False
                in_setting = True
            elif user_input == "3":
                cur_ecl = "Quartile"
                in_ecl = False
                in_setting = True
            elif user_input == "4":
                cur_ecl = "High"
                in_ecl = False
                in_setting = True
            else:
                print("Invalid Error Correction Level")
        elif in_gen:
            if user_input != "":
                cur_message = user_input
                in_gen = False
                in_gen_confirm = True
        elif in_gen_confirm:
            if user_input == "" or user_input.lower() == "n" or user_input.lower() == "no":
                cur_message = ""
                in_gen = False
                in_gen_confirm = False
                main_menu = True
            else:
                # Processing Datas To Feed The QR GENERATING Function
                feeding_version = 1
                if cur_version == "Auto":
                    feeding_version = "a"
                else:
                    feeding_version = int(cur_version)

                feeding_encoding_mode = 3
                if cur_encoding_mode == "Auto":
                    feeding_encoding_mode = "a"
                elif cur_encoding_mode == "Numeric":
                    feeding_encoding_mode = "1"
                elif cur_encoding_mode == "Alphanumeric":
                    feeding_encoding_mode = "2"
                elif cur_encoding_mode == "Byte":
                    feeding_encoding_mode = "3"

                feeding_ecl = "l"
                if cur_ecl == "Low":
                    feeding_ecl = "l"
                elif cur_ecl == "Medium":
                    feeding_ecl = "m"
                elif cur_ecl == "Quartile":
                    feeding_ecl = "q"
                elif cur_ecl == "High":
                    feeding_ecl = "h"

                in_gen_confirm = False
                main_menu = True
                generate_QR(cur_message, cli_enabled, feeding_ecl, feeding_encoding_mode, feeding_version, export_image, export_ascii_file)
                print("Success!!")
                input("Enter To Quit> ")
                quit()
        elif in_export_image:
            if user_input.lower() == "true" or user_input.lower() == "t" or user_input == "1":
                export_image = True
                in_export_image = False
                in_setting = True
            elif user_input.lower() == "false" or user_input.lower() == "f" or user_input == "0":
                export_image = False
                in_export_image = False
                in_setting = True
            elif user_input.lower() == "e":
                in_export_image = False
                in_setting = True
            else:
                print("Invalid Mode")
        elif in_export_ascii:
            if user_input.lower() == "true" or user_input.lower() == "t" or user_input == "1":
                export_ascii_file = True
                in_export_ascii = False
                in_setting = True
            elif user_input.lower() == "false" or user_input.lower() == "f" or user_input == "0":
                export_ascii_file = False
                in_export_ascii = False
                in_setting = True
            elif user_input.lower() == "e":
                in_export_ascii = False
                in_setting = True
            else:
                print("Invalid Mode")
else:
    generate_QR()