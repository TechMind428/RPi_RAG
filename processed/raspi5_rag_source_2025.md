# Raspberry Pi 5 総合リファレンス（RAG基盤用）
最終更新: 2025-10-13

本ドキュメントは、Raspberry Pi 5 に関する複数の日本語ソースを**情報密度重視**で要約・統合したものです。RAGのチャンク化を想定し、見出し単位で短い箇条書きに整形しています。各ブロック末尾に**Source**を付記しています。

> Notes for English searchers: The body is in Japanese, but each section includes English keywords to improve retrieval with multilingual embeddings.

## 1. ハードウェア概要 / Hardware Overview

**Keywords (EN):** Raspberry Pi 5 specs, Broadcom SoC, CPU GPU RAM, VideoCore, clock speed

- 英Raspberry Pi財団は現地時間9月28日、シングルボードコンピューターの最新版となる「Raspberry Pi 5」を発表した。CPU性能や拡張性など、さまざまな機能強化がなされている。提供：Raspberry Pi/ZDNET
- _EN_: On September 28, local time, the UK's Raspberry Pi Foundation announced the latest version of its single-board computer, the Raspberry Pi 5.Various functional enhancements have been made, including CPU performance and expandability.Provided by: Raspberry Pi/ZDNET
- その筆頭となるのが、BroadcomのSoC「BCM2712」（クアッドコア64ビット「Arm Cortex-A76」プロセッサー搭載）だ。「Raspberry Pi 4」に搭載されていたものより約2～3倍高速であるばかりか、消費電力も少ないため、発熱も抑えられる。提供：Raspberry Pi/ZDNET
- GPUはBroadcom製「VideoCore VII」で、旧GPUの2～3倍の性能を誇る。2台の4Kp60ディスプレイに対応し、1台の4Kp60ディスプレイか2台の4Kp30ディスプレイにしか対応していなかったRaspberry Pi 4と比べ、大きく進歩した。
- - Raspberry Pi 5 2.4GHzクアッドコア64ビットArm Cortex-A76 CPU
- _EN_: - 2.4GHz quad-core 64-bit Arm Cortex-A76 CPU
  
Source: japan_zdnet_com_article_35209685.md

- - Raspberry Pi 5 VideoCore VII GPU（OpenGL ES 3.1、Vulkan 1.2に対応）
- _EN_: - VideoCore VII GPU (compatible with OpenGL ES 3.1, Vulkan 1.2)
- - Raspberry Pi 5 LPDDR4X-4267 SDRAM（4GB/8GBを提供）
- _EN_: - LPDDR4X-4267 SDRAM (provides 4GB/8GB)
- - Raspberry Pi 5 リアルタイムクロック
- ### CPUは2015年頃のPC並の性能へ（Raspberry Pi 5）
  
Source: japan_zdnet_com_article_35209685.md; pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _In English_: The CPU has the same performance as a PC around 2015 (Raspberry Pi 5)
- Raspberry Pi 5 本体中央の銀色のカバーが付いている部品がSoCで、「Broadcom BCM2712」を搭載している。
- _EN_: The part with a silver cover in the center of the main body is the SoC, which is equipped with the "Broadcom BCM2712".
- CPUはクアッドコア2.4GHzのArm Cortex-A76を採用している。A76は2018年に登場したArmのCPUコアで、過去の記事では「Intel Skylake世代の90%に迫る性能」と紹介されたり、Raspberry Pi LtdのEben Upton CEOがJavaScriptのJetStream 1.1ベンチマークにおいて「2015年のMacBook Air程度の性能」と発言したりしていることから、8～9年ほど前のPCの性能と考えて良さそうだ。
- Raspberry Pi 5 GPUはVideoCore VII GPUを採用し、OpenGL ES 3.1とVulkan 1.2をサポートしている。
- _EN_: The GPU uses VideoCore VII GPU and supports OpenGL ES 3.1 and Vulkan 1.2.
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- また、内蔵デコーダに関しては、60fpsの4K HEVCデコーダを搭載している。Pi 4に搭載されていたH.264デコーダ/エンコーダは含まれていないが、Raspberry Pi Ltd CTOのGordon Hollingworth氏は「ハードウェアエンコーダは品質が比較的悪かったが、CPU処理では適切な品質を選択でき、1080p60のエンコードには1プロセッサあればPi4よりも高品質に処理できる」と、コメントしている。
- Raspberry Pi 5 RP1チップとSoCの間はPCI Express 2.0 x4で接続されており、2つのUSB 3.0+USB 2.0コントローラ、Gigabit Ethernet MAC、2つのMIPI(カメラとディスプレイ)、GPIOなどがこのRP1チップによって提供される。
- Raspberry Pi 5 ファンはSoCの温度に応じて加減速し、必要がない時は停止する。手元で起動したままにしている限りでは、アイドル状態なら基本的に停止していることの方が多く、時々低速で回転する程度の動作となっている。
- _EN_: The fan speeds up and slows down depending on the SoC temperature, and stops when not needed.As long as I leave it running at hand, most of the time it's basically stopped when it's idling, and it only occasionally rotates at a low speed.
- Raspberry Piは、これまで時刻を保存するRTC(リアルタイムクロック)を搭載していなかった。このため、時刻を正確に保つには、起動時にNTPで時刻同期をするか、RTCモジュールを別途搭載する必要があった。
- Raspberry Pi 5 一般的なUSB PD電源アダプタは、5Vの場合3AのPDOしか持たないため、30Wや60Wや120Wの電源を用いても、Raspberry Pi 5には5V/3Aしか供給できない。また、電圧や電流を細かく調整するためのPPS(Programmable Power Supply)規格には非対応で、今後の対応の可能性は五分五分との発言もみられるが、過度な期待はしないほうが良さそうだ。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 Raspberry Pi 5では、CPUでaesやsha1、sha2がサポートされた。/proc/cpuinfoを見ると、Pi 4に比べてFeatures数が増えているのが確認できる。
- _EN_: In Raspberry Pi 5, the CPU supports AES, SHA1, and SHA2.Looking at /proc/cpuinfo, you can see that the number of Features has increased compared to Pi 4.
- Raspberry Pi 5 `$ cat /proc/cpuinfo`
- _EN_: `$ cat /proc/cpuinfo`
- _EN_: (Pi5)
- Raspberry Pi 5 Features : fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: Features : fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp
- Raspberry Pi 5 Features : fp asimd evtstrm crc32 cpuid
- _EN_: Features : fp asimd evtstrm crc32 cpuid
- Raspberry Pi 5 CPUでの暗号化処理サポートによって、暗号化処理のパフォーマンスがPi 4よりも大幅に向上している。OpenSSLのスピードテストを実行して比較すると、AESの場合で14.5～37.7倍、sha1、sha226の場合で2.7～8.8倍の性能向上が確認できた。OpenVPNサーバーや、SSLを有効化したWebサーバーの運用などでパフォーマンスの向上が見込めそうだ。
- Raspberry Pi 5 また、デスクトップ上部のパネルにGPU使用率グラフを追加して使用率を確認すると、どちらもGPUをフルに使用していることが確認できたため、どちらもGPUをフルで動かした状態でこのような差が出ていることが確認できた。なお、ウィンドウを小さくした場合では、Raspberry Pi 5では60fpsに達し、Pi 4は25fps前後となった。
- Raspberry Pi 5 CPUへの負荷かけは「yes > /dev/null &」を4つ実行した。また、ストレージへの負荷かけはddコマンドによる書き込みとした。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: To increase the load on the CPU, execute "yes > /dev/null &" four times.In addition, the load on the storage was written using the dd command.
- Raspberry Pi 5 | モデル/取得パターン | アイドル時 | 高負荷時(CPU) | 高負荷時(ストレージ) |
- _EN_: | Model/Acquisition Pattern | Idle | High Load (CPU) | High Load (Storage) |
- Raspberry Pi 5 Pi 4とRaspberry Pi 5を比べると、アイドル時で約1.4W差、CPUの高負荷時で約2.2W差となった。しかし、高負荷時にみられた7.6Wは1.52Aということになるため、ここから消費電力が5V/5A=25Wに迫るほどRaspberry Pi 5を使い切るのはなかなか難しそうに感じた。
- _EN_: BOOT_ORDER=0xf146
- Raspberry Pi 5 しかし、現時点では60ドルの4GB RAMモデルと、80ドルの8GB RAMしか販売されていないため、これまでのModel Bの基本価格である35ドルモデルに相当していた1GB RAMモデルや、45ドルに相当していた2GB RAMモデルが選択できない。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 仮に、35ドルで(もしかすると40ドルかもしれないが)1GB RAMのRaspberry Pi 5が出たとして、欲しいかと言われると、CPU性能とのバランス的に微妙で悩ましいので、大容量RAMのモデルのみが販売されている現状は仕方ない気がするが、「35ドルPC」と呼べなくなっている点についてはすこし寂しくも思う。
- Raspberry Pi 5 | 世代/RAM容量 | 1GB | 2GB | 4GB | 8GB |
- _EN_: | Generation/RAM capacity | 1GB | 2GB | 4GB | 8GB |
- Raspberry Pi 5 そして、日本では円安の進行が、高価格化したように見える現象に追い打ちをかける。2019年頃(当時約108円/ドル)にPi 4 4GB RAMモデルが7,000円前後で買えた頃や、2012年(当時約80円/ドル)に初代が3,000円で買えた頃を思い返すと、現在のRaspberry Pi 5の価格は1万円の大台を超えてしまっており、これまでのように「気軽に買って、最悪引き出しの肥やしにしちゃってもいいか! 」といった衝動買い的な買い方をするにはかなり勇気がいるようになってしまったのが悩ましい。
- Raspberry Pi 5 | ストア/RAM容量 | 4GB | 8GB |
- _EN_: | Store/RAM capacity | 4GB | 8GB |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 筆者自身は、4GB RAMモデルと8GB RAMモデルを1台ずつ購入し、手元での作業用や、イベント展示用として月に1度程度の頻度で出動させたりしている。
- _EN_: I personally purchased one 4GB RAM model and one 8GB RAM model, and use them about once a month for on-site work and for exhibitions at events.
- 勤務先ではOpenVPNサーバーをRaspberry Pi 5で構築すべく作業中である。現在は「Jetson Nano」がOpenVPNサーバーとして稼働しているが、OSのサポートがUbuntu18.04までで終了してしまい、本来あまり汎用的なSBCでもないため、Raspberry Pi 5が発表された瞬間から絶対にRaspberry Pi 5で置き換えようと決めていた。設置にあたり、設置先のサーバールームで室温の計測をしていたRaspberry Pi 1 Model B+の役割もRaspberry Pi 5に統合して、機材数の削減にも成功した。RAMが有り余っているため、もっと別のサービスも同居させても良いかもしれない。
- 今回は、ラズパイ5の実力を徹底検証。ハードウェア仕様の詳細比較から、実際の使用感、組み立て手順、オーバークロック時の性能と発熱、日本語環境での注意点まで、ラズパイ5を最大限に活用するための情報をお届けします。
- | 項目 | ラズベリーパイ4 | ラズベリーパイ5 | 改善点 |
- Raspberry Pi 5 プロセッサ | Broadcom BCM2711 1.5GHz / 1.8GHz クアッドコア Cortex-A72 | Broadcom BCM2712 2.4GHz クアッドコア Cortex-A76 | CPU性能約2〜3倍向上 |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md; take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: Processor | Broadcom BCM2711 1.5GHz / 1.8GHz quad-core Cortex-A72 | Broadcom BCM2712 2.4GHz quad-core Cortex-A76 | CPU performance improved by approximately 2 to 3 times |
- Raspberry Pi 5 メモリ | 2GB / 4GB / 8GB LPDDR4 | 4GB / 8GB LPDDR4X | メモリ帯域幅向上 |
- _EN_: Memory | 2GB / 4GB / 8GB LPDDR4 | 4GB / 8GB LPDDR4X | Improved memory bandwidth |
- Raspberry Pi 5 GPU | VideoCore VI | VideoCore VII | 3D性能約2倍向上 |
- _EN_: GPU | VideoCore VI | VideoCore VII | 3D performance approximately doubled |
- Raspberry Pi 5 CPU性能が2〜3倍向上しています。Mac Book Air(2018年)程度の性能に迫る部分まで上がってきているとのことです。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: CPU performance has improved by 2-3 times.It is said that the performance is approaching that of the Mac Book Air (2018).
- Raspberry Pi 5 RAMの帯域幅が向上したことも加え、3D処理能力が大幅に向上しています。将来的に小型のGPUが販売されれば外付けで利用でき、AI推論処理も実行可能になるでしょう。消費電力がボトルネックになりますが、低消費電力のインテルNCSスティックを使った検証も今後紹介する予定です。
- Raspberry Pi 5 従来は40ピンGPIOから電源を取っていましたが、ファン専用のコネクタが追加されています。これにより見た目がすっきりするだけでなく、CPUの温度に応じて自動的にファン速度を制御できるようになりました。コネクタに刺すだけで済むため設定も簡単で、動作音も小さいです。
- - Raspberry Pi 5 オーバークロックで2.4GHzから2.8GHzまで引き上げても85度の温度制限に達せず、冷却性能は十分です
- _EN_: - Even if you overclock from 2.4GHz to 2.8GHz, the temperature limit of 85 degrees is not reached and the cooling performance is sufficient.
- ## オーバークロックで性能向上（Raspberry Pi 5）
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- ### オーバークロックの基本（Raspberry Pi 5）
- Raspberry Pi 5 アクティブクーラーを装着していない場合はオーバークロックを推奨しませんが、適切な冷却環境があればCPUクロックを上げることができます。テスト環境では2.8GHzまで問題なく動作しました。
- _EN_: Although overclocking is not recommended unless you have an active cooler installed, you can increase your CPU clock if you have the right cooling environment.In the test environment, it worked up to 2.8GHz without any problems.
- 一般的にオーバークロックすると保証対象外となる点に注意してください。ただし、ラズパイにはサーマルスロットリング機能があります。これはCPUが高温になりすぎると自動的に処理速度を下げて熱を抑える保護機能で、85°C付近で発動してパフォーマンスが低下します。
- Raspberry Pi 5 再起動後、負荷がかかっている状態で以下のコマンドを実行すると、実際に2.8GHzで動作していることが確認できれば完了です。
- _EN_: After restarting, run the following command under load and if you can confirm that it is actually operating at 2.8GHz, you are done.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: frequency(0)=2800037120
- Raspberry Pi 5 | クロック | 処理時間 | ３分後の温度 |
- Raspberry Pi 5 | 2.4GHz時 | 10.8秒 | 70° |
- _EN_: | At 2.4GHz | 10.8 seconds | 70° |
- Raspberry Pi 5 | 2.8GHz時 | 11.7秒 | 81° |
- _EN_: | At 2.8GHz | 11.7 seconds | 81° |
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 理論値では16%程度の性能向上が期待できますが、実際は向上幅が10%未満でした。また、3分間の負荷テスト後の温度は約10°C上昇しましたが、サーマルスロットリングが発生する85°C以下に収まっています。適切な冷却があれば2.8GHzの設定でも安全に運用できると言えるでしょう。
- 実際の使用シナリオを想定した性能評価を行いました。結論から言うと、ラズパイ4からラズパイ5への進化は大きく、多くの処理が約2倍速くなっています。一方、オーバークロックによる性能向上は限定的で、通常使用では体感できる差がわずかという結果になりました。
- | ラズパイ４ | ラズパイ５ | ラズパイ５ (2.8GHz) | |
- _EN_: | Raspberry Pi 4 | Raspberry Pi 5 | Raspberry Pi 5 (2.8GHz) | |
- ラズパイ4からラズパイ5への性能向上は非常に顕著ですが、オーバークロックの効果は用途によって異なります。特に動画エンコードなど特定の処理では若干の高速化が見られましたが、日常使用では大きな差はありません。
- - Raspberry Pi 5 アクティブクーラー装着でオーバークロックが可能だが、体感できる性能向上は限定的だった
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5は、Raspberry Pi財団のシングルボードコンピュータです。CPUに2.4GHz quad-core 64-bit Arm Cortex-A76 CPUを搭載し、前モデルRaspberry Pi 4より2～3倍のパフォーマンスを実現、更にGPUに800MHz VideoCore VIIが採用されグラフィック性能も向上し、microHDMIで4Kp60のデュアル出力が可能になっています。メモリはLPDDR4X-4267 SDRAMで容量のラインナップがあります。
- また、Raspberry Pi 5から新たに搭載されたPCIe 2.0インターフェースにより、別売りのM.2 HATを使って外付けのM.2 NVMe SSDを接続することができるようになりました。また、別売りのPoE HATを使うことでPoE+にも対応可能です。その他新たにリアルタイムクロック(RTC)や、基板上の電源ボタンが追加されています。
- Raspberry Pi 5 ・SoC：BCM2712
- _EN_: ・SoC: BCM2712
- Raspberry Pi 5 ・RAM：8GB
- _EN_: ・RAM: 8GB
  
Source: akizukidenshi_com_catalog_g_g129326.md

- Raspberry Pi 5 ・無線機能詳細：Wi-Fi(802.11ac)2.4/5GHz・Bluetooth(v5.0・BLE)
- _EN_: ・Wireless function details: Wi-Fi (802.11ac)2.4/5GHz・Bluetooth(v5.0・BLE)
- _EN_: ・Long side: 85mm
- _EN_: ・Short side: 56mm
- Raspberry Pi 5の特筆すべき点は、CPUとGPUの速度が圧倒的に速いことだ。
- _EN_: What's remarkable about the Raspberry Pi 5 is that its CPU and GPU speeds are overwhelmingly fast.
  
