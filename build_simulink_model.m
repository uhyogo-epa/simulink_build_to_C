% 
% --- Simulinkのモデルをc言語の動的ライブラリにビルドするためのスクリプト -----
%
% セクション１：: ユーザ設定（ここを編集してください）
%    - ビルドするSimulinkモデル名を入力
%    - ビルドする場合には build_on  = 1;
%    - シミュレーション設定(時間ステップなど), モデルのパラメータ, 初期値などを実行時に変更するための準備
%
%　セクション2:
%
%
clear;
clc;
%% ユーザ設定（ここを編集してください） %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%=================
% Simulinkモデル名
%=================
modelName = 'combined_cycle';  

%===============================================
% モデルのビルド (ビルドする場合: 1，チェックのみ: ０)
%===============================================
build_on  = 1;

%% ==========================
% シミュレーション設定
%==========================
% 構造体型の定義
simSet_T = Simulink.Bus;
simSet_T.Description = 'シミュレーションの設定';
simSet_T.DataScope   = 'Exported';
simSet_T.HeaderFile  = 'simSet_T.h';
simSet_T.Elements(1) = Simulink.BusElement;
simSet_T.Elements(1).Name     = 'h_step'; %時間ステップ
simSet_T.Elements(1).DataType = 'double';
% 値の設定(変数としての出力に必要)
simSet = Simulink.Parameter;
simSet.DataType     = 'Bus: simSet_T';
simSet.StorageClass = 'ExportedGlobal';
simSet.Value.h_step = 0.1;






%% ==========================
% モデルパラメータの設定
%==========================
% 構造体型の定義
params_T = Simulink.Bus;
params_T.Description = 'モデルパラメータの設定';
params_T.DataScope   = 'Exported';
params_T.HeaderFile  = 'params_T.h';
params_T.Elements(1) = Simulink.BusElement;
params_T.Elements(1).Name     = 'K3';
params_T.Elements(1).DataType = 'double';
params_T.Elements(2) = Simulink.BusElement;
params_T.Elements(2).Name     = 'K6';
params_T.Elements(2).DataType = 'double';
% 値の設定(変数としての出力に必要)
params = Simulink.Parameter;
params.DataType     = 'Bus: params_T';
params.StorageClass = 'ExportedGlobal';
params.Value.K3     = 0.7;
params.Value.K6     = 0.3;

%% ==========================
% 初期値の設定
%==========================
% 構造体型の定義
init_state_T = Simulink.Bus;
init_state_T.Description = 'モデルパラメータの設定';
init_state_T.DataScope   = 'Exported';
init_state_T.HeaderFile  = 'init_state_T.h';
init_state_T.Elements(1) = Simulink.BusElement;
init_state_T.Elements(1).Name     = 'X1';
init_state_T.Elements(1).DataType = 'double';
init_state_T.Elements(2) = Simulink.BusElement;
init_state_T.Elements(2).Name     = 'X2';
init_state_T.Elements(2).DataType = 'double';
% 値の設定(変数としての出力に必要)
init_state = Simulink.Parameter;
init_state.DataType     = 'Bus: init_state_T';
init_state.StorageClass = 'ExportedGlobal';
init_state.Value.X1     = 0.7;
init_state.Value.X2     = 0.3;


%% ビルドのためのSimlink設定　%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% === ソルバー設定 ===
% ターゲットファイルをEmbedded Coder (ert.tlc) に設定
set_param(modelName, 'SystemTargetFile', 'ert_shrlib.tlc');

% ソルバーのタイプを「固定ステップ」に設定
set_param(modelName, 'SolverType', 'Fixed-step');

% 「連続時間」のサポートを有効にする ('on'に設定)
set_param(modelName, 'SupportContinuousTime', 'on');

% 固定ステップサイズに、先ほど作成したパラメータオブジェクト'Ts'を指定
set_param(modelName, 'FixedStep', 'simSet.h_step');

% コードインターフェイスのパッケージ化を「再利用不可な関数」に設定
set_param(modelName, 'CodeInterfacePackaging', 'Nonreusable function');

% 周期的サンプル時間の制約を「サンプル時間の独立性を保証」に設定
% これにより、FixedStepで指定した周期以外のレートがモデルに存在してもエラーになりません。
set_param(modelName, 'SampleTimeConstraint', 'Unconstrained');



% Simulinkモデルの読み込み
if ~bdIsLoaded(modelName)
    load_system(modelName);
end

% Simulinkデータディクショナリの作成とモデルへのリンク
fprintf("モデル '%s' のデータディクショナリを設定します...\n", modelName);
ddFileName = [modelName '_data.sldd'];
if ~isfile(ddFileName)
    fprintf("データディクショナリ '%s' を新規作成します。\n", ddFileName);
    dd = Simulink.data.dictionary.create(ddFileName);
else
    fprintf("既存のデータディクショナリ '%s' を開きます。\n", ddFileName);
    dd = Simulink.data.dictionary.open(ddFileName);
end
set_param(modelName, 'DataDictionary', ddFileName);
fprintf("モデル '%s' をデータディクショナリにリンクしました。\n", modelName);

% Simulink Busオブジェクト (構造体型の定義) をディクショナリに登録または更新
dDataSect  = getSection(dd, 'Design Data');
busObjects = {'params_T', 'simSet_T','init_state_T'};
for i = 1:length(busObjects)
    try
        % 既存のエントリがあればそれを更新
        entryObj = getEntry(dDataSect, busObjects{i});
        entryObj.setValue(eval(busObjects{i}));
        fprintf("既存のBusオブジェクト '%s' を更新しました。\n", busObjects{i});
    catch
        % エントリが存在しない場合には新規作成
        addEntry(dDataSect, busObjects{i}, eval(busObjects{i}));
        fprintf("Busオブジェクト '%s' を新規登録します。\n", busObjects{i});
    end
end

% Simulin Parameterオブジェクト（構造体変数）をディクショナリに登録または更新
paramObjects = {'params', 'simSet','init_state'};
for i = 1:length(paramObjects)
    try
        % 同様に、まず「更新」を試みる
        entryObj = getEntry(dDataSect, paramObjects{i});
        entryObj.setValue(eval(paramObjects{i}));
        fprintf("既存のParameterオブジェクト '%s' を更新しました。\n", paramObjects{i});
    catch
        % 失敗したら「新規作成」する
        addEntry(dDataSect, paramObjects{i}, eval(paramObjects{i}));
        fprintf("Parameterオブジェクト '%s' を新規登録します。\n", paramObjects{i});
    end
end

% 保存して完了
fprintf("変更をデータディクショナリとモデルに保存しています...\n");
saveChanges(dd);
save_system(modelName);
close(dd);
fprintf("セットアップが正常に完了しました。\n");



%% ビルド
if build_on == 1
    slbuild(modelName);
end