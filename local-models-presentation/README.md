# Markdown の HTML 版

元の `最近ローカルでよく使っているモデル.md` を直接変換しています。本文の文言・順序・見出し・表の内容は変更していません。プレゼン用のコピーやスライド操作はありません。

## 開くファイル

- **親フォルダの `最近ローカルでよく使っているモデル.html`**: 画像・動画・音声をすべて内包した単体版です。Finderからブラウザで開けます。約63 MiBありますが、別の素材フォルダを必要としません。
- `dist/index.html`: ホスティング向けの軽量版です。`dist/assets/` とセットで配置してください。
- `presentation.zip`: `dist/` の中身をまとめた公開用ファイルです。元の同梱素材も含まれます。

動画は映像を再圧縮せず MP4 コンテナに変換し、先頭フレームをプレビュー画像にしています。FLAC は再生用に AAC/M4A に変換しています。元の動画・音声・画像も公開用ZIPに保持しています。

## 更新方法

本文は元の Markdown を編集してください。HTML の本文を手で直す必要はありません。

初回のみ、このフォルダの親で以下を実行します。

```sh
python3 -m venv local-models-presentation/.venv
local-models-presentation/.venv/bin/python -m pip install -r local-models-presentation/requirements.txt
```

生成:

```sh
local-models-presentation/.venv/bin/python local-models-presentation/build.py
```

`template.html` は文書の外枠とCSSです。`asset-report.json` に素材一覧を記録します。

## ホスティング

配信先: https://grgr-dkrk.github.io/md-test/

リポジトリ: https://github.com/grgr-dkrk/md-test

`main` に push すると、GitHub Actions が `dist/` を GitHub Pages にデプロイします。原稿や素材を編集した場合は、先に上記の生成コマンドを実行し、原稿・素材・生成結果をまとめてコミットしてください。

GitHub Pages とリポジトリは公開設定です。画像・動画・音声を含め、URLから閲覧できます。

Cloudflare Pages は1ファイル25 MiBの上限があり、今回の翻訳動画と単体HTMLはそのままでは配置できません。動画の圧縮や外部ストレージへの分離が必要です。

- [GitHub Pages の作成](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [公開元の設定](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Pages の制限](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [Cloudflare Pages の制限](https://developers.cloudflare.com/pages/platform/limits/)

上記の公式ドキュメント確認日: 2026-11-13。
