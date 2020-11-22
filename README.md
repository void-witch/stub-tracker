# stub-tracker

a handy tool to track which methods/functions still need stubs

## installation

pip:
```bash
pip install git+https://github.com/3n-k1/stub-tracker.git
```

poetry - add the following to your pyproject.toml:
```toml
[tool.poetry.dev-dependencies]
stub-tracker = { git = "https://github.com/3n-k1/stub-tracker.git", branch = "main" }
```

## usage

```bash
python -m stub_tracker <source_root> <stub_root>
```

## license

stub-tracker is licensed under the mit/expat license. see the [license file](./LICENSE) for more details

## contributing

1. fork it (<https://github.com/3n-k1/stub-tracker/fork>)
2. create your feature branch (`git checkout -b my-new-feature`)
3. commit your changes (`git commit -am 'Add some feature'`)
4. push to the branch (`git push origin my-new-feature`)
5. create a new pull request

## contributors

- [proxi](https://github.com/3n-k1) - creator and maintainer
