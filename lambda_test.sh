#!/bin/bash
PYTHONPATH=packages emulambda -v funnyfaces.lambda_handler s3put_event.json
