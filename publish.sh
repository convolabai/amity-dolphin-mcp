echo "Publishing package to PyPI..."
rm -rf ./dist/* && pipx run build && pipx run twine upload dist/* && rm -rf ./dist/*
echo "Package published successfully."