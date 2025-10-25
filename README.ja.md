# 💡 PanasonicLightIrControl

このリポジトリは、Panasonic製照明器具（HK9327Kリモコン規格準拠）を制御するための**各種赤外線（IR）制御システムの統合プロジェクト**です。

Windows CLIツール、スタンドアロンArduinoスケッチ、M5Stackなど、異なるハードウェアや環境でIR信号の送信・解析を行うためのシステムを**モノリポジトリ**形式で管理しています。

## 📁 Data (共通データ)

`/Data` フォルダには、プロジェクト全体で共通利用される静的アセットとデータが格納されています。

| ファイル/フォルダ | 内容 | 用途 |
| :--- | :--- | :--- |
| `panasonic_hk9327k_signals.csv` | **IR RAWタイミングデータ** | リモコンの各ボタンに対応するRAWデータを格納したCSVファイルです。 |
| `HK9327K.jpg` | **リモコンの写真** | 制御対象とするリモコン（HK9327K）の外観写真です。 |

---

## 🛠️ Systems (システム一覧)

現在開発・運用されているシステムは以下の通りです。詳細なセットアップ手順、使い方、動作環境については、各フォルダ内の `README.md` を参照してください。

### 1. [IrCliSender (Windows CLI 送信システム)](./IrCliSender/README.md)

| 概要 | Windows PCのコマンドラインでpython scriptを実行し、Arduino Uno経由でIR信号を送信するシステムです。 |
| :--- | :--- |
| **構成** | Pythonスクリプト (`cli_ir_send.py`) と Arduino スケッチ (`IrCliSender.ino`) |
| **目的** | 設定されたチャンネルとボタンに対応するIR信号を送信します。 |

### 2. [IrAnalyze (IRデータ解析システム)](./IrAnalyze/README.md)

| 概要 | Panasonic HK9327KリモコンのIR信号をキャプチャし、RAWタイミングデータを解析するためのシステムです。|
| :--- | :--- |
| **構成** | Arduino スケッチと、解析を補助するPythonスクリプト |
| **目的** | IRレシーバーで受信した信号のRAWデータを取得・表示し、共通CSVデータを生成します。 |

---

## 🚀 Get Started (共通手順)

Gitリポジトリのクローンは、通常の操作で実行できます。特別な手順は必要ありません。

```bash
git clone https://github.com/ito55/PanasonicLightIrControl.git
cd PanasonicLightIrControl