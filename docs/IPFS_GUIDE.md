# IPFS Guide

IPFS stores the images and metadata by content (a CID is a fingerprint of the files).
**Pinning** keeps them online. We use Pinata; add a second pinning service as backup.

## Setup
1. Create a Pinata account (founder's email). Check the plan's storage/file limits — 10,000 PNGs at 1024px are roughly 5–15 GB depending on the art.
2. Pinata → API Keys → New Key (admin or pinFileToIPFS) → copy the **JWT**.
3. On your computer: `export PINATA_JWT=...` (never commit it).

## Workflow (inside `art/`)
```bash
python3 ipfs_upload.py hidden      # BEFORE deploy: mystery image + hidden.json -> UNREVEALED_URI
python3 ipfs_upload.py check       # offline pre-flight: all files present, validated, no placeholders
python3 provenance.py              # provenance hash to publish on-chain before minting
python3 ipfs_upload.py images      # uploads images (named by planned character) -> IMAGES_CID
# ... mint happens, then on-chain reveal gives startingIndex N ...
python3 ipfs_upload.py metadata --starting-index N   # per-token JSON with real IMAGES_CID -> METADATA_CID
python3 ipfs_upload.py verify      # downloads a sample via gateway, compares checksums
python3 ipfs_upload.py verify --all
```
Everything is recorded in `art/output/ipfs/ipfs_record.json` (CIDs, timestamps, verification). Commit that file.
The owner then calls `reveal("ipfs://<METADATA_CID>/")`.

## Rules
- Never type a CID by hand from memory; copy from `ipfs_record.json`.
- Never deploy mainnet with a placeholder baseURI (the deploy script blocks it).
- Re-uploading the same files gives the same CID; changing one pixel changes the CID.
- Backup pin: upload the same folders to a second provider (e.g. Filebase, 4EVERLAND) and confirm the CIDs match.

## Status
Nothing has been uploaded yet (final art not delivered).
