# Gemini attempt status: 20260908_022627000_iOS.MP4

## Source

- Size: 1,351,891,106 bytes
- SHA-256: `5689A2C45EDA9B0629D7A2616852BEEF6FEDB8396BDFE34C080B4C136E4E364E`
- Duration: 721.047 seconds
- Conservative estimate: $1.1385

## Attempt record

The first launch stopped locally because the conservative estimate exceeded the default $1 cap. No Gemini request was sent during that launch.

The run was restarted with a $2 cap, consistent with the owner's approval. Gemini returned `429 RESOURCE_EXHAUSTED` during the blind identity preflight after the client's built-in retries. No preflight result, main battle review, or result archive was produced. No completed Gemini usage record was returned, so exact billed usage for the failed API attempt is unknown.

## Disposition

- The source video remains unchanged in the main Battle Logs folder.
- It has not been moved to Reviewed.
- No battle claims have been accepted.
- The temporary source video and manifest were removed from Cloud Storage.
- The bucket retains only the v6 and v7 parser packages.
- Retry later when Google capacity is available.