Source: akizukidenshi_com_catalog_g_g129326.md; picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- Raspberry Pi 5 実際、前モデルと比較して、Raspberry Pi 5はCPU性能を2〜3倍に、GPU性能を大幅にアップグレードしている。しかし、それだけでなく、まったく新しい周辺機器の世界も提供する。
- _EN_: In fact, compared to its predecessor, the Raspberry Pi 5 has two to three times the CPU performance and significantly upgraded GPU performance.But it also offers a whole new world of peripherals.
- Raspberry Pi 5 | プロセッサ | ブロードコム BCM2711 | ブロードコム BCM2712 |
- _EN_: | Processor | Broadcom BCM2711 | Broadcom BCM2712 |
- Raspberry Pi 5 | CPU | ARM-Cortex A72（4コア） | ARM-Cortex A76（4コア） |
- _EN_: | CPU | ARM-Cortex A72 (4 cores) | ARM-Cortex A76 (4 cores) |
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- Raspberry Pi 5 | CPUの能力 | 64ビット | 64ビット |
- _EN_: | CPU power | 64 bit | 64 bit |
- Raspberry Pi 5 | CPU周波数 | 1.5/1.8GHz | 2.4GHz |
- _EN_: | CPU frequency | 1.5/1.8GHz | 2.4GHz |
- Raspberry Pi 5 | GPU | ビデオコアVI 600MHz | ビデオコアVII 1GHz |
- _EN_: | GPU | Video Core VI 600MHz | Video Core VII 1GHz |
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- Raspberry Pi 5 | シンクロナスDRAM | LPDR4-3200 SDRAM（1GB、2GB、4GB、8GB） | LPDR4X-4267 SDRAM (発売時には4GBと8GBのSKUが利用可能） |
- _EN_: | Synchronous DRAM | LPDR4-3200 SDRAM (1GB, 2GB, 4GB, 8GB) | LPDR4X-4267 SDRAM (4GB and 8GB SKUs available at launch) |
- Raspberry Pi 5 | WLAN | 2.4 GHzおよび5.0 GHz 802.11ac Wi-Fi | 2.4 GHzおよび5.0 GHz 802.11ac Wi-Fi |
- _EN_: | WLAN | 2.4 GHz and 5.0 GHz 802.11ac Wi-Fi | 2.4 GHz and 5.0 GHz 802.11ac Wi-Fi |
- 上記の類似点から始めると、明らかにどちらのコンピューターも64ビットのCPUを搭載している。もちろん、どちらもMicro SDカードから起動する（Raspberry Pi 1が標準のSDカードで動作したことを覚えているだろうか？）
- _EN_: Starting with the similarities above, it's clear that both computers have 64-bit CPUs.Of course, both boot from a Micro SD card (remember how the Raspberry Pi 1 worked with a standard SD card?)
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- Raspberry Pi 5 どちらも2.4GHzと5.0GHzの802.11ac Wi-Fi、Bluetooth 5.0とBluetooth Low Energy（BLE）を備えている。
- _EN_: Both feature 2.4GHz and 5.0GHz 802.11ac Wi-Fi, Bluetooth 5.0 and Bluetooth Low Energy (BLE).
- まず、Raspberry Pi 4がBroadcom BCM2711プロセッサを搭載しているのに対し、Raspberry Pi 5はBCM2712を採用していることにお気づきだろう。Raspberry Pi 5は、ARM-Cortex A76コア（2.4GHz）を搭載した、より高速なCPUを搭載している。
- Raspberry Pi 5には、次世代のVideoCore GPUも搭載されている。つまり、Raspberry Pi 4が600MHzのVideoCore VI GPUを搭載しているのに対し、Raspberry Pi 5は1GHzのVideoCore VII GPUを搭載している。
- Raspberry Pi 5 GPUの差は、次のことを考えると非常に大きい。 Pi 4は4.4GFLOPS、Raspberry Pi 5は10GFLOPS以上.
- _EN_: The difference between GPUs is huge considering the following:Pi 4 has 4.4GFLOPS, Raspberry Pi 5 has over 10GFLOPS.
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- Raspberry Pi 4はLPDDR4-3200 SDRAM（1GB、2GB、4GB、8GB）を採用し、Raspberry Pi 5はLPDDR4X-4267 SDRAMを採用している（発売時には4GBと8GBのバリエーションが用意されている）。2GBのバリエーションが後に続き、将来的には1GBのバリエーションが登場するかもしれない。
- Raspberry Pi 5の新機能は、正確な計時のためのRTC（リアルタイムクロック）とRTCバッテリーコネクターです。
- Raspberry Pi 5 Pi5をミニ・デジタル・オーディオ・ワークステーションに組み込んでほしい。そのPCIレーンは、低レイテンシーのオーディオインターフェイス（USBは素晴らしいが、それでもデザインによるクロックレイテンシーがある）と、いくつかのソフトウェアシンセには十分なパワー（最高品質とは言えないだろうが）に最適だろう。Piは、オーディオ・ポートを含む筐体に（十分にシールドされた状態で）入れることができるだろう！
- Raspberry Pi 5 pcie、CPUスピード
- _EN_: pcie, CPU speed
- Pi 4からCPU性能は2～3倍に、GPU性能も向上しました。また、Raspberry Pi独自開発のI/OコントローラーであるRP1を搭載し、カメラ/ディスプレイ/USBなどのインタフェース機能が向上し、新規にPCIe 2.0が利用できるようになりました。その他、電源ボタンが標準搭載となり、別売りのHATを接続することによって、M.2コネクタのストレージの搭載が可能となりました。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md; www_switch-science_com_products_9250.md

- - Raspberry Pi 5 Broadcom BCM2712、2.4 GHz quad-core 64 bit Arm Cortex-A76 CPU（512KB L2キャッシュ/2MB 共有L3キャッシュ） - VideoCore VII GPU、supporting OpenGL ES 3.1、Vulkan 1.2
- - Raspberry Pi 5 8 GB LPDDR4X-4267 SDRAM
- _EN_: - 8GB LPDDR4X-4267 SDRAM
- - Raspberry Pi 5 802.11ac Wi-Fi（2.4 GHz / 5.0 GHz）
- _EN_: - 802.11ac Wi-Fi (2.4 GHz / 5.0 GHz)
- - Raspberry Pi 5 別売りの外部電源によるリアルタイムクロック（RTC）
  
Source: www_switch-science_com_products_9250.md

- 英国Raspberry Pi財団は2023年9月28日（英国時間）、最新モデルとなる「Raspberry Pi 5」を発表した。前世代の「Raspberry Pi 4」と比べCPU性能は2～3倍となったほか、新たにPCI Express 2.0も利用可能になった。
- シングルボードコンピュータ「Raspberry Pi（ラズベリーパイ、ラズパイ）」を手掛ける英国Raspberry Pi財団は2023年9月28日（英国時間）、最新モデルとなる「Raspberry Pi 5」を発表した。前世代の「Raspberry Pi 4」と比べCPU性能は2～3倍となったほか、新たにPCI Express 2.0も利用可能になった。英国では2023年10月にメモリが4Gバイト品と8Gバイト品の2モデルを発売予定。価格はそれぞれ60米ドル、80米ドルだ。
- Raspberry Pi 5は、Broadcomの16nmプロセスSoC（System on Chip）「BCM2712」を採用した。BCM2712は2.4GHz動作のArm「Cortex-A76」を4コア搭載。前世代のRaspberry Pi 4と比べてCPU性能が2～3倍以上高速化したとしている。また、GPUも新たにBroadcomの「VideoCore VII」を採用していて、こちらも従来の2倍性能が向上したという。なお、メモリは低消費電力で動作するLPDDR4Xを採用し、データレートも 4267MT/sへと引き上げられている。
- メモリ容量は1／2／4／8Gバイト品を予定していて、2023年10月に4／8Gバイトモデルから英国で販売を開始する。なお、国内でRaspberry Piシリーズを取り扱うKSYやスイッチサイエンスでは、工事設計認証の取得／表示などの対応が完了次第、順次販売を開始する予定だ。
- Raspberry Pi 5 CPU Broadcom「BCM2712」（2.4GHz／4コア 64ビットArm「Cortex-A76」（512KバイトのL2キャッシュ／2Mバイトの共有L3キャッシュ）
- _EN_: CPU Broadcom "BCM2712" (2.4 GHz / 4 cores 64-bit Arm "Cortex-A76" (512 KB L2 cache / 2 MB shared L3 cache)
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md

- Raspberry Pi 5 GPU Broadcom「VideoCore VII」（OpenGL ES 3.1、Vulkan 1.2をサポート）
- _EN_: GPU Broadcom “VideoCore VII” (supports OpenGL ES 3.1, Vulkan 1.2)
- Raspberry Pi 5 802.11ac Wi-Fi（2.4GHz／5.0GHz）
- _EN_: 802.11ac Wi-Fi (2.4GHz/5.0GHz)
- Raspberry Pi 5 別売りの外部電源によるリアルタイムクロック
- Raspberry Pi 5 ラズベリー パイ 5は、4つのCPUコアと最大8GBのメモリを搭載し、IoTデバイスの開発からプログラミング教育まで幅広く活用できる高性能なシングルボードコンピュータです。前モデルと比較して最大3倍の処理性能を実現し、2.5GbEイーサネットやPCIe Gen 2.0スロットなど、最新の技術を採用しています。技適マークを取得済みで、日本国内での無線通信機能の利用も正式に認められています。
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md; open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- ラズベリー パイ 5は、Raspberry Pi Ltd.が開発した最新のシングルボードコンピュータです。2.4GHzのクアッドコアCPUを搭載し、Pi 4と比較して最大3倍の処理性能を実現しています。特に注目すべき点は、新しいGPUアーキテクチャの採用により、グラフィック処理能力が大幅に向上したことです。これにより、IoTデバイスの開発やマルチメディア処理など、より高度な用途にも対応できるようになりました。
- ### 技術仕様（CPU・メモリ・電源等）（Raspberry Pi 5）
- _In English_: Technical specifications (CPU, memory, power supply, etc.) (Raspberry Pi 5)
- ラズパイ 5の主要スペックは以下の通りです。CPUはBroadcom BCM2712を搭載し、4つのCPUコアが高速な演算処理を実現します。メモリは4GBまたは8GBの
- _EN_: The main specifications of Raspberry Pi 5 are as follows.The CPU is equipped with Broadcom BCM2712, and the four CPU cores realize high-speed calculation processing.Memory is 4GB or 8GB
- Raspberry Pi 5 LPDDR4Xを採用し、高速なデータアクセスが可能です。電源に関しては、5V/5A（最大25W）の電源アダプタが推奨されており、従来モデルよりも安定した電力供給が必要となっています。また、PCIe Gen 2.0スロットを搭載し、拡張性も大幅に向上しています。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: 3. Programming and development environment (Raspberry Pi 5)
- _In English_: Compatible programming language (Raspberry Pi 5)
- _In English_: Development tools and frameworks (Raspberry Pi 5)
- Raspberry Pi 5 IoTデバイスとして活用する場合、GPIO（General Purpose Input/Output）ピンを介してセンサーやアクチュエータを制御できます。Python用のGPIOライブラリやNode-REDなどのビジュアルプログラミングツールを使用することで、効率的なIoTプロトタイプの開発が可能です。また、MQTT、CoAP、WebSocketなどの通信プロトコルもサポートされており、様々なIoTアプリケーションの開発に対応できます。4. 活用事例と実践ガイド
- ラズパイ 5は、IoTプラットフォームとして高い評価を得ています。特に注目すべきは、強化されたCPU性能とネットワーク機能です。例えば、工場の生産ラインでは、センサーからのデータ収集と分析をリアルタイムで行い、異常検知システムとして機能させることが可能です。また、カメラモジュールと組み合わせることで、AIを活用した画像認識システムの構築も容易になりました。農業分野では、温度・湿度センサーと連携し、自動灌水システムの制御装置として活用されています。
- Raspberry Pi 5 ラズベリー パイ 5は、前世代のPi 4と比較して大幅な性能向上を実現しています。CPUコアの処理速度は約2倍に向上し、特にマルチスレッド処理での性能改善が顕著です。メモリ帯域幅も拡大され、データ処理速度が大幅に改善されました。GPIO処理速度も向上し、センサーからのデータ読み取りやアクチュエータの制御がより高速になっています。一方で、消費電力は増加しているため、放熱対策が重要になっています。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- Raspberry Pi 5は、前モデルと比較して消費電力が増加しています。そのため、電源周りのトラブルが発生しやすくなっています。特に、GPUを多用するアプリケーションや複数のUSB機器を接続する場合は、電力供給が不安定になることがあります。これに対しては、公式の電源アダプタの使用、適切な放熱対策、電力消費の最適化が重要です。また、UPSの導入により、突然の電源断からシステムを保護することも検討に値します。
- ラズパイ 5の性能を最大限に引き出すためには、いくつかの最適化が必要です。まず、CPUのオーバークロック設定が可能ですが、適切な放熱対策が不可欠です。また、swapファイルのサイズ調整やファイルシステムの最適化により、システム全体の応答性を向上させることができます。特に、IoTアプリケーションでは、センサーデータの取得間隔やログ記録の頻度を適切に設定することで、システムリソースの効率的な利用が可能になります。
- ### ラズベリーパイ5の主な用途を教えてください
- Raspberry Pi 5 ラズベリー パイ 5は、IoTデバイス開発、プログラミング学習、ホームオートメーション、メディアサーバー、組み込みシステムの開発など、幅広い用途に活用できます。高性能なCPUとGPUを搭載しているため、AIや機械学習の実験プラットフォームとしても注目されています。教育現場での活用も多く、実践的なプログラミング教育のツールとして高い評価を得ています。
- Raspberry Pi 5は、Raspberry Pi 4と比較してCPU性能の向上、小型化、PCI Expressの追加など、多くの改良が施されています。
- _EN_: Raspberry Pi 5 has many improvements compared to Raspberry Pi 4, including improved CPU performance, smaller size, and the addition of PCI Express.
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

## 2. I/O・拡張性 / I/O & Expandability

**Keywords (EN):** PCIe, NVMe, M.2 hat, GPIO, CSI DSI camera display, USB 3, HDMI, Gigabit Ethernet

- Raspberry Pi 5 I/Oコントローラーも刷新されており、新チップ「RP1」を搭載する。2つのUSB 3.0ポート、2つのUSB 2.0ポート、ギガビットイーサネットに対応。またカメラとディスプレイ向けに、2つの4レーンMIPIトランシーバー、アナログビデオ出力、3.3V汎用I/O（GPIO）を備える。
- USB 3.0の帯域幅は2倍に強化されており、またシングルレーンのPCIeによって、高帯域幅のPCIeデバイスをRaspberry Pi 5に接続できる。
- _EN_: USB 3.0 bandwidth is doubled, and single-lane PCIe allows you to connect high-bandwidth PCIe devices to Raspberry Pi 5.
- - Raspberry Pi 5 デュアル4Kp60 HDMIディスプレイ出力
- _EN_: - Dual 4Kp60 HDMI display output
- - Raspberry Pi 5 高速microSDカードインターフェース（SDR104モードに対応）
  
Source: japan_zdnet_com_article_35209685.md

- _EN_: - High-speed microSD card interface (Supports SDR104 mode)
- - Raspberry Pi 5 USB 3.0ポート×2（同時に5Gbps動作対応）
- _EN_: - USB 3.0 ports x 2 (supports 5Gbps operation at the same time)
- - Raspberry Pi 5 USB 2.0ポート×2
- _EN_: - 2 x USB 2.0 ports
- - Raspberry Pi 5 ギガビットイーサネット、PoE+対応（別途PoE+ HATが必要、近日提供予定）
  
Source: japan_zdnet_com_article_35209685.md

- _EN_: - Gigabit Ethernet, PoE+ compatible (separate PoE+ HAT required, coming soon)
- - Raspberry Pi 5 高速周辺機器用インターフェースPCIe 2.0 x1
- _EN_: - Interface PCIe 2.0 x1 for high-speed peripherals
- - Raspberry Pi標準40ピンGPIOヘッダー
- _EN_: - Raspberry Pi standard 40-pin GPIO header
- Raspberry Pi 5 グラフィックに関しては、Pi 4に引き続きデュアルHDMIで、両方とも60fpsかつ4K解像度がサポートされている。4Kモニターが2枚ないので試せないが、パワフルな文言だ。
  
Source: japan_zdnet_com_article_35209685.md; pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: As for graphics, it follows the Pi 4 with dual HDMI, and both support 60fps and 4K resolution.I can't test it because I don't have two 4K monitors, but it's a powerful statement.
- RP1チップは、USBコネクタの左側に配置されるI/Oコントローラで、PCで言うサウスブリッジの役割を担っている。Raspberry Pi Ltdは、このRP1の開発に「7年の期間と2,500万ドルの費用を費やした」と紹介されている。
- _EN_: The RP1 chip is an I/O controller placed on the left side of the USB connector, and plays the role of a south bridge on a PC.Raspberry Pi Ltd is introduced as having "spent seven years and $25 million dollars" in developing the RP1.
- Raspberry Pi 5 USB 3.0に関しては、Pi 4ではPCI Express 2.0x1をUSB 3.0ハブチップによって帯域を共有していたものが、Raspberry Pi 5では別々のUSB 3.0コントローラに接続される形となったため、2つのUSB 3.0ポートを同時に利用しても高速なデータ転送が可能となった。
- Raspberry Pi 5 PCI Expressポートに接続可能なHATボードとして、公式からNVMe SSDが搭載可能なHATボードの発売が予告されていたものの、まだ発売されておらず、代わりにサードパーティベンダーからいろいろな形状のNVMe SSD拡張用ボードが流通している状態だ。
- Raspberry Pi 5 NVMe SSDを搭載すれば、ブート可能なファイルシステムとして利用できる(ただし、デュアルSSDタイプのものはブートできない)。さらに、PCI Express 3.0x1で安定して動作すれば、シーケンシャル性能で700～800MB/sの速度を出すことができる。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- ほかにも、2.5GbEボードや、Wi-Fiボードや、PCI Expressスロットに変換するボードなど、さまざまなRaspberry Pi 5向けPCI Express拡張ボードが、サードパーティベンダーから続々と登場しており、新しいRaspberry Piの遊び方が開拓されようとしている。
- Raspberry PiはGPIOポートからシリアル接続が可能だったが、Raspberry Pi 5では独立したシリアルポートが、2つのMicro HDMIポートの間に用意された。
- _EN_: The Raspberry Pi had a serial connection via its GPIO port, but the Raspberry Pi 5 now has a separate serial port between the two Micro HDMI ports.
- Raspberry Pi 5 このシリアルポートを使用すると、OS起動前のファームウェア段階から情報が取得可能なため、起動がうまくいかない場合の原因切り分けなどに役立つ。また、USB PD電源を接続した場合にはPDOの一覧を出力することから、USB PD電源の確認にも便利そうだ。もちろん、起動後のOSの操作もこのポートでできる。
- Raspberry Pi 5 Raspberry Pi 5の電源コネクタは、Pi 4と同じくUSB Type-Cが採用された。最低要件は5V/3A、推奨要件は5V/5A(Power Delivery)となっている。推奨要件を満たしている場合は、USBポートで利用可能な電流が合計1.6Aになるが、そうでない場合は600mAに制限される。
- Raspberry Pi 5 先述のシリアル通信で起動時のメッセージを取得すると、起動時にUSB PD電源をチェックする様子が確認できる。Raspberry Pi 5向けに発売された公式の27W USB PD電源アダプタを使用すると、5V/5AのPDOが検出されて「usb_max_current_enable」の値は5,000となる。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 一方、5V/5AのPDOがない一般的なUSB PD電源を使用すると、「usb_max_current_enable」の値は3,000となり、USBポートの電力制限を示す「Selecting USB low current limit」のメッセージが出力されることが分かる。
- Raspberry Pi 5 `USB-PD: src-cap PDO object1 0x0a0191f4`
- _EN_: `USB-PD: src-cap PDO object1 0x0a0191f4`
- Raspberry Pi 5 USB-PD: src-cap PDO object2 0x0002d12c
- _EN_: USB-PD: src-cap PDO object2 0x0002d12c
- Raspberry Pi 5 USB-PD: src-cap PDO object3 0x0003c0e1
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: USB-PD: src-cap PDO object3 0x0003c0e1
- Raspberry Pi 5 USB-PD: src-cap PDO object4 0x0004b0b4
- _EN_: USB-PD: src-cap PDO object4 0x0004b0b4
- Raspberry Pi 5 usb_max_current_enable default 0 max-current 5000
- _EN_: usb_max_current_enable default 0 max-current 5000
- Raspberry Pi 5 `USB-PD: src-cap PDO object1 0x0801912c`
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: `USB-PD: src-cap PDO object1 0x0801912c`
- Raspberry Pi 5 USB-PD: src-cap PDO object3 0x0004b0c8
- _EN_: USB-PD: src-cap PDO object3 0x0004b0c8
- Raspberry Pi 5 USB-PD: src-cap PDO object4 0x00064096
- _EN_: USB-PD: src-cap PDO object4 0x00064096
- Raspberry Pi 5 USB-PD: src-cap PDO object5 0xc8dc213c
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: USB-PD: src-cap PDO object5 0xc8dc213c
- Raspberry Pi 5 USB-PD: src-cap PDO object6 0xc9402128
- _EN_: USB-PD: src-cap PDO object6 0xc9402128
- Raspberry Pi 5 usb_max_current_enable default 0 max-current 3000
- _EN_: usb_max_current_enable default 0 max-current 3000
- Raspberry Pi 5 Selecting USB low current limit
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: Selecting USB low current limit
- Raspberry Pi 5 しかし、5V/5AのPDOをもつUSB PD電源アダプタは、Raspberry Pi 5に合わせて発売された公式の27W USB PD電源アダプタか、サードパーティベンダーが発売するRaspberry Pi 5向け電源アダプタくらいしか存在しない。
- _EN_: However, the only USB PD power adapters with a 5V/5A PDO are the official 27W USB PD power adapter released with the Raspberry Pi 5, or the Raspberry Pi 5 power adapters released by third-party vendors.
- Raspberry Pi 5 電源はUSBポートの使用の有無だけではなく、SSDやHATボードの使用状況によっては必要になると思われるため、公式の電源アダプタの日本発売が待たれる。
- _EN_: It seems that the power supply is required not only depending on whether or not the USB port is used, but also depending on the usage status of the SSD and HAT board, so we are waiting for the release of an official power adapter in Japan.
- Raspberry Pi 5 なお、PoE+を使用した給電も可能のため、こちらから給電することで電源アダプタを使用しない方法もあるが、PoE用のピンの配置が変更となったため、これまでのHATが使用できない。また、公式のRaspberry Pi 5向けPoE+ HATボードも未発売のため、現時点で唯一存在するWaveShare製のPoE+ボードを使用して4.5A給電するのが限界となっている。こちらも公式HATボードの発売が待たれる。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 筆者的には、長年のクセでケーブルを抜き差ししてしまったり、USBケーブルやLANケーブルの抜き差しの時に本体を押さえるつもりが誤って押してしまったり、ケースによって意図せず押してしまったりすることが多く、まだ慣れてはいないものの、便利な機能であることに間違いはない。
- Raspberry Pi 5 機能的に影響しない話題だが、基板の裏面にもこだわりがみられる。USB/LANvGPIOの各ポートの実装方法が変わり、各部品の足が裏面から飛び出さなくなって、直接接地しないようになった。
- _EN_: Although this is a topic that does not affect functionality, there is also some attention to detail on the back side of the board.The mounting method for each USB/LANvGPIO port has changed, and the legs of each component no longer protrude from the back and are no longer directly grounded.
- Raspberry Pi 5 代わりに、基板左下のLANポート付近と、左上のHATボードの固定穴付近に四角い金属の台がつけられており、microSDカードスロットと3点で接地するようになっている。このため、ケースなしでテーブルなどに置いて使用した場合に、各部品がショートしてしまったり、飛び出た突起によって接地面を傷つける可能性が低減されている。
- Raspberry Pi 5 また、基板のフチも、以前はGPIOポート側と電源コネクタ側のフチにはささくれがあったのが、Raspberry Pi 5ではきれいに処理されるようになり、手指に刺さってしまう危険性がなくなったのは非常に嬉しい。
- _EN_: Also, there used to be hangnails on the edges of the board, on the GPIO port side and the power connector side, but on the Raspberry Pi 5, they are now neatly removed, and I am very happy that there is no longer any risk of getting your fingers stuck.
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- ### microSDカードの読み書き性能も倍に（Raspberry Pi 5）
- _In English_: Double the read/write performance of microSD card (Raspberry Pi 5)
- Raspberry Pi 5 Raspberry Pi 5では、microSDのUHS-I SDR104モードがサポートされた。104の数値は104MB/sのバススピードをサポートするという意味になる。
- _EN_: Raspberry Pi 5 now supports UHS-I SDR104 mode for microSD.The number 104 means it supports a bus speed of 104MB/s.
- Raspberry Pi 5 実際にUHS-I対応のmicroSDカードでストレージのベンチマークテストをしてみると、シーケンシャルリードでは81.8MB/s、シーケンシャルライトでも40MB/s近い性能が確認できた。
- _EN_: When we actually performed a storage benchmark test with a UHS-I compatible microSD card, we confirmed performance of 81.8MB/s for sequential read and nearly 40MB/s for sequential write.
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 性能向上や発熱量の増加となると、次に気になるのは消費電力になるだろう。ワットモニターを使用して、公式電源アダプタを使用したときの、アイドル時の消費電力と、高負荷時の消費電力を比較してみた。また、ストレージがSDカードの場合、NVMe SSDの場合と、Pi 4の場合も合わせて取得した。
- | Raspberry Pi 5 / NVMe | 3.0W | 6.4W | 5.5W |
- _EN_: | Raspberry Pi 5 / NVMe | 3.0W | 6.4W | 5.5W |
- Raspberry Pi 5 ストレージの違いによる比較については、意外にもSDカードよりもNVMe SSDを使用した時のほうがアイドル時に低消費電力だった。一方、ストレージに書き込み負荷を与えると、SDカードはアイドル時から大きくは変わらなかったが、NVMe SSDは5.5Wに上昇したため、ストレージ使用時の電力はやはりSSDの方が大きかった。
- Raspberry Pi 5 なお、この設定はPi 4でも有効だが、Pi 4の場合はEEPROMの設定時に「WAKE_ON_GPIO=0」も必要となる。Raspberry Pi 5は電源ボタンがあるため、WAKE_ON_GPIOの設定はいらない。
- _EN_: Note that this setting is also valid for Pi 4, but in the case of Pi 4, "WAKE_ON_GPIO=0" is also required when setting the EEPROM.Raspberry Pi 5 has a power button, so there is no need to set WAKE_ON_GPIO.
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- GPIOを使ったLチカ入門や、センサーや電子工作の学習をメインにやりたいなら、2021年に登場した「Raspberry Pi Pico」シリーズを検討しても良いだろう。無線LANなしのPicoなら700円前後、無線LANありのPico Wなら1,100円前後で入手できる。プログラミング言語も、MicroPythonやCircuitPythonを選択すれば、普通のRaspberry Piと大差なく学習できるためハードルも低い。
- Raspberry Pi 5 ディスプレイ出力 | 2x micro HDMI （最大4Kp60×1 または 4Kp30×2） | 2x micro HDMI （最大4Kp60×2） | 2画面 4K/60Hz対応 |
- _EN_: Display output | 2x micro HDMI (max. 4Kp60×1 or 4Kp30×2) | 2x micro HDMI (max. 4Kp60×2) | 2 screens 4K/60Hz compatible |
- Raspberry Pi 5 USB | 2x USB 3.0 2x USB 2.0 | 2x USB 3.0 2x USB 2.0 | 変更なし |
- _EN_: USB | 2x USB 3.0 2x USB 2.0 | 2x USB 3.0 2x USB 2.0 | No change |
- Raspberry Pi 5 PCIe | なし | PCIe 2.0 x1スロット | 新規追加 |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md; take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: PCIe | None | PCIe 2.0 x1 slot | New addition |
- Raspberry Pi 5 ネットワーク | Gigabit Ethernet Wi-Fi 5 (802.11ac)Bluetooth 5.0 | Gigabit Ethernet Wi-Fi 6 Bluetooth 5.0 | Wi-Fi 6対応 (拡張モジュール必要) |
- Raspberry Pi 5 GPIO | 40ピン | 40ピン (新たに4ピンのI2Cを追加) | I2C追加 |
- _EN_: GPIO | 40 pins | 40 pins (new 4-pin I2C added) | I2C added |
- Raspberry Pi 5 電源コネクタ | USB-C | USB-C | 変更なし |
- _EN_: Power connector | USB-C | USB-C | No change |
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 カメラコネクタ | 1x MIPI CSI | 2x MIPI CSI | カメラポート追加 |
- _EN_: Camera Connector | 1x MIPI CSI | 2x MIPI CSI | Add Camera Port |
- Raspberry Pi 5 ディスプレイコネクタ | 1x DSI | 1x DSI | 変更なし |
- _EN_: Display Connector | 1x DSI | 1x DSI | No Change |
- #### PCIeスロット（Raspberry Pi 5）
- _In English_: PCIe slot (Raspberry Pi 5)
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- ラズパイ5のPCIeスロットにM.2 SSD変換アダプタを接続することで、microSDカードの約10倍の読み書き速度を実現できるそうです。これは今後検証する予定です。
- _EN_: By connecting an M.2 SSD conversion adapter to the PCIe slot of Raspberry Pi 5, it is possible to achieve read and write speeds approximately 10 times faster than a microSD card.We plan to verify this in the future.
- Raspberry Pi 5 電源ボタンが追加され、2回押すと電源がオフになります。さらに、電源オフの状態からもう一度押すと起動します。従来はUSBケーブルを抜く必要があったため、これは大変便利な改良点です。
- _EN_: Added power button, press twice to power off.Furthermore, if you press it again from the power off state, it will start up.This is a very convenient improvement since previously you had to unplug the USB cable.
- - 通信系はハイエンド志向というのがこれまでのラズパイのトレンドでしたが、Wi-Fi 6は拡張モジュール対応となっており、USB 3.0からの進化がないのも残念です。
- _EN_: - The trend of Raspberry Pi so far has been to focus on high-end communication systems, but Wi-Fi 6 supports expansion modules, and it is a shame that it has not evolved from USB 3.0.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: - Ethernet LAN connectors are no longer needed and modern connectivity methods such as Thunderbolt support are desired instead.
- - Raspberry Pi 5 microSD Sandisk Ultra 64GB
- _EN_: - microSD Sandisk Ultra 64GB
- Raspberry Pi 5 まずはmicroSDカードにOSを書き込むところから始めます。
- _EN_: First, start by writing the OS to the microSD card.
- 書き込みが終了したら、microSDをラズパイに挿入し電源を入れるだけです。しばらくするとデスクトップ画面が表示され、ラズパイライフの始まりです。以下の画面が表示されれば正常に起動しています。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: Once the writing is complete, simply insert the microSD into the Raspberry Pi and turn on the power.After a while, the desktop screen will appear and your Raspberry Pi life will begin.If the following screen is displayed, it has started normally.
- Raspberry Pi 4と比べてUSBポートは帯域幅が2倍となり、SDカードのアクセススピードも2倍向上(high-speed SDR104 mode対応)しています。Raspberry Piシリーズお馴染みの40ピンのGPIOも搭載し、さらに
- Raspberry Pi 5 2つの4-lane1Gbps MIPIインターフェースは、CSI/DSIでお好きなカメラとディスプレイの組み合わせを使うことができます。
- _EN_: Two 4-lane 1Gbps MIPI interfaces allow you to use your favorite camera and display combinations with CSI/DSI.
- 電源はUSB-Cコネクタの5V5A推奨となっており、Raspberry Pi 公式ACアダプター(27W USB PD Type-C) 黒(販売コード：130328)とRaspberry Pi 公式ACアダプター(27W USB PD Type-C) 白(販売コード：130329)がお使いいただけます。Raspberry Pi 4と同じく5V3Aの電源でも起動可能ですが、各USBポートからの供給電流が合計600mAに制限されます。
- Raspberry Pi 5 ・GPIO：26
  
Source: akizukidenshi_com_catalog_g_g129326.md; take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: ・GPIO: 26
- Raspberry Pi 5 | HDMI端子 | 2つのマイクロHDMIポート（最大4Kp60） | 2つのマイクロHDMIポート（最大4Kp60 同時に) |
- _EN_: | HDMI terminal | 2 micro HDMI ports (up to 4Kp60) | 2 micro HDMI ports (up to 4Kp60 simultaneously) |
- Raspberry Pi 5 | USBポート | USB 2.0ポート×2、USB 3.0ポート×2 | USB 2.0ポート×2、USB 3.0ポート×2 同時5Gbps動作をサポートする |
- _EN_: | USB Ports | USB 2.0 ports x 2, USB 3.0 ports x 2 | USB 2.0 ports x 2, USB 3.0 ports x 2 Supports simultaneous 5Gbps operation |
- Raspberry Pi 5 | イーサネット | ギガビット・イーサネット、PoE+対応（PoE+ HATが必要） | ギガビット・イーサネット、PoE+対応 (新しいPoE+ HATが必要) |
  
Source: akizukidenshi_com_catalog_g_g129326.md; picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: | Ethernet | Gigabit Ethernet with PoE+ (requires PoE+ HAT) | Gigabit Ethernet with PoE+ (requires new PoE+ HAT) |
- Raspberry Pi 5 | カメラポート | 2レーンMIPI DSI、2ラインMIPI CSI | 2 × 4レーンMIPIカメラ/ディスプレイ・トランシーバ |
- _EN_: | Camera Port | 2-Lane MIPI DSI, 2-Line MIPI CSI | 2 x 4-Lane MIPI Camera/Display Transceiver |
- Raspberry Pi 5 | パワー | 5V/3A DC（USB-CコネクターまたはGPIO経由） | 5V/5A DC電源（PD有効） |
- _EN_: | Power | 5V/3A DC (via USB-C connector or GPIO) | 5V/5A DC power (PD enabled) |
- Raspberry Pi 5 | パワーサプライ | USB-C | USB-C |
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: | Power Supply | USB-C | USB-C |
- Raspberry Pi 5 | PCIe | いや | 高速周辺機器用PCIe 2.0 x1インターフェース |
- _EN_: | PCIe | No | PCIe 2.0 x1 interface for high-speed peripherals |
- Raspberry Pi 5 どちらもUSB 2.0ポートが2つ、USB 3.0ポートが2つある。
- _EN_: Both have two USB 2.0 ports and two USB 3.0 ports.
- Raspberry Pi 5 そして最後に、どちらのコンピューターもギガビット・イーサネットを提供し、PoE+ HATでパワー・オーバー・イーサネット（PoE）をサポートする。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: Finally, both computers offer Gigabit Ethernet and support Power over Ethernet (PoE) with PoE+ HATs.
- また、どちらも2つのUSB 2.0ポートと2つのUSB 3.0ポートを備えているが、Raspberry Pi 5は同時5Gbps動作に対応するUSB 3.0ポートを備えている。
- _EN_: Also, while both have two USB 2.0 ports and two USB 3.0 ports, the Raspberry Pi 5 has a USB 3.0 port that supports simultaneous 5Gbps operation.
- そのため、マイクロSDカードスロットとUSBポートは一見同じように見えるが、Raspberry Pi 5でははるかに優れている。Raspberry Pi 4と比べて、Raspberry Pi 5はUSB帯域幅が2倍になり、SDカードのピーク性能も2倍になった。
- カメラ・シリアル・インターフェース（CSI）とディスプレイ・シリアル・インターフェース（DSI）は、Raspberry Pi 5でも新しいセットアップが可能です。2つの4レーンMIPIインターフェースにより、最大2台のカメラまたはディスプレイの組み合わせをサポートします。これは、立体視アプリケーションに使用できることを意味します！
- Raspberry Pi 5 オーディオを接続したい場合は、USBかブルートゥースを使う必要がある。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: If you want to connect audio, you'll need to use USB or Bluetooth.
- ## PCIe（Raspberry Pi 5）
- _In English_: PCIe (Raspberry Pi 5)
- Raspberry Pi 5は、PCIe 2.0 x1インターフェイスを搭載した初のRaspberry Piで、超高速の周辺機器を接続できる。
- _EN_: The Raspberry Pi 5 is the first Raspberry Pi to feature a PCIe 2.0 x1 interface, allowing you to connect ultra-fast peripherals.
- Raspberry Pi 4にはPCIeインターフェースがなかったが、Compute Module 4はI/Oボードを通じてPCIeを提供していた。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: The Raspberry Pi 4 did not have a PCIe interface, but the Compute Module 4 provided PCIe through an I/O board.
- Raspberry Pi 5以前は、SPIインターフェースの最大速度にしかアクセスできなかったため、帯域幅が制限されていました。PCIeでは、USBケーブルに頼ることなく、本当に高速なハードウェアをPiに内蔵できるようになりました。
- _EN_: Prior to Raspberry Pi 5, you could only access the maximum speed of the SPI interface, which limited your bandwidth.With PCIe, you can now put really fast hardware on your Pi without having to rely on a USB cable.
- Raspberry Pi 5 そのため、Piと他のデバイス間のデータ転送でより多くのことができるようになりました（4Gモデム、追加のイーサネットポート、NVMe SSDなど、あらゆる可能性を考えてみてください！）。
- _EN_: So now you can do more with data transfer between your Pi and other devices (think of all the possibilities: a 4G modem, additional Ethernet ports, NVMe SSDs, and more!).
- Raspberry Pi 5 どちらも電源にはUSB-Cコネクターを使用する。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: Both use a USB-C connector for power.
- Raspberry Pi 5 素晴らしいスペックだが、新モデルにUSB2ポートがまだいくつか残っているのは本当に驚きだ。
- _EN_: Great specs, but it's really surprising that the new model still has some USB2 ports.
- Raspberry Pi 5 そうだね！USB2ポートについて驚いたことは？
- _EN_: I agree!What surprised you about the USB2 port?
- Raspberry Pi 5 ロックダウンが始まった直後、私はCM4、CM4 I/Oボード、POEハット、POEハットを収納できるファン付きメタルケースを注文した。CM4以外はすべて到着した。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: Right after the lockdown started, I ordered a CM4, a CM4 I/O board, a POE hat, and a metal case with a fan to house the POE hat.All except CM4 have arrived.
- Raspberry Pi 5 各種コネクタなどのフォームファクタはPi 4から変更されているので、多くの既存ケースやPi 4用のPoE HATなどはご利用いただけません。ご注意ください。
- _EN_: The form factors such as various connectors have changed from the Pi 4, so many existing cases and PoE HATs for the Pi 4 cannot be used.please note.
- Raspberry Pi 5 電源はPi 4で使用していた5.1 V/ 3.0 Aでも動作します。その場合四つのUSBポートからの電流は合計600 mAに制限されます。USB PD規格に準拠したネゴシエーションが可能な5 V/ 5 Aの電源を認識した場合、1.6 Aまで自動的に上昇します。
- 2024年8月、ラズパイ5に最適なACアダプター 5.1V/5.0A USB-PD Type-Cコネクタ出力の取り扱いを開始しました。
- _EN_: In August 2024, we started handling the AC adapter 5.1V/5.0A USB-PD Type-C connector output, which is ideal for Raspberry Pi 5.
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md; www_switch-science_com_products_9250.md

- - Raspberry Pi 5 2 x 4Kp60 HDMIディスプレイ出力（HDR対応）（mirco HDMIコネクタ）
- _EN_: - 2 x 4Kp60 HDMI display outputs (HDR compatible) (mirco HDMI connector)
- - Raspberry Pi 5 2 × USB 3.0ポート（同時に5 Gbpsの通信が可能）
- _EN_: - 2 x USB 3.0 ports (5 Gbps communication possible at the same time)
- - Raspberry Pi 5 2 × USB 2.0ポート
- _EN_: - 2 x USB 2.0 ports
  
Source: www_switch-science_com_products_9250.md

- - Raspberry Pi 5 ギガビットイーサネット（別売りのRaspberry Pi 5用PoE+ HATを接続することでPoE+も利用可能)
- _EN_: - Gigabit Ethernet (PoE+ is also available by connecting PoE+ HAT for Raspberry Pi 5, sold separately)
- - Raspberry Pi 5 高速周辺機器用PCIe 2.0 x1インタフェース
- _EN_: - PCIe 2.0 x1 interface for high-speed peripherals
- さらに、IOコントローラーに独自開発の「RP1」を採用したことで、カメラ／ディスプレイ／USBなどのインタフェース機能が向上。新たにPCI Express 2.0が利用可能になった。また、Raspberry Piシリーズで初めて、ボード上に電源ボタンを設置したほか、別売りのHATを接続することでM.2ストレージの増設にも対応した。
- Raspberry Pi 5 デュアル4K/60p HDMIディスプレイ出力（HDR対応）
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md; www_switch-science_com_products_9250.md

