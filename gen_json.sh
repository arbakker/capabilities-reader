#!/usr/bin/env bash

rm -f output/*
cap_url="https://geodata.nationaalgeoregister.nl/regionale-fietsnetwerken/wms?request=getcapabilities&service=wms"; convert-cap $cap_url --service-type WMS > output/temp ; mv output/temp output/$(cat output/temp | jq -r ".md_identifier").json

cap_url="https://geodata.nationaalgeoregister.nl/regionale-wandelnetwerken/wms?request=getcapabilities&service=wms"; convert-cap $cap_url --service-type WMS > output/temp ; mv output/temp output/$(cat output/temp | jq -r ".md_identifier").json


