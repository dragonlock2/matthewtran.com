#!/bin/sh

cleanup() {
    tmux send-keys stop Enter
}

trap 'cleanup' TERM

rm log
mkfifo log
tmux new -d 'LD_LIBRARY_PATH=. ./bedrock_server > log'
cat log &
wait $! # wait for SIGTERM
wait $! # wait for server to stop
