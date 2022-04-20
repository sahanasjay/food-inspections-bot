#!/bin/bash

echo starting scrape
wget https://data.princegeorgescountymd.gov/api/views/umjn-t2iz/rows.csv? -O food_inspections.csv
python app.py
