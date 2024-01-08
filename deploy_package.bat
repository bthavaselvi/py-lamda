@echo off
rmdir /s /q package
mkdir package

pip install  --no-user -r requirements.txt -t .\package

copy app.py .\package
copy lambda_function.py .\package
copy BusinessCard.py .\package


cd package
zip -r ..\lambda_package.zip .
cd ..