- _EN_: Dual 4K/60p HDMI display output (HDR compatible)
- Raspberry Pi 5 2×USB 3.0ポート（同時に5Gbpsの通信が可能）
- _EN_: 2 x USB 3.0 ports (5Gbps communication possible at the same time)
- Raspberry Pi 5 2×USB 2.0ポート
- _EN_: 2 x USB 2.0 ports
- Raspberry Pi 5 ギガビットイーサネット（別売りのPoE+HATを接続することでPoE+も利用可能）
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md

- _EN_: Gigabit Ethernet (PoE+ can also be used by connecting PoE+HAT, sold separately)
- Raspberry Pi 5 高速ペリフェラル用PCIe 2.0 x1インタフェース
- _EN_: PCIe 2.0 x1 interface for high-speed peripherals
- Raspberry Pi標準の40ピンGPIOヘッダ
- _EN_: Raspberry Pi standard 40-pin GPIO header
- Raspberry Pi 5 基本的なセットアップには、以下の周辺機器が必要です。まず、電源アダプタは必ず5V/5A対応のものを使用してください。また、32GB以上のmicroSDカードが推奨され、特にOSの動作速度を重視する場合は、高速なUHS-I規格のカードを選択することをお勧めします。HDMIケーブル、USBキーボード・マウス、有線LANケーブル（またはWi-Fi環境）も必要となります。カメラモジュールやディスプレイを接続する場合は、専用のカメラケーブルやディスプレイケーブルも必要です。
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md; open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- セットアップは以下の手順で行います。まず、Raspberry Pi ImagerをPCにインストールし、OSイメージをmicroSDカードに書き込みます。その際、Wi-FiやSSH設定などの初期設定も同時に行えます。次に、周辺機器を接続し電源を投入します。初回起動時には、必要なアップデートやローカライズ設定を行い、開発環境の構築へと進みます。
- Raspberry Pi 5 ラズベリー パイ 5の運用において、いくつかの一般的な課題が報告されています。特に注意が必要なのは、電源供給の安定性です。推奨される5V/5A電源アダプタを使用していても、USB機器の同時接続時に電力不足が発生する場合があります。この場合、powered USBハブの使用や、接続機器の見直しが効果的です。また、microSDカードの信頼性も重要で、信頼できるメーカーの製品を使用し、定期的なバックアップを行うことが推奨されます。
- Raspberry Pi 5 ラズベリー パイ 5の性能を最大限に活用するためには、適切な周辺機器の選択が重要です。特に注目すべきは、高速なNVMe SSDを接続できるPCIeスロットです。これにより、microSDカードよりも大幅に高速なストレージアクセスが可能になります。また、4K/60Hzディスプレイ出力に対応したHDMIケーブルや、高速なネットワーク接続のための2.5GbEイーサネットアダプタなども、用途に応じて検討する価値があります。カメラモジュールについては、新しいインターフェースに対応した専用モデルが登場しており、より高速な画像処理が可能になっています。
- Raspberry Pi 5では、様々な拡張ボードを活用することで、機能を大幅に拡張できます。GPIOピンを利用した拡張ボードは、センサー制御やモーター制御など、IoTプロジェクトに不可欠です。また、HAT（Hardware Attached on Top）規格に準拠した拡張ボードも多数利用可能で、工業用制御、オーディオ処理、ディスプレイ制御などの専門的な用途に対応できます。特に、新しいPCIeインターフェースを活用した高速な拡張カードにより、これまでにない可能性が広がっています。
- ラズパイ 5には5V/5A（最大25W）の電源アダプタが必要です。これは前モデルより大きな電力を必要とするため、必ず推奨仕様を満たす電源アダプタを使用してください。特に、USB機器を複数接続する場合や高負荷時には安定した電力供給が重要です。公式の電源アダプタの使用を強く推奨します。
- Raspberry Pi 5はUSB-Cを使用した電源供給に対応し、安定した動作には最低15Wの電源が推奨されます。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _EN_: Raspberry Pi 5 supports powering using USB-C, and a minimum 15W power supply is recommended for stable operation.
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

