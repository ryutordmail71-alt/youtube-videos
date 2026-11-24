import subprocess, sys
sys.path.insert(0, '/home/claude/video')
from compose import timeline
from scripts import MOVES, FILES, ORDER

BGM = '/root/.claude/uploads/3f2fb178-41da-56af-8da6-007907094230/3b3c1c5d-_____.mp3'
SRC = '/home/claude/video/out'
DST = '/home/claude/video/out/final_long'

for k in (sys.argv[1:] or ORDER):
    lines = MOVES[k]['lines']
    tl, dur = timeline(lines, k)
    gpre = [a for (a, b), ln in zip(tl, lines) if ln.get('gag_pre')][0]
    gag = [a for (a, b), ln in zip(tl, lines) if ln.get('gag')][0]
    cut0, back0 = gpre, gag + 1.3            # music stops for the build-up and the hit, then returns
    vol = (f"volume=eval=frame:volume='0.24*if(lt(t,{cut0}),1,if(lt(t,{cut0}+0.25),1-(t-{cut0})/0.25,"
           f"if(lt(t,{back0}),0,min(1,(t-{back0})/1.2))))'")
    fo = dur - 1.6
    fc = (f"[1:a]atrim=start=23,asetpts=PTS-STARTPTS,aresample=44100,{vol},afade=t=in:d=0.8,afade=t=out:st={fo:.2f}:d=1.5[bg];"
          f"[0:a]aresample=44100,asplit=2[v][key];[bg][key]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=400[bgd];"
          f"[v][bgd]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    f = FILES[k]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{SRC}/{f}.mp4', '-i', BGM, '-filter_complex', fc,
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
                    f'{DST}/{f}.mp4'], check=True)
    subprocess.run(['cp', f'{SRC}/{f}.srt', f'{DST}/'])
    print(k, f'{dur:.1f}s', 'music cut', round(cut0, 1), '->', round(back0, 1), flush=True)
