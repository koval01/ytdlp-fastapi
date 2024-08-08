#!/bin/bash
WORKERS=$(( $(nproc) * 2 + 1 ))
uvicorn app.main:app --workers $WORKERS --host=0.0.0.0 --port=$PORT --loop uvloop --http h11

