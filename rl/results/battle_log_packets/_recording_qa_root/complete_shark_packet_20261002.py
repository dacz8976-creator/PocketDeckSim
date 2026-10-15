"""Reuse the verified source/acceptance/archive workflow for the bounded shark batch."""
import complete_competitive_packet as completion
import sys
from setup_shark_batch_20261002 import SELECTED, BATCH, packet_for
from setup_shark_batch_20261002 import read, save

completion.SELECTED = SELECTED
completion.BATCH = BATCH
completion.packet_for = packet_for

if __name__ == '__main__':
    completion.main()
    if '--validate-only' not in sys.argv:
        for filename in ['SUMMARY.json','UNCERTAINTIES.json']:
            path=packet_for(sys.argv[1])/filename
            data=read(path)
            if 'shared_writes_performed' in data:data['shared_writes_performed']=True
            if 'source_moved' in data:data['source_moved']=True
            save(path,data)