## 3. 性能・発熱・電力 / Performance, Thermals & Power

**Keywords (EN):** benchmarks, thermals, throttling, power consumption, cooling

- Raspberry Pi 5 SDカードのアクセス速度は2倍になり、ボード上に電源ボタンが設けられた。
- _EN_: SD card access speeds have been doubled and a power button has been added to the board.
- Raspberry Pi 5 価格は4GBモデルが60ドル（約9000円）、8GBモデルが80ドル（約1万2000円）。なおポートの配置が変更されているため、新たなケースが必要となる。
- _EN_: The price is $60 (about 9,000 yen) for the 4GB model and $80 (about 12,000 yen) for the 8GB model.Note that a new case is required because the port placement has changed.
- Raspberry Pi 5 英国では28日から予約受付が始まっている。最初のボードは10月末までに出荷が始まる見通しだ。
- _EN_: In the UK, pre-orders will begin on the 28th.The first boards are expected to begin shipping by the end of October.
  
Source: japan_zdnet_com_article_35209685.md

- ## Raspberry Pi 5の仕様
- _In English_: Raspberry Pi 5 specifications
- - Raspberry Pi 5 4Kp60 HEVCデコーダー
- _EN_: - 4Kp60 HEVC decoder
- - Raspberry Pi 5 デュアルバンド802.11ac WiFi
- _EN_: - Dual band 802.11ac WiFi
  
Source: japan_zdnet_com_article_35209685.md

- - Raspberry Pi 5 Bluetooth 5.0/Bluetooth Low Energy (BLE)
- _EN_: - Bluetooth 5.0/Bluetooth Low Energy (BLE)
- - Raspberry Pi 5 2×4レーンMIPIカメラ／ディスプレイ用トランシーバー
- _EN_: - 2x4 lane MIPI camera/display transceiver
- _EN_: - real time clock
- - Raspberry Pi 5 電源ボタン
  
Source: japan_zdnet_com_article_35209685.md

- _EN_: - Power button
- Raspberry Pi 5 この記事は海外Red Ventures発の記事を朝日インタラクティブが日本向けに編集したものです。
- _EN_: This article was originally published by Red Ventures overseas and edited for Japan by Asahi Interactive.
- # 改めて見る、「Raspberry Pi 5」の実力と使いどころ
- _In English_: A look at the power and uses of “Raspberry Pi 5”
- Raspberry Pi 5 2024年4月17日 06:21
  
