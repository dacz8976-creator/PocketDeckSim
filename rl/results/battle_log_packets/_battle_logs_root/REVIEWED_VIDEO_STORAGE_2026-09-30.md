# Reviewed video storage

September 30, 2026. 91 of 91 completed videos are confirmed online-only. Local video allocation fell from 43.93 GB to 0.00 GB, releasing 43.93 GB.

All 91 filenames and logical sizes are unchanged, and Windows reports their cloud contents in sync. No original was deleted. The review packets, index, archive receipts and source hashes remain available.

The original videos remain in OneDrive's Reviewed folder. Opening a video later downloads it again. The review workflow now requests online-only storage after archive verification and sync, then checks local allocation without reopening the video.

Evidence: [storage receipts](Recording_QA/CLOUD_STORAGE/RESULTS_2026-09-30.json). The operation uses [Microsoft's supported online-only command](https://learn.microsoft.com/en-us/sharepoint/files-on-demand-windows).
