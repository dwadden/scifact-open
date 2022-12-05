# Download and decompress data.

gdown https://drive.google.com/uc?id=1sz-9hJTVex8h_jm_NPjXfmTrhi_8Sz-U
tar -xvf scifact_open.tar.gz
mv scifact_open/data .
mv scifact_open/prediction .
rmdir scifact_open
rm scifact_open.tar.gz
