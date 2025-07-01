#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 14:19:21 2025

@author: hashima
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulinkモデル 'simulink_model' から生成された共有ライブラリを
Pythonから実行し、パラメータや入出力を操作するスクリプト。
"""
#================================================================================================================
#                使用する前に{simulink_model}を使用するsimulinkのモデルの名前に置換してください
#================================================================================================================


import ctypes
import os
import sys

# --- 1. ライブラリのロード ---
# slbuildが生成した共有ライブラリへのパス
LIB_PATH = './{simulink_model}.so' 

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
        # matlab上で定義したparamsの要素すべて書き出す
        ('K3', ctypes.c_double),
        ('K6', ctypes.c_double)
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
        #In1はsimulinkで使用している入力の名前，入力の数だけ羅列する
        ('In1', ctypes.c_double)
    ]

class ExtY(ctypes.Structure):
    """ 出力構造体 (combined_cycle.h) """
    _fields_ = [
        #simulinkで使用されている出力の名前すべて羅列する
        ('Te', ctypes.c_double),
        ('Eg', ctypes.c_double),
        ('Es', ctypes.c_double),
        ('Wf', ctypes.c_double),
        ('Wr', ctypes.c_double)
    ]


# --- 3. Cのグローバル変数へのリンク ---
try:
    #parms,init_stateはmatlabで定義した名前，{simulink_model}_U,Yは自動生成されるため固定
    P = params_T.in_dll(lib, "params")
    init = init_state_T.in_dll(lib, "init_state")
    U = ExtU.in_dll(lib, "{simulink_model}_U")
    Y = ExtY.in_dll(lib, "{simulink_model}_Y")
except ValueError as e:
    print(f"エラー: ライブラリ内にグローバル変数が見つかりません: {e}")
    sys.exit(1)


# --- 4. 関数のプロトタイプを定義 ---
# 今回の設計では、全ての関数は引数を持ちません
lib.{simulink_model}_initialize.argtypes = []
lib.{simulink_model}_initialize.restype = None

lib.{simulink_model}_step.argtypes = []
lib.{simulink_model}_step.restype = None

lib.{simulink_model}_terminate.argtypes = []
lib.{simulink_model}_terminate.restype = None


# --- 5. シミュレーションの実行 ---

lib.{simulink_model}_initialize()

# パラメータと入力値をPythonから設定
P.K6 = 0.23 
P.K3 = 0.73


U.In1 = 0.82 # モデルへの入力を設定



# モデルを1ステップ実行

lib.{simulink_model}_step()

# 結果を出力構造体から読み出す

print(f"出力 Te = {Y.Te:.4f}")
print(f"出力 Eg = {Y.Eg:.4f}")
print(f"出力 Es = {Y.Es:.4f}")



for i in range(5):
    lib.{simulink_model}_step()
    print(f"  ステップ {i+2}: Te = {Y.Te:.4f}")

# モデルの終了処理

lib.{simulink_model}_terminate()
