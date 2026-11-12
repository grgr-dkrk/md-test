# 最近ローカルでよく使っているモデル

元の Markdown を、画像・動画・音声を含む HTML として配信します。

- サイト: https://grgr-dkrk.github.io/md-test/
- 原稿: [最近ローカルでよく使っているモデル.md](最近ローカルでよく使っているモデル.md)
- 生成方法: [local-models-presentation/README.md](local-models-presentation/README.md)

## 更新

原稿や素材を編集し、次を実行して HTML を生成します。

```sh
local-models-presentation/.venv/bin/python local-models-presentation/build.py
```

変更した原稿・素材・生成結果をコミットして `main` に push すると、GitHub Actions が `local-models-presentation/dist/` を GitHub Pages にデプロイします。

画像・音声・動画は相対URLで参照しています。ローカルで単体利用するための大きな埋め込み HTML、ZIP、仮想環境は Git 管理の対象外です。
