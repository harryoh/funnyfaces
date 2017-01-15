#!/bin/bash

pushd packages;zip -r ../packages.zip *;popd
zip packages.zip funnyfaces.py config.py

aws lambda update-function-code \
    --function-name GetFaceRecognition \
    --zip-file fileb://packages.zip

rm -f packages.zip

#aws lambda create-function \
#    --region ap-northeast-2 \
#    --runtime python2.7 \
#    --role arn:aws:iam::550931752661:role/funnyfaces-role \
#    --descript 'funnyfaces function' \
#    --timeout 10 \
#    --memory-size 128 \
#    --handler funnyfaces.handler \
#    --zip-file fileb://funnyfaces.zip  \
#    --function-name GetFaceAnalysisFromGoogle
