# 最近ローカルでよく使っているモデル

元の Markdown を、画像・動画・音声を含む HTML として配信します。

- サイト: https://grgr-dkrk.github.io/md-test/
- 原稿: [最近ローカルでよく使っているモデル.md](最近ローカルでよく使っているモデル.md)
- 生成方法: [local-models-presentation/README.md](local-models-presentation/README.md)

## 更新

GitHub 上で原稿を編集して `main` にコミットするだけで、GitHub Actions が HTML の生成と公開を自動で行います。ローカルでのビルドは不要です。素材を追加・変更した場合も、その素材を一緒にコミットしてください。

ローカルで HTML を確認する場合は、次を実行して生成します。

```sh
local-models-presentation/.venv/bin/python local-models-presentation/build.py
```

変更した原稿・素材をコミットして `main` に push すると、GitHub Actions が `local-models-presentation/dist/` を再生成して GitHub Pages にデプロイします。

画像・音声・動画は相対URLで参照しています。ローカルで単体利用するための大きな埋め込み HTML、ZIP、仮想環境は Git 管理の対象外です。
