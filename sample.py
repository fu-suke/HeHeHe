def generate_code_for_string(input_str):
    program_parts = []
    for char in input_str:
        char_code = ord(char)
        # ここで文字コードを隠蔽するための計算を行う
        # 例: char_codeを2で割った値に2を足して再び2を掛ける（元の値に戻る）
        masked_code = f"(int({char_code} / 2 * 2))"
        program_parts.append(f"chr({masked_code})")

    # 文字列を連結して完全なプログラムを作成
    program = " + ".join(program_parts)
    return program


# 例
input_str = "abcde"
output_program = generate_code_for_string(input_str)
print(output_program)  # 出力例: chr((97 // 2 + 2) * 2)

exec("print(" + output_program + ")")