Source: japan_zdnet_com_article_35209685.md; pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: April 17, 2024 06:21
- 2023年9月に発表された「Raspberry Pi 5」が、日本でも2月から発売となった。すでに手にしている方も多数いると思われるが、「まだ迷っている」、「これから」という方に、Raspberry Pi 5の特徴や性能、どう活用したら良いかについて解説したい。
- ## ハードウェアは確かな進化（Raspberry Pi 5）
- _In English_: Hardware has definitely evolved (Raspberry Pi 5)
- 「Raspberry Pi 4」から約4年ぶりに登場したRaspberry Pi 5は、クレジットカードサイズという基本的なフォームファクタを維持しながら、着実に成長を遂げている。まずは主要なコンポーネントを見ていこう。
- _EN_: The Raspberry Pi 5, which was introduced about four years after the Raspberry Pi 4, has steadily grown while maintaining its basic form factor of credit card size.Let's start by looking at the main components.
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- 私の足元にある自作PCがSkylake世代で、いまだに不満を感じずに現役なため、そろそろRaspberry Piに追いつかれようとしている。
- _EN_: The home-built PC at my feet is of the Skylake generation, and I'm still using it without any complaints, so I think it's about to be overtaken by the Raspberry Pi.
- ## Raspberry Pi 5の目玉? 「RP1」チップとは
- _In English_: The highlight of Raspberry Pi 5? What is the “RP1” chip?
- MIPIは、以前はカメラとディスプレイが1ポートずつ搭載されていたものが、共用の2ポート構成となった。これによって、デュアルカメラ、デュアルディスプレイといった、これまでのRaspberry Pi(※Compute Moduleを除く)ではできなかった組み合わせが可能となった。
- なお、接続に必要なケーブルの形状がRaspberry Pi Zeroと同等のピッチ/ピン数となり、ディスプレイ向けとカメラ向けでアサインが異なるため、それぞれ別売りの専用ケーブルが必要となる点に注意しよう。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: Please note that the shape of the cable required for connection has the same pitch/pin count as Raspberry Pi Zero, and the assignments are different for display and camera, so special cables are required for each separately sold.
- ### 初搭載のPCI Expressポート。すでにさまざまなボードも登場（Raspberry Pi 5）
- _In English_: First installed PCI Express port.Various boards have already appeared (Raspberry Pi 5)
- Raspberry Pi 5 ユーザーが使用可能なPCI Express 2.0 x1ポートが16ピンのFPCポートとして搭載された。公式な動作保証はないが、PCI Express 3.0 x1としても設定可能だ。
- _EN_: A user-available PCI Express 2.0 x1 port is now available as a 16-pin FPC port.Although there is no official guarantee of operation, it can also be configured as PCI Express 3.0 x1.
- ### 意外と便利な専用シリアルポートが登場（Raspberry Pi 5）
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _In English_: Introducing a surprisingly convenient dedicated serial port (Raspberry Pi 5)
- シリアル接続には「Raspberry Pi Debug Probe」が別途必要となる。これは元々Raspberry Pi Picoのデバッグ用として登場した製品だったが、Raspberry Pi 5のシリアル接続としても活用できるようになった。
- _EN_: A separate ``Raspberry Pi Debug Probe'' is required for serial connection.This was originally a product for debugging the Raspberry Pi Pico, but it can now also be used as a serial connection for the Raspberry Pi 5.
- ### 発熱が心配な人も安心。専用ファンコネクタ（Raspberry Pi 5）
- _In English_: It is safe for people who are worried about fever.Dedicated fan connector (Raspberry Pi 5)
- Raspberry Pi 5 新モデルになると、いつも発熱量の増加が話題となるが、先に言えば発熱はPi 4よりも少し増えている。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: When it comes to new models, the increase in heat output is always a hot topic, and first of all, the heat output is slightly higher than the Pi 4.
- Raspberry Pi 5 Raspberry Pi 5の冷却の必要性について、Pi 4に引き続き「通常の使用範囲内ではオプション」としており、Raspberry Pi 5とPi 4で同じ負荷をかけた場合、Pi 4より動作温度は低くなると説明している。
- _EN_: Concerning the need for cooling the Raspberry Pi 5, the company continues to state that it is "optional within normal usage" as it did for the Pi 4, and explains that when the same load is applied to the Raspberry Pi 5 and Pi 4, the operating temperature will be lower than that of the Pi 4.
- Raspberry Pi 5 一方で、継続的に負荷をかけるような用途に備えて、本体上にファン専用のコネクタが用意され、公式から冷却オプションが2つ提供されるようになった。
- _EN_: On the other hand, in preparation for applications that require continuous load, a dedicated connector for the fan has been prepared on the main body, and two cooling options are now officially provided.
- Raspberry Pi 5 1つは公式のケースで、ケース内にファンが装着されており、これをRaspberry Pi 5に接続して使用できる。必要に応じて付属のヒートシンクを貼り付けて使用できる。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: One is the official case, which has a fan installed inside the case and can be used by connecting it to the Raspberry Pi 5.The included heat sink can be attached and used if necessary.
- Raspberry Pi 5 もう1つは、ヒートシンクとファンが一体になった「アクティブクーラー」で、Raspberry Pi 5に空いている取り付け用の穴に、2つのピンで固定して使用できる。
- _EN_: The other is an ``active cooler'' that combines a heat sink and fan, and can be used by fixing it in the mounting hole on the Raspberry Pi 5 with two pins.
- ### RTCも初搭載。別売りバッテリで時刻の保存が可能（Raspberry Pi 5）
- _In English_: Also equipped with RTC for the first time.Time can be saved with an optional battery (Raspberry Pi 5)
- _EN_: Until now, Raspberry Pi did not have an RTC (real-time clock) to store time.Therefore, to keep the time accurate, it was necessary to synchronize the time using NTP at startup or install a separate RTC module.
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 Raspberry Pi 5では、PMIC内にRTC機能が搭載されたため、電源コネクタ横のバッテリコネクタに別売りの電池を接続すれば、時刻のバックアップが可能になった。ネットワークがない環境で動かす場合に役に立つだろう。
- _EN_: Raspberry Pi 5 has an RTC function built into the PMIC, making it possible to back up the time by connecting an optional battery to the battery connector next to the power connector.This will be useful when running in an environment where there is no network.
- ### 電源コネクタと電源要件について（Raspberry Pi 5）
- _In English_: About power connectors and power requirements (Raspberry Pi 5)
- Raspberry Pi 5 Current 5000 mA ★5A出力
- _EN_: Current 5000 mA ★5A output
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 Voltage 5000 mV
- _EN_: Voltage 5000mV
- Raspberry Pi 5 Current 3000 mA
- _EN_: Current 3000mA
- Raspberry Pi 5 Voltage 9000 mV
- _EN_: Voltage 9000mV
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 Current 2250 mA
- _EN_: Current 2250 mA
- Raspberry Pi 5 Voltage 12000 mV
- _EN_: Voltage 12000mV
- Raspberry Pi 5 Current 1800 mA
- _EN_: Current 1800mA
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 Voltage 15000 mV
- _EN_: Voltage 15000mV
- Raspberry Pi 5 (中略)
- Raspberry Pi 5 Current 3000 mA ★3A出力
- _EN_: Current 3000 mA ★3A output
- Raspberry Pi 5 Current 2000 mA
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: Current 2000mA
- _EN_: Voltage 15000 mV
- Raspberry Pi 5 Current 1500 mA
- _EN_: Current 1500 mA
- Raspberry Pi 5 Voltage 20000 mV
- _EN_: Voltage 20000mV
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 では、公式の電源アダプタを買えばよいかと言うと、残念ながら日本では未発売で、日本で安全に利用するために必要な「PSEマーク」もない。サードパーティ製の電源については、Amazonでいくつか確認ができ、PSEマークがあるものも存在するようだが、所持はしていないため使い勝手については不明だ。
- ### これも待望の新機能? 電源ボタン（Raspberry Pi 5）
- _In English_: Is this another long-awaited new feature? Power button (Raspberry Pi 5)
- 今までのRaspberry Piには搭載されてこなかった電源ボタンも、ついに搭載された。
- _EN_: A power button, which has not been included in previous Raspberry Pis, is finally included.
- Raspberry Pi 5 電源接続時に自動的に起動する点はこれまでと変わらないが、電源ボタンを2回押せばシャットダウンし、長押しで強制断、電源ランプが赤の状態で1回押せば起動する。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: It still starts up automatically when connected to the power source, but you can shut it down by pressing the power button twice, force it off by holding it down, and start it up by pressing it once when the power light is red.
- ### なくなってしまったポートも（Raspberry Pi 5）
- _In English_: Missing ports (Raspberry Pi 5)
- Raspberry Pi 1B+から搭載され続けてきた4極3.5mmジャックが廃止された。ステレオ音声とアナログビデオを出力できるものであったが、需要がないと判断されてしまったのかもしれない。
- _EN_: The 4-pole 3.5mm jack that has been installed since Raspberry Pi 1B+ has been discontinued.It was capable of outputting stereo audio and analog video, but it may have been determined that there was no demand for it.
- Raspberry Pi 5 ただし、アナログビデオだけは、スルーホールとして残されており、RP1を通じて映像出力されるようになっている。おそらくアナログビデオを積極的に使いたい人は少数と思われるが、実際に動かしている例がYouTubeにあったので紹介したい。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: However, only the analog video remains as a through hole, and the video is output through RP1.There are probably only a few people who actively want to use analog video, but I found an example of it in action on YouTube, so I would like to introduce it to you.
- ### 基板の裏面やフチにもこだわり（Raspberry Pi 5）
- _In English_: Paying close attention to the back side and edges of the board (Raspberry Pi 5)
- ## ベンチマークで確かめるRaspberry Pi 5の性能
- _In English_: Raspberry Pi 5 performance checked with benchmarks
- Raspberry Pi 5 実際にいくつかベンチマークを取得して、Raspberry Pi 5の性能を見てみよう。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: Let's actually get some benchmarks and see how the Raspberry Pi 5 performs.
- ### JetStream 1.1（Raspberry Pi 5）
- _In English_: JetStream 1.1 (Raspberry Pi 5)
- Raspberry Pi 5 まずはEbenも言及していたJetStream 1.1ベンチマークを見てみよう。これはJavaScriptの処理性能を計測できるベンチマークスイートで、スコアが大きいほど性能が良い結果となる。
- _EN_: First, let's take a look at the JetStream 1.1 benchmark that Eben also mentioned.This is a benchmark suite that can measure JavaScript processing performance, and the higher the score, the better the performance.
- Raspberry Piは本来子どもの教育用パソコンとして開発されたものであるため、子どもたちが現代のJavaScriptをふんだんに使用したWebサイトをブラウジングするにあたり、処理が早ければ早いほど、学習用のデスクトップ用途として快適に使えるはずだ。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 3、4、5の3世代と、いくつかのマシンで取得した結果を図に示す。Raspberry Pi 5はPi 3の8.3倍、Pi 4の2.4倍のスコアとなった。
- _EN_: The figure shows the results obtained with three generations of Raspberry Pi 3, 4, and 5, and several machines.The Raspberry Pi 5 scored 8.3 times more than the Pi 3 and 2.4 times more than the Pi 4.
- Raspberry Pi 5 参考までに取得したPCでRaspberry Pi 5に最も近かったのは、2018年モデルの「MacBook Air」。まさにJavaScriptをふんだんに使用したサイトの処理の遅さに不満が出て、M2 MacBook Airへ買い替えたのを機に甥に譲渡したものだったが、電話でお願いして実行してもらった。試しに、ストレスを感じながら見ていたサイトをRaspberry Pi 5で開いてみると、体感的にRaspberry Pi 5の方がサクサク動いている気がした(思い出補正がかかっている可能性は否定しない)。
- Raspberry Pi 5 グラフでArmのMacが飛び出ているのはさておき、Raspberry Pi 5がほかの2015～2018年頃のPC各種にかなり近づいており、Pi 4よりも快適にWebブラウジング端末として利用できそうなことが分かった。
- _EN_: Aside from the fact that Arm's Mac stands out in the graph, the Raspberry Pi 5 is quite close to other PCs from around 2015 to 2018, and it seems like it can be used more comfortably as a web browsing terminal than the Pi 4.
- ### OpenSSL スピードテスト（Raspberry Pi 5）
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _In English_: OpenSSL Speed ​​Test (Raspberry Pi 5)
- Raspberry Pi 5 (Raspberry Pi 5)
- Raspberry Pi 5 (Pi 4)
- ### グラフィックスのテスト（Raspberry Pi 5）
- _In English_: Graphics testing (Raspberry Pi 5)
- Raspberry Pi 5 デスクトップ上でのグラフィックス性能をWebGL Aquariumを使用して確認してみた。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: I checked the graphics performance on the desktop using WebGL Aquarium.
- Raspberry Piをデルのモニター「U3219Q」に接続して、Raspberry Pi OSのデスクトップ環境を4K解像度で表示し、ChromiumブラウザでWebGL Aquariumを開いて、500匹の魚が泳ぐデフォルトの状態で映像を確認した。
- Raspberry Pi 5 ブラウザの画面を最大化した状態で表示した場合、Raspberry Pi 5では24fpsで描画されるのに対して、Pi 4では11fpsと半分程度の速度となった。なお、Raspberry Pi 5は何もしなくても60Hz出力されるのに対して、Pi 4では60Hz出力するための設定が必要だが、60Hz出力にしてもfpsに変化はなかった。
- Raspberry Pi 5 | Category | Test | Result |
- _EN_: | Category | Test | Result |
- Raspberry Pi 5 |---|---|---|
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 | HDParm | Disk Read | 81.88 MB/sec |
- _EN_: | HDParm | Disk Read | 81.88 MB/sec |
- Raspberry Pi 5 | HDParm | Cached Disk Read | 70.74 MB/sec |
- _EN_: | HDParm | Cached Disk Read | 70.74 MB/sec |
- Raspberry Pi 5 | DD | Disk Write | 39.8 MB/s |
- _EN_: | DD | Disk Write | 39.8 MB/s |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 | FIO | 4k random read | 3377 IOPS (13509 KB/s) |
- _EN_: | FIO | 4k random read | 3377 IOPS (13509 KB/s) |
- Raspberry Pi 5 | FIO | 4k random write | 1660 IOPS (6642 KB/s) |
- _EN_: | FIO | 4k random write | 1660 IOPS (6642 KB/s) |
- Raspberry Pi 5 | IOZone | 4k read | 16819 KB/s |
- _EN_: | IOZone | 4k read | 16819 KB/s |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 | IOZone | 4k write | 6444 KB/s |
- _EN_: | IOZone | 4k write | 6444 KB/s |
- Raspberry Pi 5 | IOZone | 4k random read | 11618 KB/s |
- _EN_: | IOZone | 4k random read | 11618 KB/s |
- Raspberry Pi 5 | IOZone | 4k random write | 6435 KB/s |
- _EN_: | IOZone | 4k random write | 6435 KB/s |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 同じSDカードをPi 4に移して同様に計測すると、シーケンシャルリードが41MB/s、シーケンシャルリードが26.5MB/sとなった。よって、Raspberry Pi 5ではPi 4の1.5～2倍ほど読み書き性能が向上したことが分かる。ランダム性能に関しても1.3～1.5倍ほどの向上がみられた。
- Raspberry Pi 5 | HDParm | Disk Read | 41.05 MB/sec |
- _EN_: | HDParm | Disk Read | 41.05 MB/sec |
- Raspberry Pi 5 | HDParm | Cached Disk Read | 41.95 MB/sec |
- _EN_: | HDParm | Cached Disk Read | 41.95 MB/sec |
- Raspberry Pi 5 | DD | Disk Write | 26.5 MB/s |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: | DD | Disk Write | 26.5 MB/s |
- Raspberry Pi 5 | FIO | 4k random read | 2758 IOPS (11035 KB/s) |
- _EN_: | FIO | 4k random read | 2758 IOPS (11035 KB/s) |
- Raspberry Pi 5 | FIO | 4k random write | 1461 IOPS (5847 KB/s) |
- _EN_: | FIO | 4k random write | 1461 IOPS (5847 KB/s) |
- Raspberry Pi 5 | IOZone | 4k read | 10772 KB/s |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: | IOZone | 4k read | 10772 KB/s |
- Raspberry Pi 5 | IOZone | 4k write | 5042 KB/s |
- _EN_: | IOZone | 4k write | 5042 KB/s |
- Raspberry Pi 5 | IOZone | 4k random read | 8208 KB/s |
- _EN_: | IOZone | 4k random read | 8208 KB/s |
- Raspberry Pi 5 | IOZone | 4k random write | 5036 KB/s |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: | IOZone | 4k random write | 5036 KB/s |
- ## 消費電力を測ってみた（Raspberry Pi 5）
- _In English_: I measured power consumption (Raspberry Pi 5)
- Raspberry Pi 5 |---|---|---|---|
- | Raspberry Pi 5 / SD | 3.6W | 7.2W | 4.2W |
- _EN_: | Raspberry Pi 5 / SD | 3.6W | 7.2W | 4.2W |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- | Raspberry Pi 4 / SD | 2.2W | 5.4W | 3.3W |
- _EN_: | Raspberry Pi 4 / SD | 2.2W | 5.4W | 3.3W |
- ## Raspberry Pi 5の待機電力は必要に応じて削減可能（Raspberry Pi 5）
- _In English_: Raspberry Pi 5 standby power can be reduced as needed (Raspberry Pi 5)
- Raspberry Pi 5 Raspberry Pi 5の電源をシャットダウンコマンドや電源ボタンで落とすと、待機の消費電力は1.7W前後となる。待機にしては電力を消費しているように思えるが、これは、シャットダウン後に3.3V電源がオフかつ5V電源がオンのままであった場合に、一部のHATボードで不具合が生じる問題への対応として、PMICによる3.3V出力を停止せずオンのままにしているためである(ここおよびここ)。
- Raspberry Pi 5 電源オフ後も3.3Vと5Vが両方出力される挙動は、Pi 3以前を再現したものだが、HATを使用しないか、問題の影響を受けないHATであることが確実な場合は、EEPROMの設定を変更することで、シャットダウン時にPMICによる3.3V出力をオフにして(5Vは出力されたまま)、待機電力を0～0.3Wまで減らすことができる。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 ただし、いろいろなHATボードを載せて遊ぶような動的な運用をする場合には、誤動作時の原因切り分けに支障が出ることが予想されるので無理に変更しないほうが良いだろう。
- _EN_: However, if you are performing dynamic operations such as playing around with various HAT boards, it is best not to force changes as it may be difficult to isolate the cause of a malfunction.
- Raspberry Pi 5 実際に変更して、変更前後の電圧と消費電力の変化について確認してみた。
- _EN_: I actually made the change and checked the changes in voltage and power consumption before and after the change.
- Raspberry Pi 5 `bash`
- Raspberry Pi 5 $ sudo rpi-eeprom-config -e
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 [all]
- Raspberry Pi 5 BOOT_UART=1
- _EN_: BOOT_UART=1
- Raspberry Pi 5 POWER_OFF_ON_HALT=1 # 0から1に変更
- _EN_: POWER_OFF_ON_HALT=1 # changed from 0 to 1
- Raspberry Pi 5 BOOT_ORDER=0xf146
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 POWER_OFF_ON_HALT設定を0から1に変更して、電源をシャットダウンすると、待機電力が減っていることが確認できる。また、テスターで3.3Vと5Vの電圧を確認すると、5Vは出力されているが、3.3Vは出力されなくなっていることが確認できた。
- ## Raspberry Pi 5は高くなった?価格について
- _In English_: Is Raspberry Pi 5 expensive? About the price
- Raspberry Pi 5 これだけ高性能化して、新機能もあれこれ追加されると「でもお高いんでしょ?」と思われるかもしれないが、標準価格設定上はPi 4と比較しても5ドルずつしか値上げされていないため、これだけ聞くと、かなりお買いに感じる。
- _EN_: With such high performance and the addition of so many new features, you might think, "But isn't it expensive?" However, the standard price is only $5 more than the Pi 4, so hearing this alone makes it seem like a great deal.
- Raspberry Pi 5 |---|---|---|---|---|
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- | Raspberry Pi 4 | 35ドル | 45ドル | 55ドル | 75ドル |
- _EN_: | Raspberry Pi 4 | $35 | $45 | $55 | $75 |
- | Raspberry Pi 5 | (未発売) | (未発売) | 60ドル | 80ドル |
- _EN_: | Raspberry Pi 5 | (Not yet released) | (Not yet released) | $60 | $80 |
- Raspberry Pi 5 円安が進行する話題しか流れてこない今日この頃、個人的にはむしろ今後も値上がりするのではと心配になっているので、迷っている人には常に「買いたい時が買い時」とアドバイスしているが、「買う理由がないと買いにくい」など、やはり財布の紐はかたくなってしまっているようだ。
- | Raspberry Pi 5(スイッチサイエンス) | 1万1,770円 | 1万5,290円 |
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: | Raspberry Pi 5 (Switch Science) | 11,770 yen | 15,290 yen |
- | Raspberry Pi 5(KSY) | 1万1,000円 | 1万4,850円 |
- _EN_: | Raspberry Pi 5(KSY) | 11,000 yen | 14,850 yen |
- ### Raspberry Piはモデルの使い分けが大事な時代に?
- _In English_: Is Raspberry Pi in an era where it is important to use different models?
- 理由は何であれ、Raspberry Pi 5が高価格になってしまったのは事実だ。しかし、過去のモデルが販売を終了したわけではないので、性能を必要としなければ、Raspberry Pi 5よりも安価にRaspberry Pi各モデルが引き続き購入できる。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- _EN_: Whatever the reason, the fact is that the Raspberry Pi 5 has become expensive.However, sales of past models have not ended, so if you don't need the performance, you can still purchase each Raspberry Pi model at a lower price than the Raspberry Pi 5.
- Pi 4は1/2/4/8GBのすべてのモデルが販売されているし、「Raspberry Pi 3 Model A+」なら4千円台後半で、「Raspberry Pi Zero 2W」なら3千円前後で購入できる。また、キーボード一体型の「Raspberry Pi 400」もある。
- このように、Raspberry Piの製品ラインナップが幅広く充実してきたため、松竹梅からとりあえず松コースを選ぶような買い方ではなく、やりたい、学びたい物事に応じて、適切なモデルを選択するのが大事になってきているのではないかと考える。
- _EN_: As the Raspberry Pi product lineup has expanded and expanded in this way, I think it is becoming more important to choose the appropriate model depending on what you want to do or learn, rather than just choosing the pine course from the pine, chikku, and bai.
- ## Raspberry Pi 5はどう使う?
- _In English_: How to use Raspberry Pi 5?
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- Raspberry Pi 5 さて、この高性能過ぎるほど進化したシングルボードコンピュータをどう使おうか。
- _EN_: Now, how should we use this highly advanced single board computer?
- Raspberry Pi 5 ベンチマークなどでも述べた通り、デスクトップ環境としてかなり普通のPCに近づいてきた印象がある。サブのLinuxデスクトップ環境として使っても良さそうだし、子どもがいるご家庭なら子ども用のPCとして使うのも(本来の趣旨にも沿っていて)良さそうだ。
- Raspberry Pi 5 Raspberry Pi 5でできる新しいことを挙げるとすれば、カメラを2台接続して、ステレオカメラなどの工作や、PCI Expressポートを活用したら新たなコンピューティングが考えられる。カメラ機能とRaspberry Pi 5の処理性能を活かして画像認識などのマシンラーニング環境の勉強に使用するにも適していると考えられる。
- Raspberry Pi 5でないとできないものではないが、先日ドイツで開かれたEmbedded World 2024ではSonyのIMX500センサーを搭載した「Raspberry Pi AI cameraが」発表され、Zero2Wに取り付けてデモ展示された。このようなAI技術と組み合わせた活用については可能性があると思われる。
- 持論として、最新モデルは作業用として1台持つこととしている。これは、古い世代のRaspberry Piをセットアップする時に、一時的に最新世代を使用することで、作業の時短ができるためだ。Pi 4でもまだまだ作業用として問題はないが、当然ながらRaspberry Pi 5のほうがもっともっと早く作業できるので、複数のRaspberry Piを持っている人にはぜひおすすめしたい使い方の1つだ。
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md

