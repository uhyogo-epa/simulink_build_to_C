#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 14:19:21 2025

@author: hashima
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulinkモデル 'combined_cycle' から生成された共有ライブラリを
Pythonから実行し、パラメータや入出力を操作するスクリプト。
"""
import ctypes
import os
import sys

# --- 1. ライブラリのロード ---
# slbuildが生成した共有ライブラリへのパス
LIB_PATH = './combined_cycle.so' 

if not os.path.exists(LIB_PATH):
    print(f"エラー: 共有ライブラリ '{LIB_PATH}' が見つかりません。")
    sys.exit(1)

try:
    lib = ctypes.CDLL(LIB_PATH)
except OSError as e:
    print(f"エラー: ライブラリのロードに失敗しました: {e}")
    sys.exit(1)


# --- 2. C言語の構造体をPythonで定義 ---
# Cヘッダファイル (params_T.h, combined_cycle.h) の定義と完全に一致させます
# rtwtypes.h より、real_T は double (ctypes.c_double) です

class params_T(ctypes.Structure):
    """ パラメータ構造体 (params_T.h) """
    _fields_ = [
        ('K3', ctypes.c_double),
        ('K6', ctypes.c_double),
        ('h_step',ctypes.c_double)
    ]
    
    
# class simSet_T(ctypes.Structure):
#     """ パラメータ構造体 (simSet_T.h) """
#     _fields_ = [
#         ('h_step', ctypes.c_double)
#     ]
    
class init_state_T(ctypes.Structure):
    """ パラメータ構造体 (init_state_T.h) """
    _fields_ = [
        ('X1', ctypes.c_double),
        ('X2', ctypes.c_double)
    ]

class ExtU(ctypes.Structure):
    """ 入力構造体 (combined_cycle.h) """
    _fields_ = [
        ('In1', ctypes.c_double)
    ]

class ExtY(ctypes.Structure):
    """ 出力構造体 (combined_cycle.h) """
    _fields_ = [
        ('Te', ctypes.c_double),
        ('Eg', ctypes.c_double),
        ('Es', ctypes.c_double),
        ('Wf', ctypes.c_double),
        ('Wr', ctypes.c_double)
    ]


# --- 3. Cのグローバル変数へのリンク ---
try:
    P = params_T.in_dll(lib, "params")
    init = init_state_T.in_dll(lib, "init_state")
    U = ExtU.in_dll(lib, "combined_cycle_U")
    Y = ExtY.in_dll(lib, "combined_cycle_Y")
except ValueError as e:
    print(f"エラー: ライブラリ内にグローバル変数が見つかりません: {e}")
    sys.exit(1)


# --- 4. 関数のプロトタイプを定義 ---
# 今回の設計では、全ての関数は引数を持ちません
lib.combined_cycle_initialize.argtypes = []
lib.combined_cycle_initialize.restype = None

lib.combined_cycle_step.argtypes = []
lib.combined_cycle_step.restype = None

lib.combined_cycle_terminate.argtypes = []
lib.combined_cycle_terminate.restype = None


# --- 5. シミュレーションの実行 ---

lib.combined_cycle_initialize()

# パラメータと入力値をPythonから設定
P.K6 = 0.23 
P.K3 = 0.73


U.In1 = 0.82 # モデルへの入力を設定



# モデルを1ステップ実行

lib.combined_cycle_step()

# 結果を出力構造体から読み出す

print(f"出力 Te = {Y.Te:.4f}")
print(f"出力 Eg = {Y.Eg:.4f}")
print(f"出力 Es = {Y.Es:.4f}")



for i in range(5):
    lib.combined_cycle_step()
    print(f"  ステップ {i+2}: Te = {Y.Te:.4f}")

# モデルの終了処理

lib.combined_cycle_terminate()
