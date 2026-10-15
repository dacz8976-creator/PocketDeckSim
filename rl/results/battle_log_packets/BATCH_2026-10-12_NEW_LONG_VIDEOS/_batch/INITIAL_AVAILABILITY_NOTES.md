# October 12 two long uploads

Intake is pending readable local sources. No visual review, full-review registration, external game entry or archive move has occurred for either source.

| Source | Logical bytes | Status |
| --- | ---: | --- |
| 20261012_010706000_iOS.MP4 | 1,531,356,838 | Cloud placeholder, zero locally allocated video bytes |
| 20261012_203719000_iOS.MP4 | 1,496,457,121 | Appeared during intake; cloud placeholder, zero locally allocated video bytes |

The older October 11 batch's three recordings are completed and archived. They were not reopened. These are the two newest unreviewed uploads requested by the owner. Source contents and names remain intact in the main queue.

The first ordinary source-hash request stalled without downloading bytes. Only its task-owned Python processes were stopped, and its verified abandoned review-log lock was cleared after checking the owner process was gone. No new shared review event had been written. Each source then received a serial Cloud Files download request using an attribute-only handle. Both timed out after 45 seconds and still showed zero allocated bytes. See each source's source_access_history folder.

A single graceful OneDrive shutdown was requested to recover downloads. The existing sync clients did not exit within the first bounded check. They exited later, and OneDrive was restarted in the background. New sync client processes were verified. The dedicated shutdown request helper was stopped after the initial check. No reset, unlink, settings changes or forced termination of existing sync clients occurred.

Windows app restoration and launch both failed with `GetCursorPos failed: Access is denied. (0x80070005)`. App inventory remained readable, but desktop input was unavailable. The in-app public Pause Games page loaded, but the database was unavailable without the owner's sign-in. No external data was changed.

Both sources are now requested to remain locally available with OneDrive's pinned preference. This preference is a download request, not proof that bytes are available. FINAL_AVAILABILITY.json contains the final metadata-only check. SHA-256, duration, recording classification and number of games remain unknown until the sources can be read.

Resume after the laptop desktop is accessible and OneDrive has downloaded these two sources. Bind size, stable modification time, SHA-256 and duration before assigning a fresh Sol full-file reviewer. Check shared events and index again before claiming either source. Classify from footage before routing to Pause Games or Ladder Log; visible Auto even OFF means computer. For multiple games, retain one game packet per match plus full source coverage. Follow the current independent acceptance, logging, archive and OneDrive storage gates. Do not reopen accepted recordings or the older paused backlog.
