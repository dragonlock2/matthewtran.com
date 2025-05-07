#!/bin/sh

cd /data
exec ~/p2pool \
    --mini \
    --host 127.0.0.1 \
    --wallet 42j7pyNRf8WE96D1xb6pjPWCwaDaYYevwZSPpELbTJjnXiKp7Lhtahbhb5Gc3p2BVxgMB3FEGNPUcbST1oZds6nBERA4jrQ \
    --merge-mine tari://127.0.0.1:18102 12AZgW4PXRsmsAzWEmfmGtBy1KKvYYKA2VByvjFBqEa7ZmuL3vrfcaA5oo5DogAPWpVyTGdfKkdLktYCQz5vVUD4Zir