- ## さいごに（Raspberry Pi 5）
- _In English_: Finally (Raspberry Pi 5)
- Raspberry Pi 5の概要とベンチマークの紹介、そして使い所について解説した。決して買いやすくない価格にはなってしまったが、それでも買って満足できるだけのパフォーマンスを発揮してくれるはずなので、ぜひ購入の理由を見つけて予算を確保し、購入して遊んでほしい。
- なお、Raspberry Pi 5も含めたRaspnberry Piの作例などを展示出展する活動をJapanese Raspberry Pi Users Groupとして行なっている。おもにオープンソースカンファレンスなどで全国各地を回っているので、実際に見て確かめたい方はぜひ遊びに来てほしい。
- ## ラズパイ５の性能比較
- _In English_: Performance comparison of Raspberry Pi 5
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md; take1bit_com_computer-ja_raspi5tutorial.md

- ラズパイ5は単なるマイコンボードの域を超え、簡易ノートPC相当の処理能力を備えるようになりました。価格も上昇していますが、その分、Mac Book Air(2018年)に迫る性能と拡張性を獲得しています。
- _EN_: Raspberry Pi 5 has gone beyond being a mere microcomputer board and now has the processing power equivalent to a simple notebook PC.Although the price has increased, it has gained performance and expandability that approaches that of the Mac Book Air (2018).
- _EN_: This time, we will thoroughly examine the capabilities of Raspberry Pi 5.We will provide you with information on how to make the most of your Raspberry Pi 5, from a detailed comparison of hardware specifications, actual usage, assembly procedures, performance and heat generation during overclocking, and precautions in a Japanese environment.
- ### ラズベリーパイ4と5のハードウェア・性能比較
- _In English_: Hardware/performance comparison of Raspberry Pi 4 and 5
- _EN_: This is a comparison table of Raspberry Pi 4 and 5.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: | Item | Raspberry Pi 4 | Raspberry Pi 5 | Improvements |
- Raspberry Pi 5 |---|---|---|---|
- Raspberry Pi 5 ビデオデコード | H.265 (4Kp60) H.264 (1080p60) | H.265 (4Kp60) H.264 (1080p60) AV1 (4Kp60) | AV1デコード対応 |
- _EN_: Video decoding | H.265 (4Kp60) H.264 (1080p60) | H.265 (4Kp60) H.264 (1080p60) AV1 (4Kp60) | AV1 decoding compatible |
- Raspberry Pi 5 ビデオエンコード | H.264 (1080p30) | H.264 (1080p60) | エンコード性能向上 |
- _EN_: Video encoding | H.264 (1080p30) | H.264 (1080p60) | Encoding performance improvement |
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 サイズ | 85mm × 56mm | 85mm × 56mm | 変更なし |
- _EN_: Size | 85mm × 56mm | 85mm × 56mm | No change |
- Raspberry Pi 5 電力消費 | 3.0W (アイドル時) 6.4W (負荷時) | 4.0W (アイドル時) 8.0W (負荷時) | 消費電力増加 |
- _EN_: Power consumption | 3.0W (idle) 6.4W (load) | 4.0W (idle) 8.0W (load) | Increased power consumption |
- Raspberry Pi 5 発熱 | 高い | より高い | 放熱対策強化推奨 |
- _EN_: Heat generation | High | Higher | Strengthening of heat radiation measures recommended |
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- オペレーティングシステム | Raspberry Pi OS (32/64ビット) | Raspberry Pi OS (64ビット) | 64ビット推奨 |
- _EN_: Operating System | Raspberry Pi OS (32/64 bit) | Raspberry Pi OS (64 bit) | 64 bit recommended |
- Raspberry Pi 5 発売時期 | 2019年6月 | 2023年10月 | – |
- _EN_: Release date | June 2019 | October 2023 | – |
- Raspberry Pi 5 | 対応電源アダプター | 5.1V 3A (15W) | 5.1v 5A (25W) | 供給電力アップ |
- _EN_: | Compatible power adapter | 5.1V 3A (15W) | 5.1v 5A (25W) | Increased power supply |
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- #### 処理性能（Raspberry Pi 5）
- _In English_: Processing performance (Raspberry Pi 5)
- Raspberry Pi 5 https://pc.watch.impress.co.jp/docs/column/hothot/1584619.html
- #### グラフィック性能（Raspberry Pi 5）
- _In English_: Graphics performance (Raspberry Pi 5)
- #### ファン用コネクタ（Raspberry Pi 5）
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _In English_: Fan connector (Raspberry Pi 5)
- #### 電源ボタン（Raspberry Pi 5）
- _In English_: Power button (Raspberry Pi 5)
- ### 物足りない部分（Raspberry Pi 5）
- _In English_: Unsatisfactory part (Raspberry Pi 5)
- - Raspberry Pi 5 イーサネットLANコネクタはもはや不要で、代わりにサンダーボルト対応などの現代的な接続方式が欲しいところです。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- ### 注意点（Raspberry Pi 5）
- _In English_: Points to note (Raspberry Pi 5)
- Raspberry Pi 5 25W電源が必要なため、従来のスマホ充電器（2A）では処理負荷がかかると動作が不安定になります。今回の電力要件アップにより、ノートPC用の電源アダプタが必要になっていますので注意が必要です。
- _EN_: Since it requires a 25W power supply, conventional smartphone chargers (2A) will become unstable when processing load is applied.Please note that due to this increase in power requirements, a power adapter for notebook PCs is required.
- - Raspberry Pi 5 電源アダプタ
- _EN_: - Power adapter
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- - 5.1Aに対応しており、ラズパイ5の性能を最大限に引き出せます。
- _EN_: - Compatible with 5.1A, allowing you to maximize the performance of Raspberry Pi 5.
- - Raspberry Pi 5 今まで念のためと思い、より高価なExtremeモデルを使っていましたが、Ultraでも性能差はほとんどありませんでした。このベンチマーク結果ではほぼ変わらずでした。
- - Raspberry Pi 5 アクティブクーラー
- _EN_: - Active cooler
- - Raspberry Pi 5 ケース
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- - Raspberry Pi 5 何かに干渉するということもなく、プラスチックなので軽量な点はグッド。
- _EN_: - It doesn't interfere with anything, and since it's made of plastic, it's lightweight.
- - Raspberry Pi 5 ケースをした状態でピン端子をアクセスできる点はとても良いと思います。
- _EN_: - I think it's great that you can access the pin terminals with the case on.
- - Raspberry Pi 5 電源ボタンも外から押せるように配慮されてます。
- _EN_: - The power button can also be pressed from the outside.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- ## 組み立て（Raspberry Pi 5）
- _In English_: Assembly (Raspberry Pi 5)
- Raspberry Pi 5 組み立てについて不明点がある場合は、別途作成した動画を参考にしてください。
- _EN_: If you have any questions about assembly, please refer to the separately created video.
- Raspberry Pi 5 IPSとしてケースがとても硬いので外すときは、以下のすきまに指の先の肉を挟む感じで引っ張ると外すことができます。
- _EN_: As an IPS case, the case is very hard, so to remove it, just pinch the flesh of your finger in the gap below and pull.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _In English_: Installing Raspberry Pi OS
- Raspberry Pi 5 専用ツール「Pi Imager」を使用すると簡単にインストールできます。以前はOSをダウンロードしてから手動でフラッシュライタを使って書き込む必要がありましたが、現在はボタン操作だけで完了します。
- _EN_: Installation is easy using the dedicated tool "Pi Imager".Previously, it was necessary to download the OS and then manually write it using a flash writer, but now it can be completed with just a button press.
- Raspberry Pi 5 現在の最新OSはBookwormですが、VNC接続で日本語のコピー&ペーストに問題があります。この問題が重要な場合は、一つ前のバージョンであるBullseyeを使用することも検討してください。詳細はこちらの記事に書いてます。
- _EN_: The current latest OS is Bookworm, but I'm having trouble copying and pasting Japanese with a VNC connection.If this issue is important to you, consider using the previous version, Bullseye.The details are written in this article.
- Raspberry Pi 5 /06/13/how-to-use-raspberry-pi-imager-1-7-2
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: /06/13/how-to-use-raspberry-pi-imager-1-7-2
- ## PI Imagerの設定（Raspberry Pi 5）
- _In English_: PI Imager settings (Raspberry Pi 5)
- Raspberry Pi 5 Wi-Fiの国設定（JP）は選択しなくても動作しますが、電波法規制に適合するために設定しておくことをお勧めします。
- _EN_: The Wi-Fi country setting (JP) will work even if you do not select it, but we recommend setting it to comply with radio regulations.
- Raspberry Pi 5 設定画面には国を選択する箇所が2か所ありますが、マウスのスクロールでは進みづらいため、カーソルキーを押し続けると素早く選択できます。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: There are two places on the settings screen to select a country, but it is difficult to navigate by scrolling with the mouse, so you can select quickly by holding down the cursor key.
- Raspberry Pi 5 この設定は保存して再利用できるため、OSを再インストールする際に便利です。
- _EN_: This setting can be saved and reused, which is useful when reinstalling the OS.
- Raspberry Pi 5 「サービス」タブでSSHを有効にしておくと後のリモート接続が容易になります。
- _EN_: Enabling SSH on the Services tab will make remote connections easier later.
- Raspberry Pi 5 以下が選択時の例になります。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: The following is an example of selection.
- ### 起動と初期設定（Raspberry Pi 5）
- _In English_: Startup and initial settings (Raspberry Pi 5)
- #### 初回起動（Raspberry Pi 5）
- _In English_: First time boot (Raspberry Pi 5)
- ### スクリーン設定（Raspberry Pi 5）
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _In English_: Screen settings (Raspberry Pi 5)
- Raspberry Pi 5 後でVNC接続を使用する場合は、解像度の設定が重要です。適切に設定しないと画面が小さく表示されてしまいます。システム設定から解像度を変更できます。
- _EN_: Setting the resolution is important if you plan to use the VNC connection later.If not set properly, the screen will appear small.You can change the resolution from system settings.
- Raspberry Pi 5 一般的なディスプレイであれば、1280×720の設定が最適です。この解像度なら拡大表示しても全体が見やすくなります。
- _EN_: For general displays, a setting of 1280 x 720 is optimal.This resolution makes it easier to see the entire image even when zoomed in.
- ### MACアドレスとIPアドレスの確認（Raspberry Pi 5）
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _In English_: Checking the MAC address and IP address (Raspberry Pi 5)
- Raspberry Pi 5 VNCやSSH接続するには、初回だけはディスプレイとキーボードを接続して起動する必要があります。
- _EN_: To connect to VNC or SSH, you need to connect a display and keyboard and start up the first time.
- Raspberry Pi 5 起動後、ターミナルで以下のコマンドを実行し、Wi-FiのIPアドレスとMACアドレスを確認します。
- _EN_: After booting, run the following command in Terminal to check the Wi-Fi IP address and MAC address.
- Raspberry Pi 5 ip a
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 「wlan0」がWi-Fiインターフェースを示します（eth0はLANケーブル接続用なので注意）。表示される情報から、MACアドレスとIPアドレスをメモしておきましょう。
- _EN_: "wlan0" indicates the Wi-Fi interface (note that eth0 is for LAN cable connection).Make a note of the MAC address and IP address from the displayed information.
- ### DHCP固定割り当ての活用（Raspberry Pi 5）
- _In English_: Leveraging DHCP fixed allocation (Raspberry Pi 5)
- Raspberry Pi 5 実用的なTIPSとして、ルーターの設定でMACアドレスに固定IPを割り当てることをお勧めします。これにより、OS再インストールやSDカード交換後もIPアドレスが変わらないため接続が容易になります。ルーターによって設定や言葉は変わりますが、以下は設定例です。
- _EN_: Although it is possible to set a fixed IP on the Raspberry Pi side, fixed DHCP assignment on the router side is convenient for the following reasons:
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- - Raspberry Pi 5 ルーターは一つだがデバイスは複数あり、IPの割り当て状況が把握しづらい
- _EN_: - There is one router but multiple devices, making it difficult to understand the IP allocation status
- - Raspberry Pi 5 ルーターのIP自動払い出しでは重複が起こる可能性がある
- _EN_: - Duplication may occur in router's automatic IP allocation
- - Raspberry Pi 5 ルーター側で設定すれば確実にIPが固定される
- _EN_: - If you set it on the router side, the IP will definitely be fixed.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- MACアドレスとIPアドレスをラベルに記載してラズパイに貼っておくと、後々の接続設定が非常に楽になります。
- _EN_: Writing the MAC address and IP address on a label and pasting it on the Raspberry Pi will make connection settings later on much easier.
- ## リモートアクセス（Raspberry Pi 5）
- _In English_: Remote access (Raspberry Pi 5)
- ### SSH接続の設定（Raspberry Pi 5）
- _In English_: Setting up an SSH connection (Raspberry Pi 5)
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 初期インストール時にSSHを有効化していれば、すぐに使用可能です。有効化していなかった場合は、ターミナルで`sudo raspi-config`
- _EN_: If you enabled SSH during initial installation, you can use it immediately.If you haven't enabled it, run `sudo raspi-config` in the terminal
- Raspberry Pi 5 コマンドを実行して設定メニューを開き、有効にしましょう。
- _EN_: Run the command to open the settings menu and enable it.
- Raspberry Pi 5 Windows環境からのSSH接続には「Tera Term」がおすすめです。以下のリンクからダウンロードできます。
- _EN_: "Tera Term" is recommended for SSH connection from a Windows environment.You can download it from the link below.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 https://forest.watch.impress.co.jp/library/software/utf8teraterm
- Tera Termを起動すると接続設定画面が表示されます。デフォルトでSSHが選択されているので、先ほどメモしたIPアドレスを入力し、ラズパイのログイン情報（ユーザー名とパスワード）を入力するだけで接続完了です。
- _EN_: When you start Tera Term, the connection settings screen will be displayed.SSH is selected by default, so simply enter the IP address you noted down earlier and the Raspberry Pi login information (username and password) to complete the connection.
- ### VNC接続の設定（Raspberry Pi 5）
- _In English_: Setting up a VNC connection (Raspberry Pi 5)
- Raspberry Pi 5 グラフィカルなリモートデスクトップとしてVNC接続も設定しておくと便利です。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: It is also useful to set up a VNC connection as a graphical remote desktop.
- Raspberry Pi 5 Windows側では「VNC Viewer」をインストールします：
- _EN_: On the Windows side, install "VNC Viewer":
- Raspberry Pi 5 https://www.realvnc.com/en/connect/download/viewer
- _EN_: On the Raspberry Pi side, the software is installed from the beginning, but it needs to be activated.Run the following command in terminal:
- Raspberry Pi 5 sudo raspi-config
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: sudo raspi-config
- Raspberry Pi 5 表示されるメニューから「Interface Options」→「VNC」を選択し、「Enable」に設定します。この設定画面はキーボード操作のみ対応なので注意してください。
- _EN_: From the menu that appears, select "Interface Options" → "VNC" and set it to "Enable".Please note that this setting screen only supports keyboard operations.
- 設定完了後、Windows側からVNC Viewerを起動し、ラズパイのIPアドレスを入力して接続します。ラズパイのユーザー名とパスワードでログインするとデスクトップが表示されます。
- _EN_: After completing the settings, start VNC Viewer from the Windows side and enter the Raspberry Pi's IP address to connect.When you log in with your Raspberry Pi username and password, the desktop will be displayed.
- **注意点**: 最新のRaspberry Pi OS (Bookworm)ではVNC接続時に日本語テキストのコピー&ペーストに問題があります。日本語テキストを扱う場合は、Tera TermのSSH接続を使うか、一つ前のOSバージョン(Bullseye)を使用することをお勧めします。詳細は以下の記事を参照してください。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _In English_: Improve performance with overclocking (Raspberry Pi 5)
- _In English_: Overclocking basics (Raspberry Pi 5)
- ### 設定方法（Raspberry Pi 5）
- _In English_: How to set up (Raspberry Pi 5)
- Raspberry Pi 5 設定ファイルを編集します。
- _EN_: Edit the configuration file.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 sudo nano /boot/firmware/config.txt
- _EN_: Sudo Nano/Boot/Formware/Config.txt
- Raspberry Pi 5 ファイルの末尾に以下の2行を追加します。
- _EN_: Add the following two lines at the end of the file.
- Raspberry Pi 5 ```
- Raspberry Pi 5 over_voltage=6
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: over_voltage=6
- Raspberry Pi 5 arm_freq=2800
- _EN_: arm_freq=2800
- Raspberry Pi 5 保存して終了後、`sudo reboot`
- _EN_: After saving and exiting, `sudo reboot`
- Raspberry Pi 5 コマンドで再起動します。
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: Restart with command.
- pi@raspberrypi:~ $ vcgencmd measure_clock arm
- _EN_: pi@raspberrypi:~ $ vcgencmd measure_clock arm
- Raspberry Pi 5 frequency(0)=2800037120
- ### 性能と熱の関係（Raspberry Pi 5）
- _In English_: Relationship between performance and heat (Raspberry Pi 5)
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- Raspberry Pi 5 性能を評価するため、以下のPythonコマンド（浮動小数点演算のループ）でテストしました：
- _EN_: To evaluate performance, we tested the following Python command (loop of floating point operations):
- Raspberry Pi 5 time python3 -c “import math; [math.sqrt(i) for i in range(10000000)]”
- _EN_: time python3 -c “import math; [math.sqrt(i) for i in range(10000000)]”
- Raspberry Pi 5 測定結果は以下の通りです。
- _EN_: The measurement results are as follows.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: | Clock | Processing time | Temperature after 3 minutes |
- ## ベンチマークで性能を比較（Raspberry Pi 5）
- _In English_: Compare performance with benchmarks (Raspberry Pi 5)
- ### 性能比較（Raspberry Pi 5）
- _In English_: Performance comparison (Raspberry Pi 5)
- Raspberry Pi 5 | 起動時間(s) | 18.74 | 11.8 | 11.5 |
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: | Startup time (s) | 18.74 | 11.8 | 11.5 |
- Raspberry Pi 5 | 書き込み時間(MB/s) | 37.0 | 26.0 | 25.9 |
- _EN_: | Write time (MB/s) | 37.0 | 26.0 | 25.9 |
- Raspberry Pi 5 | 読み込み時間(MB/s) | 45.5 | 93.5 | 94.1 |
- _EN_: | Loading time (MB/s) | 45.5 | 93.5 | 94.1 |
- Raspberry Pi 5 | １分間のFHD動画のエンコード時間 | ２分34秒 | 1分６秒 | 1分１秒 |
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: | Encoding time for 1 minute FHD video | 2 minutes 34 seconds | 1 minute 6 seconds | 1 minute 1 second |
- _EN_: The performance improvement from Raspberry Pi 4 to Raspberry Pi 5 is very noticeable, but the effects of overclocking will vary depending on the application.In particular, there was a slight speedup in certain processes such as video encoding, but in daily use there is no big difference.
- ## まとめ（Raspberry Pi 5）
- _In English_: Summary (Raspberry Pi 5)
- _EN_: I tried using Raspberry Pi for the first time in a while, and it was fun.
- - ラズパイ５は価格はアップしているが性能も大幅にアップしている
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- _EN_: - Although the price of Raspberry Pi 5 has increased, the performance has also improved significantly.
- - Raspberry Pi 5 性能に応じたキットも必要になっている
- _EN_: - Kits that match performance are also required.
- _EN_: - Overclocking is possible by installing an active cooler, but the performance improvement that can be experienced is limited.
- - 最新ラズパイOSではVNC接続時に日本語コピペに難があった
- _EN_: - With the latest Raspberry Pi OS, it was difficult to copy and paste Japanese when connecting to VNC.
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

- # Raspberry Pi 5 8GB
- _In English_: Raspberry Pi 5 8GB
- Raspberry Piシリーズ初のI/OコントローラーチップRP1を搭載し、Raspberry Pi 5のバージョンアップした豊富なインターフェース機能を提供しています。
- _EN_: Equipped with the first I/O controller chip in the Raspberry Pi series, RP1, it provides a wealth of interface functions that are an upgraded version of the Raspberry Pi 5.
- Raspberry Pi 5 ■主な仕様
- _EN_: ■Main specifications
  
Source: akizukidenshi_com_catalog_g_g129326.md

- Raspberry Pi 5 ・メーカー：Raspberry_Pi財団
- _EN_: ・Manufacturer: Raspberry_Pi Foundation
- Raspberry Pi 5 ・シリーズ：Flagship
- _EN_: ・Series: Flagship
- Raspberry Pi 5 ・電源電圧min.：5V
- _EN_: ・Power supply voltage min.: 5V
  
Source: akizukidenshi_com_catalog_g_g129326.md

- Raspberry Pi 5 ・電源電圧max：5V
- _EN_: ・Power supply voltage max: 5V
- Raspberry Pi 5 ・IO電圧min.：3.3V
- _EN_: ・IO voltage min.: 3.3V
- Raspberry Pi 5 ・IO電圧max.：3.3V
- _EN_: ・IO voltage max.: 3.3V
  
Source: akizukidenshi_com_catalog_g_g129326.md

- Raspberry Pi 5 ・拡張コネクター：Raspberry_Pi(40)
- _EN_: ・Expansion connector: Raspberry_Pi(40)
- Raspberry Pi 5 ・無線機能：Wi-Fi・Bluetooth
- _EN_: ・Wireless function: Wi-Fi/Bluetooth
- Raspberry Pi 5 ・工事設計認証(技適)番号：020-230329
- _EN_: ・Construction design certification (technical suitability) number: 020-230329
  
Source: akizukidenshi_com_catalog_g_g129326.md

- Raspberry Pi 5 ・長辺：85mm
- Raspberry Pi 5 ・短辺：56mm
- _In English_: Comparison of Raspberry Pi 4 and Raspberry Pi 5
- ## はじめに（Raspberry Pi 5）
- _In English_: Introduction (Raspberry Pi 5)
- Raspberry Pi 5の発表により、Raspberry Piの世界に新たな息吹が吹き込まれた。この時点で、あなたは "Raspberry Pi 5を待つべきか、それとも今Raspberry Pi 4を買うべきか？"と自問しているかもしれない。
  
Source: akizukidenshi_com_catalog_g_g129326.md; picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- Raspberry Pi 5 この記事では、両者のスペックを比較検討する。
- _EN_: In this article, we will compare and examine the specifications of the two.
- _EN_: Many of these interface improvements are due to a new I/O controller chip designed in-house at Raspberry Pi.
- Raspberry Pi 5 その通り、ラズベリー・パイは初めてフラッグシップ製品にラズベリー・パイのシリコンを搭載した、RP1と呼ばれるサウスブリッジチップだ。
- _EN_: That's right, the Raspberry Pi is the first flagship product to include Raspberry Pi silicon, a southbridge chip called the RP1.
- しかし、これらの詳細に入る前に、Raspberry Pi 4とRaspberry Pi 5の類似点と相違点を簡単に見てみよう。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: But before we get into these details, let's take a quick look at the similarities and differences between Raspberry Pi 4 and Raspberry Pi 5.
- ## 概要（Raspberry Pi 5）
- _In English_: Overview (Raspberry Pi 5)
- Raspberry Pi 4 | ラズベリーパイ5 | |
- _EN_: Raspberry Pi 4 | Raspberry Pi 5 | |
- Raspberry Pi 5 | SDスロット | マイクロSDカードスロット | マイクロSDカードスロット 高速SDR104モードをサポート |
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: | SD slot | Micro SD card slot | Micro SD card slot Supports high speed SDR104 mode |
- Raspberry Pi 5 | ブルートゥース | ブルートゥース5.0／ブルートゥース・ロー・エナジー（BLE） | ブルートゥース5.0／ブルートゥース・ロー・エナジー（BLE） |
- _EN_: | Bluetooth | Bluetooth 5.0/Bluetooth Low Energy (BLE) | Bluetooth 5.0/Bluetooth Low Energy (BLE) |
- Raspberry Pi 5 | オーディオジャック | 4極ステレオ・オーディオおよびコンポジット・ビデオ | いや！ |
- _EN_: | Audio Jack | 4-pole stereo audio and composite video | No!|
- Raspberry Pi 5 | RTC | いや | RTCおよびRTCバッテリコネクタ |
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: | RTC | No | RTC and RTC Battery Connector |
- Raspberry Pi 5 | 電源ボタン | いいえ | そうだ！ |
- _EN_: | Power button | No | Yes!|
- ## 何が同じなのか？（Raspberry Pi 5）
- _In English_: What is the same?(Raspberry Pi 5)
- Raspberry Pi 5 まず第一に、両者のサイズはほぼ同じだ。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: First of all, they are about the same size.
- ## 何が違うのか？（Raspberry Pi 5）
- _In English_: What's the difference?(Raspberry Pi 5)
- Raspberry Pi 5 では、その対照的な点を見ていこう！
- _EN_: Let's take a look at the contrast!
- ## ポート＆ペリフェラル（Raspberry Pi 5）
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _In English_: Ports & Peripherals (Raspberry Pi 5)
- 上述したように、どちらもマイクロSDカードスロットを搭載しているが、Raspberry Pi 5は高速SDR104モードをサポートしており、SDカードへのデータアクセスが圧倒的に速い。
- _EN_: As mentioned above, both are equipped with a micro SD card slot, but the Raspberry Pi 5 supports high-speed SDR104 mode, making data access to the SD card much faster.
- Raspberry Pi 5 冒頭で、私はRP1の重要性を強調した。RP1はこのパフォーマンス向上の大きな理由である。
- _EN_: At the beginning, I emphasized the importance of RP1.RP1 is a big reason for this performance improvement.
- Raspberry Pi 5 注意すべき重要な点は、これらの新しいコネクターは、現行の他のカメラやディスプレイ製品にあるような15極ではなく、22極だということだ。つまり、新しいPi用のアダプターケーブルが必要になるということだ。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: An important thing to note is that these new connectors have 22 pins, rather than 15 pins like other current camera and display products.That means you'll need an adapter cable for your new Pi.
- _EN_: Fortunately, Raspberry Pi has released a mini-to-standard adapter cable that works with the new MIPI connector.
- ## オーディオジャック（Raspberry Pi 5）
- _In English_: Audio jack (Raspberry Pi 5)
- すぐに気づく違いとしては、Raspberry Pi 4には4極のステレオ・オーディオ端子とコンポジット・ビデオ端子があり、オーディオとビデオの接続が可能だった。
- _EN_: One immediately noticeable difference was that the Raspberry Pi 4 had a 4-pole stereo audio jack and a composite video jack, allowing for audio and video connections.
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- 対照的に、Raspberry Pi 5にはオーディオジャックがない。
- _EN_: In contrast, the Raspberry Pi 5 doesn't have an audio jack.
- ## RTC（Raspberry Pi 5）
- _In English_: RTC (Raspberry Pi 5)
- _EN_: New features on the Raspberry Pi 5 are an RTC (Real Time Clock) and RTC battery connector for accurate timekeeping.
- RTCがあれば、Raspberry Pi 5を遠隔地のアプリケーションに役立てることができる。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: With RTC, Raspberry Pi 5 can be used for remote applications.
- Raspberry Pi 4には、もちろんRTCもRTCバッテリー用のコネクターもない。つまり、計時にはWiFiが必要なのだ。
- _EN_: Of course, the Raspberry Pi 4 doesn't have an RTC or a connector for an RTC battery.In other words, WiFi is required for timekeeping.
- ## 電源＆電源ボタン（Raspberry Pi 5）
- _In English_: Power & Power Button (Raspberry Pi 5)
- しかし、Raspberry Pi 4の5V/3A仕様に対し、Raspberry Pi 5は5V/5AのDC電源を必要とし、Power Delivery（PD）をサポートしている。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: However, compared to the 5V/3A specifications of Raspberry Pi 4, Raspberry Pi 5 requires a 5V/5A DC power supply and supports Power Delivery (PD).
- Raspberry Pi 5 この消費電力の増加は、パフォーマンスの増加と一致している。もちろん、Raspberry Pi 5は電力使用量の点でPi 4を上回っているだけではない。そのアーキテクチャのおかげで、Raspberry Pi 5はこの電力をよりうまく使うことができる。
- _EN_: This increase in power consumption is matched by an increase in performance.Of course, the Raspberry Pi 5 doesn't just outperform the Pi 4 in terms of power usage.Thanks to its architecture, the Raspberry Pi 5 can use this power better.
- また、Raspberry Pi 5には電源ボタンが搭載されていることも特筆すべき点だ！
- _EN_: It is also worth noting that the Raspberry Pi 5 has a power button!
- ## もっと見たい？（Raspberry Pi 5）
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _In English_: Want to see more?(Raspberry Pi 5)
- Raspberry Pi 5 待たされることがどれほどもどかしいか、私たちは知っている。だから、一刻も早く、皆さんに遊んでいただけるようにしたかったのです。
- _EN_: We know how frustrating it is to have to wait.That's why we wanted everyone to be able to play it as soon as possible.
- だから、ちょっとしたコンテストを準備しているんだ： *Raspberry Pi 5で思いつく最もクレイジーなことは何ですか？*
- _EN_: So I'm preparing a little contest: *What's the craziest thing you can come up with with Raspberry Pi 5?*
- Raspberry Pi 5 それを壊さない限り、あなたのアイデアを私たちに送っていただければ、私たちのアイデアでそれを実現します。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: As long as you don't break it, send us your idea and we will make it happen with our idea.
- 入賞したアイデアには、10月23日の正式発表前に、長文の専用記事と動画が掲載される。rd.その間、私たちは絶え間ないテストをアップロードし、私たちのRaspberry Pi 5であなたのアイデアを実現します。
- _EN_: The winning ideas will receive a dedicated long article and video before the official announcement on October 23rd.rd. Meanwhile, we will upload constant tests and bring your ideas to life on our Raspberry Pi 5.
- また、Raspberry Pi 5でチェックしてみたい、それほどクレイジーではないことも教えてください！
- _EN_: Also, let me know what not-so-crazy things you'd like to check out with the Raspberry Pi 5!
- Raspberry Pi 5 何かご質問があれば、お知らせください！
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: If you have any questions, please let us know!
- Raspberry Pi 5 下記のコメント欄、またはPiCockpitの公式お問い合わせページからご連絡ください。
- _EN_: Please let us know in the comments section below or via PiCockpit's official contact page.
- ## 結論（Raspberry Pi 5）
- _In English_: Conclusion (Raspberry Pi 5)
- まとめると、Raspberry Pi 5は単なるインクリメンタルなアップグレードではなく、性能の飛躍的な向上である。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: In summary, Raspberry Pi 5 is not just an incremental upgrade, but a quantum leap in performance.
- Raspberry Pi 5を使えば、デスクトップパソコンとして本当に使えるようになります。また、NASやSSDなど、大容量のデータ転送を必要とするものにも効果的に使うことができるだろう。
- _EN_: With Raspberry Pi 5, you can truly use it as a desktop computer.It can also be effectively used for devices that require large-capacity data transfer, such as NAS and SSD.
- Raspberry Pi 5についてもっと知りたい方は、記事「Raspberry Pi 5のファーストルック」をご覧ください。
- _EN_: To learn more about Raspberry Pi 5, check out our article "Raspberry Pi 5 First Look."
- しかし、Raspberry Pi 4は今でも信頼できるパートナーだ。動作温度もそれほど高くなく、価格も若干安い。あなたが組み立てようとしている多くのプロジェクトでは、Pi 4を信頼することができます。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: But the Raspberry Pi 4 remains a reliable companion.The operating temperature is not too high, and the price is slightly lower.You can rely on the Pi 4 for many projects you're looking to assemble.
- Raspberry Pi 4とRaspberry Pi 5の最も重要な違いは何ですか？以下にコメントを残してください！
- _EN_: What are the most important differences between Raspberry Pi 4 and Raspberry Pi 5?Please leave a comment below!
- Raspberry Pi 5 数カ月後、私は "支払い "を済ませたカードの有効期限が切れたことを知らされた。それでCM4は買えなくなった。CM4が期限切れになると、また手に入れることができるようだ。
- _EN_: A few months later, I was informed that the card I had "paid for" with had expired.So I can no longer buy CM4.It looks like you'll be able to get it again once CM4 expires.
- Raspberry Pi 5 Pi不足は大きく取り上げられたが、今年の回復はそれほど大きく取り上げられていない。しかし、あなたの欲望によっては、CM4はまだ時代遅れとは限らない。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- _EN_: While the Pi shortage has made headlines, this year's recovery hasn't.However, depending on your desires, CM4 may not be outdated yet.
- Raspberry Pi 5 pi4で発生したブルートゥースの通信距離の問題は修正されたのでしょうか？ある人は干渉だと言っていましたが、私のブルートゥースの通信距離はpi4では8-10フィート程度でした。
- _EN_: Has the Bluetooth communication distance problem that occurred with pi4 been fixed?Some people said it was interference, but my bluetooth range was about 8-10 feet with the pi4.
- Raspberry Pi 5 私のRaspberry Pi 5でBluetoothをテストして、詳細をご連絡します！
- _EN_: I'll test Bluetooth on my Raspberry Pi 5 and get back to you with more information!
- 私はラズベリーパイ4 8GBを持っていて、480GBのssdでツイスターを動かしている。ちょうどパイ5 8GBをクーラーと5amp電源£99で予約したところだ。これが有名なソフトウェアメーカーだったら、システムは始めるだけで£1000以上かかり、数年後には時代遅れになっているだろう。
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md

- Raspberry Pi 5 Pi5は後方互換性があるのか、もし可能なら、僕のPi4とPi5を組み合わせることができる。
- _EN_: Is the Pi5 backwards compatible? If so, can I combine my Pi4 and Pi5?
- Raspberry Pi 5 現在、彼らは新しいBookworm OSの仕上げを行っていますが、Pi 4sとRaspberry Pi 5を組み合わせることができるようになると思います。何に使うんですか？
- _EN_: They are currently putting the finishing touches on the new Bookworm OS, and I think it will be possible to mix and match the Pi 4s and Raspberry Pi 5.What do you use it for?
- # Raspberry Pi 5 / 8GB
- _In English_: Raspberry Pi 5/8GB
  
Source: picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md; www_switch-science_com_products_9250.md

- Raspberry Pi 5 発売日: 2024-02-13
- _EN_: Release date: 2024-02-13
- シングルボードコンピュータRaspberry Pi® 5の8 GBモデルです。4 GBモデルも取り扱いがあります。工事設計認証（いわゆる技適）を取得し、技適マークを表示した商品です。技適マークの表示は箱（パッケージ）にあるため、箱は捨てずに所持しておいてください。
- Raspberry Pi 5 5V / 5A供給可能な電源（ACアダプタ）については、準備を進めています。時期については本体の発売よりは時間がかかる見通しです。
- _EN_: We are currently preparing a power supply (AC adapter) that can supply 5V/5A.The timing is expected to take longer than the release of the main unit.
- Raspberry Pi 5 **汎用的な5.0 V/ 3.0 A出力の電源を使った場合の問題**
  
Source: www_switch-science_com_products_9250.md

- _EN_: **Issues when using a generic 5.0 V/3.0 A output power supply**
- ※Raspberry PiはRaspberry Pi財団の登録商標です。
- _EN_: *Raspberry Pi is a registered trademark of the Raspberry Pi Foundation.
- Raspberry Pi 5 **特長**
- _EN_: **Features**
- - Raspberry Pi 5 4Kp60 HEVCデコーダー
  
Source: www_switch-science_com_products_9250.md

- _EN_: - 4Kp60 HEVC decoder
- - Raspberry Pi 5 Bluetooth 5.0 / Bluetooth Low Energy (BLE)
- _EN_: - Bluetooth 5.0 / Bluetooth Low Energy (BLE)
- - Raspberry Pi 5 SDR104（高速区分）が利用可能なMicro SDカードスロット
- _EN_: - Micro SD card slot with SDR104 (high speed classification) available
- - Raspberry Pi 5 2 × 4レーンMIPI（カメラ/ディスプレイ用）
  
Source: www_switch-science_com_products_9250.md

- _EN_: - 2 x 4 lane MIPI (for camera/display)
- - Raspberry Pi 5 電源入力：
- _EN_: - Power input:
- - Raspberry Pi 5 推奨5 V/5 A（カスタムPD）
- _EN_: - Recommended 5 V/5 A (custom PD)
- - Raspberry Pi 5 最低5 V/3 A
  
Source: www_switch-science_com_products_9250.md

- _EN_: - Minimum 5V/3A
- - Raspberry Pi標準の40ピン ピンヘッダ
- _EN_: - Raspberry Pi standard 40-pin pin header
- _EN_: - Real-time clock (RTC) with external power supply (sold separately)
- - Raspberry Pi 5 電源ボタン搭載
- _EN_: - Equipped with power button
  
Source: www_switch-science_com_products_9250.md

- ### Raspberry Pi 5 2023年10月に英国で発売
- _In English_: Raspberry Pi 5 to be released in the UK in October 2023
- 以下が、Raspberry Pi 5の主な仕様だ。
- _EN_: Below are the main specifications of Raspberry Pi 5.
- Raspberry Pi 5 4K/60p HEVCデコーダー
- _EN_: 4K/60p HEVC decoder
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md

- Raspberry Pi 5 Bluetooth 5.0／Bluetooth Low Energy（BLE）
- _EN_: Bluetooth 5.0/Bluetooth Low Energy (BLE)
- Raspberry Pi 5 SDR104（高速区分）モードをサポートするMicro SDカードスロット
- _EN_: Micro SD card slot supporting SDR104 (high speed classification) mode
- Raspberry Pi 5 2×4レーンMIPI（カメラ／ディスプレイ用）トランシーバー
- _EN_: 2x4 lane MIPI (camera/display) transceiver
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md

- _EN_: Real-time clock with external power supply (sold separately)
- Raspberry Pi 5 ボード上に電源ボタン搭載
- _EN_: Power button installed on board
- Raspberry Pi 5 電源 最低5V／3A、推奨5V／5A
- _EN_: Power supply minimum 5V/3A, recommended 5V/5A
- # ラズベリーパイ5完全ガイド2025【技適対応・電源仕様・IoT開発】初心者からプロまで使える導入・活用・トラブル解決
  
Source: eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md; open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: Raspberry Pi 5 complete guide 2025 [Technical compliance, power supply specifications, IoT development] Installation, usage, and troubleshooting that can be used by everyone from beginners to professionals
- Raspberry Pi 5 目次
- _EN_: table of contents
- ## 1. ラズベリー パイ 5の概要（Raspberry Pi 5）
- _In English_: 1. Overview of Raspberry Pi 5 (Raspberry Pi 5)
- ### 最新モデルの特徴と性能（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: Features and performance of the latest model (Raspberry Pi 5)
- ### 技適対応状況（Raspberry Pi 5）
- _In English_: Technical compliance status (Raspberry Pi 5)
- Raspberry Pi 5 日本国内での使用に関して、ラズベリー パイ 5は技適マークを取得済みです。これにより、国内での無線通信機能の利用が法的に認められています。ただし、注意点として、一部の周辺機器やアドオンボードについては、個別に技適の確認が必要となる場合があります。
- ## 2. セットアップとシステム構築（Raspberry Pi 5）
- _In English_: 2. Setup and system construction (Raspberry Pi 5)
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- ### 推奨OSと対応状況（Raspberry Pi 5）
- _In English_: Recommended OS and compatibility (Raspberry Pi 5)
- Raspberry Pi OSが公式サポートされており、32ビット版と64ビット版の両方が利用可能です。特に、ラズパイ 5用に最適化された新バージョンでは、ハードウェアアクセラレーションが強化され、より快適な動作環境を実現しています。また、UbuntuやDebian、さらには特定用途向けのカスタムOSなど、多様なLinuxディストリビューションもサポートされています。
- ### 必要な周辺機器（Raspberry Pi 5）
- _In English_: Necessary peripherals (Raspberry Pi 5)
- ### 初期設定の手順（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: Initial setup steps (Raspberry Pi 5)
- ## 3. プログラミングと開発環境（Raspberry Pi 5）
- ### 対応プログラミング言語（Raspberry Pi 5）
- ラズベリー パイ 5は、多様なプログラミング言語に対応しています。Python、Java、C/C++といった主要な言語はもちろん、Node.js、Ruby、Goなども利用可能です。特にPythonは、豊富なライブラリとラズパイ向けの専用モジュールが用意されており、IoTプロジェクトの開発に適しています。
- ### 開発ツールとフレームワーク（Raspberry Pi 5）
- Raspberry Pi 5 Visual Studio CodeやThonnyなどの統合開発環境（IDE）が利用可能で、効率的な開発をサポートします。また、Docker対応により、コンテナベースの開発も可能になっています。Webアプリケーション開発では、Flask、Django、Express.jsなどの人気フレームワークが利用でき、IoTプラットフォームとしても、AWS IoTやAzure IoTとの連携が可能です。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- ### IoT開発環境の構築（Raspberry Pi 5）
- _In English_: Building an IoT development environment (Raspberry Pi 5)
- ### 教育現場での活用（Raspberry Pi 5）
- _In English_: Use in educational settings (Raspberry Pi 5)
- ラズベリー パイは教育分野で特に注目されています。Raspberry Pi 5の高性能化により、より実践的なプログラミング教育が可能になりました。例えば、Python言語を使用したプログラミング基礎教育では、LEDの制御から始まり、センサーデータの収集・分析、さらにはAIを活用した画像認識まで、段階的な学習が可能です。また、複数のラズパイをネットワークで接続し、分散システムの概念を学ぶための実習環境としても活用されています。
- ### IoTデバイスとしての実装（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: Implementation as an IoT device (Raspberry Pi 5)
- ### 家庭・オフィスでの活用（Raspberry Pi 5）
- _In English_: Use at home and office (Raspberry Pi 5)
- Raspberry Pi 5は、家庭やオフィスのスマート化にも貢献しています。例えば、ホームオートメーションのコントローラーとして、照明制御、温度管理、セキュリティカメラの監視などを一元化できます。また、ネットワークアタッチトストレージ（NAS）としての利用も人気で、低消費電力ながら十分な処理能力を持つファイルサーバーとして機能します。さらに、Compute Moduleを活用することで、組み込みシステムの開発プラットフォームとしても活用できます。
- ## 4. 性能評価と比較（Raspberry Pi 5）
- _In English_: 4. Performance evaluation and comparison (Raspberry Pi 5)
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- ### Pi 4との詳細比較（Raspberry Pi 5）
- _In English_: Detailed comparison with Pi 4 (Raspberry Pi 5)
- ### 競合製品との比較（Raspberry Pi 5）
- _In English_: Comparison with competitive products (Raspberry Pi 5)
- Raspberry Pi 5 シングルボードコンピュータ市場において、ラズベリー パイ 5は高いコストパフォーマンスを誇ります。特に注目すべきは、豊富な周辺機器とソフトウェアのエコシステムです。競合製品と比較して、開発リソースやコミュニティサポートが充実しており、トラブルシューティングや機能拡張が容易です。また、技適マークの取得により、日本国内での無線通信機能の利用が正式に認められている点も大きな利点です。
- ### ベンチマーク結果（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: Benchmark results (Raspberry Pi 5)
- Raspberry Pi 5 実際のベンチマークテストでは、特にグラフィック処理性能の向上が顕著です。OpenGLベースのテストでは、Pi 4と比較して最大4倍の性能を発揮します。また、機械学習タスクにおいても、TensorFlow Liteを使用した推論処理が大幅に高速化されています。これにより、リアルタイムの画像認識や自然言語処理など、より高度なアプリケーションの実装が可能になりました。
- ## 5. 購入・入手方法（Raspberry Pi 5）
- _In English_: 5. How to purchase/obtain (Raspberry Pi 5)
- ### 国内での販売状況（Raspberry Pi 5）
- _In English_: Domestic sales status (Raspberry Pi 5)
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- 日本国内でのラズベリー パイ 5の販売は、2024年より本格化しています。主要な販売チャネルとしては、電子部品専門店やオンラインマーケットプレイスがあります。ただし、世界的な半導体不足の影響で、一時的な品薄状態が続いている場合があります。Raspberry Pi財団は生産体制の強化を進めており、供給状況は徐々に改善されつつあります。
- ### 価格と入手時の注意点（Raspberry Pi 5）
- _In English_: Price and precautions when purchasing (Raspberry Pi 5)
- ラズパイ 5の価格は、モデルによって異なります。4GBモデルと8GBモデルが用意されており、それぞれ推奨小売価格が設定されています。ただし、需要と供給のバランスにより、実際の販売価格は変動する可能性があります。購入時は、技適マークの有無を確認することが重要です。また、電源アダプタやケースなどの必須アクセサリーの追加コストも考慮に入れる必要があります。
- ### 正規販売店情報（Raspberry Pi 5）
- _In English_: Authorized retailer information (Raspberry Pi 5)
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- Raspberry Pi 5の正規販売店は、日本国内に複数存在します。これらの販売店では、技適マーク付きの正規品が取り扱われており、製品保証やサポートも充実しています。また、多くの販売店では、必要な周辺機器やアクセサリーもセットで購入できるため、初心者でも安心して導入できます。オンラインでの購入時は、偽造品や並行輸入品に注意が必要です。7. トラブルシューティング
- ### 一般的な問題への対処法（Raspberry Pi 5）
- _In English_: How to deal with common problems (Raspberry Pi 5)
- ### 電源関連の課題解決（Raspberry Pi 5）
- _In English_: Solving power-related issues (Raspberry Pi 5)
- ### 性能最適化の方法（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: How to optimize performance (Raspberry Pi 5)
- ## 6. 周辺機器とハードウェア拡張（Raspberry Pi 5）
- _In English_: 6. Peripherals and hardware expansion (Raspberry Pi 5)
- ### 推奨周辺機器の選定（Raspberry Pi 5）
- _In English_: Selection of recommended peripherals (Raspberry Pi 5)
- ### 拡張ボードの活用（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: Utilizing expansion boards (Raspberry Pi 5)
- ## 7. 今後の展望と発展性（Raspberry Pi 5）
- _In English_: 7. Future outlook and development potential (Raspberry Pi 5)
- ### アップデート情報（Raspberry Pi 5）
- _In English_: Update information (Raspberry Pi 5)
- Raspberry Pi財団は、継続的なソフトウェアアップデートを提供しています。特に、Raspberry Pi OSの64ビット版の開発が活発で、より多くのアプリケーションやライブラリが64ビット環境に対応しつつあります。また、機械学習フレームワークの最適化や、コンテナ技術のサポート強化など、エンタープライズ用途での活用を見据えた開発も進んでいます。セキュリティアップデートも定期的に提供され、IoTデバイスとしての信頼性向上に貢献しています。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- ### 新機能と将来の可能性（Raspberry Pi 5）
- _In English_: New features and future possibilities (Raspberry Pi 5)
- ラズパイ 5の登場により、シングルボードコンピュータの可能性は大きく広がりました。特に、AIや機械学習の分野での活用が期待されています。エッジコンピューティングデバイスとしての性能が向上し、クラウドに依存しない独立したAI処理が可能になってきています。また、5G通信モジュールとの組み合わせにより、より高度なIoTソリューションの実現も視野に入ってきました。教育分野では、ARやVRを活用した新しい学習体験の提供も検討されています。
- ### コミュニティの動向（Raspberry Pi 5）
- _In English_: Community trends (Raspberry Pi 5)
- Raspberry Pi 5 世界中のラズベリー パイユーザーコミュニティは、活発な開発と情報共有を続けています。オープンソースプロジェクトの数は増加の一途を辿り、特にIoTやAI分野での革新的なプロジェクトが注目を集めています。日本国内でも、教育機関や企業での導入事例が増加しており、独自の活用方法や開発ノウハウが蓄積されつつあります。また、オンラインコミュニティでの情報交換も活発で、初心者から上級者まで、様々なレベルのユーザーが相互に学び合える環境が整っています。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- ## よくある質問と回答（Raspberry Pi 5）
- _In English_: Frequently asked questions and answers (Raspberry Pi 5)
- _In English_: Please tell me the main uses of Raspberry Pi 5.
- ### 必要な電源の仕様について教えてください（Raspberry Pi 5）
- _In English_: Please tell me the specifications of the required power supply (Raspberry Pi 5)
- ### 日本での技適対応状況はどうなっていますか（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: What is the technical compliance status in Japan? (Raspberry Pi 5)
- Raspberry Pi 5 ラズベリー パイ 5は技適マークを取得済みで、日本国内での無線通信機能の使用が正式に認められています。ただし、追加で接続する無線モジュールやアドオンボードについては、個別に技適認証の確認が必要です。購入時は必ず技適マークの有無を確認することをお勧めします。
- ### 推奨されるOSと対応状況を教えてください（Raspberry Pi 5）
- _In English_: Please tell me the recommended OS and compatibility (Raspberry Pi 5)
- 標準的なOSとして、Raspberry Pi OS（32ビット/64ビット）が推奨されています。その他、Ubuntu、Debian、特定用途向けのカスタムLinuxディストリビューションなども利用可能です。特にRaspberry Pi OS 64ビット版は、ラズパイ 5のハードウェア性能を最大限に活用できるよう最適化されています。
- ### ラズベリー パイ 5はどのように開発されたのか？（Raspberry Pi 5）
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: How was Raspberry Pi 5 developed?(Raspberry Pi 5)
- ラズベリー パイ 5は、Raspberry Pi 財団とEben Uptonによって開発され、前世代よりも高性能なプロセッサとPCI Express対応が特徴です。
- _EN_: Raspberry Pi 5 was developed by the Raspberry Pi Foundation and Eben Upton and features a higher-performance processor and PCI Express support than previous generations.
- ### Raspberry Pi 5はいつ発売されるのか？
- _In English_: When will Raspberry Pi 5 be released?
- Raspberry Pi 5は、2025年に発売される予定で、Amazonなどの主要な販売サイトでも取り扱いが予想されています。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _EN_: Raspberry Pi 5 is scheduled to be released in 2025, and is expected to be available on major sales sites such as Amazon.
- ### Raspberry Pi 5の技適対応状況は？
- _In English_: What is the technical compliance status of Raspberry Pi 5?
- Raspberry Pi 5は、日本国内での使用に必要な技適認証を取得しており、正式に使用可能なデバイスとなっています。
- _EN_: Raspberry Pi 5 has obtained the technical compliance certification required for use in Japan, making it an officially usable device.
- ### Raspberry Pi 5とRaspberry Pi 4の違いは？
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: What is the difference between Raspberry Pi 5 and Raspberry Pi 4?
- ### Raspberry Pi 5用の電源仕様は？
- _In English_: What are the power specifications for Raspberry Pi 5?
- ### Raspberry Pi シリーズの中でRaspberry Pi 5の特徴は？
- _In English_: What are the features of Raspberry Pi 5 in the Raspberry Pi series?
- Raspberry Pi シリーズの中でも、Raspberry Pi 5は特にIoT開発向けに最適化されており、PCI Expressを利用した高速データ転送が可能です。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _EN_: Among the Raspberry Pi series, Raspberry Pi 5 is especially optimized for IoT development and enables high-speed data transfer using PCI Express.
- ### Raspberry Pi Compute Moduleとは？
- _In English_: What is Raspberry Pi Compute Module?
- Raspberry Pi Compute Moduleは、組み込みシステム向けに開発されたモジュール型のRaspberry Piで、カスタム基板に組み込むことが可能です。
- _EN_: Raspberry Pi Compute Module is a modular Raspberry Pi developed for embedded systems and can be incorporated into custom boards.
- ### Raspberry Pi 500とは？
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _In English_: What is Raspberry Pi 500?
- Raspberry Pi 500は、一体型のコンピューターで、キーボードと統合されたデザインが特徴です。Raspberry Pi 5をベースにした製品が登場する可能性があります。
- _EN_: The Raspberry Pi 500 is an all-in-one computer, featuring an integrated keyboard design.Products based on Raspberry Pi 5 may appear.
- ### ラズベリー パイの世界累計出荷台数は？（Raspberry Pi 5）
- _In English_: What is the total number of Raspberry Pi shipped worldwide?(Raspberry Pi 5)
- Raspberry Pi 5 ラズベリー パイは、これまでに世界累計で数千万台以上が出荷され、教育用途やIoT開発で広く利用されています。
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

- _EN_: To date, more than tens of millions of Raspberry Pi units have been shipped worldwide, and they are widely used for educational purposes and IoT development.
  
Source: open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md

## 4. セットアップ・チュートリアル / Setup & Tutorials

**Keywords (EN):** setup guide, Raspberry Pi OS Bookworm, installation steps, first boot

- ## ラズパイOSのインストール
  
Source: take1bit_com_computer-ja_raspi5tutorial.md

## 5. 比較・互換性 / Comparisons & Compatibility

**Keywords (EN):** Raspberry Pi 5 vs 4B comparison, compatibility

- _EN_: (Pi 4)
- ラズパイ４と５の比較表です。
- # ラズベリーパイ4とラズベリーパイ5の比較
  
Source: pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md; picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md; take1bit_com_computer-ja_raspi5tutorial.md

## 8. 出典一覧 / Sources

- akizukidenshi_com_catalog_g_g129326.md  
- eetimes_itmedia_co_jp_ee_articles_2309_28_news177_html.md  
- japan_zdnet_com_article_35209685.md  
- open-insight_net_blog_semiconductor_raspberry-pi-5-complete-guide-2025.md  
- pc_watch_impress_co_jp_docs_column_hothot_1584619_html.md  
- picockpit_com_raspberry-pi_ja_%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A44%E3%81%A8%E3%83%A9%E3%82%BA%E3%83%99%E3%83%AA%E3%83%BC%E3%83%91%E3%82%A45%E3%81%AE%E6%AF%94%E8%BC%83.md  
- take1bit_com_computer-ja_raspi5tutorial.md  
- www_switch-science_com_products_9250.md  
